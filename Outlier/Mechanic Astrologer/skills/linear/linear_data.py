#!/usr/bin/env python3
"""
Linear Data - Manage users, teams, projects, issues, and comments.

Usage:
    # List users
    python3 linear_data.py list-users [--query Q] [--team TEAM] [--include-disabled] [--order-by FIELD] [--limit N] [--after CURSOR] [--before CURSOR]

    # Get a specific user (by ID, name, email, or "me")
    python3 linear_data.py get-user --id ID

    # Create a user
    python3 linear_data.py create-user --email EMAIL --name NAME

    # List teams
    python3 linear_data.py list-teams [--query Q] [--include-archived] [--order-by FIELD] [--limit N] [--offset N] [--created-at DATE] [--updated-at DATE]

    # Get a specific team
    python3 linear_data.py get-team --id ID

    # Create a team
    python3 linear_data.py create-team --name NAME

    # List projects
    python3 linear_data.py list-projects [--query Q] [--team TEAM] [--member USR] [--state STATE] [--include-archived] [--order-by FIELD] [--limit N] [--offset N] [--created-at DATE] [--updated-at DATE]

    # Get a specific project
    python3 linear_data.py get-project --id ID

    # Create a project
    python3 linear_data.py create-project --name NAME --team TEAM [--description D] [--summary S] [--lead USR] [--priority N] [--state STATE] [--start-date DATE] [--target-date DATE] [--labels JSON]

    # Update a project
    python3 linear_data.py update-project --id ID [--name N] [--description D] [--summary S] [--lead USR] [--priority N] [--state STATE] [--start-date DATE] [--target-date DATE] [--labels JSON]

    # List issues
    python3 linear_data.py list-issues [--query Q] [--team TEAM] [--project PROJ] [--assignee USR] [--parent-id ID] [--state STATE] [--label LBL] [--cycle CYC] [--include-archived] [--order-by FIELD] [--limit N] [--offset N] [--created-at DATE] [--updated-at DATE]

    # Get a specific issue
    python3 linear_data.py get-issue --id ID

    # Create an issue
    python3 linear_data.py create-issue --team TEAM --title TITLE [--description D] [--assignee USR] [--project PROJ] [--parent-id ID] [--priority N] [--state STATE] [--due-date DATE] [--cycle CYC] [--labels JSON] [--links JSON]

    # Update an issue
    python3 linear_data.py update-issue --id ID [--title T] [--description D] [--assignee USR] [--project PROJ] [--parent-id ID] [--priority N] [--state STATE] [--due-date DATE] [--estimate N] [--cycle CYC] [--labels JSON] [--links JSON]

    # List comments on an issue
    python3 linear_data.py list-comments --issue-id ID

    # Create a comment
    python3 linear_data.py create-comment --issue-id ID --body TEXT [--parent-id CMT]

    # Show raw data
    python3 linear_data.py show [--offset N] [--limit N]

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

def cmd_list_users(args):
    """List users with optional filters."""
    tool_args = {}
    if args.query:
        tool_args["query"] = args.query
    if args.team:
        tool_args["team"] = args.team
    if args.include_disabled:
        tool_args["includeDisabled"] = True
    if args.order_by:
        tool_args["orderBy"] = args.order_by
    if args.limit is not None:
        tool_args["limit"] = args.limit
    if args.after:
        tool_args["after"] = args.after
    if args.before:
        tool_args["before"] = args.before
    return _call_tool("linear_list_users", tool_args)


def cmd_get_user(args):
    """Get a specific user by ID, name, email, or 'me'."""
    return _call_tool("linear_get_user", {"query": args.id})


def cmd_create_user(args):
    """Create a new user."""
    return _call_tool("linear_create_user", {
        "email": args.email,
        "name": args.name,
    })


# --- Teams ---

def cmd_list_teams(args):
    """List teams with optional filters."""
    tool_args = {}
    if args.query:
        tool_args["query"] = args.query
    if args.include_archived:
        tool_args["includeArchived"] = True
    if args.order_by:
        tool_args["orderBy"] = args.order_by
    if args.limit is not None:
        tool_args["limit"] = args.limit
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.created_at:
        tool_args["createdAt"] = args.created_at
    if args.updated_at:
        tool_args["updatedAt"] = args.updated_at
    return _call_tool("linear_list_teams", tool_args)


def cmd_get_team(args):
    """Get a specific team by ID."""
    return _call_tool("linear_get_team", {"query": args.id})


def cmd_create_team(args):
    """Create a new team."""
    return _call_tool("linear_create_team", {"name": args.name})


# --- Projects ---

def cmd_list_projects(args):
    """List projects with optional filters."""
    tool_args = {}
    if args.query:
        tool_args["query"] = args.query
    if args.team:
        tool_args["team"] = args.team
    if args.member:
        tool_args["member"] = args.member
    if args.state:
        tool_args["state"] = args.state
    if args.include_archived:
        tool_args["includeArchived"] = True
    if args.order_by:
        tool_args["orderBy"] = args.order_by
    if args.limit is not None:
        tool_args["limit"] = args.limit
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.created_at:
        tool_args["createdAt"] = args.created_at
    if args.updated_at:
        tool_args["updatedAt"] = args.updated_at
    return _call_tool("linear_list_projects", tool_args)


def cmd_get_project(args):
    """Get a specific project by ID."""
    return _call_tool("linear_get_project", {"query": args.id})


def cmd_create_project(args):
    """Create a new project."""
    tool_args = {"name": args.name, "team": args.team}
    if args.description:
        tool_args["description"] = args.description
    if args.summary:
        tool_args["summary"] = args.summary
    if args.lead:
        tool_args["lead"] = args.lead
    if args.priority is not None:
        tool_args["priority"] = args.priority
    if args.state:
        tool_args["state"] = args.state
    if args.start_date:
        tool_args["startDate"] = args.start_date
    if args.target_date:
        tool_args["targetDate"] = args.target_date
    if args.labels:
        tool_args["labels"] = json.loads(args.labels)
    return _call_tool("linear_create_project", tool_args)


def cmd_update_project(args):
    """Update an existing project."""
    tool_args = {"id": args.id}
    if args.name:
        tool_args["name"] = args.name
    if args.description:
        tool_args["description"] = args.description
    if args.summary:
        tool_args["summary"] = args.summary
    if args.lead:
        tool_args["lead"] = args.lead
    if args.priority is not None:
        tool_args["priority"] = args.priority
    if args.state:
        tool_args["state"] = args.state
    if args.start_date:
        tool_args["startDate"] = args.start_date
    if args.target_date:
        tool_args["targetDate"] = args.target_date
    if args.labels:
        tool_args["labels"] = json.loads(args.labels)
    return _call_tool("linear_update_project", tool_args)


# --- Issues ---

def cmd_list_issues(args):
    """List issues with optional filters."""
    tool_args = {}
    if args.query:
        tool_args["query"] = args.query
    if args.team:
        tool_args["team"] = args.team
    if args.project:
        tool_args["project"] = args.project
    if args.assignee:
        tool_args["assignee"] = args.assignee
    if args.parent_id:
        tool_args["parentId"] = args.parent_id
    if args.state:
        tool_args["state"] = args.state
    if args.label:
        tool_args["label"] = args.label
    if args.cycle:
        tool_args["cycle"] = args.cycle
    if args.include_archived:
        tool_args["includeArchived"] = True
    if args.order_by:
        tool_args["orderBy"] = args.order_by
    if args.limit is not None:
        tool_args["limit"] = args.limit
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.created_at:
        tool_args["createdAt"] = args.created_at
    if args.updated_at:
        tool_args["updatedAt"] = args.updated_at
    return _call_tool("linear_list_issues", tool_args)


def cmd_get_issue(args):
    """Get a specific issue by ID."""
    return _call_tool("linear_get_issue", {"id": args.id})


def cmd_create_issue(args):
    """Create a new issue."""
    tool_args = {"team": args.team, "title": args.title}
    if args.description:
        tool_args["description"] = args.description
    if args.assignee:
        tool_args["assignee"] = args.assignee
    if args.project:
        tool_args["project"] = args.project
    if args.parent_id:
        tool_args["parentId"] = args.parent_id
    if args.priority is not None:
        tool_args["priority"] = args.priority
    if args.state:
        tool_args["state"] = args.state
    if args.due_date:
        tool_args["dueDate"] = args.due_date
    if args.cycle:
        tool_args["cycle"] = args.cycle
    if args.labels:
        tool_args["labels"] = json.loads(args.labels)
    if args.links:
        tool_args["links"] = json.loads(args.links)
    return _call_tool("linear_create_issue", tool_args)


def cmd_update_issue(args):
    """Update an existing issue."""
    tool_args = {"id": args.id}
    if args.title:
        tool_args["title"] = args.title
    if args.description:
        tool_args["description"] = args.description
    if args.assignee:
        tool_args["assignee"] = args.assignee
    if args.project:
        tool_args["project"] = args.project
    if args.parent_id:
        tool_args["parentId"] = args.parent_id
    if args.priority is not None:
        tool_args["priority"] = args.priority
    if args.state:
        tool_args["state"] = args.state
    if args.due_date:
        tool_args["dueDate"] = args.due_date
    if args.estimate is not None:
        tool_args["estimate"] = args.estimate
    if args.cycle:
        tool_args["cycle"] = args.cycle
    if args.labels:
        tool_args["labels"] = json.loads(args.labels)
    if args.links:
        tool_args["links"] = json.loads(args.links)
    return _call_tool("linear_update_issue", tool_args)


# --- Comments ---

def cmd_list_comments(args):
    """List comments on an issue."""
    return _call_tool("linear_list_comments", {"issueId": args.issue_id})


def cmd_create_comment(args):
    """Create a comment on an issue."""
    tool_args = {"issueId": args.issue_id, "body": args.body}
    if args.parent_id:
        tool_args["parentId"] = args.parent_id
    return _call_tool("linear_create_comment", tool_args)


# --- Utility ---

def cmd_show(args):
    """Show raw Linear data."""
    return _call_tool("linear_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Linear Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Users ---

    # list-users
    p = sub.add_parser("list-users", help="List users")
    p.add_argument("--query", type=str)
    p.add_argument("--team", type=str)
    p.add_argument("--include-disabled", action="store_true")
    p.add_argument("--order-by", type=str)
    p.add_argument("--limit", type=int)
    p.add_argument("--after", type=str)
    p.add_argument("--before", type=str)
    p.set_defaults(func=cmd_list_users)

    # get-user
    p = sub.add_parser("get-user", help="Get a user by ID, name, email, or 'me'")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_user)

    # create-user
    p = sub.add_parser("create-user", help="Create a new user")
    p.add_argument("--email", type=str, required=True)
    p.add_argument("--name", type=str, required=True)
    p.set_defaults(func=cmd_create_user)

    # --- Teams ---

    # list-teams
    p = sub.add_parser("list-teams", help="List teams")
    p.add_argument("--query", type=str)
    p.add_argument("--include-archived", action="store_true")
    p.add_argument("--order-by", type=str)
    p.add_argument("--limit", type=int)
    p.add_argument("--offset", type=int)
    p.add_argument("--created-at", type=str)
    p.add_argument("--updated-at", type=str)
    p.set_defaults(func=cmd_list_teams)

    # get-team
    p = sub.add_parser("get-team", help="Get a team by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_team)

    # create-team
    p = sub.add_parser("create-team", help="Create a new team")
    p.add_argument("--name", type=str, required=True)
    p.set_defaults(func=cmd_create_team)

    # --- Projects ---

    # list-projects
    p = sub.add_parser("list-projects", help="List projects")
    p.add_argument("--query", type=str)
    p.add_argument("--team", type=str)
    p.add_argument("--member", type=str)
    p.add_argument("--state", type=str,
                   help="State: backlog, planned, started, paused, completed, canceled")
    p.add_argument("--include-archived", action="store_true")
    p.add_argument("--order-by", type=str)
    p.add_argument("--limit", type=int)
    p.add_argument("--offset", type=int)
    p.add_argument("--created-at", type=str)
    p.add_argument("--updated-at", type=str)
    p.set_defaults(func=cmd_list_projects)

    # get-project
    p = sub.add_parser("get-project", help="Get a project by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_project)

    # create-project
    p = sub.add_parser("create-project", help="Create a new project")
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--team", type=str, required=True)
    p.add_argument("--description", type=str)
    p.add_argument("--summary", type=str)
    p.add_argument("--lead", type=str)
    p.add_argument("--priority", type=int)
    p.add_argument("--state", type=str,
                   help="State: backlog, planned, started, paused, completed, canceled")
    p.add_argument("--start-date", type=str)
    p.add_argument("--target-date", type=str)
    p.add_argument("--labels", type=str, help="JSON array of labels")
    p.set_defaults(func=cmd_create_project)

    # update-project
    p = sub.add_parser("update-project", help="Update a project")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--name", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--summary", type=str)
    p.add_argument("--lead", type=str)
    p.add_argument("--priority", type=int)
    p.add_argument("--state", type=str,
                   help="State: backlog, planned, started, paused, completed, canceled")
    p.add_argument("--start-date", type=str)
    p.add_argument("--target-date", type=str)
    p.add_argument("--labels", type=str, help="JSON array of labels")
    p.set_defaults(func=cmd_update_project)

    # --- Issues ---

    # list-issues
    p = sub.add_parser("list-issues", help="List issues")
    p.add_argument("--query", type=str)
    p.add_argument("--team", type=str)
    p.add_argument("--project", type=str)
    p.add_argument("--assignee", type=str)
    p.add_argument("--parent-id", type=str)
    p.add_argument("--state", type=str)
    p.add_argument("--label", type=str)
    p.add_argument("--cycle", type=str)
    p.add_argument("--include-archived", action="store_true")
    p.add_argument("--order-by", type=str)
    p.add_argument("--limit", type=int)
    p.add_argument("--offset", type=int)
    p.add_argument("--created-at", type=str)
    p.add_argument("--updated-at", type=str)
    p.set_defaults(func=cmd_list_issues)

    # get-issue
    p = sub.add_parser("get-issue", help="Get an issue by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_issue)

    # create-issue
    p = sub.add_parser("create-issue", help="Create a new issue")
    p.add_argument("--team", type=str, required=True)
    p.add_argument("--title", type=str, required=True)
    p.add_argument("--description", type=str)
    p.add_argument("--assignee", type=str)
    p.add_argument("--project", type=str)
    p.add_argument("--parent-id", type=str)
    p.add_argument("--priority", type=int,
                   help="Priority: 0 (none), 1 (urgent), 2 (high), 3 (medium), 4 (low)")
    p.add_argument("--state", type=str)
    p.add_argument("--due-date", type=str)
    p.add_argument("--cycle", type=str)
    p.add_argument("--labels", type=str, help="JSON array of labels")
    p.add_argument("--links", type=str, help="JSON array of URL strings")
    p.set_defaults(func=cmd_create_issue)

    # update-issue
    p = sub.add_parser("update-issue", help="Update an issue")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--title", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--assignee", type=str)
    p.add_argument("--project", type=str)
    p.add_argument("--parent-id", type=str)
    p.add_argument("--priority", type=int,
                   help="Priority: 0 (none), 1 (urgent), 2 (high), 3 (medium), 4 (low)")
    p.add_argument("--state", type=str)
    p.add_argument("--due-date", type=str)
    p.add_argument("--estimate", type=int)
    p.add_argument("--cycle", type=str)
    p.add_argument("--labels", type=str, help="JSON array of labels")
    p.add_argument("--links", type=str, help="JSON array of URL strings")
    p.set_defaults(func=cmd_update_issue)

    # --- Comments ---

    # list-comments
    p = sub.add_parser("list-comments", help="List comments on an issue")
    p.add_argument("--issue-id", type=str, required=True)
    p.set_defaults(func=cmd_list_comments)

    # create-comment
    p = sub.add_parser("create-comment", help="Create a comment on an issue")
    p.add_argument("--issue-id", type=str, required=True)
    p.add_argument("--body", type=str, required=True)
    p.add_argument("--parent-id", type=str)
    p.set_defaults(func=cmd_create_comment)

    # --- Utility ---

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
