#!/usr/bin/env python3
"""
Eight Sleep Data Fetcher - Retrieve sleep and device data from the Eight Sleep MCP server

Usage:
    # Log in to your Eight Sleep account
    python3 eight_sleep_data.py login --email EMAIL

    # Get sleep sessions (last 7 days by default)
    python3 eight_sleep_data.py sleep [--days N] [--start DATE] [--end DATE]

    # Get sleep fitness trends
    python3 eight_sleep_data.py trends [--days N]

    # Get current temperature
    python3 eight_sleep_data.py temperature

    # Get temperature schedules
    python3 eight_sleep_data.py schedules

    # Get alarms
    python3 eight_sleep_data.py alarms

    # Get device status
    python3 eight_sleep_data.py device

    # Get user profile
    python3 eight_sleep_data.py profile

    # Get all data summary
    python3 eight_sleep_data.py summary [--days N]

    # Set bed temperature (-100 to 100)
    python3 eight_sleep_data.py set-temperature --level 20 --side left

Output: JSON to stdout
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

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


def _get_date_range(days=None, start=None, end=None, default_days=7):
    """Calculate start/end ISO date strings for API calls."""
    now = datetime.now(timezone.utc)
    if start:
        start_str = start
    elif days:
        start_str = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    else:
        start_str = (now - timedelta(days=default_days)).strftime("%Y-%m-%d")

    end_str = end if end else now.strftime("%Y-%m-%d")
    return start_str, end_str


def get_sleep(days=None, start=None, end=None):
    """Get sleep session data."""
    start_str, end_str = _get_date_range(days, start, end)
    return _call_tool("eight_sleep_get_sleep_session_collection", {
        "start_date": start_str,
        "end_date": end_str,
        "limit": 100,
    })


def get_trends(days=14):
    """Get sleep fitness trends."""
    return _call_tool("eight_sleep_get_sleep_fitness_trends", {
        "days": days,
    })


def get_temperature():
    """Get current bed temperature."""
    return _call_tool("eight_sleep_get_current_temperature")


def get_schedules():
    """Get temperature schedules."""
    return _call_tool("eight_sleep_get_temperature_schedules")


def get_alarms():
    """Get configured alarms."""
    return _call_tool("eight_sleep_get_alarms")


def get_device():
    """Get device status."""
    return _call_tool("eight_sleep_get_device_status")


def get_profile():
    """Get user profile."""
    return _call_tool("eight_sleep_get_profile")


def set_temperature(level, side):
    """Set bed temperature. Level is -100 to 100, side is 'left' or 'right'."""
    return _call_tool("eight_sleep_set_temperature", {
        "temp_level": level,
        "side": side,
    })


def get_summary(days=7):
    """Get a combined summary of all data."""
    sleep = get_sleep(days=days)
    trends = get_trends(days=days)
    temperature = get_temperature()
    schedules = get_schedules()
    alarms = get_alarms()

    return {
        "period_days": days,
        "sleep": sleep,
        "trends": trends,
        "temperature": temperature,
        "schedules": schedules,
        "alarms": alarms,
    }


def login(email):
    """Log in to Eight Sleep with your email."""
    return _call_tool("eight_sleep_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch Eight Sleep Pod data")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # Sleep sessions
    sleep_p = sub.add_parser("sleep")
    sleep_p.add_argument("--days", type=int, default=7)
    sleep_p.add_argument("--start", help="ISO date (e.g., 2026-01-01)")
    sleep_p.add_argument("--end", help="ISO date")

    # Trends
    trends_p = sub.add_parser("trends")
    trends_p.add_argument("--days", type=int, default=14)

    # Temperature, schedules, alarms, device, profile (no args)
    sub.add_parser("temperature")
    sub.add_parser("schedules")
    sub.add_parser("alarms")
    sub.add_parser("device")
    sub.add_parser("profile")

    # Set temperature
    set_temp_p = sub.add_parser("set-temperature")
    set_temp_p.add_argument("--level", type=int, required=True, help="Temperature level (-100 to 100)")
    set_temp_p.add_argument("--side", required=True, choices=["left", "right"], help="Bed side")

    # Summary
    summary_p = sub.add_parser("summary")
    summary_p.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    if args.command == "login":
        result = login(args.email)
    elif args.command == "set-temperature":
        result = set_temperature(args.level, args.side)
    elif args.command == "sleep":
        result = get_sleep(args.days, args.start, args.end)
    elif args.command == "trends":
        result = get_trends(args.days)
    elif args.command == "temperature":
        result = get_temperature()
    elif args.command == "schedules":
        result = get_schedules()
    elif args.command == "alarms":
        result = get_alarms()
    elif args.command == "device":
        result = get_device()
    elif args.command == "profile":
        result = get_profile()
    elif args.command == "summary":
        result = get_summary(args.days)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
