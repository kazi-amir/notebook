#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
#
#  Pass-to-Pass Validation (with Docker)
#
#  Builds a Docker image, runs tests BEFORE and AFTER applying the golden
#  patch, then checks that all previously-passing tests still pass.
#
#  Expected layout in APP_DIR:
#
#    /app/
#    |-- Dockerfile                (required)
#    |-- run_script.sh             (required)
#    |-- parsing.py                (required)
#    |-- golden.patch              (required)
#    `-- reproduction_script.sh    (optional Ã¢â‚¬â€ run if present and non-empty)
#
#  Output files (all written to APP_DIR):
#
#    before.json                   -- parsed test results before golden patch
#    after.json                    -- parsed test results after golden patch
#    run_before_stdout.txt         -- stdout from test run (before)
#    run_before_stderr.txt         -- stderr from test run (before)
#    run_after_stdout.txt          -- stdout from test run (after)
#    run_after_stderr.txt          -- stderr from test run (after)
#    golden_patch_apply_stderr.txt -- stderr from applying golden patch
#    fail_to_pass.json             -- tests that went FAILED -> PASSED
#    pass_to_pass.json             -- tests that stayed PASSED
#    reproduction_before_stdout.txt  (only if reproduction_script.sh present)
#    reproduction_before_stderr.txt  (only if reproduction_script.sh present)
#    reproduction_after_stdout.txt   (only if reproduction_script.sh present)
#    reproduction_after_stderr.txt   (only if reproduction_script.sh present)
#
# =============================================================================

APP_DIR="$(pwd)/app"
IMAGE_TAG="p2p-validator:latest"
CONTAINER_ID=""

# =============================================================================
# Derived paths
# =============================================================================
DOCKERFILE="${APP_DIR}/Dockerfile"
RUN_SCRIPT="${APP_DIR}/run_script.sh"
PARSING_SCRIPT="${APP_DIR}/parsing.py"
GOLDEN_PATCH="${APP_DIR}/golden.patch"
REPRO_SCRIPT="${APP_DIR}/reproduction_script.sh"
STAGING_DIR="${APP_DIR}/.staging"

# =============================================================================
# Cleanup on exit: stop container, remove image, remove staging dir
# =============================================================================
cleanup() {
    [[ -n "$CONTAINER_ID" ]] && docker stop "$CONTAINER_ID" >/dev/null 2>&1 || true
    docker rmi "$IMAGE_TAG" >/dev/null 2>&1 || true
    rm -rf "$STAGING_DIR"
}
trap cleanup EXIT

# =============================================================================
# PRE-FLIGHT
# =============================================================================
echo ""
echo "============================================================"
echo "PassToPass Validation (with Docker)"
echo "============================================================"
echo "  APP_DIR: ${APP_DIR}"

MISSING=()
for f in "$DOCKERFILE" "$RUN_SCRIPT" "$PARSING_SCRIPT" "$GOLDEN_PATCH"; do
    if [[ ! -f "$f" ]]; then
        MISSING+=("$(basename "$f")")
    fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "ERROR: Required file(s) not found in ${APP_DIR}: ${MISSING[*]}" >&2
    exit 1
fi

HAS_REPRO=false
if [[ -f "$REPRO_SCRIPT" && -s "$REPRO_SCRIPT" ]]; then
    HAS_REPRO=true
    echo "  Found reproduction_script.sh"
fi

mkdir -p "$STAGING_DIR"

# =============================================================================
# Helpers
# =============================================================================

stage_patch() {
    local src="$1" dest="$2"
    tr -d '\r' < "$src" > "$dest"
    if [[ -s "$dest" ]] && [[ -n "$(tail -c 1 "$dest")" ]]; then
        echo "" >> "$dest"
    fi
}

# =============================================================================
# STEP 1: Stage patches (fix CRLF + trailing newline)
# =============================================================================
echo ""
echo "[STEP 1/5] Staging patches..."
stage_patch "$GOLDEN_PATCH" "${STAGING_DIR}/golden.patch"
echo "  Staged golden.patch"

# =============================================================================
# STEP 2: Build Docker image
# =============================================================================
echo ""
echo "[STEP 2/5] Building image ${IMAGE_TAG}..."
docker build -t "$IMAGE_TAG" -f "$DOCKERFILE" "$APP_DIR"
echo "  Built image: ${IMAGE_TAG}"

# =============================================================================
# STEP 3: Start container
# =============================================================================
echo ""
echo "[STEP 3/5] Starting container..."
CONTAINER_ID=$(docker run -d --rm "$IMAGE_TAG" -c "sleep infinity")
echo "  Container ID: ${CONTAINER_ID:0:12}"

# Copy files into the container
docker cp "$PARSING_SCRIPT"                       "${CONTAINER_ID}:/app/parsing.py"
docker cp "$RUN_SCRIPT"                           "${CONTAINER_ID}:/app/run_script.sh"
docker cp "${STAGING_DIR}/golden.patch"           "${CONTAINER_ID}:/app/golden.patch"
if $HAS_REPRO; then
    docker cp "$REPRO_SCRIPT"                     "${CONTAINER_ID}:/app/reproduction_script.sh"
fi

# =============================================================================
# STEP 4: Run test chain inside container
# =============================================================================
echo ""
echo "[STEP 4/5] Running test chain inside container..."

# --- Before golden patch ---

if $HAS_REPRO; then
    echo "  Running reproduction script (before)..."
    docker exec -u root -w /app "$CONTAINER_ID" \
        /bin/bash -c 'bash reproduction_script.sh > reproduction_before_stdout.txt 2> reproduction_before_stderr.txt || true'
fi

echo "  Running run_script.sh (before)..."
docker exec -u root -w /app "$CONTAINER_ID" \
    /bin/bash -c 'bash run_script.sh > run_before_stdout.txt 2> run_before_stderr.txt || true'

echo "  Parsing before.json..."
docker exec -u root -w /app "$CONTAINER_ID" \
    /bin/bash -c 'python3 parsing.py run_before_stdout.txt run_before_stderr.txt before.json || echo "{\"tests\": []}" > before.json'

# --- Apply golden patch ---

echo "  Applying golden patch..."
docker exec -u root -w /app "$CONTAINER_ID" \
    /bin/bash -c 'git apply --ignore-space-change --ignore-whitespace golden.patch 2> golden_patch_apply_stderr.txt || echo "WARNING: golden patch failed to apply"'

# --- After golden patch ---

if $HAS_REPRO; then
    echo "  Running reproduction script (after)..."
    docker exec -u root -w /app "$CONTAINER_ID" \
        /bin/bash -c 'bash reproduction_script.sh > reproduction_after_stdout.txt 2> reproduction_after_stderr.txt || true'
fi

echo "  Running run_script.sh (after)..."
docker exec -u root -w /app "$CONTAINER_ID" \
    /bin/bash -c 'bash run_script.sh > run_after_stdout.txt 2> run_after_stderr.txt || true'

echo "  Parsing after.json..."
docker exec -u root -w /app "$CONTAINER_ID" \
    /bin/bash -c 'python3 parsing.py run_after_stdout.txt run_after_stderr.txt after.json || echo "{\"tests\": []}" > after.json'

# --- Copy results back to host ---

echo "  Copying results back to host..."
for f in before.json after.json \
         run_before_stdout.txt run_before_stderr.txt \
         run_after_stdout.txt run_after_stderr.txt \
         golden_patch_apply_stderr.txt; do
    docker cp "${CONTAINER_ID}:/app/${f}" "${APP_DIR}/${f}" 2>/dev/null || true
done

if $HAS_REPRO; then
    for f in reproduction_before_stdout.txt reproduction_before_stderr.txt \
             reproduction_after_stdout.txt reproduction_after_stderr.txt; do
        docker cp "${CONTAINER_ID}:/app/${f}" "${APP_DIR}/${f}" 2>/dev/null || true
    done
fi

echo "  Results copied."

# =============================================================================
# STEP 5: Generate fail_to_pass.json, pass_to_pass.json, and validate
# =============================================================================
echo ""
echo "[STEP 5/5] Generating fail_to_pass.json and pass_to_pass.json..."

python3 << PYEOF
import json, sys

def load_tests(path):
    try:
        with open(path) as f:
            data = json.load(f)
        tests = data.get('tests', [])
        if not isinstance(tests, list):
            print('WARNING: "tests" in {} is not a list, defaulting to empty.'.format(path), file=sys.stderr)
            return []
        return tests
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print('WARNING: Failed to parse {}: {}. Defaulting to empty test list.'.format(path, e), file=sys.stderr)
        return []

before_tests = load_tests('${APP_DIR}/before.json')
after_tests  = load_tests('${APP_DIR}/after.json')

before_map = {t['name']: t['status'] for t in before_tests}
after_map  = {t['name']: t['status'] for t in after_tests}

f2p = [name for name, status in before_map.items()
       if status != 'PASSED' and after_map.get(name) == 'PASSED']
f2f = [name for name, status in before_map.items()
       if status != 'PASSED' and after_map.get(name) != 'PASSED']
new_passes = [name for name, status in after_map.items()
              if name not in before_map and status == 'PASSED']
f2p.extend(new_passes)

p2p = [name for name, status in before_map.items()
       if status == 'PASSED' and after_map.get(name) == 'PASSED']

regressed = [name for name, status in before_map.items()
             if status == 'PASSED' and after_map.get(name) != 'PASSED']

with open('${APP_DIR}/fail_to_pass.json', 'w') as f:
    json.dump(f2p, f, indent=2)
with open('${APP_DIR}/pass_to_pass.json', 'w') as f:
    json.dump(p2p, f, indent=2)
with open('${APP_DIR}/fail_to_fail.json', 'w') as f:
    json.dump(f2f, f, indent=2)

print('  fail_to_pass.json: {} test(s)'.format(len(f2p)))
print('  fail_to_fail.json: {} test(s)'.format(len(f2f)))
print('  pass_to_pass.json: {} test(s)'.format(len(p2p)))

if regressed:
    print('FAILED: {} test(s) regressed (were PASSED before, not PASSED after):'.format(len(regressed)), file=sys.stderr)
    for name in regressed:
        print('  - {}'.format(name), file=sys.stderr)
    sys.exit(1)

if f2f:
    print('FAILED: failed tests found.', file=sys.stderr)
    sys.exit(1)

if not p2p:
    print('FAILED: No pass-to-pass tests found.', file=sys.stderr)
    sys.exit(1)

print('OK: All {} previously-passing tests still pass.'.format(len(p2p)))
PYEOF

# =============================================================================
# DONE
# =============================================================================
echo ""
echo "[*] Done! All outputs saved to ${APP_DIR}/:"
echo "    before.json  after.json  golden_patch_apply_stderr.txt"
echo "    run_before_stdout.txt  run_before_stderr.txt"
echo "    run_after_stdout.txt   run_after_stderr.txt"
echo "    fail_to_pass.json      pass_to_pass.json"