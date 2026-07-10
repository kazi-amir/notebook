#!/usr/bin/env python3
"""
CRM Data - Manage contacts, companies, deals, leads, and engagements.

Usage:
    # Search contacts
    python3 crm_data.py search-contacts --full-name NAME

    # Get a specific contact
    python3 crm_data.py get-contact --id ID

    # Create a contact
    python3 crm_data.py create-contact --full-name NAME --email EMAIL [--company-id ID] [--company N] [--address N] [--city N] [--state N] [--country N] [--zip N] [--phone N] [--mobilephone N] [--jobtitle N] [--website N]

    # Delete a contact
    python3 crm_data.py delete-contact --id ID

    # Search companies
    python3 crm_data.py search-companies --name NAME

    # Get a specific company
    python3 crm_data.py get-company --id ID

    # Create a company
    python3 crm_data.py create-company --name NAME [--contact-ids JSON] [--domain N] [--address N] [--city N] [--state N] [--country N] [--zip N] [--phone N] [--industry N] [--annualrevenue N] [--numberofemployees N] [--description N] [--type N]

    # Delete a company
    python3 crm_data.py delete-company --id ID

    # Search deals
    python3 crm_data.py search-deals [--dealname NAME] [--company-id ID]

    # Get a specific deal
    python3 crm_data.py get-deal --id ID

    # Create a deal
    python3 crm_data.py create-deal --dealname NAME --dealstage STAGE [--pipeline N] [--company-id ID] [--amount N] [--closedate DATE] [--description N]

    # Update deal stage
    python3 crm_data.py update-deal-stage --id ID --dealstage STAGE

    # Delete a deal
    python3 crm_data.py delete-deal --id ID

    # Search leads
    python3 crm_data.py search-leads [--full-name NAME] [--company-id ID]

    # Get a specific lead
    python3 crm_data.py get-lead --id ID

    # Create a lead
    python3 crm_data.py create-lead --full-name NAME --email EMAIL [--company-id ID] [--phone N] [--company N] [--jobtitle N] [--leadsource N] [--rating N] [--notes N]

    # Delete a lead
    python3 crm_data.py delete-lead --id ID

    # Create an engagement
    python3 crm_data.py create-engagement --engagement-type TYPE --body TEXT [--contact-ids JSON] [--company-ids JSON] [--title N] [--description N] [--phone N]

    # List engagements
    python3 crm_data.py list-engagements [--contact-ids JSON] [--company-ids JSON]

    # Delete an engagement
    python3 crm_data.py delete-engagement --id ID

    # Show raw data
    python3 crm_data.py show [--offset N] [--limit N]

    # Reset to initial state
    python3 crm_data.py reset

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


# --- Contacts ---

def cmd_search_contacts(args):
    """Search contacts by full name."""
    return _call_tool("crm_search_contacts", {"full_name": args.full_name})


def cmd_get_contact(args):
    """Get a specific contact by ID."""
    return _call_tool("crm_get_contact", {"id": args.id})


def cmd_create_contact(args):
    """Create a new contact."""
    tool_args = {"full_name": args.full_name, "email": args.email}
    if args.company_id:
        tool_args["company_id"] = args.company_id
    if args.company:
        tool_args["company"] = args.company
    if args.address:
        tool_args["address"] = args.address
    if args.city:
        tool_args["city"] = args.city
    if args.state:
        tool_args["state"] = args.state
    if args.country:
        tool_args["country"] = args.country
    if args.zip:
        tool_args["zip"] = args.zip
    if args.phone:
        tool_args["phone"] = args.phone
    if args.mobilephone:
        tool_args["mobilephone"] = args.mobilephone
    if args.jobtitle:
        tool_args["jobtitle"] = args.jobtitle
    if args.website:
        tool_args["website"] = args.website
    return _call_tool("crm_create_contact", tool_args)


def cmd_delete_contact(args):
    """Delete a contact."""
    return _call_tool("crm_delete_contact", {"id": args.id})


# --- Companies ---

def cmd_search_companies(args):
    """Search companies by name."""
    return _call_tool("crm_search_companies", {"name": args.name})


def cmd_get_company(args):
    """Get a specific company by ID."""
    return _call_tool("crm_get_company", {"id": args.id})


def cmd_create_company(args):
    """Create a new company."""
    tool_args = {"name": args.name}
    if args.contact_ids:
        tool_args["contact_ids"] = json.loads(args.contact_ids)
    if args.domain:
        tool_args["domain"] = args.domain
    if args.address:
        tool_args["address"] = args.address
    if args.city:
        tool_args["city"] = args.city
    if args.state:
        tool_args["state"] = args.state
    if args.country:
        tool_args["country"] = args.country
    if args.zip:
        tool_args["zip"] = args.zip
    if args.phone:
        tool_args["phone"] = args.phone
    if args.industry:
        tool_args["industry"] = args.industry
    if args.annualrevenue is not None:
        tool_args["annualrevenue"] = args.annualrevenue
    if args.numberofemployees is not None:
        tool_args["numberofemployees"] = args.numberofemployees
    if args.description:
        tool_args["description"] = args.description
    if args.type:
        tool_args["type"] = args.type
    return _call_tool("crm_create_company", tool_args)


def cmd_delete_company(args):
    """Delete a company."""
    return _call_tool("crm_delete_company", {"id": args.id})


# --- Deals ---

def cmd_search_deals(args):
    """Search deals by name or company."""
    tool_args = {}
    if args.dealname:
        tool_args["dealname"] = args.dealname
    if args.company_id:
        tool_args["company_id"] = args.company_id
    return _call_tool("crm_search_deals", tool_args)


def cmd_get_deal(args):
    """Get a specific deal by ID."""
    return _call_tool("crm_get_deal", {"id": args.id})


def cmd_create_deal(args):
    """Create a new deal."""
    tool_args = {"dealname": args.dealname, "dealstage": args.dealstage}
    if args.pipeline:
        tool_args["pipeline"] = args.pipeline
    if args.company_id:
        tool_args["company_id"] = args.company_id
    if args.amount is not None:
        tool_args["amount"] = args.amount
    if args.closedate:
        tool_args["closedate"] = args.closedate
    if args.description:
        tool_args["description"] = args.description
    return _call_tool("crm_create_deal", tool_args)


def cmd_update_deal_stage(args):
    """Update a deal's stage."""
    return _call_tool("crm_update_deal_stage", {
        "id": args.id,
        "dealstage": args.dealstage,
    })


def cmd_delete_deal(args):
    """Delete a deal."""
    return _call_tool("crm_delete_deal", {"id": args.id})


# --- Leads ---

def cmd_search_leads(args):
    """Search leads by name or company."""
    tool_args = {}
    if args.full_name:
        tool_args["full_name"] = args.full_name
    if args.company_id:
        tool_args["company_id"] = args.company_id
    return _call_tool("crm_search_leads", tool_args)


def cmd_get_lead(args):
    """Get a specific lead by ID."""
    return _call_tool("crm_get_lead", {"id": args.id})


def cmd_create_lead(args):
    """Create a new lead."""
    tool_args = {"full_name": args.full_name, "email": args.email}
    if args.company_id:
        tool_args["company_id"] = args.company_id
    if args.phone:
        tool_args["phone"] = args.phone
    if args.company:
        tool_args["company"] = args.company
    if args.jobtitle:
        tool_args["jobtitle"] = args.jobtitle
    if args.leadsource:
        tool_args["leadsource"] = args.leadsource
    if args.rating:
        tool_args["rating"] = args.rating
    if args.notes:
        tool_args["notes"] = args.notes
    return _call_tool("crm_create_lead", tool_args)


def cmd_delete_lead(args):
    """Delete a lead."""
    return _call_tool("crm_delete_lead", {"id": args.id})


# --- Engagements ---

def cmd_create_engagement(args):
    """Create a new engagement."""
    tool_args = {
        "engagement_type": args.engagement_type,
        "body": args.body,
    }
    if args.contact_ids:
        tool_args["contact_ids"] = json.loads(args.contact_ids)
    if args.company_ids:
        tool_args["company_ids"] = json.loads(args.company_ids)
    if args.title:
        tool_args["title"] = args.title
    if args.description:
        tool_args["description"] = args.description
    if args.phone:
        tool_args["phone"] = args.phone
    return _call_tool("crm_create_engagement", tool_args)


def cmd_list_engagements(args):
    """List engagements with optional filters."""
    tool_args = {}
    if args.contact_ids:
        tool_args["contact_ids"] = json.loads(args.contact_ids)
    if args.company_ids:
        tool_args["company_ids"] = json.loads(args.company_ids)
    return _call_tool("crm_list_engagements", tool_args)


def cmd_delete_engagement(args):
    """Delete an engagement."""
    return _call_tool("crm_delete_engagement", {"id": args.id})


# --- Utility ---

def cmd_show(args):
    """Show raw CRM data."""
    return _call_tool("crm_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


def cmd_reset(args):
    """Reset to initial state."""
    return _call_tool("crm_reset")


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="CRM Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Contacts ---

    # search-contacts
    p = sub.add_parser("search-contacts", help="Search contacts by name")
    p.add_argument("--full-name", type=str, required=True)
    p.set_defaults(func=cmd_search_contacts)

    # get-contact
    p = sub.add_parser("get-contact", help="Get a contact by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_contact)

    # create-contact
    p = sub.add_parser("create-contact", help="Create a new contact")
    p.add_argument("--full-name", type=str, required=True)
    p.add_argument("--email", type=str, required=True)
    p.add_argument("--company-id", type=str)
    p.add_argument("--company", type=str)
    p.add_argument("--address", type=str)
    p.add_argument("--city", type=str)
    p.add_argument("--state", type=str)
    p.add_argument("--country", type=str)
    p.add_argument("--zip", type=str)
    p.add_argument("--phone", type=str)
    p.add_argument("--mobilephone", type=str)
    p.add_argument("--jobtitle", type=str)
    p.add_argument("--website", type=str)
    p.set_defaults(func=cmd_create_contact)

    # delete-contact
    p = sub.add_parser("delete-contact", help="Delete a contact")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_delete_contact)

    # --- Companies ---

    # search-companies
    p = sub.add_parser("search-companies", help="Search companies by name")
    p.add_argument("--name", type=str, required=True)
    p.set_defaults(func=cmd_search_companies)

    # get-company
    p = sub.add_parser("get-company", help="Get a company by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_company)

    # create-company
    p = sub.add_parser("create-company", help="Create a new company")
    p.add_argument("--name", type=str, required=True)
    p.add_argument("--contact-ids", type=str, help="JSON array of contact IDs")
    p.add_argument("--domain", type=str)
    p.add_argument("--address", type=str)
    p.add_argument("--city", type=str)
    p.add_argument("--state", type=str)
    p.add_argument("--country", type=str)
    p.add_argument("--zip", type=str)
    p.add_argument("--phone", type=str)
    p.add_argument("--industry", type=str)
    p.add_argument("--annualrevenue", type=float)
    p.add_argument("--numberofemployees", type=int)
    p.add_argument("--description", type=str)
    p.add_argument("--type", type=str)
    p.set_defaults(func=cmd_create_company)

    # delete-company
    p = sub.add_parser("delete-company", help="Delete a company")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_delete_company)

    # --- Deals ---

    # search-deals
    p = sub.add_parser("search-deals", help="Search deals")
    p.add_argument("--dealname", type=str)
    p.add_argument("--company-id", type=str)
    p.set_defaults(func=cmd_search_deals)

    # get-deal
    p = sub.add_parser("get-deal", help="Get a deal by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_deal)

    # create-deal
    p = sub.add_parser("create-deal", help="Create a new deal")
    p.add_argument("--dealname", type=str, required=True)
    p.add_argument("--dealstage", type=str, required=True,
                   help="Stage: appointmentscheduled, qualifiedtobuy, presentationscheduled, decisionmakerboughtin, contractsent, closedwon, closedlost")
    p.add_argument("--pipeline", type=str)
    p.add_argument("--company-id", type=str)
    p.add_argument("--amount", type=float)
    p.add_argument("--closedate", type=str)
    p.add_argument("--description", type=str)
    p.set_defaults(func=cmd_create_deal)

    # update-deal-stage
    p = sub.add_parser("update-deal-stage", help="Update a deal's stage")
    p.add_argument("--id", type=str, required=True)
    p.add_argument("--dealstage", type=str, required=True)
    p.set_defaults(func=cmd_update_deal_stage)

    # delete-deal
    p = sub.add_parser("delete-deal", help="Delete a deal")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_delete_deal)

    # --- Leads ---

    # search-leads
    p = sub.add_parser("search-leads", help="Search leads")
    p.add_argument("--full-name", type=str)
    p.add_argument("--company-id", type=str)
    p.set_defaults(func=cmd_search_leads)

    # get-lead
    p = sub.add_parser("get-lead", help="Get a lead by ID")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_get_lead)

    # create-lead
    p = sub.add_parser("create-lead", help="Create a new lead")
    p.add_argument("--full-name", type=str, required=True)
    p.add_argument("--email", type=str, required=True)
    p.add_argument("--company-id", type=str)
    p.add_argument("--phone", type=str)
    p.add_argument("--company", type=str)
    p.add_argument("--jobtitle", type=str)
    p.add_argument("--leadsource", type=str)
    p.add_argument("--rating", type=str, help="hot, warm, or cold")
    p.add_argument("--notes", type=str)
    p.set_defaults(func=cmd_create_lead)

    # delete-lead
    p = sub.add_parser("delete-lead", help="Delete a lead")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_delete_lead)

    # --- Engagements ---

    # create-engagement
    p = sub.add_parser("create-engagement", help="Create a new engagement")
    p.add_argument("--engagement-type", type=str, required=True,
                   help="Type: EMAIL, CALL, or NOTE")
    p.add_argument("--body", type=str, required=True)
    p.add_argument("--contact-ids", type=str, help="JSON array of contact IDs")
    p.add_argument("--company-ids", type=str, help="JSON array of company IDs")
    p.add_argument("--title", type=str)
    p.add_argument("--description", type=str)
    p.add_argument("--phone", type=str)
    p.set_defaults(func=cmd_create_engagement)

    # list-engagements
    p = sub.add_parser("list-engagements", help="List engagements")
    p.add_argument("--contact-ids", type=str, help="JSON array of contact IDs")
    p.add_argument("--company-ids", type=str, help="JSON array of company IDs")
    p.set_defaults(func=cmd_list_engagements)

    # delete-engagement
    p = sub.add_parser("delete-engagement", help="Delete an engagement")
    p.add_argument("--id", type=str, required=True)
    p.set_defaults(func=cmd_delete_engagement)

    # --- Utility ---

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
