#!/usr/bin/env python3
"""
Health Guardian - Apple Health Data Fetcher

Queries Apple Health data via typed MCP tool calls through the
agent-environment /step API.

Usage:
    # Log in to your Apple Health account
    python3 health_data.py login --email EMAIL

    # Get heart rate data (last 7 days by default)
    python3 health_data.py heart-rate [--days N] [--start DATE] [--end DATE]

    # Get resting heart rate
    python3 health_data.py resting-hr [--days N] [--start DATE] [--end DATE]

    # Get HRV data
    python3 health_data.py hrv [--days N] [--start DATE] [--end DATE]

    # Get sleep analysis
    python3 health_data.py sleep [--days N] [--start DATE] [--end DATE]

    # Get step count
    python3 health_data.py steps [--days N] [--start DATE] [--end DATE]

    # Get workout data
    python3 health_data.py workouts [--days N] [--start DATE] [--end DATE]

    # Get VO2 Max
    python3 health_data.py vo2max [--days N] [--start DATE] [--end DATE]

    # Get body measurements (weight history)
    python3 health_data.py body [--days N] [--start DATE] [--end DATE]

    # Get activity summary (calories, exercise, stand hours)
    python3 health_data.py activity [--days N] [--start DATE] [--end DATE]

    # Get user profile
    python3 health_data.py profile

    # Get combined health summary with averages
    python3 health_data.py summary [--days N]

    # Import data (no-op, data is pre-loaded -- kept for compatibility)
    python3 health_data.py import

Output: JSON to stdout
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

_AGENT_ENV_BASE = os.environ.get("AGENT_ENV_URL", "http://localhost:8000").rstrip("/")
AGENT_ENV_URL = _AGENT_ENV_BASE.removesuffix("/mcp")
_TOOL_ENDPOINT = "/step" if _AGENT_ENV_BASE.endswith("/mcp") else "/call-tool"


def _agent_env_headers() -> dict:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "openclaw-skill/1.0",
    }
    cf_client_id = os.environ.get("CF_ACCESS_CLIENT_ID")
    cf_client_secret = os.environ.get("CF_ACCESS_CLIENT_SECRET")
    if cf_client_id and cf_client_secret:
        headers["CF-Access-Client-Id"] = cf_client_id
        headers["CF-Access-Client-Secret"] = cf_client_secret
    return headers



def _call_tool(tool_name: str, tool_args: dict = None) -> dict:
    """Call an MCP tool via the agent-environment API.

    Supports both legacy /call-tool and new /step endpoints.
    Payload format and response parsing adapt based on _TOOL_ENDPOINT.
    """
    if _TOOL_ENDPOINT == "/step":
        payload = json.dumps({
            "action": "call_tool",
            "tool_name": tool_name,
            "arguments": tool_args or {},
        }).encode("utf-8")
    else:
        payload = json.dumps({
            "tool_name": tool_name,
            "tool_args": tool_args or {},
        }).encode("utf-8")
    req = urllib.request.Request(
        f"{AGENT_ENV_URL}{_TOOL_ENDPOINT}",
        data=payload,
        headers=_agent_env_headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            # /step wraps content in {"content": [...], "isError": bool}
            # /call-tool returns the content blocks array directly
            if isinstance(raw, dict) and "content" in raw:
                if raw.get("isError"):
                    return {"error": raw.get("error", "Unknown tool error")}
                content_blocks = raw["content"]
            elif isinstance(raw, list):
                content_blocks = raw
            else:
                content_blocks = raw.get("content", [])
            for block in content_blocks:
                if block.get("type") == "text":
                    try:
                        return json.loads(block["text"])
                    except json.JSONDecodeError:
                        return {"text": block["text"]}
            return {"content": content_blocks}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"API error {e.code}: {body}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e.reason}"}


def _build_args(days=None, start=None, end=None):
    """Build args dict from parameters, only including non-None values."""
    args = {}
    if days is not None:
        args["days"] = days
    if start is not None:
        args["start"] = start
    if end is not None:
        args["end"] = end
    return args


# ---- Public API functions ----


def get_heart_rate(days=None, start=None, end=None):
    """Get heart rate readings."""
    return _call_tool("apple_health_get_heart_rate", _build_args(days, start, end))


def get_resting_hr(days=None, start=None, end=None):
    """Get resting heart rate readings."""
    return _call_tool("apple_health_get_resting_hr", _build_args(days, start, end))


def get_hrv(days=None, start=None, end=None):
    """Get HRV (Heart Rate Variability SDNN) readings."""
    return _call_tool("apple_health_get_hrv", _build_args(days, start, end))


def get_sleep(days=None, start=None, end=None):
    """Get sleep analysis data."""
    return _call_tool("apple_health_get_sleep", _build_args(days, start, end))


def get_steps(days=None, start=None, end=None):
    """Get step count aggregated by day."""
    return _call_tool("apple_health_get_steps", _build_args(days, start, end))


def get_workouts(days=None, start=None, end=None):
    """Get workout data."""
    return _call_tool("apple_health_get_workouts", _build_args(days, start, end))


def get_vo2max(days=None, start=None, end=None):
    """Get VO2 Max readings."""
    return _call_tool("apple_health_get_vo2max", _build_args(days, start, end))


def get_body(days=None, start=None, end=None):
    """Get body measurements (weight history + height)."""
    return _call_tool("apple_health_get_body", _build_args(days, start, end))


def get_activity(days=None, start=None, end=None):
    """Get daily activity summary (calories, exercise, stand hours, distance)."""
    return _call_tool("apple_health_get_activity", _build_args(days, start, end))


def get_profile():
    """Get user profile from available health data."""
    return _call_tool("apple_health_get_profile")


def get_summary(days=7):
    """Get a combined health summary with averages."""
    args = {}
    if days is not None:
        args["days"] = days
    return _call_tool("apple_health_get_summary", args)


def do_import():
    """No-op import command for compatibility with original skill."""
    return {
        "status": "success",
        "message": "Data is pre-loaded via MCP server. No import needed.",
    }


def login(email):
    """Log in to Apple Health with your email."""
    return _call_tool("apple_health_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Apple Health Data Fetcher")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    for cmd in ["heart-rate", "resting-hr", "hrv", "sleep", "steps", "workouts", "vo2max", "body", "activity"]:
        p = sub.add_parser(cmd)
        p.add_argument("--days", type=int, default=7)
        p.add_argument("--start", help="ISO date (e.g., 2026-01-01)")
        p.add_argument("--end", help="ISO date")

    sub.add_parser("profile")
    sub.add_parser("import")

    summary_p = sub.add_parser("summary")
    summary_p.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    commands = {
        "login": lambda: login(args.email),
        "heart-rate": lambda: get_heart_rate(args.days, args.start, args.end),
        "resting-hr": lambda: get_resting_hr(args.days, args.start, args.end),
        "hrv": lambda: get_hrv(args.days, args.start, args.end),
        "sleep": lambda: get_sleep(args.days, args.start, args.end),
        "steps": lambda: get_steps(args.days, args.start, args.end),
        "workouts": lambda: get_workouts(args.days, args.start, args.end),
        "vo2max": lambda: get_vo2max(args.days, args.start, args.end),
        "body": lambda: get_body(args.days, args.start, args.end),
        "activity": lambda: get_activity(args.days, args.start, args.end),
        "profile": get_profile,
        "import": do_import,
        "summary": lambda: get_summary(args.days),
    }

    if args.command in commands:
        result = commands[args.command]()
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
