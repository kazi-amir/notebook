#!/usr/bin/env python3
"""
Contacts Data - Browse, search, add, edit, and delete contacts.

Usage:
    python3 contacts_data.py list [--offset N]
    python3 contacts_data.py get --id ID
    python3 contacts_data.py search --query TEXT
    python3 contacts_data.py add --first-name TEXT --last-name TEXT [--email TEXT]
        [--phone TEXT] [--gender TEXT] [--age N] [--nationality TEXT]
        [--city TEXT] [--country TEXT] [--status TEXT] [--job TEXT]
        [--description TEXT] [--address TEXT]
    python3 contacts_data.py edit --id ID --updates JSON
    python3 contacts_data.py delete --id ID
    python3 contacts_data.py show [--offset N] [--limit N]

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
    """List contacts with pagination."""
    return _call_tool("contacts_get_contacts", {"offset": args.offset})


def cmd_get(args):
    """Get a specific contact by ID."""
    return _call_tool("contacts_get_contact", {"contact_id": args.id})


def cmd_search(args):
    """Search contacts by name, email, or phone."""
    return _call_tool("contacts_search_contacts", {"query": args.query})


def cmd_add(args):
    """Add a new contact."""
    tool_args = {
        "first_name": args.first_name,
        "last_name": args.last_name,
    }
    if args.email:
        tool_args["email"] = args.email
    if args.phone:
        tool_args["phone"] = args.phone
    if args.gender:
        tool_args["gender"] = args.gender
    if args.age is not None:
        tool_args["age"] = args.age
    if args.nationality:
        tool_args["nationality"] = args.nationality
    if args.city:
        tool_args["city_living"] = args.city
    if args.country:
        tool_args["country"] = args.country
    if args.status:
        tool_args["status"] = args.status
    if args.job:
        tool_args["job"] = args.job
    if args.description:
        tool_args["description"] = args.description
    if args.address:
        tool_args["address"] = args.address
    return _call_tool("contacts_add_new_contact", tool_args)


def cmd_edit(args):
    """Edit a contact's fields."""
    updates = json.loads(args.updates)
    return _call_tool("contacts_edit_contact", {
        "contact_id": args.id,
        "updates": updates,
    })


def cmd_delete(args):
    """Delete a contact."""
    return _call_tool("contacts_delete_contact", {"contact_id": args.id})


def cmd_show(args):
    """Show raw contacts data."""
    return _call_tool("contacts_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Contacts Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List contacts")
    p.add_argument("--offset", type=int, default=0)
    p.set_defaults(func=cmd_list)

    # get
    p = sub.add_parser("get", help="Get contact by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get)

    # search
    p = sub.add_parser("search", help="Search contacts")
    p.add_argument("--query", type=str, required=True)
    p.set_defaults(func=cmd_search)

    # add
    p = sub.add_parser("add", help="Add a new contact")
    p.add_argument("--first-name", type=str, required=True)
    p.add_argument("--last-name", type=str, required=True)
    p.add_argument("--email", type=str)
    p.add_argument("--phone", type=str)
    p.add_argument("--gender", type=str)
    p.add_argument("--age", type=int)
    p.add_argument("--nationality", type=str)
    p.add_argument("--city", type=str)
    p.add_argument("--country", type=str)
    p.add_argument("--status", type=str)
    p.add_argument("--job", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--address", type=str)
    p.set_defaults(func=cmd_add)

    # edit
    p = sub.add_parser("edit", help="Edit a contact")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--updates", type=str, required=True, help='JSON: \'{"phone": "..."}\'')
    p.set_defaults(func=cmd_edit)

    # delete
    p = sub.add_parser("delete", help="Delete a contact")
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
