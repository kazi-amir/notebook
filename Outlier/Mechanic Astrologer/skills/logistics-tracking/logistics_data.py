#!/usr/bin/env python3
"""
Logistics Tracking Data Fetcher - Track packages via the Logistics Tracking MCP server

Usage:
    # Track a single package
    python3 logistics_data.py track <tracking_number> [--carrier CARRIER]

    # Detect carrier from tracking number
    python3 logistics_data.py detect <tracking_number>

    # Batch track multiple packages
    python3 logistics_data.py batch <tracking_number1> <tracking_number2> ...

    # Explain a status code
    python3 logistics_data.py status <code>

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


def track_package(tracking_number: str, carrier: str = None) -> dict:
    """Track a single package by tracking number."""
    args = {"tracking_number": tracking_number}
    if carrier:
        args["carrier"] = carrier
    return _call_tool("logistics_tracking_track_package", args)


def detect_carrier(tracking_number: str) -> dict:
    """Detect carrier from tracking number format."""
    return _call_tool("logistics_tracking_detect_carrier", {"tracking_number": tracking_number})


def batch_track(tracking_numbers: list[str]) -> dict:
    """Track multiple packages at once."""
    return _call_tool("logistics_tracking_batch_track", {"tracking_numbers": tracking_numbers})


def explain_status(status_code: str) -> dict:
    """Get human-readable explanation of a status code."""
    return _call_tool("logistics_tracking_explain_status", {"status_code": status_code})


def main():
    parser = argparse.ArgumentParser(description="Fetch logistics tracking data")
    sub = parser.add_subparsers(dest="command")

    # track
    track_p = sub.add_parser("track")
    track_p.add_argument("tracking_number", help="Tracking number")
    track_p.add_argument("--carrier", help="Carrier hint (auto-detected if omitted)")

    # detect
    detect_p = sub.add_parser("detect")
    detect_p.add_argument("tracking_number", help="Tracking number to analyze")

    # batch
    batch_p = sub.add_parser("batch")
    batch_p.add_argument("tracking_numbers", nargs="+", help="Tracking numbers (up to 40)")

    # status
    status_p = sub.add_parser("status")
    status_p.add_argument("code", help="Status code (InfoReceived, InTransit, OutForDelivery, Delivered, Exception, Returned)")

    args = parser.parse_args()

    if args.command == "track":
        result = track_package(args.tracking_number, args.carrier)
    elif args.command == "detect":
        result = detect_carrier(args.tracking_number)
    elif args.command == "batch":
        result = batch_track(args.tracking_numbers)
    elif args.command == "status":
        result = explain_status(args.code)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
