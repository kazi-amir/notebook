#!/usr/bin/env python3
"""
Renpho Data Fetcher - Retrieve body composition data from the Renpho MCP server

Usage:
    # Log in to your Renpho account
    python3 renpho_data.py login --email EMAIL

    # Get latest measurement
    python3 renpho_data.py latest

    # Get detailed body composition with health classifications
    python3 renpho_data.py composition

    # Get weight trend over N days
    python3 renpho_data.py trend [--days N]

    # Get historical measurements
    python3 renpho_data.py measurements [--days N] [--start DATE] [--end DATE]

    # Get user profile
    python3 renpho_data.py profile

    # Get all data summary
    python3 renpho_data.py summary [--days N]

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


def _get_date_range(days=None, start=None, end=None, default_days=30):
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


def get_latest():
    """Get the most recent measurement."""
    return _call_tool("renpho_get_latest_measurement")


def get_composition():
    """Get detailed body composition with health classifications."""
    return _call_tool("renpho_get_body_composition")


def get_trend(days=30):
    """Get weight trend analysis."""
    return _call_tool("renpho_get_weight_trend", {
        "days": days,
    })


def get_measurements(days=None, start=None, end=None):
    """Get historical measurements."""
    start_str, end_str = _get_date_range(days, start, end)
    return _call_tool("renpho_get_measurements", {
        "start_date": start_str,
        "end_date": end_str,
        "limit": 100,
    })


def get_profile():
    """Get user profile."""
    return _call_tool("renpho_get_current_user")


def get_summary(days=30):
    """Get a combined summary of all data."""
    latest = get_latest()
    composition = get_composition()
    trend = get_trend(days=days)
    measurements = get_measurements(days=days)

    return {
        "period_days": days,
        "latest": latest,
        "composition": composition,
        "trend": trend,
        "measurements": measurements,
    }


def login(email):
    """Log in to Renpho with your email."""
    return _call_tool("renpho_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch Renpho body composition data")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # No-arg commands
    sub.add_parser("latest")
    sub.add_parser("composition")
    sub.add_parser("profile")

    # Trend
    trend_p = sub.add_parser("trend")
    trend_p.add_argument("--days", type=int, default=30)

    # Measurements
    meas_p = sub.add_parser("measurements")
    meas_p.add_argument("--days", type=int, default=30)
    meas_p.add_argument("--start", help="ISO date (e.g., 2026-01-01)")
    meas_p.add_argument("--end", help="ISO date")

    # Summary
    summary_p = sub.add_parser("summary")
    summary_p.add_argument("--days", type=int, default=30)

    args = parser.parse_args()

    if args.command == "login":
        result = login(args.email)
    elif args.command == "latest":
        result = get_latest()
    elif args.command == "composition":
        result = get_composition()
    elif args.command == "trend":
        result = get_trend(args.days)
    elif args.command == "measurements":
        result = get_measurements(args.days, getattr(args, "start", None), getattr(args, "end", None))
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
