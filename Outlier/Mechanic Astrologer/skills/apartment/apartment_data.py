#!/usr/bin/env python3
"""
Apartment Data - Search apartments, view details, and manage saved listings.

Usage:
    # List all apartments
    python3 apartment_data.py list-all

    # Get apartment details
    python3 apartment_data.py get-details --apartment-id APT001

    # Save an apartment
    python3 apartment_data.py save --apartment-id APT001

    # Remove a saved apartment
    python3 apartment_data.py remove-saved --apartment-id APT001

    # List saved apartments
    python3 apartment_data.py list-saved

    # Search apartments with filters
    python3 apartment_data.py search [--name TEXT] [--location TEXT] [--zip-code TEXT]
        [--min-price N] [--max-price N] [--number-of-bedrooms N]
        [--number-of-bathrooms N] [--property-type TYPE] [--square-footage N]
        [--furnished-status STATUS] [--floor-level LEVEL] [--pet-policy POLICY]
        [--lease-term TERM] [--amenities JSON] [--saved-only BOOL]

    # Show raw apartment data
    python3 apartment_data.py show

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


def cmd_list_all(args):
    """List all apartments."""
    return _call_tool("apartment_list_all_apartments")


def cmd_get_details(args):
    """Get details for a specific apartment."""
    return _call_tool("apartment_get_apartment_details", {
        "apartment_id": args.apartment_id,
    })


def cmd_save(args):
    """Save an apartment to favorites."""
    return _call_tool("apartment_save_apartment", {
        "apartment_id": args.apartment_id,
    })


def cmd_remove_saved(args):
    """Remove a saved apartment from favorites."""
    return _call_tool("apartment_remove_saved_apartment", {
        "apartment_id": args.apartment_id,
    })


def cmd_list_saved(args):
    """List all saved apartments."""
    return _call_tool("apartment_list_saved_apartments")


def cmd_search(args):
    """Search apartments with filters."""
    tool_args = {}

    if args.name:
        tool_args["name"] = args.name
    if args.location:
        tool_args["location"] = args.location
    if args.zip_code:
        tool_args["zip_code"] = args.zip_code
    if args.min_price is not None:
        tool_args["min_price"] = args.min_price
    if args.max_price is not None:
        tool_args["max_price"] = args.max_price
    if args.number_of_bedrooms is not None:
        tool_args["number_of_bedrooms"] = args.number_of_bedrooms
    if args.number_of_bathrooms is not None:
        tool_args["number_of_bathrooms"] = args.number_of_bathrooms
    if args.property_type:
        tool_args["property_type"] = args.property_type
    if args.square_footage is not None:
        tool_args["square_footage"] = args.square_footage
    if args.furnished_status:
        tool_args["furnished_status"] = args.furnished_status
    if args.floor_level:
        tool_args["floor_level"] = args.floor_level
    if args.pet_policy:
        tool_args["pet_policy"] = args.pet_policy
    if args.lease_term:
        tool_args["lease_term"] = args.lease_term
    if args.amenities:
        tool_args["amenities"] = args.amenities
    if args.saved_only:
        tool_args["saved_only"] = args.saved_only.lower() in ("true", "1", "yes")

    return _call_tool("apartment_search_apartments", tool_args)


def cmd_show(args):
    """Show raw apartment data."""
    return _call_tool("apartment_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Apartment Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # list-all
    p = sub.add_parser("list-all", help="List all apartments")
    p.set_defaults(func=cmd_list_all)

    # get-details
    p = sub.add_parser("get-details", help="Get apartment details")
    p.add_argument("--apartment-id", type=str, required=True, help="Apartment ID")
    p.set_defaults(func=cmd_get_details)

    # save
    p = sub.add_parser("save", help="Save an apartment to favorites")
    p.add_argument("--apartment-id", type=str, required=True, help="Apartment ID")
    p.set_defaults(func=cmd_save)

    # remove-saved
    p = sub.add_parser("remove-saved", help="Remove a saved apartment")
    p.add_argument("--apartment-id", type=str, required=True, help="Apartment ID")
    p.set_defaults(func=cmd_remove_saved)

    # list-saved
    p = sub.add_parser("list-saved", help="List saved apartments")
    p.set_defaults(func=cmd_list_saved)

    # search
    p = sub.add_parser("search", help="Search apartments with filters")
    p.add_argument("--name", type=str, help="Filter by name")
    p.add_argument("--location", type=str, help="Filter by location")
    p.add_argument("--zip-code", type=str, help="Filter by zip code")
    p.add_argument("--min-price", type=int, help="Minimum monthly rent")
    p.add_argument("--max-price", type=int, help="Maximum monthly rent")
    p.add_argument("--number-of-bedrooms", type=int, help="Number of bedrooms")
    p.add_argument("--number-of-bathrooms", type=int, help="Number of bathrooms")
    p.add_argument("--property-type", type=str,
                   help="Apartment, Condo, Loft, Studio, Townhouse, House")
    p.add_argument("--square-footage", type=int, help="Minimum square footage")
    p.add_argument("--furnished-status", type=str,
                   help="Furnished, Unfurnished, Semi-furnished")
    p.add_argument("--floor-level", type=str,
                   help="Ground floor, Upper floors, Penthouse, Basement")
    p.add_argument("--pet-policy", type=str,
                   help="Pets allowed, No pets, Cats allowed, Dogs allowed")
    p.add_argument("--lease-term", type=str,
                   help="Month-to-month, 6 months, 1 year, Long term")
    p.add_argument("--amenities", type=str,
                   help='JSON array of amenities, e.g. \'["Pool", "Gym"]\'')
    p.add_argument("--saved-only", type=str,
                   help="true/false - show only saved apartments")
    p.set_defaults(func=cmd_search)

    # show
    p = sub.add_parser("show", help="Show raw apartment data")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_show)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
