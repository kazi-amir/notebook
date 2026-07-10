#!/usr/bin/env python3
"""
Zillow Real Estate Data - Search properties, analyze markets, calculate mortgages.

Usage:
    # Log in
    python3 zillow_data.py login --email EMAIL

    # Search properties with filters
    python3 zillow_data.py search [--location TEXT] [--city TEXT] [--state XX]
        [--zip TEXT] [--min-price N] [--max-price N] [--min-beds N] [--max-beds N]
        [--min-baths N] [--max-baths N] [--min-sqft N] [--max-sqft N]
        [--home-type TYPE] [--status STATUS] [--min-year N] [--max-hoa N]
        [--sort-by FIELD] [--sort-order ASC|DESC] [--limit N]

    # Get full property details
    python3 zillow_data.py details --id N

    # Get Zestimate valuation
    python3 zillow_data.py zestimate --id N

    # Get comparable properties
    python3 zillow_data.py comps --id N [--limit N]

    # Get market trends
    python3 zillow_data.py market [--region TEXT] [--state XX] [--limit N]

    # Get top performing markets
    python3 zillow_data.py top-markets [--metric METRIC] [--limit N]

    # Calculate mortgage payment
    python3 zillow_data.py mortgage --price N [--down-payment PCT] [--rate PCT]
        [--term YEARS] [--tax-rate PCT] [--insurance N] [--hoa N]

    # Investment analysis for a property
    python3 zillow_data.py invest-analyze --id N [--down-payment PCT] [--rate PCT]
        [--vacancy PCT] [--expense-ratio PCT]

    # Get your saved properties
    python3 zillow_data.py saved [--limit N]

    # Get your scheduled tours
    python3 zillow_data.py tours [--limit N]

    # List available locations (cities/states)
    python3 zillow_data.py locations

    # List available home types
    python3 zillow_data.py home-types

    # Get user profile
    python3 zillow_data.py profile

Output: JSON to stdout
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
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


# ==================== Subcommand Handlers ====================


def cmd_search(args):
    """Search properties with filters."""
    tool_args = {}

    if args.location:
        tool_args["location"] = args.location
    if args.city:
        tool_args["city"] = args.city
    if args.state:
        tool_args["state"] = args.state.upper()
    if args.zip:
        tool_args["zip_code"] = args.zip
    if args.min_price is not None:
        tool_args["min_price"] = args.min_price
    if args.max_price is not None:
        tool_args["max_price"] = args.max_price
    if args.min_beds is not None:
        tool_args["min_bedrooms"] = args.min_beds
    if args.max_beds is not None:
        tool_args["max_bedrooms"] = args.max_beds
    if args.min_baths is not None:
        tool_args["min_bathrooms"] = args.min_baths
    if args.max_baths is not None:
        tool_args["max_bathrooms"] = args.max_baths
    if args.min_sqft is not None:
        tool_args["min_sqft"] = args.min_sqft
    if args.max_sqft is not None:
        tool_args["max_sqft"] = args.max_sqft
    if args.home_type:
        tool_args["home_type"] = args.home_type
    if args.status:
        tool_args["property_status"] = args.status
    if args.min_year is not None:
        tool_args["min_year_built"] = args.min_year
    if args.max_hoa is not None:
        tool_args["max_hoa"] = args.max_hoa
    if args.sort_by:
        tool_args["sort_by"] = args.sort_by
    if args.sort_order:
        tool_args["sort_order"] = args.sort_order
    tool_args["limit"] = args.limit

    data = _call_tool("zillow_search_properties", tool_args)

    # Build active filters for display
    filters = {}
    if args.location:
        filters["location"] = args.location
    if args.city:
        filters["city"] = args.city
    if args.state:
        filters["state"] = args.state
    if args.zip:
        filters["zip_code"] = args.zip
    if args.min_price is not None:
        filters["min_price"] = args.min_price
    if args.max_price is not None:
        filters["max_price"] = args.max_price
    if args.min_beds is not None:
        filters["min_bedrooms"] = args.min_beds
    if args.max_beds is not None:
        filters["max_bedrooms"] = args.max_beds
    if args.home_type:
        filters["home_type"] = args.home_type
    if args.status:
        filters["property_status"] = args.status

    properties = data.get("properties", [])
    return {
        "filters": filters,
        "results_count": len(properties),
        "properties": properties,
    }


def cmd_details(args):
    """Get full property details."""
    data = _call_tool("zillow_get_property_details", {"property_id": args.id})
    return data


def cmd_zestimate(args):
    """Get Zestimate valuation data for a property."""
    data = _call_tool("zillow_get_zestimate", {"property_id": args.id})
    return data


def cmd_comps(args):
    """Get comparable/similar properties."""
    data = _call_tool("zillow_get_similar_properties", {
        "property_id": args.id,
        "limit": args.limit,
    })
    return data


def cmd_market(args):
    """Get market trends."""
    tool_args = {}
    if args.region:
        tool_args["region"] = args.region
    if args.state:
        tool_args["state"] = args.state.upper()
    tool_args["limit"] = args.limit

    data = _call_tool("zillow_get_market_trends", tool_args)
    return data


def cmd_top_markets(args):
    """Get top performing markets by metric."""
    data = _call_tool("zillow_get_top_markets", {
        "metric": args.metric,
        "limit": args.limit,
    })
    return data


def cmd_mortgage(args):
    """Calculate monthly mortgage payment with full breakdown."""
    tool_args = {
        "home_price": args.price,
        "down_payment_percent": args.down_payment,
        "interest_rate": args.rate,
        "loan_term_years": args.term,
        "property_tax_rate": args.tax_rate,
        "home_insurance_annual": args.insurance,
        "hoa_monthly": args.hoa,
    }

    # Add PMI rate if down payment < 20%
    if args.down_payment < 20:
        tool_args["pmi_rate"] = 0.5

    data = _call_tool("zillow_calculate_mortgage", tool_args)
    return data


def cmd_invest_analyze(args):
    """Run investment analysis on a property."""
    # Get property details
    prop_data = _call_tool("zillow_get_property_details", {"property_id": args.id})
    if prop_data.get("error") or prop_data.get("success") is False:
        return {"success": False, "error": f"Property with ID {args.id} not found"}

    prop = prop_data.get("property", prop_data)

    price = int(prop.get("price", 0))
    monthly_rent = int(prop.get("rent_zestimate", 0))
    annual_rent = monthly_rent * 12

    # Down payment and loan
    down_pct = args.down_payment
    down_payment = price * (down_pct / 100)
    loan = price - down_payment
    monthly_rate = (args.rate / 100) / 12
    num_payments = 360  # 30-year

    if monthly_rate > 0 and loan > 0:
        monthly_pi = loan * (monthly_rate * (1 + monthly_rate) ** num_payments) / (
            (1 + monthly_rate) ** num_payments - 1
        )
    else:
        monthly_pi = loan / num_payments if num_payments > 0 else 0

    annual_debt_service = monthly_pi * 12

    # Expenses
    vacancy_loss = annual_rent * (args.vacancy / 100)
    effective_income = annual_rent - vacancy_loss
    operating_expenses = effective_income * (args.expense_ratio / 100)
    noi = effective_income - operating_expenses

    # Metrics
    cap_rate = (noi / price * 100) if price > 0 else 0
    cash_flow = noi - annual_debt_service
    total_cash_invested = down_payment + (price * 0.03)  # ~3% closing costs
    cash_on_cash = (cash_flow / total_cash_invested * 100) if total_cash_invested > 0 else 0
    grm = (price / annual_rent) if annual_rent > 0 else 0
    one_pct_rule = monthly_rent >= (price * 0.01)
    dscr = (noi / annual_debt_service) if annual_debt_service > 0 else 0

    return {
        "success": True,
        "property": {
            "id": prop.get("id"),
            "address": prop.get("address", ""),
            "city": prop.get("city", ""),
            "state": prop.get("state", ""),
            "price": price,
            "rent_zestimate": monthly_rent,
        },
        "assumptions": {
            "down_payment_percent": down_pct,
            "interest_rate": args.rate,
            "vacancy_rate": args.vacancy,
            "expense_ratio": args.expense_ratio,
        },
        "financials": {
            "annual_gross_rent": annual_rent,
            "vacancy_loss": round(vacancy_loss, 2),
            "effective_income": round(effective_income, 2),
            "operating_expenses": round(operating_expenses, 2),
            "net_operating_income": round(noi, 2),
            "annual_debt_service": round(annual_debt_service, 2),
            "annual_cash_flow": round(cash_flow, 2),
            "monthly_cash_flow": round(cash_flow / 12, 2),
        },
        "metrics": {
            "cap_rate": round(cap_rate, 2),
            "cash_on_cash_return": round(cash_on_cash, 2),
            "gross_rent_multiplier": round(grm, 1),
            "meets_1_pct_rule": one_pct_rule,
            "dscr": round(dscr, 2),
        },
    }


def cmd_saved(args):
    """Get saved properties for the current user."""
    data = _call_tool("zillow_get_saved_properties", {"limit": args.limit})
    return data


def cmd_tours(args):
    """Get scheduled tours for the current user."""
    data = _call_tool("zillow_get_scheduled_tours", {"limit": args.limit})
    return data


def cmd_locations(args):
    """Get all available cities and states."""
    data = _call_tool("zillow_get_available_locations")
    return data


def cmd_home_types(args):
    """Get all available home types."""
    data = _call_tool("zillow_get_home_types")
    return data


def cmd_profile(args):
    """Get user profile."""
    data = _call_tool("zillow_get_current_user")
    return data


def login(email):
    """Log in to Zillow with your email."""
    return _call_tool("zillow_login", {"email": email})


# ==================== CLI ====================


def main():
    parser = argparse.ArgumentParser(description="Zillow Real Estate Data")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # login
    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # search
    p = sub.add_parser("search", help="Search properties with filters")
    p.add_argument("--location", help="General location search (city, state, or zip)")
    p.add_argument("--city", help="Filter by city name")
    p.add_argument("--state", help="Filter by state (2-letter code)")
    p.add_argument("--zip", help="Filter by ZIP code")
    p.add_argument("--min-price", type=int, help="Minimum price")
    p.add_argument("--max-price", type=int, help="Maximum price")
    p.add_argument("--min-beds", type=int, help="Minimum bedrooms")
    p.add_argument("--max-beds", type=int, help="Maximum bedrooms")
    p.add_argument("--min-baths", type=float, help="Minimum bathrooms")
    p.add_argument("--max-baths", type=float, help="Maximum bathrooms")
    p.add_argument("--min-sqft", type=int, help="Minimum square footage")
    p.add_argument("--max-sqft", type=int, help="Maximum square footage")
    p.add_argument("--home-type", help="Home type (Single Family, Condo, Townhouse, Multi-Family, Land)")
    p.add_argument("--status", help="Property status (For Sale, For Rent, Sold, Pending)")
    p.add_argument("--min-year", type=int, help="Minimum year built")
    p.add_argument("--max-hoa", type=int, help="Maximum HOA fee/month")
    p.add_argument("--sort-by", default="days_on_zillow", help="Sort by field")
    p.add_argument("--sort-order", default="ASC", help="ASC or DESC")
    p.add_argument("--limit", type=int, default=20, help="Max results (default 20)")

    # details
    p = sub.add_parser("details", help="Get property details")
    p.add_argument("--id", type=int, required=True, help="Property ID")

    # zestimate
    p = sub.add_parser("zestimate", help="Get Zestimate valuation")
    p.add_argument("--id", type=int, required=True, help="Property ID")

    # comps
    p = sub.add_parser("comps", help="Get comparable properties")
    p.add_argument("--id", type=int, required=True, help="Property ID")
    p.add_argument("--limit", type=int, default=10, help="Max results (default 10)")

    # market
    p = sub.add_parser("market", help="Get market trends")
    p.add_argument("--region", help="City or metro area name")
    p.add_argument("--state", help="State filter (2-letter code)")
    p.add_argument("--limit", type=int, default=20, help="Max results (default 20)")

    # top-markets
    p = sub.add_parser("top-markets", help="Get top performing markets")
    p.add_argument("--metric", default="price_change_yoy",
                   help="Metric (median_home_price, price_change_yoy, inventory, homes_sold)")
    p.add_argument("--limit", type=int, default=10, help="Max results (default 10)")

    # mortgage
    p = sub.add_parser("mortgage", help="Calculate mortgage payment")
    p.add_argument("--price", type=int, required=True, help="Home price")
    p.add_argument("--down-payment", type=float, default=20.0, help="Down payment %% (default 20)")
    p.add_argument("--rate", type=float, default=6.5, help="Interest rate %% (default 6.5)")
    p.add_argument("--term", type=int, default=30, help="Loan term years (default 30)")
    p.add_argument("--tax-rate", type=float, default=1.1, help="Property tax rate %% (default 1.1)")
    p.add_argument("--insurance", type=int, default=1200, help="Annual insurance (default $1200)")
    p.add_argument("--hoa", type=int, default=0, help="Monthly HOA (default $0)")

    # invest-analyze
    p = sub.add_parser("invest-analyze", help="Investment analysis for a property")
    p.add_argument("--id", type=int, required=True, help="Property ID")
    p.add_argument("--down-payment", type=float, default=20.0, help="Down payment %% (default 20)")
    p.add_argument("--rate", type=float, default=6.5, help="Interest rate %% (default 6.5)")
    p.add_argument("--vacancy", type=float, default=8.0, help="Vacancy rate %% (default 8)")
    p.add_argument("--expense-ratio", type=float, default=50.0, help="Expense ratio %% (default 50)")

    # saved
    p = sub.add_parser("saved", help="Get your saved properties")
    p.add_argument("--limit", type=int, default=50, help="Max results (default 50)")

    # tours
    p = sub.add_parser("tours", help="Get your scheduled tours")
    p.add_argument("--limit", type=int, default=20, help="Max results (default 20)")

    # locations
    sub.add_parser("locations", help="List available cities and states")

    # home-types
    sub.add_parser("home-types", help="List available home types")

    # profile
    sub.add_parser("profile", help="Get user profile")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    handlers = {
        "login": lambda a: login(a.email),
        "search": cmd_search,
        "details": cmd_details,
        "zestimate": cmd_zestimate,
        "comps": cmd_comps,
        "market": cmd_market,
        "top-markets": cmd_top_markets,
        "mortgage": cmd_mortgage,
        "invest-analyze": cmd_invest_analyze,
        "saved": cmd_saved,
        "tours": cmd_tours,
        "locations": cmd_locations,
        "home-types": cmd_home_types,
        "profile": cmd_profile,
    }

    result = handlers[args.command](args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
