#!/usr/bin/env python3
"""
Shopping Data - Browse products, manage cart, apply discount codes, and place orders.

Usage:
    # Products
    python3 shopping_data.py list-products [--offset N] [--limit N]
    python3 shopping_data.py get-product --product-id ID
    python3 shopping_data.py search-product --product-name NAME [--offset N] [--limit N]

    # Cart
    python3 shopping_data.py add-to-cart --item-id ID [--quantity N]
    python3 shopping_data.py remove-from-cart --item-id ID [--quantity N]
    python3 shopping_data.py list-cart

    # Checkout & Orders
    python3 shopping_data.py checkout [--discount-code CODE]
    python3 shopping_data.py list-orders
    python3 shopping_data.py get-order --order-id ID
    python3 shopping_data.py cancel-order --order-id ID

    # Discount Codes
    python3 shopping_data.py get-discount-code --discount-code CODE
    python3 shopping_data.py get-all-discount-codes

    # Utility
    python3 shopping_data.py show [--offset N] [--limit N]
    python3 shopping_data.py reset

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


# --- Products ---

def cmd_list_products(args):
    """List all products in catalog."""
    tool_args = {}
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.limit is not None:
        tool_args["limit"] = args.limit
    return _call_tool("shopping_list_all_products", tool_args)


def cmd_get_product(args):
    """Get full product details including variants."""
    return _call_tool("shopping_get_product_details", {"product_id": args.product_id})


def cmd_search_product(args):
    """Search products by name."""
    tool_args = {"product_name": args.product_name}
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.limit is not None:
        tool_args["limit"] = args.limit
    return _call_tool("shopping_search_product", tool_args)


# --- Cart ---

def cmd_add_to_cart(args):
    """Add an item to the cart."""
    tool_args = {"item_id": args.item_id}
    if args.quantity is not None:
        tool_args["quantity"] = args.quantity
    return _call_tool("shopping_add_to_cart", tool_args)


def cmd_remove_from_cart(args):
    """Remove an item from the cart."""
    tool_args = {"item_id": args.item_id}
    if args.quantity is not None:
        tool_args["quantity"] = args.quantity
    return _call_tool("shopping_remove_from_cart", tool_args)


def cmd_list_cart(args):
    """List all items currently in the cart."""
    return _call_tool("shopping_list_cart")


# --- Checkout & Orders ---

def cmd_checkout(args):
    """Checkout and create an order from cart."""
    tool_args = {}
    if args.discount_code:
        tool_args["discount_code"] = args.discount_code
    return _call_tool("shopping_checkout", tool_args)


def cmd_list_orders(args):
    """List all placed orders."""
    return _call_tool("shopping_list_orders")


def cmd_get_order(args):
    """Get details for a specific order."""
    return _call_tool("shopping_get_order_details", {"order_id": args.order_id})


def cmd_cancel_order(args):
    """Cancel an order."""
    return _call_tool("shopping_cancel_order", {"order_id": args.order_id})


# --- Discount Codes ---

def cmd_get_discount_code(args):
    """Get items and percentages for a discount code."""
    return _call_tool("shopping_get_discount_code_info", {"discount_code": args.discount_code})


def cmd_get_all_discount_codes(args):
    """List all available discount codes."""
    return _call_tool("shopping_get_all_discount_codes")


# --- Utility ---

def cmd_show(args):
    """Show raw shopping data."""
    return _call_tool("shopping_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


def cmd_reset(args):
    """Reset to initial state."""
    return _call_tool("shopping_reset")


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Shopping Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Products ---

    # list-products
    p = sub.add_parser("list-products", help="List all products")
    p.add_argument("--offset", type=int)
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_list_products)

    # get-product
    p = sub.add_parser("get-product", help="Get product details")
    p.add_argument("--product-id", type=str, required=True)
    p.set_defaults(func=cmd_get_product)

    # search-product
    p = sub.add_parser("search-product", help="Search products by name")
    p.add_argument("--product-name", type=str, required=True)
    p.add_argument("--offset", type=int)
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_search_product)

    # --- Cart ---

    # add-to-cart
    p = sub.add_parser("add-to-cart", help="Add item to cart")
    p.add_argument("--item-id", type=str, required=True)
    p.add_argument("--quantity", type=int, help="Quantity (default 1)")
    p.set_defaults(func=cmd_add_to_cart)

    # remove-from-cart
    p = sub.add_parser("remove-from-cart", help="Remove item from cart")
    p.add_argument("--item-id", type=str, required=True)
    p.add_argument("--quantity", type=int, help="Quantity to remove (default 1)")
    p.set_defaults(func=cmd_remove_from_cart)

    # list-cart
    p = sub.add_parser("list-cart", help="List cart contents")
    p.set_defaults(func=cmd_list_cart)

    # --- Checkout & Orders ---

    # checkout
    p = sub.add_parser("checkout", help="Checkout and create order")
    p.add_argument("--discount-code", type=str, help="Optional discount code")
    p.set_defaults(func=cmd_checkout)

    # list-orders
    p = sub.add_parser("list-orders", help="List all orders")
    p.set_defaults(func=cmd_list_orders)

    # get-order
    p = sub.add_parser("get-order", help="Get order details")
    p.add_argument("--order-id", type=str, required=True)
    p.set_defaults(func=cmd_get_order)

    # cancel-order
    p = sub.add_parser("cancel-order", help="Cancel an order")
    p.add_argument("--order-id", type=str, required=True)
    p.set_defaults(func=cmd_cancel_order)

    # --- Discount Codes ---

    # get-discount-code
    p = sub.add_parser("get-discount-code", help="Get discount code info")
    p.add_argument("--discount-code", type=str, required=True)
    p.set_defaults(func=cmd_get_discount_code)

    # get-all-discount-codes
    p = sub.add_parser("get-all-discount-codes", help="List all discount codes")
    p.set_defaults(func=cmd_get_all_discount_codes)

    # --- Utility ---

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
