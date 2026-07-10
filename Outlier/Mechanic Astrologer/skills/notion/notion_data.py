#!/usr/bin/env python3
"""
Notion Data - Browse and manage Notion workspace pages, databases, blocks, comments, and users.

Usage:
    # Users
    python3 notion_data.py get-self
    python3 notion_data.py get-user --user-id ID
    python3 notion_data.py get-users [--start-cursor CURSOR] [--page-size N]
    python3 notion_data.py create-user --name NAME --email EMAIL [--avatar-url URL]

    # Databases
    python3 notion_data.py retrieve-database --database-id ID
    python3 notion_data.py create-database --parent JSON --properties JSON [--title TEXT] [--description TEXT] [--icon JSON] [--cover JSON]
    python3 notion_data.py update-database --database-id ID [--title TEXT] [--description TEXT] [--properties JSON]
    python3 notion_data.py query-database --database-id ID [--filter JSON] [--sorts JSON] [--start-cursor CURSOR] [--page-size N]

    # Pages
    python3 notion_data.py retrieve-page --page-id ID [--filter-properties JSON]
    python3 notion_data.py create-page --parent JSON [--properties JSON] [--icon JSON] [--cover JSON]
    python3 notion_data.py update-page --page-id ID [--properties JSON] [--archived] [--in-trash] [--icon JSON] [--cover JSON]
    python3 notion_data.py retrieve-page-property --page-id ID --property-id ID [--start-cursor CURSOR] [--page-size N]

    # Blocks & Comments
    python3 notion_data.py retrieve-block --block-id ID
    python3 notion_data.py retrieve-comments --block-id ID [--start-cursor CURSOR] [--page-size N]
    python3 notion_data.py create-comment --parent JSON --rich-text JSON

    # Search
    python3 notion_data.py search [--query TEXT] [--filter JSON] [--sort JSON] [--start-cursor CURSOR] [--page-size N]

    # Utility
    python3 notion_data.py show [--offset N] [--limit N]
    python3 notion_data.py reset

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


# --- Users ---

def cmd_get_self(args):
    """Get the authenticated bot user."""
    return _call_tool("notion_get_self")


def cmd_get_user(args):
    """Get a user by ID."""
    return _call_tool("notion_get_user", {"user_id": args.user_id})


def cmd_get_users(args):
    """List all users with pagination."""
    tool_args = {}
    if args.start_cursor:
        tool_args["start_cursor"] = args.start_cursor
    if args.page_size:
        tool_args["page_size"] = args.page_size
    return _call_tool("notion_get_users", tool_args)


def cmd_create_user(args):
    """Create a new user."""
    tool_args = {"name": args.name, "email": args.email}
    if args.avatar_url:
        tool_args["avatar_url"] = args.avatar_url
    return _call_tool("notion_create_user", tool_args)


# --- Databases ---

def cmd_retrieve_database(args):
    """Get a database by ID."""
    return _call_tool("notion_retrieve_database", {"database_id": args.database_id})


def cmd_create_database(args):
    """Create a new database."""
    tool_args = {
        "parent": json.loads(args.parent),
        "properties": json.loads(args.properties),
    }
    if args.title:
        tool_args["title"] = args.title
    if args.description:
        tool_args["description"] = args.description
    if args.icon:
        tool_args["icon"] = json.loads(args.icon)
    if args.cover:
        tool_args["cover"] = json.loads(args.cover)
    return _call_tool("notion_create_database", tool_args)


def cmd_update_database(args):
    """Update a database."""
    tool_args = {"database_id": args.database_id}
    if args.title:
        tool_args["title"] = args.title
    if args.description:
        tool_args["description"] = args.description
    if args.properties:
        tool_args["properties"] = json.loads(args.properties)
    return _call_tool("notion_update_database", tool_args)


def cmd_query_database(args):
    """Query pages in a database with filters and sorts."""
    tool_args = {"database_id": args.database_id}
    if args.filter:
        tool_args["filter"] = json.loads(args.filter)
    if args.sorts:
        tool_args["sorts"] = json.loads(args.sorts)
    if args.start_cursor:
        tool_args["start_cursor"] = args.start_cursor
    if args.page_size:
        tool_args["page_size"] = args.page_size
    return _call_tool("notion_query_database", tool_args)


# --- Pages ---

def cmd_retrieve_page(args):
    """Get a page by ID."""
    tool_args = {"page_id": args.page_id}
    if args.filter_properties:
        tool_args["filter_properties"] = json.loads(args.filter_properties)
    return _call_tool("notion_retrieve_page", tool_args)


def cmd_create_page(args):
    """Create a new page."""
    tool_args = {"parent": json.loads(args.parent)}
    if args.properties:
        tool_args["properties"] = json.loads(args.properties)
    if args.icon:
        tool_args["icon"] = json.loads(args.icon)
    if args.cover:
        tool_args["cover"] = json.loads(args.cover)
    return _call_tool("notion_create_page", tool_args)


def cmd_update_page(args):
    """Update a page."""
    tool_args = {"page_id": args.page_id}
    if args.properties:
        tool_args["properties"] = json.loads(args.properties)
    if args.archived:
        tool_args["archived"] = True
    if args.in_trash:
        tool_args["in_trash"] = True
    if args.icon:
        tool_args["icon"] = json.loads(args.icon)
    if args.cover:
        tool_args["cover"] = json.loads(args.cover)
    return _call_tool("notion_update_page", tool_args)


def cmd_retrieve_page_property(args):
    """Get a specific property value."""
    tool_args = {
        "page_id": args.page_id,
        "property_id": args.property_id,
    }
    if args.start_cursor:
        tool_args["start_cursor"] = args.start_cursor
    if args.page_size:
        tool_args["page_size"] = args.page_size
    return _call_tool("notion_retrieve_page_property", tool_args)


# --- Blocks & Comments ---

def cmd_retrieve_block(args):
    """Get a block by ID."""
    return _call_tool("notion_retrieve_block", {"block_id": args.block_id})


def cmd_retrieve_comments(args):
    """Get comments for a block or page."""
    tool_args = {"block_id": args.block_id}
    if args.start_cursor:
        tool_args["start_cursor"] = args.start_cursor
    if args.page_size:
        tool_args["page_size"] = args.page_size
    return _call_tool("notion_retrieve_comments", tool_args)


def cmd_create_comment(args):
    """Create a comment on a page."""
    return _call_tool("notion_create_comment", {
        "parent": json.loads(args.parent),
        "rich_text": json.loads(args.rich_text),
    })


# --- Search & Utility ---

def cmd_search(args):
    """Search pages and databases by title."""
    tool_args = {}
    if args.query:
        tool_args["query"] = args.query
    if args.filter:
        tool_args["filter"] = json.loads(args.filter)
    if args.sort:
        tool_args["sort"] = json.loads(args.sort)
    if args.start_cursor:
        tool_args["start_cursor"] = args.start_cursor
    if args.page_size:
        tool_args["page_size"] = args.page_size
    return _call_tool("notion_search", tool_args)


def cmd_show(args):
    """Show raw Notion data."""
    return _call_tool("notion_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


def cmd_reset(args):
    """Reset to initial state."""
    return _call_tool("notion_reset")


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Notion Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Users ---

    # get-self
    p = sub.add_parser("get-self", help="Get the authenticated bot user")
    p.set_defaults(func=cmd_get_self)

    # get-user
    p = sub.add_parser("get-user", help="Get a user by ID")
    p.add_argument("--user-id", type=str, required=True)
    p.set_defaults(func=cmd_get_user)

    # get-users
    p = sub.add_parser("get-users", help="List all users")
    p.add_argument("--start-cursor", type=str)
    p.add_argument("--page-size", type=int)
    p.set_defaults(func=cmd_get_users)

    # create-user
    p = sub.add_parser("create-user", help="Create a new user")
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--email", type=str, required=True)
    p.add_argument("--avatar-url", type=str)
    p.set_defaults(func=cmd_create_user)

    # --- Databases ---

    # retrieve-database
    p = sub.add_parser("retrieve-database", help="Get a database by ID")
    p.add_argument("--database-id", type=str, required=True)
    p.set_defaults(func=cmd_retrieve_database)

    # create-database
    p = sub.add_parser("create-database", help="Create a new database")
    p.add_argument("--parent", type=str, required=True, help='JSON: \'{"page_id": "..."}\'')
    p.add_argument("--properties", type=str, required=True,
                   help='JSON object with property definitions (must include one title property)')
    p.add_argument("--title", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--icon", type=str, help="JSON icon object")
    p.add_argument("--cover", type=str, help="JSON cover object")
    p.set_defaults(func=cmd_create_database)

    # update-database
    p = sub.add_parser("update-database", help="Update a database")
    p.add_argument("--database-id", type=str, required=True)
    p.add_argument("--title", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--properties", type=str, help="JSON object with property updates")
    p.set_defaults(func=cmd_update_database)

    # query-database
    p = sub.add_parser("query-database", help="Query pages in a database")
    p.add_argument("--database-id", type=str, required=True)
    p.add_argument("--filter", type=str, help="JSON filter object")
    p.add_argument("--sorts", type=str, help="JSON array of sort objects")
    p.add_argument("--start-cursor", type=str)
    p.add_argument("--page-size", type=int)
    p.set_defaults(func=cmd_query_database)

    # --- Pages ---

    # retrieve-page
    p = sub.add_parser("retrieve-page", help="Get a page by ID")
    p.add_argument("--page-id", type=str, required=True)
    p.add_argument("--filter-properties", type=str, help="JSON array of property IDs")
    p.set_defaults(func=cmd_retrieve_page)

    # create-page
    p = sub.add_parser("create-page", help="Create a new page")
    p.add_argument("--parent", type=str, required=True,
                   help='JSON: \'{"database_id": "..."}\' or \'{"page_id": "..."}\'')
    p.add_argument("--properties", type=str, help="JSON object with property values")
    p.add_argument("--icon", type=str, help="JSON icon object")
    p.add_argument("--cover", type=str, help="JSON cover object")
    p.set_defaults(func=cmd_create_page)

    # update-page
    p = sub.add_parser("update-page", help="Update a page")
    p.add_argument("--page-id", type=str, required=True)
    p.add_argument("--properties", type=str, help="JSON object with property updates")
    p.add_argument("--archived", action="store_true")
    p.add_argument("--in-trash", action="store_true")
    p.add_argument("--icon", type=str, help="JSON icon object")
    p.add_argument("--cover", type=str, help="JSON cover object")
    p.set_defaults(func=cmd_update_page)

    # retrieve-page-property
    p = sub.add_parser("retrieve-page-property", help="Get a property value")
    p.add_argument("--page-id", type=str, required=True)
    p.add_argument("--property-id", type=str, required=True)
    p.add_argument("--start-cursor", type=str)
    p.add_argument("--page-size", type=int)
    p.set_defaults(func=cmd_retrieve_page_property)

    # --- Blocks & Comments ---

    # retrieve-block
    p = sub.add_parser("retrieve-block", help="Get a block by ID")
    p.add_argument("--block-id", type=str, required=True)
    p.set_defaults(func=cmd_retrieve_block)

    # retrieve-comments
    p = sub.add_parser("retrieve-comments", help="Get comments for a block or page")
    p.add_argument("--block-id", type=str, required=True)
    p.add_argument("--start-cursor", type=str)
    p.add_argument("--page-size", type=int)
    p.set_defaults(func=cmd_retrieve_comments)

    # create-comment
    p = sub.add_parser("create-comment", help="Create a comment on a page")
    p.add_argument("--parent", type=str, required=True,
                   help='JSON: \'{"page_id": "..."}\'')
    p.add_argument("--rich-text", type=str, required=True,
                   help='JSON array of rich text objects')
    p.set_defaults(func=cmd_create_comment)

    # --- Search & Utility ---

    # search
    p = sub.add_parser("search", help="Search pages and databases")
    p.add_argument("--query", type=str)
    p.add_argument("--filter", type=str, help='JSON: \'{"property": "object", "value": "page"}\'')
    p.add_argument("--sort", type=str, help="JSON sort object")
    p.add_argument("--start-cursor", type=str)
    p.add_argument("--page-size", type=int)
    p.set_defaults(func=cmd_search)

    # show
    p = sub.add_parser("show", help="Show raw data")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_show)

    # reset
    p = sub.add_parser("reset", help="Reset to initial state")
    p.set_defaults(func=cmd_reset)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
