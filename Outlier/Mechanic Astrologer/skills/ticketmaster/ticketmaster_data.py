#!/usr/bin/env python3
"""
Ticketmaster Data Fetcher - Retrieve event and ticket data from the Ticketmaster MCP server

Usage:
    # Log in
    python3 ticketmaster_data.py login --email EMAIL

    # Search events
    python3 ticketmaster_data.py search [QUERY] [--segment SEG] [--genre GENRE]
        [--city CITY] [--state ST] [--date-from DATE] [--date-to DATE]
        [--min-price N] [--max-price N] [--status STATUS] [--sort-by SORT] [--limit N]

    # Event details
    python3 ticketmaster_data.py event <event_id>

    # Browse/filter venues
    python3 ticketmaster_data.py venues [--city CITY] [--state ST] [--venue-type TYPE]

    # Venue details with upcoming events
    python3 ticketmaster_data.py venue <venue_id>

    # Search attractions (artists, bands, teams, comedians, companies)
    python3 ticketmaster_data.py attractions [QUERY] [--type TYPE] [--genre GENRE]

    # Attraction details with upcoming events
    python3 ticketmaster_data.py attraction <attraction_id>

    # Classification hierarchy (Segment > Genre > Sub-Genre)
    python3 ticketmaster_data.py classifications

    # Ticket availability for an event
    python3 ticketmaster_data.py availability <event_id>

    # Section-based seat map
    python3 ticketmaster_data.py seatmap <event_id>

    # Add tickets to cart
    python3 ticketmaster_data.py add-to-cart <event_id> <ticket_type_id> <quantity>

    # View cart
    python3 ticketmaster_data.py cart

    # Remove from cart
    python3 ticketmaster_data.py remove-from-cart <cart_item_id>

    # Checkout
    python3 ticketmaster_data.py checkout

    # Order history
    python3 ticketmaster_data.py orders

    # Order details
    python3 ticketmaster_data.py order <identifier>

    # User profile
    python3 ticketmaster_data.py profile

    # Spending analytics
    python3 ticketmaster_data.py spending

    # Account summary
    python3 ticketmaster_data.py summary

Output: JSON to stdout
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict

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


# ---- Discovery subcommands ----


def search_events(
    query=None,
    segment=None,
    genre=None,
    city=None,
    state=None,
    date_from=None,
    date_to=None,
    min_price=None,
    max_price=None,
    status=None,
    sort_by="date",
    limit=20,
) -> dict:
    """Search for events with various filters."""
    args = {}
    if query:
        args["query"] = query
    if segment:
        args["segment"] = segment
    if genre:
        args["genre"] = genre
    if city:
        args["city"] = city
    if state:
        args["state"] = state
    if date_from:
        args["date_from"] = date_from
    if date_to:
        args["date_to"] = date_to
    if min_price is not None:
        args["min_price"] = min_price
    if max_price is not None:
        args["max_price"] = max_price
    if status:
        args["status"] = status
    if sort_by:
        args["sort_by"] = sort_by
    args["limit"] = limit

    return _call_tool("ticketmaster_search_events", args)


def get_event_details(event_id: str) -> dict:
    """Get full event details with venue, attractions, and ticket types."""
    return _call_tool("ticketmaster_get_event_details", {"event_id": event_id})


def get_venues(city=None, state=None, venue_type=None) -> dict:
    """Browse and filter venues."""
    args = {}
    if city:
        args["city"] = city
    if state:
        args["state"] = state
    if venue_type:
        args["venue_type"] = venue_type
    return _call_tool("ticketmaster_get_venues", args)


def get_venue_details(venue_id: str) -> dict:
    """Get venue info with upcoming events."""
    return _call_tool("ticketmaster_get_venue_details", {"venue_id": venue_id})


def get_attractions(query=None, attraction_type=None, genre=None) -> dict:
    """Search attractions (artists, bands, teams, comedians, companies)."""
    args = {}
    if query:
        args["query"] = query
    if attraction_type:
        args["type"] = attraction_type
    if genre:
        args["genre"] = genre
    return _call_tool("ticketmaster_get_attractions", args)


def get_attraction_details(attraction_id: str) -> dict:
    """Get attraction info with upcoming events."""
    return _call_tool(
        "ticketmaster_get_attraction_details", {"attraction_id": attraction_id}
    )


def get_classifications() -> dict:
    """Get the Segment > Genre > Sub-Genre hierarchy."""
    return _call_tool("ticketmaster_get_classifications")


# ---- Ticket subcommands ----


def get_ticket_availability(event_id: str) -> dict:
    """Get ticket types, prices, and availability for an event."""
    return _call_tool(
        "ticketmaster_get_ticket_availability", {"event_id": event_id}
    )


def get_event_seat_map(event_id: str) -> dict:
    """Get section-based availability map."""
    return _call_tool(
        "ticketmaster_get_event_seat_map", {"event_id": event_id}
    )


# ---- Commerce subcommands ----


def add_to_cart(event_id: str, ticket_type_id: str, quantity: int) -> dict:
    """Add tickets to cart."""
    return _call_tool(
        "ticketmaster_add_to_cart",
        {
            "event_id": event_id,
            "ticket_type_id": ticket_type_id,
            "quantity": quantity,
        },
    )


def get_cart() -> dict:
    """Get current cart contents."""
    return _call_tool("ticketmaster_get_cart")


def remove_from_cart(cart_item_id: int) -> dict:
    """Remove item from cart."""
    return _call_tool(
        "ticketmaster_remove_from_cart", {"cart_item_id": cart_item_id}
    )


def do_checkout() -> dict:
    """Complete purchase of all items in cart."""
    return _call_tool("ticketmaster_checkout")


def get_order_history() -> dict:
    """Get order history."""
    return _call_tool("ticketmaster_get_order_history")


def get_order_details(identifier: str) -> dict:
    """Get order by ID or confirmation code."""
    return _call_tool(
        "ticketmaster_get_order_details", {"identifier": identifier}
    )


def get_profile() -> dict:
    """Get current user profile."""
    return _call_tool("ticketmaster_get_current_user")


# ---- Analytics subcommands (client-side aggregation) ----


def get_spending() -> dict:
    """Analyze ticket spending from order history."""
    result = _call_tool("ticketmaster_get_order_history")
    orders = result.get("orders", [])

    if not orders:
        return {
            "total_spent": 0,
            "order_count": 0,
            "avg_per_order": 0,
            "total_tickets": 0,
            "total_service_fees": 0,
            "total_processing_fees": 0,
            "by_segment": [],
            "by_venue": [],
        }

    total_spent = sum(float(o.get("total_price", 0)) for o in orders)
    total_tickets = sum(int(o.get("quantity", 0)) for o in orders)
    total_service = sum(float(o.get("service_fee", 0)) for o in orders)
    total_processing = sum(
        float(o.get("order_processing_fee", 0)) for o in orders
    )

    # By segment
    seg_spend: Counter = Counter()
    seg_count: Counter = Counter()
    for o in orders:
        seg = o.get("segment", "Unknown")
        seg_spend[seg] += float(o.get("total_price", 0))
        seg_count[seg] += 1

    by_segment = [
        {
            "segment": seg,
            "total": round(total, 2),
            "order_count": seg_count[seg],
        }
        for seg, total in seg_spend.most_common()
    ]

    # By venue
    venue_spend: Counter = Counter()
    venue_count: Counter = Counter()
    for o in orders:
        venue = o.get("venue_name", "Unknown")
        venue_spend[venue] += float(o.get("total_price", 0))
        venue_count[venue] += 1

    by_venue = [
        {
            "venue": v,
            "total": round(total, 2),
            "order_count": venue_count[v],
        }
        for v, total in venue_spend.most_common()
    ]

    return {
        "total_spent": round(total_spent, 2),
        "order_count": len(orders),
        "avg_per_order": round(total_spent / len(orders), 2),
        "total_tickets": total_tickets,
        "total_service_fees": round(total_service, 2),
        "total_processing_fees": round(total_processing, 2),
        "by_segment": by_segment,
        "by_venue": by_venue,
    }


def get_summary() -> dict:
    """Get account overview with recent orders and spending breakdown."""
    orders_result = _call_tool("ticketmaster_get_order_history")
    orders = orders_result.get("orders", [])

    if not orders:
        return {
            "total_orders": 0,
            "total_spent": 0,
            "total_tickets": 0,
            "recent_orders": [],
            "upcoming_events": [],
            "by_segment": [],
        }

    total_spent = sum(float(o.get("total_price", 0)) for o in orders)
    total_tickets = sum(int(o.get("quantity", 0)) for o in orders)

    # Recent 5 orders
    recent = []
    for o in orders[:5]:
        recent.append({
            "order_id": o.get("id", ""),
            "confirmation_code": o.get("confirmation_code", ""),
            "event_name": o.get("event_name", ""),
            "event_date": o.get("event_date", ""),
            "venue_name": o.get("venue_name", ""),
            "quantity": o.get("quantity", 0),
            "total_price": float(o.get("total_price", 0)),
        })

    # Upcoming events (events with dates in the future are still relevant)
    upcoming = []
    for o in orders:
        event_date = o.get("event_date", "")
        if event_date:
            upcoming.append({
                "event_name": o.get("event_name", ""),
                "event_date": event_date,
                "event_time": o.get("event_time", ""),
                "venue_name": o.get("venue_name", ""),
                "venue_city": o.get("venue_city", ""),
                "venue_state": o.get("venue_state", ""),
                "ticket_type": o.get("ticket_type", ""),
                "quantity": o.get("quantity", 0),
            })
    upcoming.sort(key=lambda x: x.get("event_date", ""))

    # By segment
    seg_spend: Counter = Counter()
    seg_tickets: Counter = Counter()
    for o in orders:
        seg = o.get("segment", "Unknown")
        seg_spend[seg] += float(o.get("total_price", 0))
        seg_tickets[seg] += int(o.get("quantity", 0))

    by_segment = [
        {
            "segment": seg,
            "total": round(total, 2),
            "tickets": seg_tickets[seg],
        }
        for seg, total in seg_spend.most_common()
    ]

    return {
        "total_orders": len(orders),
        "total_spent": round(total_spent, 2),
        "avg_per_order": round(total_spent / len(orders), 2),
        "total_tickets": total_tickets,
        "recent_orders": recent,
        "upcoming_events": upcoming,
        "by_segment": by_segment,
    }


def login(email):
    """Log in to Ticketmaster with your email."""
    return _call_tool("ticketmaster_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Ticketmaster event and ticket data"
    )
    sub = parser.add_subparsers(dest="command")

    # login
    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # search
    search_p = sub.add_parser("search", help="Search events")
    search_p.add_argument("query", nargs="?", default=None, help="Search query")
    search_p.add_argument("--segment", help="Music, Sports, Arts & Theater, Comedy, Family")
    search_p.add_argument("--genre", help="Genre (Pop, Rock, Hip-Hop, NBA, NFL, Musical, Stand-Up, etc.)")
    search_p.add_argument("--city", help="Venue city")
    search_p.add_argument("--state", help="Venue state (2-letter code)")
    search_p.add_argument("--date-from", help="Start date (YYYY-MM-DD)")
    search_p.add_argument("--date-to", help="End date (YYYY-MM-DD)")
    search_p.add_argument("--min-price", type=float, help="Minimum price")
    search_p.add_argument("--max-price", type=float, help="Maximum price")
    search_p.add_argument("--status", help="on_sale, presale, limited, sold_out, cancelled, postponed")
    search_p.add_argument("--sort-by", default="date", help="date, relevance, price_asc, price_desc, name")
    search_p.add_argument("--limit", type=int, default=20, help="Max results")

    # event
    event_p = sub.add_parser("event", help="Get event details")
    event_p.add_argument("event_id", help="Event ID (e.g., EVT001)")

    # venues
    venues_p = sub.add_parser("venues", help="Browse venues")
    venues_p.add_argument("--city", help="Filter by city")
    venues_p.add_argument("--state", help="Filter by state (2-letter code)")
    venues_p.add_argument("--venue-type", help="arena, stadium, theater, club, outdoor")

    # venue
    venue_p = sub.add_parser("venue", help="Get venue details")
    venue_p.add_argument("venue_id", help="Venue ID (e.g., VEN001)")

    # attractions
    attr_p = sub.add_parser("attractions", help="Search attractions")
    attr_p.add_argument("query", nargs="?", default=None, help="Search query")
    attr_p.add_argument("--type", dest="attraction_type", help="artist, band, team, comedian, company")
    attr_p.add_argument("--genre", help="Genre filter")

    # attraction
    attr_detail_p = sub.add_parser("attraction", help="Get attraction details")
    attr_detail_p.add_argument("attraction_id", help="Attraction ID (e.g., ATT001)")

    # classifications
    sub.add_parser("classifications", help="Show classification hierarchy")

    # availability
    avail_p = sub.add_parser("availability", help="Get ticket availability")
    avail_p.add_argument("event_id", help="Event ID")

    # seatmap
    seat_p = sub.add_parser("seatmap", help="Get section-based seat map")
    seat_p.add_argument("event_id", help="Event ID")

    # add-to-cart
    add_cart_p = sub.add_parser("add-to-cart", help="Add tickets to cart")
    add_cart_p.add_argument("event_id", help="Event ID")
    add_cart_p.add_argument("ticket_type_id", help="Ticket type ID (e.g., TKT001)")
    add_cart_p.add_argument("quantity", type=int, help="Number of tickets")

    # cart
    sub.add_parser("cart", help="View cart")

    # remove-from-cart
    rm_cart_p = sub.add_parser("remove-from-cart", help="Remove from cart")
    rm_cart_p.add_argument("cart_item_id", type=int, help="Cart item ID")

    # checkout
    sub.add_parser("checkout", help="Complete purchase")

    # orders
    sub.add_parser("orders", help="View order history")

    # order
    order_p = sub.add_parser("order", help="Get order details")
    order_p.add_argument("identifier", help="Order ID or confirmation code (e.g., TM-A7B3K9)")

    # profile
    sub.add_parser("profile", help="View user profile")

    # spending
    sub.add_parser("spending", help="Spending analytics")

    # summary
    sub.add_parser("summary", help="Account summary")

    args = parser.parse_args()

    if args.command == "login":
        result = login(args.email)
    elif args.command == "search":
        result = search_events(
            query=args.query,
            segment=args.segment,
            genre=args.genre,
            city=args.city,
            state=args.state,
            date_from=args.date_from,
            date_to=args.date_to,
            min_price=args.min_price,
            max_price=args.max_price,
            status=args.status,
            sort_by=args.sort_by,
            limit=args.limit,
        )
    elif args.command == "event":
        result = get_event_details(args.event_id)
    elif args.command == "venues":
        result = get_venues(
            city=args.city,
            state=args.state,
            venue_type=args.venue_type,
        )
    elif args.command == "venue":
        result = get_venue_details(args.venue_id)
    elif args.command == "attractions":
        result = get_attractions(
            query=args.query,
            attraction_type=args.attraction_type,
            genre=args.genre,
        )
    elif args.command == "attraction":
        result = get_attraction_details(args.attraction_id)
    elif args.command == "classifications":
        result = get_classifications()
    elif args.command == "availability":
        result = get_ticket_availability(args.event_id)
    elif args.command == "seatmap":
        result = get_event_seat_map(args.event_id)
    elif args.command == "add-to-cart":
        result = add_to_cart(args.event_id, args.ticket_type_id, args.quantity)
    elif args.command == "cart":
        result = get_cart()
    elif args.command == "remove-from-cart":
        result = remove_from_cart(args.cart_item_id)
    elif args.command == "checkout":
        result = do_checkout()
    elif args.command == "orders":
        result = get_order_history()
    elif args.command == "order":
        result = get_order_details(args.identifier)
    elif args.command == "profile":
        result = get_profile()
    elif args.command == "spending":
        result = get_spending()
    elif args.command == "summary":
        result = get_summary()
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
