#!/usr/bin/env python3
"""
Airtable Data - Browse and manage Airtable bases, tables, fields, and records.

Usage:
    python3 airtable_data.py list-bases
    python3 airtable_data.py list-tables --base-id ID
    python3 airtable_data.py describe-table --base-id ID --table-id ID
    python3 airtable_data.py create-table --base-id ID --name TEXT [--description TEXT]
    python3 airtable_data.py update-table --base-id ID --table-id ID [--name TEXT] [--description TEXT]
    python3 airtable_data.py create-field --base-id ID --table-id ID --field JSON
    python3 airtable_data.py update-field --base-id ID --table-id ID --field-id ID --updates JSON
    python3 airtable_data.py list-records --base-id ID --table NAME [--max N]
    python3 airtable_data.py get-record --base-id ID --table NAME --record-id ID
    python3 airtable_data.py create-record --base-id ID --table NAME --fields JSON
    python3 airtable_data.py update-records --base-id ID --table-id ID --records JSON
    python3 airtable_data.py delete-records --base-id ID --table-id ID --record-ids JSON
    python3 airtable_data.py search-records --base-id ID --table NAME --field NAME --value TEXT
    python3 airtable_data.py show [--offset N] [--limit N]

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


def cmd_list_bases(args):
    """List all Airtable bases."""
    return _call_tool("airtable_list_bases")


def cmd_list_tables(args):
    """List tables in a base."""
    return _call_tool("airtable_list_tables", {"base_id": args.base_id})


def cmd_describe_table(args):
    """Describe a table's schema and fields."""
    return _call_tool("airtable_describe_table", {
        "base_id": args.base_id,
        "table_id": args.table_id,
    })


def cmd_create_table(args):
    """Create a new table in a base."""
    tool_args = {"base_id": args.base_id, "table_name": args.name}
    if args.description:
        tool_args["description"] = args.description
    if args.fields:
        tool_args["fields"] = json.loads(args.fields)
    return _call_tool("airtable_create_table", tool_args)


def cmd_update_table(args):
    """Update a table's name or description."""
    tool_args = {"base_id": args.base_id, "table_id": args.table_id}
    if args.name:
        tool_args["name"] = args.name
    if args.description:
        tool_args["description"] = args.description
    return _call_tool("airtable_update_table", tool_args)


def cmd_create_field(args):
    """Create a new field in a table."""
    return _call_tool("airtable_create_field", {
        "base_id": args.base_id,
        "table_id": args.table_id,
        "field": json.loads(args.field),
    })


def cmd_update_field(args):
    """Update a field in a table."""
    return _call_tool("airtable_update_field", {
        "base_id": args.base_id,
        "table_id": args.table_id,
        "field_id": args.field_id,
        "updates": json.loads(args.updates),
    })


def cmd_list_records(args):
    """List records in a table."""
    tool_args = {"base_id": args.base_id, "table_name": args.table}
    if args.max:
        tool_args["max_records"] = args.max
    return _call_tool("airtable_list_records", tool_args)


def cmd_get_record(args):
    """Get a specific record by ID."""
    return _call_tool("airtable_get_record", {
        "base_id": args.base_id,
        "table_name": args.table,
        "record_id": args.record_id,
    })


def cmd_create_record(args):
    """Create a new record in a table."""
    return _call_tool("airtable_create_record", {
        "base_id": args.base_id,
        "table_name": args.table,
        "fields": json.loads(args.fields),
    })


def cmd_update_records(args):
    """Update one or more records (max 10 per call)."""
    return _call_tool("airtable_update_records", {
        "base_id": args.base_id,
        "table_id": args.table_id,
        "records": json.loads(args.records),
    })


def cmd_delete_records(args):
    """Delete one or more records."""
    return _call_tool("airtable_delete_records", {
        "base_id": args.base_id,
        "table_id": args.table_id,
        "record_ids": json.loads(args.record_ids),
    })


def cmd_search_records(args):
    """Search records by field value."""
    return _call_tool("airtable_search_records", {
        "base_id": args.base_id,
        "table_name": args.table,
        "field_name": args.field,
        "value": args.value,
    })


def cmd_show(args):
    """Show raw Airtable data."""
    return _call_tool("airtable_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Airtable Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # list-bases
    p = sub.add_parser("list-bases", help="List all bases")
    p.set_defaults(func=cmd_list_bases)

    # list-tables
    p = sub.add_parser("list-tables", help="List tables in a base")
    p.add_argument("--base-id", type=str, required=True)
    p.set_defaults(func=cmd_list_tables)

    # describe-table
    p = sub.add_parser("describe-table", help="Describe a table's schema")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table-id", type=str, required=True)
    p.set_defaults(func=cmd_describe_table)

    # create-table
    p = sub.add_parser("create-table", help="Create a new table")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--description", type=str)
    p.add_argument("--fields", type=str, help="JSON array of field definitions")
    p.set_defaults(func=cmd_create_table)

    # update-table
    p = sub.add_parser("update-table", help="Update a table's name or description")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table-id", type=str, required=True)
    p.add_argument("--name", type=str)
    p.add_argument("--description", type=str)
    p.set_defaults(func=cmd_update_table)

    # create-field
    p = sub.add_parser("create-field", help="Create a new field in a table")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table-id", type=str, required=True)
    p.add_argument("--field", type=str, required=True, help='JSON: \'{"name": "...", "type": "..."}\'')
    p.set_defaults(func=cmd_create_field)

    # update-field
    p = sub.add_parser("update-field", help="Update a field in a table")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table-id", type=str, required=True)
    p.add_argument("--field-id", type=str, required=True)
    p.add_argument("--updates", type=str, required=True, help='JSON: \'{"name": "..."}\'')
    p.set_defaults(func=cmd_update_field)

    # list-records
    p = sub.add_parser("list-records", help="List records in a table")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table", type=str, required=True)
    p.add_argument("--max", type=int, help="Maximum number of records to return")
    p.set_defaults(func=cmd_list_records)

    # get-record
    p = sub.add_parser("get-record", help="Get a record by ID")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table", type=str, required=True)
    p.add_argument("--record-id", type=str, required=True)
    p.set_defaults(func=cmd_get_record)

    # create-record
    p = sub.add_parser("create-record", help="Create a new record")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table", type=str, required=True)
    p.add_argument("--fields", type=str, required=True, help='JSON object: \'{"Field": "value"}\'')
    p.set_defaults(func=cmd_create_record)

    # update-records
    p = sub.add_parser("update-records", help="Update records (max 10)")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table-id", type=str, required=True)
    p.add_argument("--records", type=str, required=True,
                   help='JSON array: \'[{"id": "recXXX", "fields": {"Field": "value"}}]\'')
    p.set_defaults(func=cmd_update_records)

    # delete-records
    p = sub.add_parser("delete-records", help="Delete records")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table-id", type=str, required=True)
    p.add_argument("--record-ids", type=str, required=True, help='JSON array: \'["recXXX"]\'')
    p.set_defaults(func=cmd_delete_records)

    # search-records
    p = sub.add_parser("search-records", help="Search records by field value")
    p.add_argument("--base-id", type=str, required=True)
    p.add_argument("--table", type=str, required=True)
    p.add_argument("--field", type=str, required=True)
    p.add_argument("--value", type=str, required=True)
    p.set_defaults(func=cmd_search_records)

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
