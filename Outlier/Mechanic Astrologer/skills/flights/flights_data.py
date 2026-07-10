#!/usr/bin/env python3
"""
Flights Data Fetcher - Search flights and look up airport codes via the Flights MCP server

Usage:
    # Search flights
    python3 flights_data.py search-flights --origin JFK --destination LAX --departure-date 2026-06-15
    python3 flights_data.py search-flights --origin SFO --destination ORD --departure-date 2026-07-01 \
        --trip-type round_trip --return-date 2026-07-08 --passengers 2 --cabin-class business

    # Search airport codes
    python3 flights_data.py search-airports --query "San Francisco"
    python3 flights_data.py search-airports --query "London" --country-code GB --limit 5

    # Show raw data
    python3 flights_data.py show

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


# ---- Subcommand handlers ----


def cmd_search_flights(args):
    """Search for flights by origin, destination, and date."""
    tool_args = {
        "origin": args.origin,
        "destination": args.destination,
        "departure_date": args.departure_date,
    }
    if args.trip_type:
        tool_args["trip_type"] = args.trip_type
    if args.return_date:
        tool_args["return_date"] = args.return_date
    if args.passengers is not None:
        tool_args["passengers"] = args.passengers
    if args.cabin_class:
        tool_args["cabin_class"] = args.cabin_class
    if args.carry_on_bag is not None:
        tool_args["carry_on_bag"] = bool(args.carry_on_bag)
    if args.checked_bags is not None:
        tool_args["checked_bags"] = args.checked_bags
    if args.offset is not None:
        tool_args["offset"] = args.offset
    if args.limit is not None:
        tool_args["limit"] = args.limit
    return _call_tool("flights_search_flights", tool_args)


def cmd_search_airports(args):
    """Search for airport IATA codes by city name or code."""
    tool_args = {"query": args.query}
    if args.country_code:
        tool_args["country_code"] = args.country_code
    if args.limit is not None:
        tool_args["limit"] = args.limit
    return _call_tool("flights_search_airport_codes", tool_args)


def cmd_show(args):
    """Show raw flight data."""
    return _call_tool("flights_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ---- Main ----


def main():
    parser = argparse.ArgumentParser(
        description="Search flights and look up airport codes"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search-flights
    sf_p = sub.add_parser("search-flights", help="Search for flights")
    sf_p.add_argument("--origin", required=True, help="Departure airport IATA code (e.g., JFK)")
    sf_p.add_argument("--destination", required=True, help="Arrival airport IATA code (e.g., LAX)")
    sf_p.add_argument("--departure-date", required=True, help="Departure date (YYYY-MM-DD)")
    sf_p.add_argument("--trip-type", choices=["one_way", "round_trip"], default=None, help="Trip type")
    sf_p.add_argument("--return-date", default=None, help="Return date for round_trip (YYYY-MM-DD)")
    sf_p.add_argument("--passengers", type=int, default=None, help="Number of passengers")
    sf_p.add_argument("--cabin-class", choices=["economy", "business", "first"], default=None, help="Cabin class")
    sf_p.add_argument("--carry-on-bag", type=int, default=None, help="Number of carry-on bags")
    sf_p.add_argument("--checked-bags", type=int, default=None, help="Number of checked bags")
    sf_p.add_argument("--offset", type=int, default=None, help="Pagination offset")
    sf_p.add_argument("--limit", type=int, default=None, help="Max results to return")
    sf_p.set_defaults(func=cmd_search_flights)

    # search-airports
    sa_p = sub.add_parser("search-airports", help="Search airport IATA codes")
    sa_p.add_argument("--query", required=True, help="City name or airport code to search")
    sa_p.add_argument("--country-code", default=None, help="2-letter country code filter (e.g., US, GB)")
    sa_p.add_argument("--limit", type=int, default=None, help="Max results to return")
    sa_p.set_defaults(func=cmd_search_airports)

    # show
    show_p = sub.add_parser("show", help="Show raw flight data")
    show_p.add_argument("--offset", type=int, default=0)
    show_p.add_argument("--limit", type=int, default=100)
    show_p.set_defaults(func=cmd_show)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
