#!/usr/bin/env python3
"""
Target Data Fetcher - Retrieve shopping data from the Target MCP server

Usage:
    # Log in
    python3 target_data.py login --email EMAIL

    # Search products
    python3 target_data.py search "headphones" [--category CAT] [--department DEPT]
        [--brand BRAND] [--min-price N] [--max-price N] [--in-stock-only]
        [--circle-deals-only] [--limit N]

    # List categories
    python3 target_data.py categories

    # List departments
    python3 target_data.py departments

    # List brands (optionally by category or department)
    python3 target_data.py brands [--category CAT] [--department DEPT] [--limit N]

    # Get Circle member deals
    python3 target_data.py circle-deals [--limit N]

    # Get product details by product ID
    python3 target_data.py product <product_id>

    # Order history (persona-scoped)
    python3 target_data.py orders [--days N] [--start DATE] [--end DATE] [--status STATUS] [--limit N]

    # Single order details
    python3 target_data.py order <order_id>

    # Spending analytics
    python3 target_data.py spending [--days N] [--start DATE] [--end DATE]

    # Frequently purchased products
    python3 target_data.py favorites [--days N] [--limit N]

    # User profile
    python3 target_data.py profile

    # Account summary
    python3 target_data.py summary [--days N]

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
    """Get all orders from the Target MCP server."""
    result = _call_tool("target_get_order_history")
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        if "error" in result:
            return []
        if "text" in result:
            return []
        if "orders" in result:
            return result["orders"]
    return []


# ---- Subcommand implementations ----


def search_products(
    query: str,
    category: str = None,
    department: str = None,
    brand: str = None,
    min_price: float = None,
    max_price: float = None,
    in_stock_only: bool = False,
    circle_deals_only: bool = False,
    limit: int = 20,
) -> dict:
    """Search products by keyword with optional filters."""
    args = {"query": query}
    if category:
        args["category"] = category
    if department:
        args["department"] = department
    if min_price is not None:
        args["min_price"] = min_price
    if max_price is not None:
        args["max_price"] = max_price
    if in_stock_only:
        args["in_stock_only"] = True
    if circle_deals_only:
        args["circle_deals_only"] = True

    result = _call_tool("target_search_products", args)

    products = []
    if isinstance(result, list):
        products = result
    elif isinstance(result, dict):
        if "text" in result:
            return {"products": [], "total_results": 0, "query": query}
        if "results" in result:
            products = result["results"]
        elif "products" in result:
            products = result["products"]

    # Apply client-side brand filter (not supported by MCP tool)
    if brand:
        products = [p for p in products if p.get("brand", "").lower() == brand.lower()]

    # Sort by rating desc, then review_count desc
    products.sort(key=lambda x: (-float(x.get("rating") or 0), -int(x.get("review_count") or 0)))
    products = products[:limit]
    return {"products": products, "total_results": len(products), "query": query}


def get_categories() -> dict:
    """List all categories with product counts."""
    result = _call_tool("target_get_categories")
    if isinstance(result, dict) and "categories" in result:
        categories = result["categories"]
        return {"categories": categories, "total_categories": len(categories)}
    return {"categories": [], "total_categories": 0}


def get_departments() -> dict:
    """List all departments with product counts."""
    result = _call_tool("target_get_departments")
    if isinstance(result, dict) and "departments" in result:
        departments = result["departments"]
        return {"departments": departments, "total_departments": len(departments)}
    return {"departments": [], "total_departments": 0}


def get_brands(category: str = None, department: str = None, limit: int = 50) -> dict:
    """List brands with product counts, optionally filtered."""
    products = []
    if category:
        result = _call_tool("target_browse_by_category", {"category": category, "limit": 200})
    elif department:
        result = _call_tool("target_browse_by_department", {"department": department, "limit": 200})
    else:
        result = _call_tool("target_search_products", {"query": "*"})

    if isinstance(result, dict):
        if "error" in result:
            return result
        if "results" in result:
            products = result["results"]
        elif "products" in result:
            products = result["products"]

    counts: Counter = Counter()
    for p in products:
        b = p.get("brand", "").strip()
        if b:
            counts[b] += 1

    brands = [
        {"name": name, "product_count": count}
        for name, count in counts.most_common(limit)
    ]
    return {
        "brands": brands,
        "total_brands": len(counts),
        "showing": len(brands),
    }


def get_circle_deals(limit: int = 20) -> dict:
    """Get Target Circle member deals."""
    result = _call_tool("target_get_circle_deals", {"limit": limit})
    if isinstance(result, dict):
        if "circle_deals" in result:
            return {"deals": result["circle_deals"], "total_deals": result.get("count", len(result["circle_deals"]))}
        if "results" in result:
            return {"deals": result["results"], "total_deals": len(result["results"])}
    return {"deals": [], "total_deals": 0}


def get_product(product_id: str) -> dict:
    """Get a single product by product ID."""
    result = _call_tool("target_get_product_details", {"product_id": product_id})
    if isinstance(result, dict):
        if "error" in result:
            return result
        if "text" in result:
            return {"error": result["text"]}
        return {"product": result}
    return {"error": f"Product not found: {product_id}"}


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
    result = _call_tool("target_get_order_details", {"order_id": order_id})
    if isinstance(result, dict):
        if "error" in result:
            return result
        if "text" in result:
            return {"error": result["text"]}
        return {"order": result}
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
            "by_department": [],
            "by_brand": [],
        }

    totals = [float(o.get("total") or 0) for o in filtered]
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
        monthly[month_key]["total"] += float(o.get("total") or 0)
        monthly[month_key]["order_count"] += 1

    by_month = [
        {
            "month": m,
            "total": round(d["total"], 2),
            "order_count": d["order_count"],
        }
        for m, d in sorted(monthly.items(), reverse=True)
    ]

    # By category, department, and brand from order items
    cat_spend: Counter = Counter()
    dept_spend: Counter = Counter()
    brand_spend: Counter = Counter()
    for o in filtered:
        items = o.get("items", [])
        for item in items:
            category = item.get("category", "Unknown")
            department = item.get("department", "Unknown")
            brand = item.get("brand", "Unknown")
            line_total = float(item.get("price_at_purchase") or item.get("price") or 0) * int(item.get("quantity") or 1)
            cat_spend[category] += line_total
            dept_spend[department] += line_total
            brand_spend[brand] += line_total

    by_category = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in cat_spend.most_common()
    ]

    by_department = [
        {"department": dept, "total": round(total, 2)}
        for dept, total in dept_spend.most_common()
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
        "by_department": by_department,
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
            pid = item.get("product_id", "unknown")
            qty = int(item.get("quantity") or 1)
            price = float(item.get("price_at_purchase") or item.get("price") or 0)
            freq[pid] += 1
            qty_totals[pid] += qty
            total_spend[pid] += round(price * qty, 2)
            if pid not in item_info:
                item_info[pid] = item

    favorites = []
    for pid, count in freq.most_common(limit):
        info = item_info.get(pid, {})
        favorites.append({
            "product_id": pid,
            "name": info.get("name", "Unknown"),
            "category": info.get("category", ""),
            "department": info.get("department", ""),
            "brand": info.get("brand", ""),
            "times_ordered": count,
            "total_quantity": qty_totals[pid],
            "total_spent": round(total_spend[pid], 2),
            "current_price": float(info["price"]) if info.get("price") is not None else None,
            "rating": float(info["rating"]) if info.get("rating") is not None else None,
        })

    return {"favorites": favorites, "total_results": len(favorites)}


def get_profile() -> dict:
    """Get user profile."""
    result = _call_tool("target_get_current_user")
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
            "top_departments": [],
            "top_brands": [],
            "top_favorites": [],
            "order_status_breakdown": {
                "delivered": 0,
                "pending": 0,
                "shipped": 0,
                "processing": 0,
                "cancelled": 0,
            },
        }

    totals = [float(o.get("total") or 0) for o in filtered]
    total_spent = round(sum(totals), 2)

    # Recent 5 orders
    recent = []
    for o in filtered[:5]:
        recent.append({
            "order_id": o.get("order_id", ""),
            "status": o.get("status", ""),
            "total": float(o.get("total") or 0),
            "created_at": o.get("created_at", ""),
        })

    # Status breakdown
    status_counts: Counter = Counter()
    for o in filtered:
        status_counts[o.get("status", "unknown")] += 1

    # Top categories, departments, brands, favorites from order items
    cat_spend: Counter = Counter()
    dept_spend: Counter = Counter()
    brand_spend: Counter = Counter()
    freq: Counter = Counter()
    qty_totals: Counter = Counter()
    item_info: dict[str, dict] = {}

    for o in filtered:
        items = o.get("items", [])
        for item in items:
            pid = item.get("product_id", "unknown")
            category = item.get("category", "Unknown")
            department = item.get("department", "Unknown")
            brand = item.get("brand", "Unknown")
            qty = int(item.get("quantity") or 1)
            price = float(item.get("price_at_purchase") or item.get("price") or 0)
            line_total = price * qty
            cat_spend[category] += line_total
            dept_spend[department] += line_total
            brand_spend[brand] += line_total
            freq[pid] += 1
            qty_totals[pid] += qty
            if pid not in item_info:
                item_info[pid] = item

    top_categories = [
        {"category": cat, "total": round(total, 2)}
        for cat, total in cat_spend.most_common(5)
    ]

    top_departments = [
        {"department": dept, "total": round(total, 2)}
        for dept, total in dept_spend.most_common(5)
    ]

    top_brands = [
        {"brand": b, "total": round(total, 2)}
        for b, total in brand_spend.most_common(5)
    ]

    top_favorites = []
    for pid, count in freq.most_common(5):
        info = item_info.get(pid, {})
        top_favorites.append({
            "product_id": pid,
            "name": info.get("name", "Unknown"),
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
        "top_departments": top_departments,
        "top_brands": top_brands,
        "top_favorites": top_favorites,
        "order_status_breakdown": {
            "delivered": status_counts.get("delivered", 0),
            "pending": status_counts.get("pending", 0),
            "shipped": status_counts.get("shipped", 0),
            "processing": status_counts.get("processing", 0),
            "cancelled": status_counts.get("cancelled", 0),
        },
    }


def login(email):
    """Log in to Target with your email."""
    return _call_tool("target_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Fetch Target shopping data")
    sub = parser.add_subparsers(dest="command")

    # login
    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # search
    search_p = sub.add_parser("search")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--category", help="Filter by category")
    search_p.add_argument("--department", help="Filter by department")
    search_p.add_argument("--brand", help="Filter by brand")
    search_p.add_argument("--min-price", type=float, help="Minimum price")
    search_p.add_argument("--max-price", type=float, help="Maximum price")
    search_p.add_argument(
        "--in-stock-only", action="store_true", help="Only in-stock items"
    )
    search_p.add_argument(
        "--circle-deals-only", action="store_true", help="Only Circle member deals"
    )
    search_p.add_argument("--limit", type=int, default=20, help="Max results")

    # categories
    sub.add_parser("categories")

    # departments
    sub.add_parser("departments")

    # brands
    brands_p = sub.add_parser("brands")
    brands_p.add_argument("--category", help="Filter brands by category")
    brands_p.add_argument("--department", help="Filter brands by department")
    brands_p.add_argument("--limit", type=int, default=50, help="Max results")

    # circle-deals
    circle_p = sub.add_parser("circle-deals")
    circle_p.add_argument("--limit", type=int, default=20, help="Max results")

    # product
    product_p = sub.add_parser("product")
    product_p.add_argument("product_id", help="Product ID (e.g., TGT00000001)")

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
            args.department,
            args.brand,
            args.min_price,
            args.max_price,
            args.in_stock_only,
            args.circle_deals_only,
            args.limit,
        )
    elif args.command == "categories":
        result = get_categories()
    elif args.command == "departments":
        result = get_departments()
    elif args.command == "brands":
        result = get_brands(args.category, args.department, args.limit)
    elif args.command == "circle-deals":
        result = get_circle_deals(args.limit)
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
