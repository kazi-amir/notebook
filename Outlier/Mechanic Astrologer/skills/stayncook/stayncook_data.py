#!/usr/bin/env python3
"""
StayNCook Data - Search vacation rental listings and check availability.

Usage:
    python3 stayncook_data.py search [--city CITY] [--country-code CC]
        [--checkin DATE] [--checkout DATE] [--adults N] [--children N]
        [--infants N] [--pets N] [--min-price P] [--max-price P]
        [--offset N] [--limit N]
    python3 stayncook_data.py listing-details --id ID [--checkin DATE]
        [--checkout DATE] [--adults N] [--children N] [--infants N]
        [--pets N]
    python3 stayncook_data.py show

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


def cmd_search(args):
    """Search vacation rental listings."""
    tool_args = {"city": args.city}
    if args.country_code:
        tool_args["country_code"] = args.country_code
    if args.checkin:
        tool_args["checkin"] = args.checkin
    if args.checkout:
        tool_args["checkout"] = args.checkout
    if args.adults is not None:
        tool_args["adults"] = args.adults
    if args.children is not None:
        tool_args["children"] = args.children
    if args.infants is not None:
        tool_args["infants"] = args.infants
    if args.pets is not None:
        tool_args["pets"] = args.pets
    if args.min_price is not None:
        tool_args["min_price"] = args.min_price
    if args.max_price is not None:
        tool_args["max_price"] = args.max_price
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.limit is not None:
        tool_args["limit"] = args.limit
    return _call_tool("stayncook_search", tool_args)


def cmd_listing_details(args):
    """Get detailed info for a specific listing."""
    tool_args = {
        "id": args.id,
    }
    if args.checkin:
        tool_args["checkin"] = args.checkin
    if args.checkout:
        tool_args["checkout"] = args.checkout
    if args.adults is not None:
        tool_args["adults"] = args.adults
    if args.children is not None:
        tool_args["children"] = args.children
    if args.infants is not None:
        tool_args["infants"] = args.infants
    if args.pets is not None:
        tool_args["pets"] = args.pets
    return _call_tool("stayncook_listing_details", tool_args)


# --- Utility ---

def cmd_show(args):
    """Show raw StayNCook data."""
    return _call_tool("stayncook_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="StayNCook Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Search ---

    # search
    p = sub.add_parser("search", help="Search vacation rental listings")
    p.add_argument("--city", type=str, required=True, help="City name")
    p.add_argument("--country-code", type=str, help="Two-letter ISO country code")
    p.add_argument("--checkin", type=str, help="Check-in date (YYYY-MM-DD)")
    p.add_argument("--checkout", type=str, help="Check-out date (YYYY-MM-DD)")
    p.add_argument("--adults", type=int, help="Number of adults")
    p.add_argument("--children", type=int, help="Number of children")
    p.add_argument("--infants", type=int, help="Number of infants")
    p.add_argument("--pets", type=int, help="Number of pets")
    p.add_argument("--min-price", type=float, help="Minimum price per night")
    p.add_argument("--max-price", type=float, help="Maximum price per night")
    p.add_argument("--offset", type=int, help="Pagination offset")
    p.add_argument("--limit", type=int, help="Number of results to return")
    p.set_defaults(func=cmd_search)

    # --- Listing Details ---

    # listing-details
    p = sub.add_parser("listing-details", help="Get listing details")
    p.add_argument("--id", type=str, required=True, help="Listing ID")
    p.add_argument("--checkin", type=str, help="Check-in date (YYYY-MM-DD)")
    p.add_argument("--checkout", type=str, help="Check-out date (YYYY-MM-DD)")
    p.add_argument("--adults", type=int, help="Number of adults")
    p.add_argument("--children", type=int, help="Number of children")
    p.add_argument("--infants", type=int, help="Number of infants")
    p.add_argument("--pets", type=int, help="Number of pets")
    p.set_defaults(func=cmd_listing_details)

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
