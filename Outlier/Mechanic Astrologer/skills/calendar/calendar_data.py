#!/usr/bin/env python3
"""
Calendar Data - View, create, edit, search, and delete calendar events.

Usage:
    python3 calendar_data.py today
    python3 calendar_data.py range --start "YYYY-MM-DD HH:MM:SS" --end "YYYY-MM-DD HH:MM:SS"
        [--offset N] [--limit N]
    python3 calendar_data.py get --id ID
    python3 calendar_data.py tags
    python3 calendar_data.py by-tag --tag TAG
    python3 calendar_data.py search --query TEXT
    python3 calendar_data.py add --title TEXT [--start "YYYY-MM-DD HH:MM:SS"]
        [--end "YYYY-MM-DD HH:MM:SS"] [--tag TAG] [--description TEXT]
        [--location TEXT] [--attendees JSON]
    python3 calendar_data.py edit --id ID [--title TEXT] [--start "..."] [--end "..."]
        [--tag TAG] [--description TEXT] [--location TEXT] [--attendees JSON]
    python3 calendar_data.py delete --id ID
    python3 calendar_data.py show [--offset N] [--limit N]

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


# ==================== Subcommand Handlers ====================


def cmd_today(args):
    """Get today's events."""
    return _call_tool("calendar_read_today_calendar_events")


def cmd_range(args):
    """Get events in a date range."""
    return _call_tool("calendar_get_calendar_events_from_to", {
        "start_datetime": args.start,
        "end_datetime": args.end,
        "offset": args.offset,
        "limit": args.limit,
    })


def cmd_get(args):
    """Get an event by ID."""
    return _call_tool("calendar_get_calendar_event", {"event_id": args.id})


def cmd_tags(args):
    """List all tags."""
    return _call_tool("calendar_get_all_tags")


def cmd_by_tag(args):
    """Get events by tag."""
    return _call_tool("calendar_get_calendar_events_by_tag", {"tag": args.tag})


def cmd_search(args):
    """Search events by keyword."""
    return _call_tool("calendar_search_events", {"query": args.query})


def cmd_add(args):
    """Create a new event."""
    tool_args = {"title": args.title}
    if args.start:
        tool_args["start_datetime"] = args.start
    if args.end:
        tool_args["end_datetime"] = args.end
    if args.tag:
        tool_args["tag"] = args.tag
    if args.description:
        tool_args["description"] = args.description
    if args.location:
        tool_args["location"] = args.location
    if args.attendees:
        tool_args["attendees"] = json.loads(args.attendees)
    return _call_tool("calendar_add_calendar_event", tool_args)


def cmd_edit(args):
    """Edit an existing event."""
    tool_args = {"event_id": args.id}
    if args.title:
        tool_args["title"] = args.title
    if args.start:
        tool_args["start_datetime"] = args.start
    if args.end:
        tool_args["end_datetime"] = args.end
    if args.tag:
        tool_args["tag"] = args.tag
    if args.description:
        tool_args["description"] = args.description
    if args.location:
        tool_args["location"] = args.location
    if args.attendees:
        tool_args["attendees"] = json.loads(args.attendees)
    return _call_tool("calendar_edit_calendar_event", tool_args)


def cmd_delete(args):
    """Delete an event."""
    return _call_tool("calendar_delete_calendar_event", {"event_id": args.id})


def cmd_show(args):
    """Show raw calendar data."""
    return _call_tool("calendar_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Calendar Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # today
    p = sub.add_parser("today", help="Get today's events")
    p.set_defaults(func=cmd_today)

    # range
    p = sub.add_parser("range", help="Get events in a date range")
    p.add_argument("--start", type=str, required=True, help='"YYYY-MM-DD HH:MM:SS"')
    p.add_argument("--end", type=str, required=True, help='"YYYY-MM-DD HH:MM:SS"')
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_range)

    # get
    p = sub.add_parser("get", help="Get event by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get)

    # tags
    p = sub.add_parser("tags", help="List all tags")
    p.set_defaults(func=cmd_tags)

    # by-tag
    p = sub.add_parser("by-tag", help="Get events by tag")
    p.add_argument("--tag", type=str, required=True)
    p.set_defaults(func=cmd_by_tag)

    # search
    p = sub.add_parser("search", help="Search events")
    p.add_argument("--query", type=str, required=True)
    p.set_defaults(func=cmd_search)

    # add
    p = sub.add_parser("add", help="Create a new event")
    p.add_argument("--title", type=str, default="Event")
    p.add_argument("--start", type=str, help='"YYYY-MM-DD HH:MM:SS"')
    p.add_argument("--end", type=str, help='"YYYY-MM-DD HH:MM:SS"')
    p.add_argument("--tag", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--location", type=str)
    p.add_argument("--attendees", type=str, help='JSON array: \'["name"]\'')
    p.set_defaults(func=cmd_add)

    # edit
    p = sub.add_parser("edit", help="Edit an event")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--title", type=str)
    p.add_argument("--start", type=str)
    p.add_argument("--end", type=str)
    p.add_argument("--tag", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--location", type=str)
    p.add_argument("--attendees", type=str, help='JSON array')
    p.set_defaults(func=cmd_edit)

    # delete
    p = sub.add_parser("delete", help="Delete an event")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_delete)

    # show
    p = sub.add_parser("show", help="Show raw data")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_show)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
