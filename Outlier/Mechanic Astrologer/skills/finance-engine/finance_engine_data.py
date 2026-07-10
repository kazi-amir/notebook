#!/usr/bin/env python3
"""
Finance Engine Data Fetcher - Look up stock tickers, quotes, price history, and sector leaders
via the Finance Engine MCP server

Usage:
    # Get ticker info
    python3 finance_engine_data.py get-ticker --symbol AAPL

    # Search company quotes
    python3 finance_engine_data.py search-quotes --query "Apple"

    # Get price history
    python3 finance_engine_data.py price-history --symbol AAPL --period 1y --interval 1d

    # Get sector leaders
    python3 finance_engine_data.py get-top --sector "Technology" --top-type top_companies --top-n 10

    # Show raw data
    python3 finance_engine_data.py show

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


def cmd_get_ticker(args):
    """Get detailed ticker information for a stock symbol."""
    return _call_tool("finance_engine_get_ticker_info", {"symbol": args.symbol})


def cmd_search_quotes(args):
    """Search for company stock quotes."""
    return _call_tool("finance_engine_search_quotes", {"query": args.query})


def cmd_price_history(args):
    """Get historical price data for a ticker."""
    tool_args = {"symbol": args.symbol}
    if args.period:
        tool_args["period"] = args.period
    if args.interval:
        tool_args["interval"] = args.interval
    return _call_tool("finance_engine_get_price_history", tool_args)


def cmd_get_top(args):
    """Get top companies, ETFs, or mutual funds by sector."""
    tool_args = {
        "sector": args.sector,
        "top_type": args.top_type,
    }
    if args.top_n is not None:
        tool_args["top_n"] = args.top_n
    return _call_tool("finance_engine_get_top", tool_args)


def cmd_show(args):
    """Show raw finance data."""
    return _call_tool("finance_engine_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ---- Main ----


def main():
    parser = argparse.ArgumentParser(
        description="Look up stock tickers, quotes, price history, and sector leaders"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # get-ticker
    gt_p = sub.add_parser("get-ticker", help="Get detailed ticker info")
    gt_p.add_argument("--symbol", required=True, help="Stock ticker symbol (e.g., AAPL)")
    gt_p.set_defaults(func=cmd_get_ticker)

    # search-quotes
    sq_p = sub.add_parser("search-quotes", help="Search company stock quotes")
    sq_p.add_argument("--query", required=True, help="Company name or keyword to search")
    sq_p.set_defaults(func=cmd_search_quotes)

    # price-history
    ph_p = sub.add_parser("price-history", help="Get historical price data")
    ph_p.add_argument("--symbol", required=True, help="Stock ticker symbol (e.g., AAPL)")
    ph_p.add_argument(
        "--period",
        choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        default=None,
        help="Time period",
    )
    ph_p.add_argument(
        "--interval",
        choices=["1d", "5d", "1wk", "1mo", "3mo"],
        default=None,
        help="Data interval",
    )
    ph_p.set_defaults(func=cmd_price_history)

    # get-top
    top_p = sub.add_parser("get-top", help="Get sector leaders")
    top_p.add_argument("--sector", required=True, help="Sector name (e.g., Technology, Healthcare)")
    top_p.add_argument(
        "--top-type",
        required=True,
        choices=[
            "top_etfs",
            "top_mutual_funds",
            "top_companies",
            "top_growth_companies",
            "top_performing_companies",
        ],
        help="Type of ranking",
    )
    top_p.add_argument("--top-n", type=int, default=None, help="Number of results to return")
    top_p.set_defaults(func=cmd_get_top)

    # show
    show_p = sub.add_parser("show", help="Show raw finance data")
    show_p.add_argument("--offset", type=int, default=0)
    show_p.add_argument("--limit", type=int, default=100)
    show_p.set_defaults(func=cmd_show)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
