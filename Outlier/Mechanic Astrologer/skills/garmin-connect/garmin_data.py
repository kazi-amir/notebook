#!/usr/bin/env python3
"""
Garmin Connect Data Fetcher - Retrieve health data from the Garmin Health MCP server

Usage:
    # Log in to your Garmin Connect account
    python3 garmin_data.py login --email EMAIL

    # Get daily activity summary (steps, HR, calories, distance)
    python3 garmin_data.py summary [--days N] [--start DATE] [--end DATE]

    # Get sleep data
    python3 garmin_data.py sleep [--days N] [--start DATE] [--end DATE]

    # Get activities/workouts
    python3 garmin_data.py activities [--days N] [--start DATE] [--end DATE]

    # Get heart rate data
    python3 garmin_data.py heart_rate [--days N] [--start DATE] [--end DATE]

    # Get HRV data
    python3 garmin_data.py hrv [--days N] [--start DATE] [--end DATE]

    # Get stress data
    python3 garmin_data.py stress [--days N] [--start DATE] [--end DATE]

    # Get body battery data
    python3 garmin_data.py body_battery [--days N] [--start DATE] [--end DATE]

    # Get SpO2 data
    python3 garmin_data.py spo2 [--days N] [--start DATE] [--end DATE]

    # Get respiration data
    python3 garmin_data.py respiration [--days N] [--start DATE] [--end DATE]

    # Get body composition (weight, BMI, body fat)
    python3 garmin_data.py body_composition [--days N] [--start DATE] [--end DATE]

    # Get training readiness scores
    python3 garmin_data.py training_readiness [--days N] [--start DATE] [--end DATE]

    # Get registered devices
    python3 garmin_data.py devices

    # Get combined health snapshot
    python3 garmin_data.py health_snapshot [--days N]

    # Get user profile
    python3 garmin_data.py profile

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


# ---- Helpers ----


def _resolve_days(days=None, start=None, end=None, default=7):
    """Convert --start/--end to a days count, falling back to --days or default.

    NOTE: Most Garmin MCP tools only accept a `days` parameter, not date ranges.
    When --start/--end are provided, this computes the span in days but the window
    is anchored to today (not to the original start date). Use get_summary() for
    exact date-range queries — it supports start_date/end_date natively.
    """
    if start:
        now = datetime.now(timezone.utc)
        end_dt = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc) if end else now
        start_dt = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return max(int((end_dt - start_dt).days), 1)
    return days if days else default


# ---- Public API functions ----


def get_summary(days=None, start=None, end=None):
    """Get daily activity summaries (steps, HR, calories, distance)."""
    start_str, end_str = _get_date_range(days, start, end)
    return _call_tool("garmin_health_get_daily_stats_range", {
        "start_date": start_str,
        "end_date": end_str,
    })


def get_sleep(days=None, start=None, end=None):
    """Get sleep data."""
    return _call_tool("garmin_health_get_sleep_history", {"days": _resolve_days(days, start, end)})


def get_activities(days=None, start=None, end=None):
    """Get activities/workouts."""
    return _call_tool("garmin_health_get_activities", {"limit": _resolve_days(days, start, end, default=50)})


def get_heart_rate(days=None, start=None, end=None):
    """Get heart rate data."""
    return _call_tool("garmin_health_get_resting_heart_rate_trend", {"days": _resolve_days(days, start, end)})


def get_hrv(days=None, start=None, end=None):
    """Get HRV data."""
    return _call_tool("garmin_health_get_hrv", {})


def get_stress(days=None, start=None, end=None):
    """Get stress data."""
    return _call_tool("garmin_health_get_stress_history", {"days": _resolve_days(days, start, end)})


def get_body_battery(days=None, start=None, end=None):
    """Get body battery data."""
    return _call_tool("garmin_health_get_body_battery_history", {"days": _resolve_days(days, start, end)})


def get_spo2(days=None, start=None, end=None):
    """Get SpO2 data."""
    return _call_tool("garmin_health_get_spo2_history", {"days": _resolve_days(days, start, end)})


def get_respiration(days=None, start=None, end=None):
    """Get respiration data."""
    return _call_tool("garmin_health_get_respiration", {})


def get_body_composition(days=None, start=None, end=None):
    """Get body composition data."""
    return _call_tool("garmin_health_get_weight_history", {"days": _resolve_days(days, start, end, default=30)})


def get_training_readiness(days=None, start=None, end=None):
    """Get training readiness data."""
    return _call_tool("garmin_health_get_training_readiness_history", {"days": _resolve_days(days, start, end)})


def get_devices():
    """Get registered Garmin devices."""
    return _call_tool("garmin_health_get_devices")


def get_profile():
    """Get user profile."""
    return _call_tool("garmin_health_get_current_user")


def get_health_snapshot(days=7):
    """Get a combined health snapshot across all metrics."""
    return _call_tool("garmin_health_get_health_snapshot", {})


def login(email):
    """Log in to Garmin Connect with your email."""
    return _call_tool("garmin_health_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch Garmin Connect health data")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # Commands with date range support
    date_range_cmds = [
        "summary", "sleep", "activities", "heart_rate", "hrv",
        "stress", "body_battery", "spo2", "respiration",
        "body_composition", "training_readiness",
    ]
    for cmd in date_range_cmds:
        p = sub.add_parser(cmd)
        p.add_argument("--days", type=int, default=7)
        p.add_argument("--start", help="ISO date (e.g., 2026-01-01)")
        p.add_argument("--end", help="ISO date")

    # Commands without date range
    sub.add_parser("devices")
    sub.add_parser("profile")

    snapshot_p = sub.add_parser("health_snapshot")
    snapshot_p.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    handlers = {
        "login": lambda: login(args.email),
        "summary": lambda: get_summary(args.days, args.start, args.end),
        "sleep": lambda: get_sleep(args.days, args.start, args.end),
        "activities": lambda: get_activities(args.days, args.start, args.end),
        "heart_rate": lambda: get_heart_rate(args.days, args.start, args.end),
        "hrv": lambda: get_hrv(args.days, args.start, args.end),
        "stress": lambda: get_stress(args.days, args.start, args.end),
        "body_battery": lambda: get_body_battery(args.days, args.start, args.end),
        "spo2": lambda: get_spo2(args.days, args.start, args.end),
        "respiration": lambda: get_respiration(args.days, args.start, args.end),
        "body_composition": lambda: get_body_composition(args.days, args.start, args.end),
        "training_readiness": lambda: get_training_readiness(args.days, args.start, args.end),
        "devices": get_devices,
        "profile": get_profile,
        "health_snapshot": lambda: get_health_snapshot(args.days),
    }

    if args.command not in handlers:
        parser.print_help()
        sys.exit(1)

    result = handlers[args.command]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
