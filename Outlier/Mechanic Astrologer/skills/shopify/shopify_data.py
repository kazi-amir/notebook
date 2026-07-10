#!/usr/bin/env python3
"""
Shopify Data Fetcher - Retrieve e-commerce data from the Shopify MCP server

Usage:
    # Customers
    python3 shopify_data.py customers
    python3 shopify_data.py customer <id>
    python3 shopify_data.py search-customers <query>

    # Orders
    python3 shopify_data.py orders
    python3 shopify_data.py order <id>
    python3 shopify_data.py order-by-number <order_number>
    python3 shopify_data.py orders-by-customer <customer_id>
    python3 shopify_data.py search-orders [--status S] [--date-from D] [--date-to D] [--min-amount N] [--max-amount N]

    # Products
    python3 shopify_data.py products
    python3 shopify_data.py product <id>
    python3 shopify_data.py product-by-sku <sku>
    python3 shopify_data.py search-products [--brand B] [--category C] [--gender G] [--min-price N] [--max-price N]

    # Order Updates
    python3 shopify_data.py update-order-status <order_id> <status> [--notes N]

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


# ---- Subcommand implementations ----


def cmd_customers() -> dict:
    return _call_tool("shopify_get_all_customers")


def cmd_customer(customer_id: int) -> dict:
    return _call_tool("shopify_get_customer", {"id": customer_id})


def cmd_search_customers(query: str) -> dict:
    return _call_tool("shopify_search_customers", {"query": query})


def cmd_orders() -> dict:
    return _call_tool("shopify_get_all_orders")


def cmd_order(order_id: int) -> dict:
    return _call_tool("shopify_get_order", {"id": order_id})


def cmd_order_by_number(order_number: str) -> dict:
    return _call_tool("shopify_get_order_by_number", {"order_number": order_number})


def cmd_orders_by_customer(customer_id: int) -> dict:
    return _call_tool("shopify_get_orders_by_customer", {"customer_id": customer_id})


def cmd_search_orders(status=None, date_from=None, date_to=None, min_amount=None, max_amount=None) -> dict:
    args = {}
    if status:
        args["status"] = status
    if date_from:
        args["date_from"] = date_from
    if date_to:
        args["date_to"] = date_to
    if min_amount is not None:
        args["min_amount"] = min_amount
    if max_amount is not None:
        args["max_amount"] = max_amount
    return _call_tool("shopify_search_orders", args)


def cmd_products() -> dict:
    return _call_tool("shopify_get_all_products")


def cmd_product(product_id: int) -> dict:
    return _call_tool("shopify_get_product", {"id": product_id})


def cmd_product_by_sku(sku: str) -> dict:
    return _call_tool("shopify_get_product_by_sku", {"sku": sku})


def cmd_search_products(brand=None, category=None, gender=None, min_price=None, max_price=None) -> dict:
    args = {}
    if brand:
        args["brand"] = brand
    if category:
        args["category"] = category
    if gender:
        args["gender"] = gender
    if min_price is not None:
        args["min_price"] = min_price
    if max_price is not None:
        args["max_price"] = max_price
    return _call_tool("shopify_search_products", args)


def cmd_update_order_status(order_id: int, status: str, notes: str = None) -> dict:
    args = {"id": order_id, "status": status}
    if notes:
        args["notes"] = notes
    return _call_tool("shopify_update_order_status", args)


def main():
    parser = argparse.ArgumentParser(description="Fetch Shopify e-commerce data")
    sub = parser.add_subparsers(dest="command")

    # customers
    sub.add_parser("customers")

    # customer
    cust_p = sub.add_parser("customer")
    cust_p.add_argument("id", type=int, help="Customer ID")

    # search-customers
    sc_p = sub.add_parser("search-customers")
    sc_p.add_argument("query", help="Search query (name or email)")

    # orders
    sub.add_parser("orders")

    # order
    ord_p = sub.add_parser("order")
    ord_p.add_argument("id", type=int, help="Order ID")

    # order-by-number
    obn_p = sub.add_parser("order-by-number")
    obn_p.add_argument("order_number", help="Order number (e.g., STR-50001)")

    # orders-by-customer
    obc_p = sub.add_parser("orders-by-customer")
    obc_p.add_argument("customer_id", type=int, help="Customer ID")

    # search-orders
    so_p = sub.add_parser("search-orders")
    so_p.add_argument("--status", help="Filter by status")
    so_p.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
    so_p.add_argument("--date-to", help="End date (YYYY-MM-DD)")
    so_p.add_argument("--min-amount", type=float, help="Minimum order total")
    so_p.add_argument("--max-amount", type=float, help="Maximum order total")

    # products
    sub.add_parser("products")

    # product
    prod_p = sub.add_parser("product")
    prod_p.add_argument("id", type=int, help="Product ID")

    # product-by-sku
    pbs_p = sub.add_parser("product-by-sku")
    pbs_p.add_argument("sku", help="Product SKU")

    # search-products
    sp_p = sub.add_parser("search-products")
    sp_p.add_argument("--brand", help="Filter by brand")
    sp_p.add_argument("--category", help="Filter by category")
    sp_p.add_argument("--gender", help="Filter by gender")
    sp_p.add_argument("--min-price", type=float, help="Minimum price")
    sp_p.add_argument("--max-price", type=float, help="Maximum price")

    # update-order-status
    uos_p = sub.add_parser("update-order-status")
    uos_p.add_argument("order_id", type=int, help="Order ID")
    uos_p.add_argument("status", help="New status")
    uos_p.add_argument("--notes", help="Notes for the status change")

    args = parser.parse_args()

    if args.command == "customers":
        result = cmd_customers()
    elif args.command == "customer":
        result = cmd_customer(args.id)
    elif args.command == "search-customers":
        result = cmd_search_customers(args.query)
    elif args.command == "orders":
        result = cmd_orders()
    elif args.command == "order":
        result = cmd_order(args.id)
    elif args.command == "order-by-number":
        result = cmd_order_by_number(args.order_number)
    elif args.command == "orders-by-customer":
        result = cmd_orders_by_customer(args.customer_id)
    elif args.command == "search-orders":
        result = cmd_search_orders(args.status, args.date_from, args.date_to, args.min_amount, args.max_amount)
    elif args.command == "products":
        result = cmd_products()
    elif args.command == "product":
        result = cmd_product(args.id)
    elif args.command == "product-by-sku":
        result = cmd_product_by_sku(args.sku)
    elif args.command == "search-products":
        result = cmd_search_products(args.brand, args.category, args.gender, args.min_price, args.max_price)
    elif args.command == "update-order-status":
        result = cmd_update_order_status(args.order_id, args.status, args.notes)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
