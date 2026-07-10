#!/usr/bin/env python3
"""
Cab Data - Book rides, get quotations, and manage ride history.

Usage:
    python3 cab_data.py get-quotation --start-location LOC --end-location LOC
        [--service-type TYPE] [--ride-time TIME]
    python3 cab_data.py list-rides --start-location LOC --end-location LOC
        [--ride-time TIME]
    python3 cab_data.py order-ride --start-location LOC --end-location LOC
        --service-type TYPE [--ride-time TIME]
    python3 cab_data.py cancel-ride
    python3 cab_data.py ride-status
    python3 cab_data.py get-ride --idx N
    python3 cab_data.py ride-history [--offset N] [--limit N]
    python3 cab_data.py ride-history-length
    python3 cab_data.py show

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


def cmd_get_quotation(args):
    """Get a price quotation for a ride."""
    tool_args = {
        "start_location": args.start_location,
        "end_location": args.end_location,
    }
    if args.service_type:
        tool_args["service_type"] = args.service_type
    if args.ride_time:
        tool_args["ride_time"] = args.ride_time
    return _call_tool("cab_get_quotation", tool_args)


def cmd_list_rides(args):
    """List available rides between two locations."""
    tool_args = {
        "start_location": args.start_location,
        "end_location": args.end_location,
    }
    if args.ride_time:
        tool_args["ride_time"] = args.ride_time
    return _call_tool("cab_list_rides", tool_args)


def cmd_order_ride(args):
    """Order a ride."""
    tool_args = {
        "start_location": args.start_location,
        "end_location": args.end_location,
        "service_type": args.service_type,
    }
    if args.ride_time:
        tool_args["ride_time"] = args.ride_time
    return _call_tool("cab_order_ride", tool_args)


def cmd_cancel_ride(args):
    """Cancel the current ride."""
    return _call_tool("cab_user_cancel_ride")


def cmd_ride_status(args):
    """Get current ride status."""
    return _call_tool("cab_get_current_ride_status")


def cmd_get_ride(args):
    """Get a specific ride from history by index."""
    return _call_tool("cab_get_ride", {"idx": args.idx})


def cmd_ride_history(args):
    """List ride history with pagination."""
    tool_args = {}
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.limit is not None:
        tool_args["limit"] = args.limit
    return _call_tool("cab_get_ride_history", tool_args)


def cmd_ride_history_length(args):
    """Get total number of rides in history."""
    return _call_tool("cab_get_ride_history_length")


# --- Utility ---

def cmd_show(args):
    """Show raw cab data."""
    return _call_tool("cab_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Cab Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Quotations ---

    # get-quotation
    p = sub.add_parser("get-quotation", help="Get a price quotation")
    p.add_argument("--start-location", type=str, required=True)
    p.add_argument("--end-location", type=str, required=True)
    p.add_argument("--service-type", type=str, help="Default, Premium, or Van")
    p.add_argument("--ride-time", type=str, help="Ride time (e.g. '2026-04-15 10:00:00')")
    p.set_defaults(func=cmd_get_quotation)

    # --- Booking ---

    # list-rides
    p = sub.add_parser("list-rides", help="List available rides")
    p.add_argument("--start-location", type=str, required=True)
    p.add_argument("--end-location", type=str, required=True)
    p.add_argument("--ride-time", type=str, help="Ride time")
    p.set_defaults(func=cmd_list_rides)

    # order-ride
    p = sub.add_parser("order-ride", help="Order a ride")
    p.add_argument("--start-location", type=str, required=True)
    p.add_argument("--end-location", type=str, required=True)
    p.add_argument("--service-type", type=str, required=True, help="Default, Premium, or Van")
    p.add_argument("--ride-time", type=str, help="Ride time")
    p.set_defaults(func=cmd_order_ride)

    # --- Ride Status ---

    # cancel-ride
    p = sub.add_parser("cancel-ride", help="Cancel the current ride")
    p.set_defaults(func=cmd_cancel_ride)

    # ride-status
    p = sub.add_parser("ride-status", help="Get current ride status")
    p.set_defaults(func=cmd_ride_status)

    # --- Ride History ---

    # get-ride
    p = sub.add_parser("get-ride", help="Get a ride by history index")
    p.add_argument("--idx", type=int, required=True, help="Index in ride history")
    p.set_defaults(func=cmd_get_ride)

    # ride-history
    p = sub.add_parser("ride-history", help="List ride history")
    p.add_argument("--offset", type=int)
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_ride_history)

    # ride-history-length
    p = sub.add_parser("ride-history-length", help="Get total rides in history")
    p.set_defaults(func=cmd_ride_history_length)

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
