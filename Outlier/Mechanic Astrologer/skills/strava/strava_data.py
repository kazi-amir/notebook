#!/usr/bin/env python3
"""
Strava Data Fetcher - Retrieve fitness data from the Strava MCP server

Usage:
    # Log in to your Strava account
    python3 strava_data.py login --email EMAIL

    # List recent activities (last 30 by default)
    python3 strava_data.py activities [--per-page N] [--page N] [--type TYPE]
                                      [--days N] [--after DATE] [--before DATE]

    # Get activity details by ID
    python3 strava_data.py activity --id ACTIVITY_ID

    # Get athlete profile
    python3 strava_data.py profile

    # Get athlete statistics (YTD, all-time, recent totals)
    python3 strava_data.py stats

    # Get personal records
    python3 strava_data.py records

    # Get training zones (heart rate + power)
    python3 strava_data.py zones

    # Combined fitness summary
    python3 strava_data.py summary [--days N]

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


def _get_date_range(days=None, default_days=30):
    """Calculate after date as ISO string from --days."""
    now = datetime.now(timezone.utc)
    if days:
        return (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (now - timedelta(days=default_days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_activities(per_page=30, page=1, activity_type=None, days=None, after=None, before=None):
    """List recent activities with optional filtering."""
    args = {
        "page": page,
        "per_page": per_page,
    }
    if activity_type:
        args["activity_type"] = activity_type
    if days:
        args["after"] = _get_date_range(days)
    elif after:
        args["after"] = after
    if before:
        args["before"] = before

    return _call_tool("strava_get_recent_activities", args)


def get_activity(activity_id: int):
    """Get detailed information for a specific activity."""
    return _call_tool("strava_get_activity_details", {"activity_id": activity_id})


def get_profile():
    """Get athlete profile."""
    return _call_tool("strava_get_profile")


def get_stats():
    """Get athlete statistics (YTD, all-time, recent totals)."""
    return _call_tool("strava_get_athlete_stats")


def get_records():
    """Get personal records."""
    return _call_tool("strava_get_personal_records")


def get_zones():
    """Get training zones (heart rate + power)."""
    return _call_tool("strava_get_training_zones")


def get_summary(days=30):
    """Get a combined fitness summary."""
    activities = get_activities(per_page=999, days=days)
    stats = get_stats()
    profile = get_profile()

    activity_list = activities.get("activities", [])

    type_counts = {}
    total_distance = 0
    total_moving_time = 0
    total_elevation = 0
    total_calories = 0

    for a in activity_list:
        atype = a.get("type", "Unknown")
        type_counts[atype] = type_counts.get(atype, 0) + 1
        total_distance += a.get("distance") or 0
        total_moving_time += a.get("moving_time") or 0
        total_elevation += a.get("total_elevation_gain") or 0
        total_calories += a.get("calories") or 0

    return {
        "type": "summary",
        "period_days": days,
        "athlete": profile.get("athlete"),
        "recent_activities": {
            "count": len(activity_list),
            "total_distance_m": round(total_distance, 1),
            "total_distance_km": round(total_distance / 1000, 1),
            "total_moving_time_s": total_moving_time,
            "total_moving_time_hours": round(total_moving_time / 3600, 1),
            "total_elevation_gain_m": round(total_elevation, 1),
            "total_calories": round(total_calories),
            "by_type": type_counts,
        },
        "all_time_stats": stats.get("stats", stats),
    }


def login(email):
    """Log in to Strava with your email."""
    return _call_tool("strava_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch Strava fitness data")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # activities
    act_p = sub.add_parser("activities")
    act_p.add_argument("--per-page", type=int, default=30)
    act_p.add_argument("--page", type=int, default=1)
    act_p.add_argument(
        "--type",
        choices=[
            "Run",
            "Ride",
            "Swim",
            "Walk",
            "Hike",
            "WeightTraining",
            "Yoga",
            "Workout",
        ],
    )
    act_p.add_argument("--days", type=int)
    act_p.add_argument("--after", help="ISO date (e.g., 2026-01-01)")
    act_p.add_argument("--before", help="ISO date")

    # activity detail
    det_p = sub.add_parser("activity")
    det_p.add_argument("--id", type=int, required=True, help="Activity ID")

    # profile, stats, records, zones (no args)
    sub.add_parser("profile")
    sub.add_parser("stats")
    sub.add_parser("records")
    sub.add_parser("zones")

    # summary
    sum_p = sub.add_parser("summary")
    sum_p.add_argument("--days", type=int, default=30)

    args = parser.parse_args()

    handlers = {
        "login": lambda: login(args.email),
        "activities": lambda: get_activities(
            per_page=args.per_page,
            page=args.page,
            activity_type=args.type,
            days=args.days,
            after=args.after,
            before=args.before,
        ),
        "activity": lambda: get_activity(args.id),
        "profile": get_profile,
        "stats": get_stats,
        "records": get_records,
        "zones": get_zones,
        "summary": lambda: get_summary(args.days),
    }

    if args.command not in handlers:
        parser.print_help()
        sys.exit(1)

    result = handlers[args.command]()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
