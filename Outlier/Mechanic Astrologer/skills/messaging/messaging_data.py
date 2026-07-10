#!/usr/bin/env python3
"""
Messaging Data - Send and receive messages, manage conversations.

Usage:
    python3 messaging_data.py list [--offset N] [--limit N]
    python3 messaging_data.py get --conversation-id ID [--offset N] [--limit N]
    python3 messaging_data.py search --query TEXT [--limit N]
    python3 messaging_data.py send --user-id ID --content TEXT [--attachment PATH]
    python3 messaging_data.py send-to --conversation-id ID --content TEXT [--attachment PATH]
    python3 messaging_data.py create --participant-ids JSON [--title TEXT]
    python3 messaging_data.py add-user --conversation-id ID --user-id ID
    python3 messaging_data.py show [--offset N] [--limit N]

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
    """List conversations sorted by last updated."""
    return _call_tool("messaging_list_conversations", {
        "offset": args.offset,
        "limit": args.limit,
    })


def cmd_get(args):
    """Get a conversation with its messages."""
    tool_args = {"conversation_id": args.conversation_id}
    if args.offset:
        tool_args["offset"] = args.offset
    if args.limit:
        tool_args["limit"] = args.limit
    return _call_tool("messaging_get_conversation", tool_args)


def cmd_search(args):
    """Search conversations by title, participant names, or message content."""
    tool_args = {"query": args.query}
    if args.limit:
        tool_args["limit"] = args.limit
    return _call_tool("messaging_search_conversations", tool_args)


def cmd_send(args):
    """Send a message to a user (creates conversation if needed)."""
    tool_args = {"user_id": args.user_id}
    if args.content:
        tool_args["content"] = args.content
    if args.attachment:
        tool_args["attachment_path"] = args.attachment
    return _call_tool("messaging_send_message", tool_args)


def cmd_send_to(args):
    """Send a message to an existing conversation."""
    tool_args = {"conversation_id": args.conversation_id}
    if args.content:
        tool_args["content"] = args.content
    if args.attachment:
        tool_args["attachment_path"] = args.attachment
    return _call_tool("messaging_send_message_to_conversation", tool_args)


def cmd_create(args):
    """Create a new conversation."""
    tool_args = {"participant_ids": json.loads(args.participant_ids)}
    if args.title:
        tool_args["title"] = args.title
    return _call_tool("messaging_create_conversation", tool_args)


def cmd_add_user(args):
    """Add a user to an existing conversation."""
    return _call_tool("messaging_add_user_to_conversation", {
        "conversation_id": args.conversation_id,
        "user_id": args.user_id,
    })


def cmd_show(args):
    """Show raw messaging data."""
    return _call_tool("messaging_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Messaging Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List conversations")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_list)

    # get
    p = sub.add_parser("get", help="Get a conversation with messages")
    p.add_argument("--conversation-id", type=str, required=True)
    p.add_argument("--offset", type=int)
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_get)

    # search
    p = sub.add_parser("search", help="Search conversations")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_search)

    # send
    p = sub.add_parser("send", help="Send a message to a user")
    p.add_argument("--user-id", type=str, required=True)
    p.add_argument("--content", type=str)
    p.add_argument("--attachment", type=str, help="Path to attachment file")
    p.set_defaults(func=cmd_send)

    # send-to
    p = sub.add_parser("send-to", help="Send a message to a conversation")
    p.add_argument("--conversation-id", type=str, required=True)
    p.add_argument("--content", type=str)
    p.add_argument("--attachment", type=str, help="Path to attachment file")
    p.set_defaults(func=cmd_send_to)

    # create
    p = sub.add_parser("create", help="Create a new conversation")
    p.add_argument("--participant-ids", type=str, required=True,
                   help='JSON array: \'["user_001", "user_002"]\'')
    p.add_argument("--title", type=str)
    p.set_defaults(func=cmd_create)

    # add-user
    p = sub.add_parser("add-user", help="Add a user to a conversation")
    p.add_argument("--conversation-id", type=str, required=True)
    p.add_argument("--user-id", type=str, required=True)
    p.set_defaults(func=cmd_add_user)

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
