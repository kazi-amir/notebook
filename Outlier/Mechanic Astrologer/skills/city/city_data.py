#!/usr/bin/env python3
"""
City Crime Data - Look up crime rates by zip code.

Usage:
    # Get crime rate for a zip code
    python3 city_data.py get-crime-rate --zip-code 90210

    # Check API call count
    python3 city_data.py api-call-count

    # Check API call limit
    python3 city_data.py api-call-limit

    # Show raw crime data
    python3 city_data.py show

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


def cmd_get_crime_rate(args):
    """Get crime rate data for a zip code."""
    return _call_tool("city_get_crime_rate", {"zip_code": args.zip_code})


def cmd_api_call_count(args):
    """Get the current API call count."""
    return _call_tool("city_get_api_call_count")


def cmd_api_call_limit(args):
    """Get the API call limit."""
    return _call_tool("city_get_api_call_limit")


def cmd_show(args):
    """Show raw crime data."""
    return _call_tool("city_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="City Crime Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # get-crime-rate
    p = sub.add_parser("get-crime-rate", help="Get crime rate for a zip code")
    p.add_argument("--zip-code", type=str, required=True, help="5-digit zip code")
    p.set_defaults(func=cmd_get_crime_rate)

    # api-call-count
    p = sub.add_parser("api-call-count", help="Get current API call count")
    p.set_defaults(func=cmd_api_call_count)

    # api-call-limit
    p = sub.add_parser("api-call-limit", help="Get API call limit")
    p.set_defaults(func=cmd_api_call_limit)

    # show
    p = sub.add_parser("show", help="Show raw crime data")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=100)
    p.set_defaults(func=cmd_show)

    args = parser.parse_args()
    result = args.func(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
