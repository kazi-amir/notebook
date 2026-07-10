#!/usr/bin/env python3
"""
Email Data - Read, send, reply, forward, search, and manage emails.

Usage:
    python3 email_data.py list [--folder FOLDER] [--offset N] [--limit N]
    python3 email_data.py get --id ID [--folder FOLDER]
    python3 email_data.py get-by-index --index N [--folder FOLDER]
    python3 email_data.py send --sender ADDR --recipients JSON [--subject TEXT]
        [--content TEXT] [--cc JSON]
    python3 email_data.py reply --id ID --sender ADDR --content TEXT
        [--folder FOLDER] [--cc JSON]
    python3 email_data.py forward --id ID --sender ADDR --recipients JSON
        [--content TEXT] [--folder FOLDER]
    python3 email_data.py move --id ID --from-folder FOLDER --to-folder FOLDER
    python3 email_data.py delete --id ID [--folder FOLDER]
    python3 email_data.py search --query TEXT [--folder FOLDER] [--limit N]
    python3 email_data.py mailboxes
    python3 email_data.py mailbox --id ID
    python3 email_data.py jmap-list --mailbox-id ID [--limit N] [--offset N]
    python3 email_data.py jmap-get --id ID
    python3 email_data.py thread --id ID
    python3 email_data.py show [--offset N] [--limit N]

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


def cmd_list(args):
    """List emails in a folder."""
    return _call_tool("list_emails", {
        "folder_name": args.folder,
        "offset": args.offset,
        "limit": args.limit,
    })


def cmd_get(args):
    """Get an email by ID."""
    return _call_tool("get_email_by_id", {
        "email_id": args.id,
        "folder_name": args.folder,
    })


def cmd_get_by_index(args):
    """Get an email by index."""
    return _call_tool("get_email_by_index", {
        "idx": args.index,
        "folder_name": args.folder,
    })


def cmd_send(args):
    """Send an email."""
    tool_args = {
        "sender": args.sender,
        "recipients": json.loads(args.recipients),
        "subject": args.subject,
        "content": args.content,
    }
    if args.cc:
        tool_args["cc"] = json.loads(args.cc)
    return _call_tool("send_email", tool_args)


def cmd_reply(args):
    """Reply to an email."""
    tool_args = {
        "email_id": args.id,
        "sender": args.sender,
        "content": args.content,
        "folder_name": args.folder,
    }
    if args.cc:
        tool_args["cc"] = json.loads(args.cc)
    return _call_tool("reply_to_email", tool_args)


def cmd_forward(args):
    """Forward an email."""
    tool_args = {
        "email_id": args.id,
        "sender": args.sender,
        "recipients": json.loads(args.recipients),
        "folder_name": args.folder,
    }
    if args.content:
        tool_args["content"] = args.content
    return _call_tool("forward_email", tool_args)


def cmd_move(args):
    """Move an email between folders."""
    return _call_tool("move_email", {
        "email_id": args.id,
        "from_folder": args.from_folder,
        "to_folder": args.to_folder,
    })


def cmd_delete(args):
    """Delete an email."""
    return _call_tool("delete_email", {
        "email_id": args.id,
        "folder_name": args.folder,
    })


def cmd_search(args):
    """Search emails."""
    tool_args = {"query": args.query}
    if args.folder:
        tool_args["folder_name"] = args.folder
    if args.limit:
        tool_args["limit"] = args.limit
    return _call_tool("search_emails", tool_args)


def cmd_mailboxes(args):
    """List all mailboxes."""
    return _call_tool("list_mailboxes")


def cmd_mailbox(args):
    """Get a specific mailbox."""
    return _call_tool("get_mailbox", {"mailbox_id": args.id})


def cmd_jmap_list(args):
    """List JMAP-formatted emails."""
    return _call_tool("list_jmap_emails", {
        "mailbox_id": args.mailbox_id,
        "limit": args.limit,
        "offset": args.offset,
    })


def cmd_jmap_get(args):
    """Get a JMAP email by ID."""
    return _call_tool("get_jmap_email", {"email_id": args.id})


def cmd_thread(args):
    """Get an email thread."""
    return _call_tool("get_thread", {"thread_id": args.id})


def cmd_show(args):
    """Show raw email data."""
    return _call_tool("show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Email Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List emails in a folder")
    p.add_argument("--folder", type=str, default="INBOX")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_list)

    # get
    p = sub.add_parser("get", help="Get email by ID")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--folder", type=str, default="INBOX")
    p.set_defaults(func=cmd_get)

    # get-by-index
    p = sub.add_parser("get-by-index", help="Get email by index")
    p.add_argument("--index", type=int, required=True)
    p.add_argument("--folder", type=str, default="INBOX")
    p.set_defaults(func=cmd_get_by_index)

    # send
    p = sub.add_parser("send", help="Send an email")
    p.add_argument("--sender", type=str, required=True)
    p.add_argument("--recipients", type=str, required=True, help='JSON array: \'["a@b.com"]\'')
    p.add_argument("--subject", type=str, default="")
    p.add_argument("--content", type=str, default="")
    p.add_argument("--cc", type=str, help='JSON array: \'["c@d.com"]\'')
    p.set_defaults(func=cmd_send)

    # reply
    p = sub.add_parser("reply", help="Reply to an email")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--sender", type=str, required=True)
    p.add_argument("--content", type=str, required=True)
    p.add_argument("--folder", type=str, default="INBOX")
    p.add_argument("--cc", type=str, help='JSON array')
    p.set_defaults(func=cmd_reply)

    # forward
    p = sub.add_parser("forward", help="Forward an email")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--sender", type=str, required=True)
    p.add_argument("--recipients", type=str, required=True, help='JSON array')
    p.add_argument("--content", type=str, default="")
    p.add_argument("--folder", type=str, default="INBOX")
    p.set_defaults(func=cmd_forward)

    # move
    p = sub.add_parser("move", help="Move email between folders")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--from-folder", type=str, required=True)
    p.add_argument("--to-folder", type=str, required=True)
    p.set_defaults(func=cmd_move)

    # delete
    p = sub.add_parser("delete", help="Delete an email")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--folder", type=str, default="INBOX")
    p.set_defaults(func=cmd_delete)

    # search
    p = sub.add_parser("search", help="Search emails")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--folder", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    # mailboxes
    p = sub.add_parser("mailboxes", help="List mailboxes")
    p.set_defaults(func=cmd_mailboxes)

    # mailbox
    p = sub.add_parser("mailbox", help="Get a mailbox")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_mailbox)

    # jmap-list
    p = sub.add_parser("jmap-list", help="List JMAP emails")
    p.add_argument("--mailbox-id", type=str, required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--offset", type=int, default=0)
    p.set_defaults(func=cmd_jmap_list)

    # jmap-get
    p = sub.add_parser("jmap-get", help="Get JMAP email by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_jmap_get)

    # thread
    p = sub.add_parser("thread", help="Get email thread")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_thread)

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
