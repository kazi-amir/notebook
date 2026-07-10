#!/usr/bin/env python3
"""
QuickBooks Accounting Data - Manage customers, vendors, invoices, bills, and accounts.

Usage:
    # Search customers
    python3 quickbooks_data.py search-customers [--criteria JSON] [--limit N] [--offset N] [--asc FIELD] [--desc FIELD] [--count] [--fetch-all]

    # Get a specific customer
    python3 quickbooks_data.py get-customer --id ID

    # Create a customer
    python3 quickbooks_data.py create-customer --display-name NAME [--given-name N] [--family-name N] [--company-name N] [--phone N] [--email N] [--bill-addr JSON] [--ship-addr JSON] [--taxable]

    # Search vendors
    python3 quickbooks_data.py search-vendors [--criteria JSON] [--limit N] [--offset N] [--asc FIELD] [--desc FIELD] [--count] [--fetch-all]

    # Get a specific vendor
    python3 quickbooks_data.py get-vendor --id ID

    # Create a vendor
    python3 quickbooks_data.py create-vendor --display-name NAME [--given-name N] [--family-name N] [--company-name N] [--active] [--vendor-1099] [--phone N] [--email N] [--bill-addr JSON]

    # Search invoices
    python3 quickbooks_data.py search-invoices [--criteria JSON]

    # Get a specific invoice
    python3 quickbooks_data.py get-invoice --id ID

    # Create an invoice
    python3 quickbooks_data.py create-invoice --customer-ref JSON --line-items JSON [--txn-date DATE] [--doc-number N]

    # Search bills
    python3 quickbooks_data.py search-bills [--criteria JSON] [--limit N] [--offset N] [--asc FIELD] [--desc FIELD] [--count] [--fetch-all]

    # Get a specific bill
    python3 quickbooks_data.py get-bill --id ID

    # Create a bill
    python3 quickbooks_data.py create-bill --vendor-ref JSON --line JSON [--due-date DATE] [--balance N] [--total-amt N] [--txn-date DATE] [--doc-number N]

    # Search accounts
    python3 quickbooks_data.py search-accounts [--criteria JSON] [--limit N] [--offset N] [--asc FIELD] [--desc FIELD] [--count] [--fetch-all]

    # Create an account
    python3 quickbooks_data.py create-account --name NAME --type TYPE [--sub-type T] [--description T]

    # Update an account
    python3 quickbooks_data.py update-account --id ID --patch JSON

    # Show raw data
    python3 quickbooks_data.py show [--offset N] [--limit N]

    # Reset to initial state
    python3 quickbooks_data.py reset

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


def cmd_search_customers(args):
    """Search customers with criteria."""
    tool_args = {}
    if args.criteria:
        tool_args["criteria"] = json.loads(args.criteria)
    if args.limit:
        tool_args["limit"] = args.limit
    if args.offset:
        tool_args["offset"] = args.offset
    if args.asc:
        tool_args["asc"] = args.asc
    if args.desc:
        tool_args["desc"] = args.desc
    if args.count:
        tool_args["count"] = True
    if args.fetch_all:
        tool_args["fetchAll"] = True
    return _call_tool("quickbooks_search_customers", tool_args)


def cmd_get_customer(args):
    """Get a specific customer by ID."""
    return _call_tool("quickbooks_get_customer", {"id": args.id})


def cmd_create_customer(args):
    """Create a new customer."""
    tool_args = {"DisplayName": args.display_name}
    if args.given_name:
        tool_args["GivenName"] = args.given_name
    if args.family_name:
        tool_args["FamilyName"] = args.family_name
    if args.company_name:
        tool_args["CompanyName"] = args.company_name
    if args.phone:
        tool_args["PrimaryPhone"] = args.phone
    if args.email:
        tool_args["PrimaryEmailAddr"] = args.email
    if args.bill_addr:
        tool_args["BillAddr"] = json.loads(args.bill_addr)
    if args.ship_addr:
        tool_args["ShipAddr"] = json.loads(args.ship_addr)
    if args.taxable:
        tool_args["Taxable"] = True
    return _call_tool("quickbooks_create_customer", tool_args)


def cmd_search_vendors(args):
    """Search vendors with criteria."""
    tool_args = {}
    if args.criteria:
        tool_args["criteria"] = json.loads(args.criteria)
    if args.limit:
        tool_args["limit"] = args.limit
    if args.offset:
        tool_args["offset"] = args.offset
    if args.asc:
        tool_args["asc"] = args.asc
    if args.desc:
        tool_args["desc"] = args.desc
    if args.count:
        tool_args["count"] = True
    if args.fetch_all:
        tool_args["fetchAll"] = True
    return _call_tool("quickbooks_search_vendors", tool_args)


def cmd_get_vendor(args):
    """Get a specific vendor by ID."""
    return _call_tool("quickbooks_get_vendor", {"id": args.id})


def cmd_create_vendor(args):
    """Create a new vendor."""
    tool_args = {"DisplayName": args.display_name}
    if args.given_name:
        tool_args["GivenName"] = args.given_name
    if args.family_name:
        tool_args["FamilyName"] = args.family_name
    if args.company_name:
        tool_args["CompanyName"] = args.company_name
    if args.active is not None:
        tool_args["Active"] = args.active
    if args.vendor_1099:
        tool_args["Vendor1099"] = True
    if args.phone:
        tool_args["PrimaryPhone"] = args.phone
    if args.email:
        tool_args["PrimaryEmailAddr"] = args.email
    if args.bill_addr:
        tool_args["BillAddr"] = json.loads(args.bill_addr)
    return _call_tool("quickbooks_create_vendor", tool_args)


def cmd_search_invoices(args):
    """Search invoices with criteria."""
    tool_args = {}
    if args.criteria:
        tool_args["criteria"] = json.loads(args.criteria)
    return _call_tool("quickbooks_search_invoices", tool_args)


def cmd_get_invoice(args):
    """Get a specific invoice by ID."""
    return _call_tool("quickbooks_read_invoice", {"invoice_id": args.id})


def cmd_create_invoice(args):
    """Create a new invoice."""
    tool_args = {
        "customer_ref": json.loads(args.customer_ref),
        "line_items": json.loads(args.line_items),
    }
    if args.txn_date:
        tool_args["txn_date"] = args.txn_date
    if args.doc_number:
        tool_args["doc_number"] = args.doc_number
    return _call_tool("quickbooks_create_invoice", tool_args)


def cmd_search_bills(args):
    """Search bills with criteria."""
    tool_args = {}
    if args.criteria:
        tool_args["criteria"] = json.loads(args.criteria)
    if args.limit:
        tool_args["limit"] = args.limit
    if args.offset:
        tool_args["offset"] = args.offset
    if args.asc:
        tool_args["asc"] = args.asc
    if args.desc:
        tool_args["desc"] = args.desc
    if args.count:
        tool_args["count"] = True
    if args.fetch_all:
        tool_args["fetchAll"] = True
    return _call_tool("quickbooks_search_bills", tool_args)


def cmd_get_bill(args):
    """Get a specific bill by ID."""
    return _call_tool("quickbooks_get_bill", {"id": args.id})


def cmd_create_bill(args):
    """Create a new bill."""
    tool_args = {
        "VendorRef": json.loads(args.vendor_ref),
        "Line": json.loads(args.line),
    }
    if args.due_date:
        tool_args["DueDate"] = args.due_date
    if args.balance is not None:
        tool_args["Balance"] = args.balance
    if args.total_amt is not None:
        tool_args["TotalAmt"] = args.total_amt
    if args.txn_date:
        tool_args["TxnDate"] = args.txn_date
    if args.doc_number:
        tool_args["DocNumber"] = args.doc_number
    return _call_tool("quickbooks_create_bill", tool_args)


def cmd_search_accounts(args):
    """Search accounts with criteria."""
    tool_args = {}
    if args.criteria:
        tool_args["criteria"] = json.loads(args.criteria)
    if args.limit:
        tool_args["limit"] = args.limit
    if args.offset:
        tool_args["offset"] = args.offset
    if args.asc:
        tool_args["asc"] = args.asc
    if args.desc:
        tool_args["desc"] = args.desc
    if args.count:
        tool_args["count"] = True
    if args.fetch_all:
        tool_args["fetchAll"] = True
    return _call_tool("quickbooks_search_accounts", tool_args)


def cmd_create_account(args):
    """Create a new account."""
    tool_args = {"name": args.name, "type": args.type}
    if args.sub_type:
        tool_args["sub_type"] = args.sub_type
    if args.description:
        tool_args["description"] = args.description
    return _call_tool("quickbooks_create_account", tool_args)


def cmd_update_account(args):
    """Update an existing account."""
    return _call_tool("quickbooks_update_account", {
        "account_id": args.id,
        "patch": json.loads(args.patch),
    })


def cmd_show(args):
    """Show raw QuickBooks data."""
    return _call_tool("quickbooks_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


def cmd_reset(args):
    """Reset to initial state."""
    return _call_tool("quickbooks_reset")


# ==================== Main ====================


def _add_search_args(p):
    """Add common search arguments to a subparser."""
    p.add_argument("--criteria", type=str, help="JSON array of search criteria")
    p.add_argument("--limit", type=int, help="Maximum results to return")
    p.add_argument("--offset", type=int, help="Results offset")
    p.add_argument("--asc", type=str, help="Sort ascending by field")
    p.add_argument("--desc", type=str, help="Sort descending by field")
    p.add_argument("--count", action="store_true", help="Return count only")
    p.add_argument("--fetch-all", action="store_true", help="Fetch all results")


def main():
    parser = argparse.ArgumentParser(description="QuickBooks Accounting Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # search-customers
    p = sub.add_parser("search-customers", help="Search customers")
    _add_search_args(p)
    p.set_defaults(func=cmd_search_customers)

    # get-customer
    p = sub.add_parser("get-customer", help="Get a customer by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_customer)

    # create-customer
    p = sub.add_parser("create-customer", help="Create a new customer")
    p.add_argument("--display-name", type=str, required=True)
    p.add_argument("--given-name", type=str)
    p.add_argument("--family-name", type=str)
    p.add_argument("--company-name", type=str)
    p.add_argument("--phone", type=str)
    p.add_argument("--email", type=str)
    p.add_argument("--bill-addr", type=str, help="JSON address object")
    p.add_argument("--ship-addr", type=str, help="JSON address object")
    p.add_argument("--taxable", action="store_true")
    p.set_defaults(func=cmd_create_customer)

    # search-vendors
    p = sub.add_parser("search-vendors", help="Search vendors")
    _add_search_args(p)
    p.set_defaults(func=cmd_search_vendors)

    # get-vendor
    p = sub.add_parser("get-vendor", help="Get a vendor by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_vendor)

    # create-vendor
    p = sub.add_parser("create-vendor", help="Create a new vendor")
    p.add_argument("--display-name", type=str, required=True)
    p.add_argument("--given-name", type=str)
    p.add_argument("--family-name", type=str)
    p.add_argument("--company-name", type=str)
    p.add_argument("--active", action="store_true", default=None)
    p.add_argument("--vendor-1099", action="store_true")
    p.add_argument("--phone", type=str)
    p.add_argument("--email", type=str)
    p.add_argument("--bill-addr", type=str, help="JSON address object")
    p.set_defaults(func=cmd_create_vendor)

    # search-invoices
    p = sub.add_parser("search-invoices", help="Search invoices")
    p.add_argument("--criteria", type=str, help="JSON object with key-value filters")
    p.set_defaults(func=cmd_search_invoices)

    # get-invoice
    p = sub.add_parser("get-invoice", help="Get an invoice by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_invoice)

    # create-invoice
    p = sub.add_parser("create-invoice", help="Create a new invoice")
    p.add_argument("--customer-ref", type=str, required=True, help="JSON customer reference")
    p.add_argument("--line-items", type=str, required=True, help="JSON array of line items")
    p.add_argument("--txn-date", type=str, help="Transaction date")
    p.add_argument("--doc-number", type=str, help="Document number")
    p.set_defaults(func=cmd_create_invoice)

    # search-bills
    p = sub.add_parser("search-bills", help="Search bills")
    _add_search_args(p)
    p.set_defaults(func=cmd_search_bills)

    # get-bill
    p = sub.add_parser("get-bill", help="Get a bill by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_bill)

    # create-bill
    p = sub.add_parser("create-bill", help="Create a new bill")
    p.add_argument("--vendor-ref", type=str, required=True, help="JSON vendor reference")
    p.add_argument("--line", type=str, required=True, help="JSON array of line items")
    p.add_argument("--due-date", type=str, help="Due date")
    p.add_argument("--balance", type=float, help="Balance amount")
    p.add_argument("--total-amt", type=float, help="Total amount")
    p.add_argument("--txn-date", type=str, help="Transaction date")
    p.add_argument("--doc-number", type=str, help="Document number")
    p.set_defaults(func=cmd_create_bill)

    # search-accounts
    p = sub.add_parser("search-accounts", help="Search accounts")
    _add_search_args(p)
    p.set_defaults(func=cmd_search_accounts)

    # create-account
    p = sub.add_parser("create-account", help="Create a new account")
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--type", type=str, required=True, help="Account type (e.g. Bank, Expense)")
    p.add_argument("--sub-type", type=str)
    p.add_argument("--description", type=str)
    p.set_defaults(func=cmd_create_account)

    # update-account
    p = sub.add_parser("update-account", help="Update an existing account")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--patch", type=str, required=True, help="JSON object with fields to update")
    p.set_defaults(func=cmd_update_account)

    # show
    p = sub.add_parser("show", help="Show raw data")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_show)

    # reset
    p = sub.add_parser("reset", help="Reset to initial state")
    p.set_defaults(func=cmd_reset)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
