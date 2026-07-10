import sys
import json
import re
from typing import List, Dict

def parse_test_output(stdout_content: str, stderr_content: str) -> List[Dict[str, str]]:
    tests = []
    # Match standard dotnet test detailed output for Passed/Failed tests
    # Example: "Passed ComInterfaceGenerator.Unit.Tests.ComClassGeneratorDiagnostics.UnsafeCodeNotEnabledWarns"
    pattern = re.compile(r"^\s*(Passed|Failed|Skipped)\s+(.+)$", re.MULTILINE)
    
    for match in pattern.finditer(stdout_content):
        status_raw = match.group(1).upper()
        test_name = match.group(2).strip()
        
        # Normalize status
        if status_raw == "PASSED":
            status = "PASSED"
        elif status_raw == "FAILED":
            status = "FAILED"
        elif status_raw == "SKIPPED":
            status = "SKIPPED"
        else:
            status = "ERROR"
            
        tests.append({
            "name": test_name,
            "status": status
        })
        
    return tests

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 parsing.py <stdout.txt> <stderr.txt> <results.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        stdout = f.read()
    with open(sys.argv[2], 'r') as f:
        stderr = f.read()

    parsed_tests = parse_test_output(stdout, stderr)

    with open(sys.argv[3], 'w') as f:
        json.dump({"tests": parsed_tests}, f, indent=4)