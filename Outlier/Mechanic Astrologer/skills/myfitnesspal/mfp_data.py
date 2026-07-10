#!/usr/bin/env python3
"""
MyFitnessPal Data Fetcher - Retrieve nutrition and fitness data from the MyFitnessPal MCP server

Usage:
    # Log in to your MyFitnessPal account
    python3 mfp_data.py login --email EMAIL

    # Daily summary (calories, macros, exercise, water)
    python3 mfp_data.py daily_summary [--date DATE]

    # Meal breakdown (per-meal food items with nutrition)
    python3 mfp_data.py meals [--date DATE]

    # Detailed macro/micronutrient breakdown
    python3 mfp_data.py macros [--date DATE]

    # Exercise log
    python3 mfp_data.py exercise [--date DATE]

    # Water intake
    python3 mfp_data.py water [--date DATE]

    # Date range summary with averages
    python3 mfp_data.py date_range --start DATE --end DATE

    # Search food database
    python3 mfp_data.py search_foods --query TEXT [--limit N]

    # Search exercise database
    python3 mfp_data.py search_exercises --query TEXT [--limit N]

    # User profile and nutrition goals
    python3 mfp_data.py profile

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


# ---- Public API functions ----


def get_daily_summary(date=None):
    """Get comprehensive daily summary: calories, macros, exercise, water."""
    args = {}
    if date:
        args["date"] = date
    return _call_tool("myfitnesspal_get_daily_summary", args)


def get_meals(date=None):
    """Get meal-by-meal food breakdown with per-item nutrition."""
    args = {}
    if date:
        args["date"] = date
    return _call_tool("myfitnesspal_get_daily_meals", args)


def get_macros(date=None):
    """Get detailed macro/micronutrient breakdown with goal comparison."""
    args = {}
    if date:
        args["date"] = date
    return _call_tool("myfitnesspal_get_daily_macros", args)


def get_exercise(date=None):
    """Get exercise activities for a day."""
    args = {}
    if date:
        args["date"] = date
    return _call_tool("myfitnesspal_get_daily_exercise", args)


def get_water(date=None):
    """Get water intake for a day."""
    args = {}
    if date:
        args["date"] = date
    return _call_tool("myfitnesspal_get_water_intake", args)


def get_date_range(start, end=None):
    """Get aggregate summary across a date range."""
    args = {"start_date": start}
    if end:
        args["end_date"] = end
    return _call_tool("myfitnesspal_get_date_range_summary", args)


def search_foods(query, limit=20):
    """Search food database by name or brand."""
    return _call_tool("myfitnesspal_search_foods", {
        "query": query,
        "limit": limit,
    })


def search_exercises(query, limit=20):
    """Search exercise database by name."""
    return _call_tool("myfitnesspal_search_exercises", {
        "query": query,
        "limit": limit,
    })


def get_profile():
    """Get user profile and nutrition goals."""
    return _call_tool("myfitnesspal_get_current_user_profile")


def login(email):
    """Log in to MyFitnessPal with your email."""
    return _call_tool("myfitnesspal_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch MyFitnessPal nutrition data")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # Date-based commands
    for cmd in ["daily_summary", "meals", "macros", "exercise", "water"]:
        p = sub.add_parser(cmd)
        p.add_argument("--date", help="Date in YYYY-MM-DD format")

    # Date range
    dr = sub.add_parser("date_range")
    dr.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    dr.add_argument("--end", help="End date YYYY-MM-DD")

    # Search commands
    sf = sub.add_parser("search_foods")
    sf.add_argument("--query", required=True, help="Search query")
    sf.add_argument("--limit", type=int, default=20)

    se = sub.add_parser("search_exercises")
    se.add_argument("--query", required=True, help="Search query")
    se.add_argument("--limit", type=int, default=20)

    # Profile
    sub.add_parser("profile")

    args = parser.parse_args()

    handlers = {
        "login": lambda: login(args.email),
        "daily_summary": lambda: get_daily_summary(args.date),
        "meals": lambda: get_meals(args.date),
        "macros": lambda: get_macros(args.date),
        "exercise": lambda: get_exercise(args.date),
        "water": lambda: get_water(args.date),
        "date_range": lambda: get_date_range(args.start, args.end),
        "search_foods": lambda: search_foods(args.query, args.limit),
        "search_exercises": lambda: search_exercises(args.query, args.limit),
        "profile": get_profile,
    }

    if args.command not in handlers:
        parser.print_help()
        sys.exit(1)

    result = handlers[args.command]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
