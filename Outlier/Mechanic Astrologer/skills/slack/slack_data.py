#!/usr/bin/env python3
"""
Slack Data - Browse channels, read message history, search, and post messages.

Usage:
    python3 slack_data.py channels [--types TYPES] [--limit N]
    python3 slack_data.py history --channel ID [--limit 1d|1w|30d|90d|N]
    python3 slack_data.py thread --channel ID --ts TIMESTAMP [--limit N]
    python3 slack_data.py search --query TEXT [--limit N]
        [--in-channel ID] [--in-dm ID] [--from-user ID]
        [--after DATE] [--before DATE] [--during DATE]
        [--threads-only]
    python3 slack_data.py post --channel ID --content TEXT
        [--thread-ts TIMESTAMP] [--user-id ID] [--content-type markdown|plain]

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


def cmd_channels(args):
    """List channels and DMs."""
    tool_args = {}
    if args.types:
        tool_args["channel_types"] = args.types
    if args.limit:
        tool_args["limit"] = args.limit
    return _call_tool("channels_list", tool_args)


def cmd_history(args):
    """Get message history for a channel."""
    tool_args = {"channel_id": args.channel}
    if args.limit:
        tool_args["limit"] = args.limit
    return _call_tool("conversations_history", tool_args)


def cmd_thread(args):
    """Get replies in a message thread."""
    tool_args = {"channel_id": args.channel, "thread_ts": args.ts}
    if args.limit:
        tool_args["limit"] = args.limit
    return _call_tool("conversations_replies", tool_args)


def cmd_search(args):
    """Search messages across conversations."""
    tool_args = {}
    if args.query:
        tool_args["search_query"] = args.query
    if args.limit:
        tool_args["limit"] = args.limit
    if args.in_channel:
        tool_args["filter_in_channel"] = args.in_channel
    if args.in_dm:
        tool_args["filter_in_im_or_mpim"] = args.in_dm
    if args.from_user:
        tool_args["filter_users_from"] = args.from_user
    if args.after:
        tool_args["filter_date_after"] = args.after
    if args.before:
        tool_args["filter_date_before"] = args.before
    if args.during:
        tool_args["filter_date_during"] = args.during
    if args.threads_only:
        tool_args["filter_threads_only"] = True
    return _call_tool("conversations_search_messages", tool_args)


def cmd_post(args):
    """Post a message to a channel or thread."""
    tool_args = {
        "channel_id": args.channel,
        "payload": args.content,
    }
    if args.content_type:
        tool_args["content_type"] = args.content_type
    if args.thread_ts:
        tool_args["thread_ts"] = args.thread_ts
    if args.user_id:
        tool_args["user_id"] = args.user_id
    return _call_tool("conversations_add_message", tool_args)


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Slack Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # channels
    p = sub.add_parser("channels", help="List channels and DMs")
    p.add_argument("--types", type=str,
                   help="Comma-separated types: public_channel,private_channel,im,mpim")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_channels)

    # history
    p = sub.add_parser("history", help="Get message history for a channel")
    p.add_argument("--channel", type=str, required=True,
                   help="Channel ID, #channel-name, or @username")
    p.add_argument("--limit", type=str,
                   help='Time window (1d, 1w, 30d, 90d) or message count (e.g. "50")')
    p.set_defaults(func=cmd_history)

    # thread
    p = sub.add_parser("thread", help="Get replies in a message thread")
    p.add_argument("--channel", type=str, required=True)
    p.add_argument("--ts", type=str, required=True, help="Parent message timestamp")
    p.add_argument("--limit", type=str)
    p.set_defaults(func=cmd_thread)

    # search
    p = sub.add_parser("search", help="Search messages")
    p.add_argument("--query", type=str)
    p.add_argument("--limit", type=int)
    p.add_argument("--in-channel", type=str, help="Filter to a specific channel ID")
    p.add_argument("--in-dm", type=str, help="Filter to a specific DM/MPIM channel ID")
    p.add_argument("--from-user", type=str, help="Filter by sender user ID")
    p.add_argument("--after", type=str, help="Filter messages after date (YYYY-MM-DD)")
    p.add_argument("--before", type=str, help="Filter messages before date (YYYY-MM-DD)")
    p.add_argument("--during", type=str, help="Filter messages during date (YYYY-MM-DD)")
    p.add_argument("--threads-only", action="store_true", help="Only return thread replies")
    p.set_defaults(func=cmd_search)

    # post
    p = sub.add_parser("post", help="Post a message")
    p.add_argument("--channel", type=str, required=True,
                   help="Channel ID, #channel-name, or @username")
    p.add_argument("--content", type=str, required=True)
    p.add_argument("--content-type", type=str, choices=["markdown", "plain"],
                   help="Content format (default: markdown)")
    p.add_argument("--thread-ts", type=str, help="Reply in a thread (parent message timestamp)")
    p.add_argument("--user-id", type=str, help="Post as this user ID")
    p.set_defaults(func=cmd_post)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
