#!/usr/bin/env python3
"""
Hotel PMS Data - Manage rooms, guests, reservations, occupancy, and OTA pricing.

Usage:
    python3 hotel_data.py rooms [--limit N]
    python3 hotel_data.py room --number NUM
    python3 hotel_data.py search-rooms [--room-type TYPE] [--floor N] [--view VIEW]
    python3 hotel_data.py available-rooms --start DATE --end DATE [--room-type TYPE]
    python3 hotel_data.py guests [--limit N]
    python3 hotel_data.py guest --id ID
    python3 hotel_data.py search-guests --query TEXT [--limit N]
    python3 hotel_data.py reservations [--status STATUS] [--limit N]
    python3 hotel_data.py reservation --code CODE
    python3 hotel_data.py search-reservations [--guest-id ID] [--status STATUS]
        [--start DATE] [--end DATE] [--limit N]
    python3 hotel_data.py todays-checkins
    python3 hotel_data.py todays-checkouts
    python3 hotel_data.py emails [--limit N]
    python3 hotel_data.py email --id ID
    python3 hotel_data.py search-emails --query TEXT [--limit N]
    python3 hotel_data.py emails-by-reservation --code CODE
    python3 hotel_data.py occupancy --start DATE --end DATE
    python3 hotel_data.py occupancy-summary --start DATE --end DATE
    python3 hotel_data.py ota-pricing --room-type TYPE --date DATE
    python3 hotel_data.py rate-comparison --date DATE [--room-type TYPE]

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


def cmd_rooms(args):
    return _call_tool("hotel_get_all_rooms", {"limit": args.limit})


def cmd_room(args):
    return _call_tool("hotel_get_room", {"room_number": args.number})


def cmd_search_rooms(args):
    tool_args = {}
    if args.room_type:
        tool_args["room_type"] = args.room_type
    if args.floor is not None:
        tool_args["floor"] = args.floor
    if args.view:
        tool_args["view"] = args.view
    return _call_tool("hotel_search_rooms", tool_args)


def cmd_available_rooms(args):
    tool_args = {"start_date": args.start, "end_date": args.end}
    if args.room_type:
        tool_args["room_type"] = args.room_type
    return _call_tool("hotel_get_available_rooms", tool_args)


def cmd_guests(args):
    return _call_tool("hotel_get_all_guests", {"limit": args.limit})


def cmd_guest(args):
    return _call_tool("hotel_get_guest", {"guest_id": args.id})


def cmd_search_guests(args):
    return _call_tool("hotel_search_guests", {"query": args.query, "limit": args.limit})


def cmd_reservations(args):
    tool_args = {"limit": args.limit}
    if args.status:
        tool_args["status"] = args.status
    return _call_tool("hotel_get_all_reservations", tool_args)


def cmd_reservation(args):
    return _call_tool("hotel_get_reservation", {"confirmation_code": args.code})


def cmd_search_reservations(args):
    tool_args = {"limit": args.limit}
    if args.guest_id:
        tool_args["guest_id"] = args.guest_id
    if args.status:
        tool_args["status"] = args.status
    if args.start:
        tool_args["start_date"] = args.start
    if args.end:
        tool_args["end_date"] = args.end
    return _call_tool("hotel_search_reservations", tool_args)


def cmd_todays_checkins(args):
    return _call_tool("hotel_get_todays_checkins")


def cmd_todays_checkouts(args):
    return _call_tool("hotel_get_todays_checkouts")


def cmd_emails(args):
    return _call_tool("hotel_get_all_emails", {"limit": args.limit})


def cmd_email(args):
    return _call_tool("hotel_get_email", {"email_id": args.id})


def cmd_search_emails(args):
    return _call_tool("hotel_search_emails", {"query": args.query, "limit": args.limit})


def cmd_emails_by_reservation(args):
    return _call_tool("hotel_get_emails_by_reservation", {"confirmation_code": args.code})


def cmd_occupancy(args):
    return _call_tool("hotel_get_occupancy", {"start_date": args.start, "end_date": args.end})


def cmd_occupancy_summary(args):
    return _call_tool("hotel_get_occupancy_summary", {"start_date": args.start, "end_date": args.end})


def cmd_ota_pricing(args):
    return _call_tool("hotel_get_ota_pricing", {"room_type": args.room_type, "date": args.date})


def cmd_rate_comparison(args):
    tool_args = {"date": args.date}
    if args.room_type:
        tool_args["room_type"] = args.room_type
    return _call_tool("hotel_get_rate_comparison", tool_args)


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Hotel PMS Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # rooms
    p = sub.add_parser("rooms", help="List all rooms")
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(func=cmd_rooms)

    # room
    p = sub.add_parser("room", help="Get room by number")
    p.add_argument("--number", type=str, required=True)
    p.set_defaults(func=cmd_room)

    # search-rooms
    p = sub.add_parser("search-rooms", help="Search rooms")
    p.add_argument("--room-type", type=str)
    p.add_argument("--floor", type=int)
    p.add_argument("--view", type=str)
    p.set_defaults(func=cmd_search_rooms)

    # available-rooms
    p = sub.add_parser("available-rooms", help="Get available rooms for dates")
    p.add_argument("--start", type=str, required=True)
    p.add_argument("--end", type=str, required=True)
    p.add_argument("--room-type", type=str)
    p.set_defaults(func=cmd_available_rooms)

    # guests
    p = sub.add_parser("guests", help="List all guests")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_guests)

    # guest
    p = sub.add_parser("guest", help="Get guest by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_guest)

    # search-guests
    p = sub.add_parser("search-guests", help="Search guests")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_search_guests)

    # reservations
    p = sub.add_parser("reservations", help="List reservations")
    p.add_argument("--status", type=str)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_reservations)

    # reservation
    p = sub.add_parser("reservation", help="Get reservation by code")
    p.add_argument("--code", type=str, required=True)
    p.set_defaults(func=cmd_reservation)

    # search-reservations
    p = sub.add_parser("search-reservations", help="Search reservations")
    p.add_argument("--guest-id", type=str)
    p.add_argument("--status", type=str)
    p.add_argument("--start", type=str)
    p.add_argument("--end", type=str)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_search_reservations)

    # todays-checkins
    p = sub.add_parser("todays-checkins", help="Today's check-ins")
    p.set_defaults(func=cmd_todays_checkins)

    # todays-checkouts
    p = sub.add_parser("todays-checkouts", help="Today's check-outs")
    p.set_defaults(func=cmd_todays_checkouts)

    # emails
    p = sub.add_parser("emails", help="List hotel emails")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_emails)

    # email
    p = sub.add_parser("email", help="Get email by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_email)

    # search-emails
    p = sub.add_parser("search-emails", help="Search emails")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_search_emails)

    # emails-by-reservation
    p = sub.add_parser("emails-by-reservation", help="Emails for a reservation")
    p.add_argument("--code", type=str, required=True)
    p.set_defaults(func=cmd_emails_by_reservation)

    # occupancy
    p = sub.add_parser("occupancy", help="Occupancy data for date range")
    p.add_argument("--start", type=str, required=True)
    p.add_argument("--end", type=str, required=True)
    p.set_defaults(func=cmd_occupancy)

    # occupancy-summary
    p = sub.add_parser("occupancy-summary", help="Occupancy summary")
    p.add_argument("--start", type=str, required=True)
    p.add_argument("--end", type=str, required=True)
    p.set_defaults(func=cmd_occupancy_summary)

    # ota-pricing
    p = sub.add_parser("ota-pricing", help="OTA pricing for room type and date")
    p.add_argument("--room-type", type=str, required=True)
    p.add_argument("--date", type=str, required=True)
    p.set_defaults(func=cmd_ota_pricing)

    # rate-comparison
    p = sub.add_parser("rate-comparison", help="Rate comparison across OTAs")
    p.add_argument("--date", type=str, required=True)
    p.add_argument("--room-type", type=str)
    p.set_defaults(func=cmd_rate_comparison)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
