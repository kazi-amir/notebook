#!/usr/bin/env python3
"""
Fitbit Data Fetcher - Retrieve health data from the Fitbit MCP server

Usage:
    # Log in to your Fitbit account
    python3 fitbit_data.py login --email EMAIL

    # Sleep logs (last 7 days by default)
    python3 fitbit_data.py sleep [--days N] [--start DATE] [--end DATE]

    # Heart rate zones + resting HR
    python3 fitbit_data.py heart-rate [--days N] [--start DATE] [--end DATE]

    # Daily activity (steps, calories, distance, floors, active zones)
    python3 fitbit_data.py activity [--days N] [--start DATE] [--end DATE]

    # Exercise activities / workouts
    python3 fitbit_data.py workouts [--days N] [--start DATE] [--end DATE]

    # Body measurements (weight, BMI, body fat)
    python3 fitbit_data.py body [--days N] [--start DATE] [--end DATE]

    # Food / nutrition logs
    python3 fitbit_data.py food [--date DATE]

    # Water intake logs
    python3 fitbit_data.py water [--date DATE]

    # User profile
    python3 fitbit_data.py profile

    # Connected devices
    python3 fitbit_data.py devices

    # Achievement badges
    python3 fitbit_data.py badges

    # Lifetime statistics
    python3 fitbit_data.py lifetime

    # Combined health summary
    python3 fitbit_data.py summary [--days N]

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


def _days_to_period(days):
    """Map a --days value to a Fitbit API period string."""
    if days is None or days <= 1:
        return "1d"
    if days <= 7:
        return "7d"
    return "30d"


def get_sleep(days=None, start=None, end=None):
    """Get sleep data."""
    start_str, end_str = _get_date_range(days, start, end)
    return _call_tool("fitbit_get_sleep_logs", {
        "start_date": start_str,
        "end_date": end_str,
    })


def get_heart_rate(days=None, start=None, end=None):
    """Get heart rate data."""
    period = _days_to_period(days)
    return _call_tool("fitbit_get_heart_rate", {
        "period": period,
    })


def get_activity(days=None, start=None, end=None):
    """Get daily activity data."""
    start_str, end_str = _get_date_range(days, start, end)
    return _call_tool("fitbit_get_activities", {
        "start_date": start_str,
        "end_date": end_str,
    })


def get_workouts(days=None, start=None, end=None):
    """Get workout / exercise activity data."""
    start_str, end_str = _get_date_range(days, start, end)
    return _call_tool("fitbit_get_activities", {
        "start_date": start_str,
        "end_date": end_str,
    })


def get_body(days=None, start=None, end=None):
    """Get body measurements."""
    period = _days_to_period(days)
    return _call_tool("fitbit_get_body_measurements", {
        "period": period,
    })


def get_food(date=None):
    """Get food / nutrition logs for a specific date."""
    args = {}
    if date:
        args["date"] = date
    return _call_tool("fitbit_get_food_logs", args)


def get_water(date=None):
    """Get water intake logs for a specific date."""
    args = {}
    if date:
        args["date"] = date
    return _call_tool("fitbit_get_water_logs", args)


def get_profile():
    """Get user profile."""
    return _call_tool("fitbit_get_user_profile")


def get_devices():
    """Get connected devices."""
    return _call_tool("fitbit_get_devices")


def get_badges():
    """Get achievement badges."""
    return _call_tool("fitbit_get_badges")


def get_lifetime():
    """Get lifetime statistics."""
    return _call_tool("fitbit_get_lifetime_stats")


def get_summary(days=7):
    """Get a combined summary of all health data."""
    sleep = get_sleep(days=days)
    heart_rate = get_heart_rate(days=days)
    activity = get_activity(days=days)

    return {
        "period_days": days,
        "sleep": sleep,
        "heart_rate": heart_rate,
        "activity": activity,
    }


def login(email):
    """Log in to Fitbit with your email."""
    return _call_tool("fitbit_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch Fitbit health data")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    for cmd in ["sleep", "heart-rate", "activity", "workouts", "body"]:
        p = sub.add_parser(cmd)
        p.add_argument("--days", type=int, default=7)
        p.add_argument("--start", help="ISO date (e.g., 2026-01-01)")
        p.add_argument("--end", help="ISO date")

    for cmd in ["food", "water"]:
        p = sub.add_parser(cmd)
        p.add_argument("--date", help="ISO date (e.g., 2026-02-02)")

    sub.add_parser("profile")
    sub.add_parser("devices")
    sub.add_parser("badges")
    sub.add_parser("lifetime")

    summary_p = sub.add_parser("summary")
    summary_p.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    handlers = {
        "login": lambda: login(args.email),
        "sleep": lambda: get_sleep(args.days, args.start, args.end),
        "heart-rate": lambda: get_heart_rate(args.days, args.start, args.end),
        "activity": lambda: get_activity(args.days, args.start, args.end),
        "workouts": lambda: get_workouts(args.days, args.start, args.end),
        "body": lambda: get_body(args.days, args.start, args.end),
        "food": lambda: get_food(args.date),
        "water": lambda: get_water(args.date),
        "profile": get_profile,
        "devices": get_devices,
        "badges": get_badges,
        "lifetime": get_lifetime,
        "summary": lambda: get_summary(args.days),
    }

    if args.command not in handlers:
        parser.print_help()
        sys.exit(1)

    result = handlers[args.command]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
