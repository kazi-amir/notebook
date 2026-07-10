#!/usr/bin/env python3
"""
Stripe Billing & Payments Data - Manage customers, invoices, payments, subscriptions.

Usage:
    # List customers
    python3 stripe_data.py customers [--limit N]

    # Get a specific customer
    python3 stripe_data.py customer --id ID

    # Search customers
    python3 stripe_data.py search-customers --query TEXT [--limit N]

    # List payment methods for a customer
    python3 stripe_data.py payment-methods --customer-id ID

    # List invoices
    python3 stripe_data.py invoices [--customer-id ID] [--status STATUS] [--limit N]

    # Get a specific invoice
    python3 stripe_data.py invoice --id ID

    # List invoice items
    python3 stripe_data.py invoice-items [--invoice-id ID] [--customer-id ID] [--limit N]

    # List payment intents
    python3 stripe_data.py payments [--customer-id ID] [--status STATUS] [--limit N]

    # Get a specific payment intent
    python3 stripe_data.py payment --id ID

    # List charges
    python3 stripe_data.py charges [--customer-id ID] [--payment-intent-id ID] [--limit N]

    # Search charges
    python3 stripe_data.py search-charges --query TEXT [--limit N]

    # List products
    python3 stripe_data.py products [--limit N]

    # Get a specific product
    python3 stripe_data.py product --id ID

    # List prices
    python3 stripe_data.py prices [--product-id ID] [--limit N]

    # List subscriptions
    python3 stripe_data.py subscriptions [--customer-id ID] [--status STATUS] [--limit N]

    # Get a specific subscription
    python3 stripe_data.py subscription --id ID

    # List refunds
    python3 stripe_data.py refunds [--charge-id ID] [--limit N]

    # List disputes
    python3 stripe_data.py disputes [--status STATUS] [--limit N]

    # Get account info
    python3 stripe_data.py account

    # List balance transactions
    python3 stripe_data.py balance-transactions [--type TYPE] [--limit N]

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


def cmd_customers(args):
    """List customers."""
    return _call_tool("stripe_list_customers", {"limit": args.limit})


def cmd_customer(args):
    """Get a specific customer."""
    return _call_tool("stripe_get_customer", {"customer_id": args.id})


def cmd_search_customers(args):
    """Search customers by name or email."""
    return _call_tool("stripe_search_customers", {
        "query": args.query, "limit": args.limit,
    })


def cmd_payment_methods(args):
    """List payment methods for a customer."""
    tool_args = {"customer_id": args.customer_id, "limit": args.limit}
    if args.type:
        tool_args["type"] = args.type
    return _call_tool("stripe_list_payment_methods", tool_args)


def cmd_invoices(args):
    """List invoices with optional filters."""
    tool_args = {"limit": args.limit}
    if args.customer_id:
        tool_args["customer_id"] = args.customer_id
    if args.status:
        tool_args["status"] = args.status
    return _call_tool("stripe_list_invoices", tool_args)


def cmd_invoice(args):
    """Get a specific invoice."""
    return _call_tool("stripe_get_invoice", {"invoice_id": args.id})


def cmd_invoice_items(args):
    """List invoice items."""
    tool_args = {"limit": args.limit}
    if args.invoice_id:
        tool_args["invoice_id"] = args.invoice_id
    if args.customer_id:
        tool_args["customer_id"] = args.customer_id
    return _call_tool("stripe_list_invoice_items", tool_args)


def cmd_payments(args):
    """List payment intents."""
    tool_args = {"limit": args.limit}
    if args.customer_id:
        tool_args["customer_id"] = args.customer_id
    if args.status:
        tool_args["status"] = args.status
    return _call_tool("stripe_list_payment_intents", tool_args)


def cmd_payment(args):
    """Get a specific payment intent."""
    return _call_tool("stripe_get_payment_intent", {"payment_intent_id": args.id})


def cmd_charges(args):
    """List charges."""
    tool_args = {"limit": args.limit}
    if args.customer_id:
        tool_args["customer_id"] = args.customer_id
    if args.payment_intent_id:
        tool_args["payment_intent_id"] = args.payment_intent_id
    return _call_tool("stripe_list_charges", tool_args)


def cmd_search_charges(args):
    """Search charges."""
    return _call_tool("stripe_search_charges", {
        "query": args.query, "limit": args.limit,
    })


def cmd_products(args):
    """List products."""
    return _call_tool("stripe_list_products", {"limit": args.limit})


def cmd_product(args):
    """Get a specific product."""
    return _call_tool("stripe_get_product", {"product_id": args.id})


def cmd_prices(args):
    """List prices."""
    tool_args = {"limit": args.limit}
    if args.product_id:
        tool_args["product_id"] = args.product_id
    return _call_tool("stripe_list_prices", tool_args)


def cmd_subscriptions(args):
    """List subscriptions."""
    tool_args = {"limit": args.limit}
    if args.customer_id:
        tool_args["customer_id"] = args.customer_id
    if args.status:
        tool_args["status"] = args.status
    return _call_tool("stripe_list_subscriptions", tool_args)


def cmd_subscription(args):
    """Get a specific subscription."""
    return _call_tool("stripe_get_subscription", {"subscription_id": args.id})


def cmd_refunds(args):
    """List refunds."""
    tool_args = {"limit": args.limit}
    if args.charge_id:
        tool_args["charge_id"] = args.charge_id
    return _call_tool("stripe_list_refunds", tool_args)


def cmd_disputes(args):
    """List disputes."""
    tool_args = {"limit": args.limit}
    if args.status:
        tool_args["status"] = args.status
    return _call_tool("stripe_list_disputes", tool_args)


def cmd_account(args):
    """Get account info."""
    return _call_tool("stripe_get_account_info")


def cmd_balance_transactions(args):
    """List balance transactions."""
    tool_args = {"limit": args.limit}
    if args.type:
        tool_args["type"] = args.type
    return _call_tool("stripe_list_balance_transactions", tool_args)


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Stripe Billing & Payments Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # customers
    p = sub.add_parser("customers", help="List customers")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_customers)

    # customer
    p = sub.add_parser("customer", help="Get a customer by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_customer)

    # search-customers
    p = sub.add_parser("search-customers", help="Search customers")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search_customers)

    # payment-methods
    p = sub.add_parser("payment-methods", help="List payment methods")
    p.add_argument("--customer-id", type=str, required=True)
    p.add_argument("--type", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_payment_methods)

    # invoices
    p = sub.add_parser("invoices", help="List invoices")
    p.add_argument("--customer-id", type=str)
    p.add_argument("--status", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_invoices)

    # invoice
    p = sub.add_parser("invoice", help="Get an invoice by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_invoice)

    # invoice-items
    p = sub.add_parser("invoice-items", help="List invoice items")
    p.add_argument("--invoice-id", type=str)
    p.add_argument("--customer-id", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_invoice_items)

    # payments
    p = sub.add_parser("payments", help="List payment intents")
    p.add_argument("--customer-id", type=str)
    p.add_argument("--status", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_payments)

    # payment
    p = sub.add_parser("payment", help="Get a payment intent by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_payment)

    # charges
    p = sub.add_parser("charges", help="List charges")
    p.add_argument("--customer-id", type=str)
    p.add_argument("--payment-intent-id", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_charges)

    # search-charges
    p = sub.add_parser("search-charges", help="Search charges")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search_charges)

    # products
    p = sub.add_parser("products", help="List products")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_products)

    # product
    p = sub.add_parser("product", help="Get a product by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_product)

    # prices
    p = sub.add_parser("prices", help="List prices")
    p.add_argument("--product-id", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_prices)

    # subscriptions
    p = sub.add_parser("subscriptions", help="List subscriptions")
    p.add_argument("--customer-id", type=str)
    p.add_argument("--status", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_subscriptions)

    # subscription
    p = sub.add_parser("subscription", help="Get a subscription by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_subscription)

    # refunds
    p = sub.add_parser("refunds", help="List refunds")
    p.add_argument("--charge-id", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_refunds)

    # disputes
    p = sub.add_parser("disputes", help="List disputes")
    p.add_argument("--status", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_disputes)

    # account
    p = sub.add_parser("account", help="Get account info")
    p.set_defaults(func=cmd_account)

    # balance-transactions
    p = sub.add_parser("balance-transactions", help="List balance transactions")
    p.add_argument("--type", type=str)
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_balance_transactions)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
