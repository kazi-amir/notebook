#!/usr/bin/env python3
"""
Buildium Property Management Data - Manage properties, units, tenants, leases, work orders.

Usage:
    # List all properties
    python3 buildium_data.py properties [--limit N]

    # Get a specific property
    python3 buildium_data.py property --id N

    # Get preferred vendors for a property
    python3 buildium_data.py property-vendors --id N

    # List/search units
    python3 buildium_data.py units [--status STATUS] [--property-id N]
        [--min-beds N] [--max-rent N] [--limit N]

    # Get a specific unit
    python3 buildium_data.py unit --id N

    # List tenants
    python3 buildium_data.py tenants [--status STATUS] [--property-id N] [--limit N]

    # Get a specific tenant
    python3 buildium_data.py tenant --id N

    # Search tenants by name/email
    python3 buildium_data.py search-tenants --query TEXT [--limit N]

    # List leases
    python3 buildium_data.py leases [--limit N]

    # Get a specific lease
    python3 buildium_data.py lease --id N

    # Get expiring leases
    python3 buildium_data.py expiring-leases [--within-days N]

    # List work orders
    python3 buildium_data.py work-orders [--status STATUS] [--priority PRIORITY]
        [--category CAT] [--property-id N] [--limit N]

    # Get a specific work order
    python3 buildium_data.py work-order --id N

    # Search work orders
    python3 buildium_data.py search-work-orders --query TEXT [--limit N]

    # Get work order statistics
    python3 buildium_data.py work-order-stats

    # List vendors
    python3 buildium_data.py vendors [--category CAT] [--limit N]

    # Get a specific vendor
    python3 buildium_data.py vendor --id N

    # List vendor categories
    python3 buildium_data.py vendor-categories

    # List applicants
    python3 buildium_data.py applicants [--status STATUS] [--unit-id N] [--limit N]

    # Get a specific applicant
    python3 buildium_data.py applicant --id N

    # Get dashboard stats
    python3 buildium_data.py dashboard

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


def cmd_properties(args):
    """List all rental properties."""
    return _call_tool("buildium_get_all_rentals", {"limit": args.limit})


def cmd_property(args):
    """Get a specific property by ID."""
    return _call_tool("buildium_get_rental_by_id", {"property_id": args.id})


def cmd_property_vendors(args):
    """Get preferred vendors for a property."""
    return _call_tool("buildium_get_rental_preferred_vendors", {"property_id": args.id})


def cmd_units(args):
    """List/search units with filters."""
    tool_args = {}
    if args.status:
        tool_args["status"] = args.status
    if args.property_id:
        tool_args["property_id"] = args.property_id
    if args.min_beds is not None:
        tool_args["min_bedrooms"] = args.min_beds
    if args.max_rent is not None:
        tool_args["max_rent"] = args.max_rent
    tool_args["limit"] = args.limit
    return _call_tool("buildium_get_all_rental_units", tool_args)


def cmd_unit(args):
    """Get a specific unit by ID."""
    return _call_tool("buildium_get_rental_unit_by_id", {"unit_id": args.id})


def cmd_tenants(args):
    """List tenants with optional filters."""
    tool_args = {"limit": args.limit}
    if args.status:
        tool_args["status"] = args.status
    if args.property_id:
        tool_args["property_id"] = args.property_id
    return _call_tool("buildium_get_all_tenants", tool_args)


def cmd_tenant(args):
    """Get a specific tenant by ID."""
    return _call_tool("buildium_get_tenant_by_id", {"tenant_id": args.id})


def cmd_search_tenants(args):
    """Search tenants by name or email."""
    return _call_tool("buildium_search_tenants", {
        "query": args.query, "limit": args.limit,
    })


def cmd_leases(args):
    """List all leases."""
    return _call_tool("buildium_get_all_leases", {"limit": args.limit})


def cmd_lease(args):
    """Get a specific lease by ID."""
    return _call_tool("buildium_get_lease_by_id", {"lease_id": args.id})


def cmd_expiring_leases(args):
    """Get leases expiring within N days."""
    return _call_tool("buildium_get_lease_renewals", {
        "within_days": args.within_days,
    })


def cmd_work_orders(args):
    """List work orders with filters."""
    tool_args = {"limit": args.limit}
    if args.status:
        tool_args["status"] = args.status
    if args.priority:
        tool_args["priority"] = args.priority
    if args.category:
        tool_args["category"] = args.category
    if args.property_id:
        tool_args["property_id"] = args.property_id
    return _call_tool("buildium_get_all_work_orders", tool_args)


def cmd_work_order(args):
    """Get a specific work order by ID."""
    return _call_tool("buildium_get_work_order_by_id", {"work_order_id": args.id})


def cmd_search_work_orders(args):
    """Search work orders by keyword."""
    return _call_tool("buildium_search_work_orders", {
        "query": args.query, "limit": args.limit,
    })


def cmd_work_order_stats(args):
    """Get work order statistics."""
    return _call_tool("buildium_get_work_order_stats")


def cmd_vendors(args):
    """List vendors with optional category filter."""
    tool_args = {"limit": args.limit}
    if args.category:
        tool_args["category"] = args.category
    return _call_tool("buildium_get_all_vendors", tool_args)


def cmd_vendor(args):
    """Get a specific vendor by ID."""
    return _call_tool("buildium_get_vendor_by_id", {"vendor_id": args.id})


def cmd_vendor_categories(args):
    """List all vendor categories."""
    return _call_tool("buildium_get_vendor_categories")


def cmd_applicants(args):
    """List applicants with optional filters."""
    tool_args = {"limit": args.limit}
    if args.status:
        tool_args["status"] = args.status
    if args.unit_id:
        tool_args["unit_id"] = args.unit_id
    return _call_tool("buildium_get_applicants", tool_args)


def cmd_applicant(args):
    """Get a specific applicant by ID."""
    return _call_tool("buildium_get_applicant_by_id", {"applicant_id": args.id})


def cmd_dashboard(args):
    """Get portfolio dashboard statistics."""
    return _call_tool("buildium_get_dashboard_stats")


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Buildium Property Management Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # properties
    p = sub.add_parser("properties", help="List all properties")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_properties)

    # property
    p = sub.add_parser("property", help="Get a property by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_property)

    # property-vendors
    p = sub.add_parser("property-vendors", help="Get preferred vendors for a property")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_property_vendors)

    # units
    p = sub.add_parser("units", help="List/search units")
    p.add_argument("--status", type=str)
    p.add_argument("--property-id", type=int)
    p.add_argument("--min-beds", type=int)
    p.add_argument("--max-rent", type=float)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_units)

    # unit
    p = sub.add_parser("unit", help="Get a unit by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_unit)

    # tenants
    p = sub.add_parser("tenants", help="List tenants")
    p.add_argument("--status", type=str)
    p.add_argument("--property-id", type=int)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_tenants)

    # tenant
    p = sub.add_parser("tenant", help="Get a tenant by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_tenant)

    # search-tenants
    p = sub.add_parser("search-tenants", help="Search tenants by name/email")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_search_tenants)

    # leases
    p = sub.add_parser("leases", help="List all leases")
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_leases)

    # lease
    p = sub.add_parser("lease", help="Get a lease by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_lease)

    # expiring-leases
    p = sub.add_parser("expiring-leases", help="Get leases expiring soon")
    p.add_argument("--within-days", type=int, default=90)
    p.set_defaults(func=cmd_expiring_leases)

    # work-orders
    p = sub.add_parser("work-orders", help="List work orders")
    p.add_argument("--status", type=str)
    p.add_argument("--priority", type=str)
    p.add_argument("--category", type=str)
    p.add_argument("--property-id", type=int)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_work_orders)

    # work-order
    p = sub.add_parser("work-order", help="Get a work order by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_work_order)

    # search-work-orders
    p = sub.add_parser("search-work-orders", help="Search work orders")
    p.add_argument("--query", type=str, required=True)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_search_work_orders)

    # work-order-stats
    p = sub.add_parser("work-order-stats", help="Get work order statistics")
    p.set_defaults(func=cmd_work_order_stats)

    # vendors
    p = sub.add_parser("vendors", help="List vendors")
    p.add_argument("--category", type=str)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_vendors)

    # vendor
    p = sub.add_parser("vendor", help="Get a vendor by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_vendor)

    # vendor-categories
    p = sub.add_parser("vendor-categories", help="List vendor categories")
    p.set_defaults(func=cmd_vendor_categories)

    # applicants
    p = sub.add_parser("applicants", help="List applicants")
    p.add_argument("--status", type=str)
    p.add_argument("--unit-id", type=int)
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_applicants)

    # applicant
    p = sub.add_parser("applicant", help="Get an applicant by ID")
    p.add_argument("--id", type=int, required=True)
    p.set_defaults(func=cmd_applicant)

    # dashboard
    p = sub.add_parser("dashboard", help="Get portfolio dashboard stats")
    p.set_defaults(func=cmd_dashboard)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
