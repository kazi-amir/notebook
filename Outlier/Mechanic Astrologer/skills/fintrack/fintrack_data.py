#!/usr/bin/env python3
"""
FinTrack Personal Finance Data - Manage users, accounts, transactions, and subscriptions.

Usage:
    python3 fintrack_data.py users [--limit N]
    python3 fintrack_data.py user --id ID
    python3 fintrack_data.py search-users --query TEXT [--limit N]
    python3 fintrack_data.py accounts [--limit N]
    python3 fintrack_data.py account --id ID
    python3 fintrack_data.py accounts-by-user --user-id ID
    python3 fintrack_data.py search-accounts [--institution TEXT] [--type TYPE]
        [--status STATUS] [--limit N]
    python3 fintrack_data.py transactions [--limit N]
    python3 fintrack_data.py transaction --id ID
    python3 fintrack_data.py transactions-by-user --user-id ID [--limit N]
    python3 fintrack_data.py search-transactions [--merchant TEXT] [--category TEXT]
        [--start DATE] [--end DATE] [--min-amount N] [--max-amount N]
        [--user-id ID] [--limit N]
    python3 fintrack_data.py spending-by-category --user-id ID [--start DATE] [--end DATE]
    python3 fintrack_data.py subscriptions [--limit N]
    python3 fintrack_data.py subscription --id ID
    python3 fintrack_data.py subscriptions-by-user --user-id ID
    python3 fintrack_data.py active-subscriptions [--limit N]
    python3 fintrack_data.py upcoming-billings [--days N]

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


def cmd_users(args):
    return _call_tool("fintrack_get_all_users", {"limit": args.limit})


def cmd_user(args):
    return _call_tool("fintrack_get_user", {"user_id": args.id})


def cmd_search_users(args):
    return _call_tool("fintrack_search_users", {"query": args.query, "limit": args.limit})


def cmd_accounts(args):
    return _call_tool("fintrack_get_all_accounts", {"limit": args.limit})


def cmd_account(args):
    return _call_tool("fintrack_get_account", {"account_id": args.id})


def cmd_accounts_by_user(args):
    return _call_tool("fintrack_get_accounts_by_user", {"user_id": args.user_id})


def cmd_search_accounts(args):
    tool_args = {"limit": args.limit}
    if args.institution:
        tool_args["institution"] = args.institution
    if args.type:
        # Normalize account type: "Credit Card" -> "credit_card", etc.
        tool_args["account_type"] = args.type.lower().replace(" ", "_")
    if args.status:
        tool_args["status"] = args.status
    return _call_tool("fintrack_search_accounts", tool_args)


def cmd_transactions(args):
    return _call_tool("fintrack_get_all_transactions", {"limit": args.limit})


def cmd_transaction(args):
    return _call_tool("fintrack_get_transaction", {"transaction_id": args.id})


def cmd_transactions_by_user(args):
    return _call_tool("fintrack_get_transactions_by_user", {"user_id": args.user_id, "limit": args.limit})


def cmd_search_transactions(args):
    tool_args = {"limit": args.limit}
    if args.merchant:
        tool_args["merchant"] = args.merchant
    if args.category:
        tool_args["category"] = args.category
    if args.start:
        tool_args["date_from"] = args.start
    if args.end:
        tool_args["date_to"] = args.end
    if args.min_amount is not None:
        tool_args["amount_min"] = args.min_amount
    if args.max_amount is not None:
        tool_args["amount_max"] = args.max_amount
    if args.user_id:
        tool_args["user_id"] = args.user_id
    return _call_tool("fintrack_search_transactions", tool_args)


def cmd_spending_by_category(args):
    tool_args = {"user_id": args.user_id}
    if args.start:
        tool_args["date_from"] = args.start
    if args.end:
        tool_args["date_to"] = args.end
    return _call_tool("fintrack_get_spending_by_category", tool_args)


def cmd_subscriptions(args):
    return _call_tool("fintrack_get_all_subscriptions", {"limit": args.limit})


def cmd_subscription(args):
    return _call_tool("fintrack_get_subscription", {"subscription_id": args.id})


def cmd_subscriptions_by_user(args):
    return _call_tool("fintrack_get_subscriptions_by_user", {"user_id": args.user_id})


def cmd_active_subscriptions(args):
    return _call_tool("fintrack_get_active_subscriptions", {"limit": args.limit})


def cmd_upcoming_billings(args):
    return _call_tool("fintrack_get_upcoming_billings", {"within_days": args.days})


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="FinTrack Personal Finance Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # users
    p = sub.add_parser("users", help="List all users")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_users)

    # user
    p = sub.add_parser("user", help="Get user by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_user)

    # search-users
    p = sub.add_parser("search-users", help="Search users")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_search_users)

    # accounts
    p = sub.add_parser("accounts", help="List all accounts")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_accounts)

    # account
    p = sub.add_parser("account", help="Get account by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_account)

    # accounts-by-user
    p = sub.add_parser("accounts-by-user", help="Get accounts for a user")
    p.add_argument("--user-id", type=str, required=True)
    p.set_defaults(func=cmd_accounts_by_user)

    # search-accounts
    p = sub.add_parser("search-accounts", help="Search accounts")
    p.add_argument("--institution", type=str)
    p.add_argument("--type", type=str)
    p.add_argument("--status", type=str)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_search_accounts)

    # transactions
    p = sub.add_parser("transactions", help="List all transactions")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_transactions)

    # transaction
    p = sub.add_parser("transaction", help="Get transaction by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_transaction)

    # transactions-by-user
    p = sub.add_parser("transactions-by-user", help="Get transactions for a user")
    p.add_argument("--user-id", type=str, required=True)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_transactions_by_user)

    # search-transactions
    p = sub.add_parser("search-transactions", help="Search transactions")
    p.add_argument("--merchant", type=str)
    p.add_argument("--category", type=str)
    p.add_argument("--start", type=str)
    p.add_argument("--end", type=str)
    p.add_argument("--min-amount", type=float)
    p.add_argument("--max-amount", type=float)
    p.add_argument("--user-id", type=str)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_search_transactions)

    # spending-by-category
    p = sub.add_parser("spending-by-category", help="Spending breakdown by category")
    p.add_argument("--user-id", type=str, required=True)
    p.add_argument("--start", type=str)
    p.add_argument("--end", type=str)
    p.set_defaults(func=cmd_spending_by_category)

    # subscriptions
    p = sub.add_parser("subscriptions", help="List all subscriptions")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_subscriptions)

    # subscription
    p = sub.add_parser("subscription", help="Get subscription by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_subscription)

    # subscriptions-by-user
    p = sub.add_parser("subscriptions-by-user", help="Get subscriptions for a user")
    p.add_argument("--user-id", type=str, required=True)
    p.set_defaults(func=cmd_subscriptions_by_user)

    # active-subscriptions
    p = sub.add_parser("active-subscriptions", help="Get active subscriptions")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_active_subscriptions)

    # upcoming-billings
    p = sub.add_parser("upcoming-billings", help="Get upcoming billings")
    p.add_argument("--days", type=int, default=7)
    p.set_defaults(func=cmd_upcoming_billings)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
