#!/usr/bin/env python3
"""
Amazon Data Fetcher - Retrieve shopping data from the Amazon MCP server

Usage:
    # Log in
    python3 amazon_data.py login --email EMAIL

    # Search products
    python3 amazon_data.py search "wireless headphones" [--category CAT] [--brand BRAND]
        [--min-price N] [--max-price N] [--min-rating N] [--prime-only] [--limit N]

    # Get product details by ASIN
    python3 amazon_data.py product <asin>

    # Order history (persona-scoped)
    python3 amazon_data.py orders [--days N] [--start DATE] [--end DATE] [--status STATUS] [--limit N]

    # Single order details
    python3 amazon_data.py order <order_id>

    # Spending analytics
    python3 amazon_data.py spending [--days N] [--start DATE] [--end DATE]

    # Frequently purchased products
    python3 amazon_data.py favorites [--days N] [--limit N]

    # User profile
    python3 amazon_data.py profile

    # Account summary
    python3 amazon_data.py summary [--days N]

Output: JSON to stdout
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

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


def _parse_iso_datetime(value: str) -> datetime | None:
    """Parse ISO date or datetime string to timezone-aware datetime."""
    if not value or value.strip() == "":
        return None
    if len(value) == 10 and "T" not in value:
        value = f"{value}T00:00:00Z"
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _get_date_range(days=None, start=None, end=None, default_days=90):
    """Calculate start/end datetimes for filtering."""
    now = datetime.now(timezone.utc)
    if start:
        start_dt = _parse_iso_datetime(start)
    elif days:
        start_dt = now - timedelta(days=days)
    else:
        start_dt = now - timedelta(days=default_days)

    if end:
        end_dt = _parse_iso_datetime(end)
    else:
        end_dt = now

    return start_dt, end_dt


def _filter_orders_by_date(orders, date_field, days=None, start=None, end=None):
    """Filter order dicts by date range."""
    start_dt, end_dt = _get_date_range(days, start, end)

    filtered = []
    for row in orders:
        try:
            row_dt = _parse_iso_datetime(row.get(date_field, ""))
            if row_dt and start_dt <= row_dt <= end_dt:
                filtered.append(row)
        except (ValueError, KeyError):
            continue

    filtered.sort(key=lambda r: r.get(date_field, ""), reverse=True)
    return filtered


def _get_orders_from_api() -> list[dict]:
    """Get all orders from the Amazon MCP server."""
    result = _call_tool("amazon_get_orders_history")
    # The tool returns a JSON string which _call_tool parses.
    # Result could be a list of orders directly, or a dict, or {"text": "No orders found."}
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if "error" in result:
            return []
        if "text" in result:
            # Plain text response like "No orders found."
            return []
        # Could be a dict with orders key
        if "orders" in result:
            return result["orders"]
    return []


# ---- Subcommand implementations ----


def search_products(
    query: str,
    category: str = None,
    brand: str = None,
    min_price: float = None,
    max_price: float = None,
    min_rating: float = None,
    prime_only: bool = False,
    limit: int = 20,
) -> dict:
    """Search products by keyword with optional filters."""
    result = _call_tool("amazon_search_products", {"searchTerm": query})

    # Result is parsed JSON - could be a list of products or a dict
    products = []
    if isinstance(result, list):
        products = result
    elif isinstance(result, dict):
        if "text" in result:
            # Text response like 'No products found...'
            return {"products": [], "total_results": 0, "query": query}
        if "products" in result:
            products = result["products"]
        elif "results" in result:
            products = result["results"]

    # Apply client-side filters not supported by the MCP search tool
    filtered = []
    for p in products:
        if category and p.get("category", "").lower() != category.lower():
            continue
        if brand and p.get("brand", "").lower() != brand.lower():
            continue
        price = float(p.get("price", 0))
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue
        rating = float(p.get("rating", 0))
        if min_rating is not None and rating < min_rating:
            continue
        if prime_only and not p.get("prime_eligible", False):
            continue
        filtered.append(p)

    # Sort by rating desc, then review_count desc
    filtered.sort(key=lambda x: (-float(x.get("rating", 0)), -int(x.get("review_count", 0))))
    filtered = filtered[:limit]
    return {"products": filtered, "total_results": len(filtered), "query": query}


def get_product(asin: str) -> dict:
    """Get a single product by ASIN."""
    result = _call_tool("amazon_get_product_details", {"asin": asin})
    if isinstance(result, dict):
        if "error" in result:
            return result
        if "text" in result:
            # Error message from the tool
            return {"error": result["text"]}
        # The tool returns product details directly
        return {"product": result}
    return {"error": f"Product not found: {asin}"}


def get_orders(
    days=None, start=None, end=None, status=None, limit=20
) -> dict:
    """Get order history for the current persona."""
    all_orders = _get_orders_from_api()
    filtered = _filter_orders_by_date(all_orders, "created_at", days, start, end)

    if status:
        filtered = [o for o in filtered if o.get("status", "").lower() == status.lower()]

    filtered = filtered[:limit]
    return {"orders": filtered, "total_orders": len(filtered)}


def get_order(order_id: str) -> dict:
    """Get a single order with details."""
    all_orders = _get_orders_from_api()
    for o in all_orders:
        if o.get("order_id") == order_id:
            return {"order": o}
    return {"error": f"Order not found: {order_id}"}


def get_spending(days=None, start=None, end=None) -> dict:
    """Get spending analytics for the current persona."""
    all_orders = _get_orders_from_api()
    filtered = _filter_orders_by_date(all_orders, "created_at", days, start, end)

    if not filtered:
        return {
            "total_spent": 0,
            "order_count": 0,
            "avg_per_order": 0,
            "by_month": [],
            "by_category": [],
            "by_brand": [],
        }

    totals = [float(o.get("total", 0)) for o in filtered]
    total_spent = round(sum(totals), 2)
    avg_per_order = round(total_spent / len(totals), 2)
    most_expensive = round(max(totals), 2)
    cheapest = round(min(totals), 2)

    # By month
    monthly: dict[str, dict] = defaultdict(
        lambda: {"total": 0.0, "order_count": 0}
    )
    for o in filtered:
        created = o.get("created_at", "")
        month_key = created[:7] if len(created) >= 7 else "unknown"
        monthly[month_key]["total"] += float(o.get("total", 0))
        monthly[month_key]["order_count"] += 1

    by_month = [
        {
            "month": m,
            "total": round(d["total"], 2),
            "order_count": d["order_count"],
        }
        for m, d in sorted(monthly.items(), reverse=True)
    ]

    # By category and brand from order items
    cat_spend: Counter = Counter()
    brand_spend: Counter = Counter()
    for o in filtered:
        items = o.get("items", [])
        for item in items:
            category = item.get("category", "Unknown")
            brand = item.get("brand", "Unknown")
            line_total = float(item.get("price_at_purchase", item.get("price", 0))) * int(item.get("quantity", 1))
            cat_spend[category] += line_total
            brand_spend[brand] += line_total

    by_category = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in cat_spend.most_common()
    ]

    by_brand = [
        {"brand": b, "total": round(total, 2)}
        for b, total in brand_spend.most_common(15)
    ]

    return {
        "total_spent": total_spent,
        "order_count": len(filtered),
        "avg_per_order": avg_per_order,
        "most_expensive_order": most_expensive,
        "cheapest_order": cheapest,
        "by_month": by_month,
        "by_category": by_category,
        "by_brand": by_brand,
    }


def get_favorites(days=None, limit=10) -> dict:
    """Get most frequently purchased products."""
    all_orders = _get_orders_from_api()
    filtered = _filter_orders_by_date(all_orders, "created_at", days)

    freq: Counter = Counter()
    qty_totals: Counter = Counter()
    total_spend: Counter = Counter()
    item_info: dict[str, dict] = {}

    for o in filtered:
        items = o.get("items", [])
        for item in items:
            asin = item.get("asin", item.get("product_id", "unknown"))
            qty = int(item.get("quantity", 1))
            price = float(item.get("price_at_purchase", item.get("price", 0)))
            freq[asin] += 1
            qty_totals[asin] += qty
            total_spend[asin] += round(price * qty, 2)
            if asin not in item_info:
                item_info[asin] = item

    favorites = []
    for asin, count in freq.most_common(limit):
        info = item_info.get(asin, {})
        favorites.append({
            "asin": asin,
            "title": info.get("title", info.get("name", "Unknown")),
            "category": info.get("category", ""),
            "brand": info.get("brand", ""),
            "times_ordered": count,
            "total_quantity": qty_totals[asin],
            "total_spent": round(total_spend[asin], 2),
            "current_price": float(info["price"]) if info.get("price") else None,
            "rating": float(info["rating"]) if info.get("rating") else None,
        })

    return {"favorites": favorites, "total_results": len(favorites)}


def get_profile() -> dict:
    """Get user profile."""
    result = _call_tool("amazon_get_current_user")
    if isinstance(result, dict):
        if "error" in result:
            return result
        if "text" in result:
            return {"error": result["text"]}
        return result
    return {"error": "Profile not found"}


def get_summary(days=None) -> dict:
    """Get account overview."""
    all_orders = _get_orders_from_api()
    filtered = _filter_orders_by_date(all_orders, "created_at", days)

    if not filtered:
        return {
            "period_days": days or 90,
            "total_orders": 0,
            "total_spent": 0,
            "recent_orders": [],
            "top_categories": [],
            "top_brands": [],
            "top_favorites": [],
            "order_status_breakdown": {
                "delivered": 0,
                "pending": 0,
                "shipped": 0,
                "cancelled": 0,
            },
        }

    totals = [float(o.get("total", 0)) for o in filtered]
    total_spent = round(sum(totals), 2)

    # Recent 5 orders (brief)
    recent = []
    for o in filtered[:5]:
        recent.append({
            "order_id": o.get("order_id", ""),
            "status": o.get("status", ""),
            "total": float(o.get("total", 0)),
            "created_at": o.get("created_at", ""),
        })

    # Status breakdown
    status_counts: Counter = Counter()
    for o in filtered:
        status_counts[o.get("status", "unknown")] += 1

    # Top categories, brands, favorites from order items
    cat_spend: Counter = Counter()
    brand_spend: Counter = Counter()
    freq: Counter = Counter()
    qty_totals: Counter = Counter()
    item_info: dict[str, dict] = {}

    for o in filtered:
        items = o.get("items", [])
        for item in items:
            asin = item.get("asin", item.get("product_id", "unknown"))
            category = item.get("category", "Unknown")
            brand = item.get("brand", "Unknown")
            qty = int(item.get("quantity", 1))
            price = float(item.get("price_at_purchase", item.get("price", 0)))
            line_total = price * qty
            cat_spend[category] += line_total
            brand_spend[brand] += line_total
            freq[asin] += 1
            qty_totals[asin] += qty
            if asin not in item_info:
                item_info[asin] = item

    top_categories = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in cat_spend.most_common(5)
    ]

    top_brands = [
        {"brand": b, "total": round(total, 2)}
        for b, total in brand_spend.most_common(5)
    ]

    top_favorites = []
    for asin, count in freq.most_common(5):
        info = item_info.get(asin, {})
        top_favorites.append({
            "asin": asin,
            "title": info.get("title", info.get("name", "Unknown")),
            "times_ordered": count,
            "total_quantity": qty_totals[asin],
        })

    return {
        "period_days": days or 90,
        "total_orders": len(filtered),
        "total_spent": total_spent,
        "avg_per_order": round(total_spent / len(filtered), 2),
        "recent_orders": recent,
        "top_categories": top_categories,
        "top_brands": top_brands,
        "top_favorites": top_favorites,
        "order_status_breakdown": {
            "delivered": status_counts.get("delivered", 0),
            "pending": status_counts.get("pending", 0),
            "shipped": status_counts.get("shipped", 0),
            "cancelled": status_counts.get("cancelled", 0),
        },
    }


def login(email):
    """Log in to Amazon with your email."""
    return _call_tool("amazon_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch Amazon shopping data")
    sub = parser.add_subparsers(dest="command")

    # login
    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # search
    search_p = sub.add_parser("search")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--category", help="Filter by category")
    search_p.add_argument("--brand", help="Filter by brand")
    search_p.add_argument("--min-price", type=float, help="Minimum price")
    search_p.add_argument("--max-price", type=float, help="Maximum price")
    search_p.add_argument("--min-rating", type=float, help="Minimum rating (1-5)")
    search_p.add_argument(
        "--prime-only", action="store_true", help="Only Prime eligible"
    )
    search_p.add_argument("--limit", type=int, default=20, help="Max results")

    # product
    product_p = sub.add_parser("product")
    product_p.add_argument("asin", help="Product ASIN (10-character ID)")

    # orders
    orders_p = sub.add_parser("orders")
    orders_p.add_argument("--days", type=int, default=90)
    orders_p.add_argument("--start", help="ISO date (e.g., 2026-01-01)")
    orders_p.add_argument("--end", help="ISO date")
    orders_p.add_argument("--status", help="Filter by status")
    orders_p.add_argument("--limit", type=int, default=20, help="Max results")

    # order
    order_p = sub.add_parser("order")
    order_p.add_argument("order_id", help="Order ID")

    # spending
    spending_p = sub.add_parser("spending")
    spending_p.add_argument("--days", type=int, default=90)
    spending_p.add_argument("--start", help="ISO date")
    spending_p.add_argument("--end", help="ISO date")

    # favorites
    fav_p = sub.add_parser("favorites")
    fav_p.add_argument("--days", type=int, default=90)
    fav_p.add_argument("--limit", type=int, default=10, help="Max results")

    # profile
    sub.add_parser("profile")

    # summary
    summary_p = sub.add_parser("summary")
    summary_p.add_argument("--days", type=int, default=90)

    args = parser.parse_args()

    if args.command == "login":
        result = login(args.email)
    elif args.command == "search":
        result = search_products(
            args.query,
            args.category,
            args.brand,
            args.min_price,
            args.max_price,
            args.min_rating,
            args.prime_only,
            args.limit,
        )
    elif args.command == "product":
        result = get_product(args.asin)
    elif args.command == "orders":
        result = get_orders(args.days, args.start, args.end, args.status, args.limit)
    elif args.command == "order":
        result = get_order(args.order_id)
    elif args.command == "spending":
        result = get_spending(args.days, args.start, args.end)
    elif args.command == "favorites":
        result = get_favorites(args.days, args.limit)
    elif args.command == "profile":
        result = get_profile()
    elif args.command == "summary":
        result = get_summary(args.days)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
