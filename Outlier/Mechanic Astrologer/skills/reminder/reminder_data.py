#!/usr/bin/env python3
"""
Reminder Data - Add, view, and delete reminders with optional repetition.

Usage:
    python3 reminder_data.py list
    python3 reminder_data.py due
    python3 reminder_data.py add --title TEXT --due "YYYY-MM-DD HH:MM:SS" --description TEXT
        [--repeat-unit UNIT] [--repeat-value N]
    python3 reminder_data.py delete --id ID
    python3 reminder_data.py delete-all
    python3 reminder_data.py show [--offset N] [--limit N]

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
    """Call an MCP tool via the agent-environment API."""
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


def cmd_list(args):
    """Get all reminders."""
    return _call_tool("reminder_get_all_reminders")


def cmd_due(args):
    """Get reminders that are currently due."""
    return _call_tool("reminder_get_due_reminders")


def cmd_add(args):
    """Add a new reminder."""
    tool_args = {
        "title": args.title,
        "due_datetime": args.due,
        "description": args.description,
    }
    if args.repeat_unit:
        tool_args["repetition_unit"] = args.repeat_unit
    if args.repeat_value is not None:
        tool_args["repetition_value"] = args.repeat_value
    return _call_tool("reminder_add_reminder", tool_args)


def cmd_delete(args):
    """Delete a reminder by ID."""
    return _call_tool("reminder_delete_reminder", {"reminder_id": args.id})


def cmd_delete_all(args):
    """Delete all reminders."""
    return _call_tool("reminder_delete_all_reminders")


def cmd_show(args):
    """Show raw reminder data."""
    return _call_tool("reminder_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Reminder Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="Get all reminders")
    p.set_defaults(func=cmd_list)

    # due
    p = sub.add_parser("due", help="Get reminders currently due")
    p.set_defaults(func=cmd_due)

    # add
    p = sub.add_parser("add", help="Add a new reminder")
    p.add_argument("--title", type=str, required=True)
    p.add_argument("--due", type=str, required=True, help='"YYYY-MM-DD HH:MM:SS"')
    p.add_argument("--description", type=str, required=True)
    p.add_argument("--repeat-unit", type=str,
                   choices=["second", "minute", "hour", "day", "week", "month"],
                   help="Repetition unit")
    p.add_argument("--repeat-value", type=int, help="Repetition interval (e.g. 1 for every 1 unit)")
    p.set_defaults(func=cmd_add)

    # delete
    p = sub.add_parser("delete", help="Delete a reminder")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_delete)

    # delete-all
    p = sub.add_parser("delete-all", help="Delete all reminders")
    p.set_defaults(func=cmd_delete_all)

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
