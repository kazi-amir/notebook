#!/usr/bin/env python3
"""
Zendesk Help Desk Data - Manage tickets, users, organizations, groups, and comments.

Usage:
    python3 zendesk_data.py list-tickets [--status STATUS] [--priority PRIORITY]
        [--assignee-id ID] [--requester-id ID] [--organization-id ID] [--group-id ID]
        [--limit N] [--offset N] [--sort-by FIELD] [--sort-order ORDER]
    python3 zendesk_data.py get-ticket --id ID
    python3 zendesk_data.py create-ticket --subject TEXT --description TEXT --requester-id ID
        [--status STATUS] [--priority PRIORITY] [--type TYPE] [--assignee-id ID]
        [--organization-id ID] [--group-id ID] [--tags TAG1,TAG2]
        [--custom-fields JSON] [--due-at DATE]
    python3 zendesk_data.py update-ticket --id ID [--subject TEXT] [--status STATUS]
        [--priority PRIORITY] [--assignee-id ID] [--group-id ID] [--tags TAG1,TAG2]
        [--custom-fields JSON] [--due-at DATE]
    python3 zendesk_data.py delete-ticket --id ID
    python3 zendesk_data.py list-users [--role ROLE] [--email EMAIL]
        [--organization-id ID] [--active BOOL] [--limit N] [--offset N]
    python3 zendesk_data.py get-user --id ID
    python3 zendesk_data.py create-user --name TEXT --email TEXT [--role ROLE]
        [--organization-id ID] [--phone TEXT] [--time-zone TZ] [--locale LOCALE]
        [--tags TAG1,TAG2]
    python3 zendesk_data.py update-user --id ID [--name TEXT] [--email TEXT]
        [--role ROLE] [--active BOOL] [--verified BOOL] [--organization-id ID]
        [--tags TAG1,TAG2]
    python3 zendesk_data.py list-organizations [--name TEXT] [--domain TEXT]
        [--limit N] [--offset N]
    python3 zendesk_data.py get-organization --id ID
    python3 zendesk_data.py create-organization --name TEXT [--domain-names D1,D2]
        [--details TEXT] [--group-id ID] [--shared-tickets] [--shared-comments]
        [--tags TAG1,TAG2]
    python3 zendesk_data.py list-ticket-comments --ticket-id ID [--include-private]
    python3 zendesk_data.py add-ticket-comment --ticket-id ID --body TEXT
        [--author-id ID] [--public BOOL]
    python3 zendesk_data.py list-groups
    python3 zendesk_data.py create-group --name TEXT [--description TEXT] [--is-public BOOL]
    python3 zendesk_data.py search --query TEXT [--type TYPE] [--limit N]
    python3 zendesk_data.py stats

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


def cmd_list_tickets(args):
    tool_args = {"limit": args.limit, "offset": args.offset, "sort_by": args.sort_by, "sort_order": args.sort_order}
    if args.status:
        tool_args["status"] = args.status
    if args.priority:
        tool_args["priority"] = args.priority
    if args.assignee_id is not None:
        tool_args["assignee_id"] = args.assignee_id
    if args.requester_id is not None:
        tool_args["requester_id"] = args.requester_id
    if args.organization_id is not None:
        tool_args["organization_id"] = args.organization_id
    if args.group_id is not None:
        tool_args["group_id"] = args.group_id
    return _call_tool("zendesk_list_tickets", tool_args)


def cmd_get_ticket(args):
    return _call_tool("zendesk_get_ticket", {"ticket_id": args.id})


def cmd_create_ticket(args):
    tool_args = {
        "subject": args.subject,
        "description": args.description,
        "requester_id": args.requester_id,
        "status": args.status,
        "priority": args.priority,
        "type": args.type,
    }
    if args.assignee_id is not None:
        tool_args["assignee_id"] = args.assignee_id
    if args.organization_id is not None:
        tool_args["organization_id"] = args.organization_id
    if args.group_id is not None:
        tool_args["group_id"] = args.group_id
    if args.tags:
        tool_args["tags"] = [t.strip() for t in args.tags.split(",")]
    if args.custom_fields:
        tool_args["custom_fields"] = json.loads(args.custom_fields)
    if args.due_at:
        tool_args["due_at"] = args.due_at
    return _call_tool("zendesk_create_ticket", tool_args)


def cmd_update_ticket(args):
    tool_args = {"ticket_id": args.id}
    if args.subject:
        tool_args["subject"] = args.subject
    if args.status:
        tool_args["status"] = args.status
    if args.priority:
        tool_args["priority"] = args.priority
    if args.assignee_id is not None:
        tool_args["assignee_id"] = args.assignee_id
    if args.group_id is not None:
        tool_args["group_id"] = args.group_id
    if args.tags:
        tool_args["tags"] = [t.strip() for t in args.tags.split(",")]
    if args.custom_fields:
        tool_args["custom_fields"] = json.loads(args.custom_fields)
    if args.due_at:
        tool_args["due_at"] = args.due_at
    return _call_tool("zendesk_update_ticket", tool_args)


def cmd_delete_ticket(args):
    return _call_tool("zendesk_delete_ticket", {"ticket_id": args.id})


def cmd_list_users(args):
    tool_args = {"limit": args.limit, "offset": args.offset}
    if args.role:
        tool_args["role"] = args.role
    if args.email:
        tool_args["email"] = args.email
    if args.organization_id is not None:
        tool_args["organization_id"] = args.organization_id
    if args.active is not None:
        tool_args["active"] = args.active
    return _call_tool("zendesk_list_users", tool_args)


def cmd_get_user(args):
    return _call_tool("zendesk_get_user", {"user_id": args.id})


def cmd_create_user(args):
    tool_args = {
        "name": args.name,
        "email": args.email,
        "role": args.role,
        "time_zone": args.time_zone,
        "locale": args.locale,
    }
    if args.organization_id is not None:
        tool_args["organization_id"] = args.organization_id
    if args.phone:
        tool_args["phone"] = args.phone
    if args.tags:
        tool_args["tags"] = [t.strip() for t in args.tags.split(",")]
    return _call_tool("zendesk_create_user", tool_args)


def cmd_update_user(args):
    tool_args = {"user_id": args.id}
    if args.name:
        tool_args["name"] = args.name
    if args.email:
        tool_args["email"] = args.email
    if args.role:
        tool_args["role"] = args.role
    if args.active is not None:
        tool_args["active"] = args.active
    if args.verified is not None:
        tool_args["verified"] = args.verified
    if args.organization_id is not None:
        tool_args["organization_id"] = args.organization_id
    if args.tags:
        tool_args["tags"] = [t.strip() for t in args.tags.split(",")]
    return _call_tool("zendesk_update_user", tool_args)


def cmd_list_organizations(args):
    tool_args = {"limit": args.limit, "offset": args.offset}
    if args.name:
        tool_args["name"] = args.name
    if args.domain:
        tool_args["domain"] = args.domain
    return _call_tool("zendesk_list_organizations", tool_args)


def cmd_get_organization(args):
    return _call_tool("zendesk_get_organization", {"organization_id": args.id})


def cmd_create_organization(args):
    tool_args = {
        "name": args.name,
        "shared_tickets": args.shared_tickets,
        "shared_comments": args.shared_comments,
    }
    if args.domain_names:
        tool_args["domain_names"] = [d.strip() for d in args.domain_names.split(",")]
    if args.details:
        tool_args["details"] = args.details
    if args.group_id is not None:
        tool_args["group_id"] = args.group_id
    if args.tags:
        tool_args["tags"] = [t.strip() for t in args.tags.split(",")]
    return _call_tool("zendesk_create_organization", tool_args)


def cmd_list_ticket_comments(args):
    return _call_tool("zendesk_list_ticket_comments", {
        "ticket_id": args.ticket_id,
        "include_private": args.include_private,
    })


def cmd_add_ticket_comment(args):
    tool_args = {
        "ticket_id": args.ticket_id,
        "body": args.body,
        "public": args.public,
    }
    if args.author_id is not None:
        tool_args["author_id"] = args.author_id
    return _call_tool("zendesk_add_ticket_comment", tool_args)


def cmd_list_groups(args):
    return _call_tool("zendesk_list_groups")


def cmd_create_group(args):
    tool_args = {"name": args.name, "is_public": args.is_public}
    if args.description:
        tool_args["description"] = args.description
    return _call_tool("zendesk_create_group", tool_args)


def cmd_search(args):
    tool_args = {"query": args.query, "limit": args.limit}
    if args.type:
        tool_args["type"] = args.type
    return _call_tool("zendesk_search", tool_args)


def cmd_stats(args):
    return _call_tool("zendesk_get_stats")


# ==================== Main ====================


def _str_to_bool(value):
    """Convert string to bool for argparse."""
    if value.lower() in ("true", "1", "yes"):
        return True
    elif value.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"Boolean value expected, got '{value}'")


def main():
    parser = argparse.ArgumentParser(description="Zendesk Help Desk Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- Tickets ----

    # list-tickets
    p = sub.add_parser("list-tickets", help="List tickets with filters")
    p.add_argument("--status", type=str, help="Filter: new, open, pending, hold, solved, closed")
    p.add_argument("--priority", type=str, help="Filter: low, normal, high, urgent")
    p.add_argument("--assignee-id", type=int, help="Filter by assignee ID")
    p.add_argument("--requester-id", type=int, help="Filter by requester ID")
    p.add_argument("--organization-id", type=int, help="Filter by organization ID")
    p.add_argument("--group-id", type=int, help="Filter by group ID")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--sort-by", type=str, default="created_at")
    p.add_argument("--sort-order", type=str, default="desc")
    p.set_defaults(func=cmd_list_tickets)

    # get-ticket
    p = sub.add_parser("get-ticket", help="Get ticket by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_get_ticket)

    # create-ticket
    p = sub.add_parser("create-ticket", help="Create a new ticket")
    p.add_argument("--subject", type=str, required=True)
    p.add_argument("--description", type=str, required=True)
    p.add_argument("--requester-id", type=int, required=True)
    p.add_argument("--status", type=str, default="new")
    p.add_argument("--priority", type=str, default="normal")
    p.add_argument("--type", type=str, default="problem")
    p.add_argument("--assignee-id", type=int)
    p.add_argument("--organization-id", type=int)
    p.add_argument("--group-id", type=int)
    p.add_argument("--tags", type=str, help="Comma-separated tags")
    p.add_argument("--custom-fields", type=str, help="JSON string of custom fields")
    p.add_argument("--due-at", type=str, help="Due date (ISO format)")
    p.set_defaults(func=cmd_create_ticket)

    # update-ticket
    p = sub.add_parser("update-ticket", help="Update an existing ticket")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--subject", type=str)
    p.add_argument("--status", type=str)
    p.add_argument("--priority", type=str)
    p.add_argument("--assignee-id", type=int)
    p.add_argument("--group-id", type=int)
    p.add_argument("--tags", type=str, help="Comma-separated tags")
    p.add_argument("--custom-fields", type=str, help="JSON string of custom fields")
    p.add_argument("--due-at", type=str, help="Due date (ISO format)")
    p.set_defaults(func=cmd_update_ticket)

    # delete-ticket
    p = sub.add_parser("delete-ticket", help="Delete a ticket")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_delete_ticket)

    # ---- Users ----

    # list-users
    p = sub.add_parser("list-users", help="List users with filters")
    p.add_argument("--role", type=str, help="Filter: end-user, agent, admin")
    p.add_argument("--email", type=str, help="Filter by email (partial match)")
    p.add_argument("--organization-id", type=int, help="Filter by organization ID")
    p.add_argument("--active", type=_str_to_bool, help="Filter by active status")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--offset", type=int, default=0)
    p.set_defaults(func=cmd_list_users)

    # get-user
    p = sub.add_parser("get-user", help="Get user by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_get_user)

    # create-user
    p = sub.add_parser("create-user", help="Create a new user")
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--email", type=str, required=True)
    p.add_argument("--role", type=str, default="end-user")
    p.add_argument("--organization-id", type=int)
    p.add_argument("--phone", type=str)
    p.add_argument("--time-zone", type=str, default="UTC")
    p.add_argument("--locale", type=str, default="en-US")
    p.add_argument("--tags", type=str, help="Comma-separated tags")
    p.set_defaults(func=cmd_create_user)

    # update-user
    p = sub.add_parser("update-user", help="Update an existing user")
    p.add_argument("--id", type=int, required=True)
    p.add_argument("--name", type=str)
    p.add_argument("--email", type=str)
    p.add_argument("--role", type=str)
    p.add_argument("--active", type=_str_to_bool)
    p.add_argument("--verified", type=_str_to_bool)
    p.add_argument("--organization-id", type=int)
    p.add_argument("--tags", type=str, help="Comma-separated tags")
    p.set_defaults(func=cmd_update_user)

    # ---- Organizations ----

    # list-organizations
    p = sub.add_parser("list-organizations", help="List organizations with filters")
    p.add_argument("--name", type=str, help="Filter by name (partial match)")
    p.add_argument("--domain", type=str, help="Filter by domain")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--offset", type=int, default=0)
    p.set_defaults(func=cmd_list_organizations)

    # get-organization
    p = sub.add_parser("get-organization", help="Get organization by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_get_organization)

    # create-organization
    p = sub.add_parser("create-organization", help="Create a new organization")
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--domain-names", type=str, help="Comma-separated domain names")
    p.add_argument("--details", type=str)
    p.add_argument("--group-id", type=int)
    p.add_argument("--shared-tickets", action="store_true", default=False)
    p.add_argument("--shared-comments", action="store_true", default=False)
    p.add_argument("--tags", type=str, help="Comma-separated tags")
    p.set_defaults(func=cmd_create_organization)

    # ---- Comments ----

    # list-ticket-comments
    p = sub.add_parser("list-ticket-comments", help="List comments for a ticket")
    p.add_argument("--ticket-id", type=int, required=True)
    p.add_argument("--include-private", action="store_true", default=False)
    p.set_defaults(func=cmd_list_ticket_comments)

    # add-ticket-comment
    p = sub.add_parser("add-ticket-comment", help="Add a comment to a ticket")
    p.add_argument("--ticket-id", type=int, required=True)
    p.add_argument("--body", type=str, required=True)
    p.add_argument("--author-id", type=int)
    p.add_argument("--public", type=_str_to_bool, default=True)
    p.set_defaults(func=cmd_add_ticket_comment)

    # ---- Groups ----

    # list-groups
    p = sub.add_parser("list-groups", help="List all agent groups")
    p.set_defaults(func=cmd_list_groups)

    # create-group
    p = sub.add_parser("create-group", help="Create a new agent group")
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--description", type=str)
    p.add_argument("--is-public", type=_str_to_bool, default=True)
    p.set_defaults(func=cmd_create_group)

    # ---- Search & Stats ----

    # search
    p = sub.add_parser("search", help="Search tickets, users, and organizations")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--type", type=str, help="Entity type: ticket, user, organization")
    p.add_argument("--limit", type=int, default=25)
    p.set_defaults(func=cmd_search)

    # stats
    p = sub.add_parser("stats", help="Get system statistics")
    p.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
