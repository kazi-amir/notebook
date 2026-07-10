#!/usr/bin/env python3
"""
FreshDirect Data Fetcher - Retrieve grocery data via MCP API

Usage:
    # Log in
    python3 freshdirect_data.py login --email EMAIL

    # Search products
    python3 freshdirect_data.py search "organic milk" [--category CAT] [--organic] [--limit N]

    # Get product details
    python3 freshdirect_data.py product <product_id>

    # Order history (persona-scoped)
    python3 freshdirect_data.py orders [--days N] [--start DATE] [--end DATE] [--status STATUS] [--limit N]

    # Single order details
    python3 freshdirect_data.py order <order_id>

    # Spending analytics
    python3 freshdirect_data.py spending [--days N] [--start DATE] [--end DATE]

    # Frequently ordered products
    python3 freshdirect_data.py favorites [--days N] [--limit N]

    # Deliveries
    python3 freshdirect_data.py deliveries [--days N] [--status STATUS]

    # Reorder items from a past order
    python3 freshdirect_data.py reorder <order_id>

    # User profile
    python3 freshdirect_data.py profile

    # Account summary
    python3 freshdirect_data.py summary [--days N]

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


def _parse_iso_datetime(value: str) -> datetime:
    """Parse ISO date or datetime string to timezone-aware datetime."""
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
        val = row.get(date_field, "")
        if not val:
            continue
        try:
            row_dt = _parse_iso_datetime(val)
            if start_dt <= row_dt <= end_dt:
                filtered.append(row)
        except (ValueError, KeyError):
            continue

    filtered.sort(key=lambda r: r.get(date_field, ""), reverse=True)
    return filtered


def _get_all_orders(limit=50) -> list[dict]:
    """Fetch purchase history from the MCP server."""
    data = _call_tool("fresh_direct_get_purchase_history", {"limit": limit})
    return data.get("orders", [])


# ---- Subcommand implementations ----


def search_products(query: str, category: str = None, organic: bool = False, limit: int = 20) -> dict:
    """Search products by name/description/category/tags."""
    data = _call_tool("fresh_direct_search_shop_catalog", {
        "query": query,
        "context": "product search",
    })

    products = data.get("products", [])

    # Apply client-side filters not supported by the API
    if category:
        products = [p for p in products if p.get("category", "").lower() == category.lower()]
    if organic:
        products = [p for p in products if p.get("is_organic") in (True, "1", 1)]

    products = products[:limit]
    return {"products": products, "total_results": len(products), "query": query}


def get_product(product_id: str) -> dict:
    """Get a single product by ID."""
    data = _call_tool("fresh_direct_search_shop_catalog", {
        "query": product_id,
        "context": "product lookup",
    })

    products = data.get("products", [])
    # Try to find exact match by ID
    for p in products:
        if str(p.get("id", "")) == str(product_id):
            return {"product": p}

    # If no exact match, return first result or error
    if products:
        return {"product": products[0]}
    return {"error": f"Product not found: {product_id}"}


def get_orders(days=None, start=None, end=None, status=None, limit=20) -> dict:
    """Get order history for the current persona."""
    orders = _get_all_orders(limit=50)
    filtered = _filter_orders_by_date(orders, "created_at", days, start, end)

    if status:
        filtered = [o for o in filtered if o.get("status", "").lower() == status.lower()]

    filtered = filtered[:limit]
    return {"orders": filtered, "total_orders": len(filtered)}


def get_order(order_id: str) -> dict:
    """Get a single order with details."""
    data = _call_tool("fresh_direct_get_order_details", {"order_id": order_id})
    if data.get("error"):
        return {"error": f"Order not found: {order_id}"}
    return data


def get_spending(days=None, start=None, end=None) -> dict:
    """Get spending analytics for the current persona."""
    orders = _get_all_orders(limit=50)
    filtered = _filter_orders_by_date(orders, "created_at", days, start, end)

    if not filtered:
        return {
            "total_spent": 0,
            "order_count": 0,
            "avg_per_order": 0,
            "by_month": [],
            "by_category": [],
        }

    totals = []
    for o in filtered:
        try:
            totals.append(float(o.get("total", 0)))
        except (ValueError, TypeError):
            totals.append(0)

    total_spent = round(sum(totals), 2)
    avg_per_order = round(total_spent / len(totals), 2) if totals else 0
    most_expensive = round(max(totals), 2) if totals else 0
    cheapest = round(min(totals), 2) if totals else 0

    # By month
    monthly: dict[str, dict] = defaultdict(lambda: {"total": 0.0, "order_count": 0})
    for o in filtered:
        created = o.get("created_at", "")
        if len(created) >= 7:
            month_key = created[:7]
        else:
            continue
        try:
            monthly[month_key]["total"] += float(o.get("total", 0))
        except (ValueError, TypeError):
            pass
        monthly[month_key]["order_count"] += 1

    by_month = [
        {"month": m, "total": round(d["total"], 2), "order_count": d["order_count"]}
        for m, d in sorted(monthly.items(), reverse=True)
    ]

    # By category - gather from order details
    cat_spend: Counter = Counter()
    for o in filtered:
        items = o.get("items", [])
        for item in items:
            category = item.get("category", "Unknown")
            try:
                line_total = float(item.get("price_at_purchase", 0)) * int(item.get("quantity", 1))
            except (ValueError, TypeError):
                line_total = float(item.get("line_total", 0))
            cat_spend[category] += line_total

    by_category = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in cat_spend.most_common()
    ]

    return {
        "total_spent": total_spent,
        "order_count": len(filtered),
        "avg_per_order": avg_per_order,
        "most_expensive_order": most_expensive,
        "cheapest_order": cheapest,
        "by_month": by_month,
        "by_category": by_category,
    }


def get_favorites(days=None, limit=10) -> dict:
    """Get most frequently ordered products."""
    orders = _get_all_orders(limit=50)
    filtered = _filter_orders_by_date(orders, "created_at", days)

    freq: Counter = Counter()
    qty_totals: Counter = Counter()
    product_info: dict[str, dict] = {}

    for o in filtered:
        items = o.get("items", [])
        for item in items:
            pid = str(item.get("product_id", ""))
            if not pid:
                continue
            freq[pid] += 1
            try:
                qty_totals[pid] += int(item.get("quantity", 1))
            except (ValueError, TypeError):
                qty_totals[pid] += 1
            if pid not in product_info:
                product_info[pid] = {
                    "product_name": item.get("product_name", item.get("name", "Unknown")),
                    "category": item.get("category", ""),
                    "current_price": item.get("price_at_purchase"),
                }

    favorites = []
    for pid, count in freq.most_common(limit):
        info = product_info.get(pid, {})
        price = info.get("current_price")
        try:
            price = float(price) if price is not None else None
        except (ValueError, TypeError):
            price = None
        favorites.append({
            "product_id": pid,
            "product_name": info.get("product_name", "Unknown"),
            "category": info.get("category", ""),
            "times_ordered": count,
            "total_quantity": qty_totals[pid],
            "current_price": price,
        })

    return {"favorites": favorites, "total_results": len(favorites)}


def get_deliveries(days=None, status=None) -> dict:
    """Get upcoming/recent deliveries."""
    orders = _get_all_orders(limit=50)
    filtered = _filter_orders_by_date(orders, "delivery_date", days)

    if status:
        filtered = [o for o in filtered if o.get("status", "").lower() == status.lower()]

    deliveries = []
    for o in filtered:
        deliveries.append({
            "order_id": o.get("id", ""),
            "status": o.get("status", ""),
            "total": float(o.get("total", 0)),
            "created_at": o.get("created_at", ""),
            "delivery_date": o.get("delivery_date", ""),
            "delivery_slot": o.get("delivery_slot", ""),
            "shipping_address": o.get("shipping_address", ""),
        })

    return {"deliveries": deliveries, "total_deliveries": len(deliveries)}


def get_reorder(order_id: str) -> dict:
    """Get items from a past order for reorder."""
    data = _call_tool("fresh_direct_get_order_details", {"order_id": order_id})

    if data.get("error"):
        return {"error": f"Order not found: {order_id}"}

    order = data.get("order", data)
    items = order.get("items", [])

    reorder_items = []
    for item in items:
        purchase_price = float(item.get("price_at_purchase", 0))
        current_price = item.get("current_price")
        try:
            current_price = float(current_price) if current_price is not None else None
        except (ValueError, TypeError):
            current_price = None

        entry = {
            "product_id": item.get("product_id", ""),
            "product_name": item.get("product_name", item.get("name", "Unknown")),
            "category": item.get("category", ""),
            "quantity": int(item.get("quantity", 1)),
            "price_at_purchase": purchase_price,
            "current_price": current_price,
            "in_stock": item.get("in_stock", True),
        }

        if current_price is not None and current_price != purchase_price:
            entry["price_changed"] = True
            entry["price_difference"] = round(current_price - purchase_price, 2)
        else:
            entry["price_changed"] = False

        reorder_items.append(entry)

    return {
        "order_id": order_id,
        "original_date": order.get("created_at", ""),
        "items": reorder_items,
        "item_count": len(reorder_items),
    }


def get_profile() -> dict:
    """Get user profile."""
    data = _call_tool("fresh_direct_get_current_user")
    if data.get("error"):
        return {"error": "Profile not found"}
    return data


def get_summary(days=None) -> dict:
    """Get account overview."""
    orders = _get_all_orders(limit=50)
    filtered = _filter_orders_by_date(orders, "created_at", days)

    if not filtered:
        return {
            "period_days": days or 90,
            "total_orders": 0,
            "total_spent": 0,
            "recent_orders": [],
            "top_categories": [],
            "top_favorites": [],
            "delivery_stats": {"delivered": 0, "pending": 0, "shipped": 0, "cancelled": 0},
        }

    totals = []
    for o in filtered:
        try:
            totals.append(float(o.get("total", 0)))
        except (ValueError, TypeError):
            totals.append(0)

    total_spent = round(sum(totals), 2)

    # Recent 5 orders (brief)
    recent = []
    for o in filtered[:5]:
        recent.append({
            "id": o.get("id", ""),
            "status": o.get("status", ""),
            "total": float(o.get("total", 0)),
            "created_at": o.get("created_at", ""),
            "delivery_date": o.get("delivery_date", ""),
        })

    # Delivery stats
    status_counts: Counter = Counter()
    for o in filtered:
        status_counts[o.get("status", "unknown")] += 1

    # Top categories by spend and favorites
    cat_spend: Counter = Counter()
    freq: Counter = Counter()
    qty_totals: Counter = Counter()
    product_info: dict[str, dict] = {}

    for o in filtered:
        items = o.get("items", [])
        for item in items:
            category = item.get("category", "Unknown")
            try:
                line_total = float(item.get("price_at_purchase", 0)) * int(item.get("quantity", 1))
            except (ValueError, TypeError):
                line_total = float(item.get("line_total", 0))
            cat_spend[category] += line_total

            pid = str(item.get("product_id", ""))
            if pid:
                freq[pid] += 1
                try:
                    qty_totals[pid] += int(item.get("quantity", 1))
                except (ValueError, TypeError):
                    qty_totals[pid] += 1
                if pid not in product_info:
                    product_info[pid] = {
                        "product_name": item.get("product_name", item.get("name", "Unknown")),
                    }

    top_categories = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in cat_spend.most_common(5)
    ]

    top_favorites = []
    for pid, count in freq.most_common(5):
        info = product_info.get(pid, {})
        top_favorites.append({
            "product_id": pid,
            "product_name": info.get("product_name", "Unknown"),
            "times_ordered": count,
            "total_quantity": qty_totals[pid],
        })

    return {
        "period_days": days or 90,
        "total_orders": len(filtered),
        "total_spent": total_spent,
        "avg_per_order": round(total_spent / len(filtered), 2),
        "recent_orders": recent,
        "top_categories": top_categories,
        "top_favorites": top_favorites,
        "delivery_stats": {
            "delivered": status_counts.get("delivered", 0),
            "pending": status_counts.get("pending", 0),
            "shipped": status_counts.get("shipped", 0),
            "cancelled": status_counts.get("cancelled", 0),
        },
    }


def login(email):
    """Log in to FreshDirect with your email."""
    return _call_tool("fresh_direct_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch FreshDirect grocery data")
    sub = parser.add_subparsers(dest="command")

    # login
    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # search
    search_p = sub.add_parser("search")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--category", help="Filter by category")
    search_p.add_argument("--organic", action="store_true", help="Only organic products")
    search_p.add_argument("--limit", type=int, default=20, help="Max results")

    # product
    product_p = sub.add_parser("product")
    product_p.add_argument("product_id", help="Product ID")

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

    # deliveries
    del_p = sub.add_parser("deliveries")
    del_p.add_argument("--days", type=int, default=90)
    del_p.add_argument("--status", help="Filter by delivery status")

    # reorder
    reorder_p = sub.add_parser("reorder")
    reorder_p.add_argument("order_id", help="Order ID to reorder from")

    # profile
    sub.add_parser("profile")

    # summary
    summary_p = sub.add_parser("summary")
    summary_p.add_argument("--days", type=int, default=90)

    args = parser.parse_args()

    if args.command == "login":
        result = login(args.email)
    elif args.command == "search":
        result = search_products(args.query, args.category, args.organic, args.limit)
    elif args.command == "product":
        result = get_product(args.product_id)
    elif args.command == "orders":
        result = get_orders(args.days, args.start, args.end, args.status, args.limit)
    elif args.command == "order":
        result = get_order(args.order_id)
    elif args.command == "spending":
        result = get_spending(args.days, args.start, args.end)
    elif args.command == "favorites":
        result = get_favorites(args.days, args.limit)
    elif args.command == "deliveries":
        result = get_deliveries(args.days, args.status)
    elif args.command == "reorder":
        result = get_reorder(args.order_id)
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
