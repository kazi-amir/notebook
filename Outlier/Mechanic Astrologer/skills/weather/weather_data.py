#!/usr/bin/env python3
"""
Weather Data - Check forecasts, history, alerts, air quality, astronomy, and sports events.

Usage:
    python3 weather_data.py search-location --city CITY [--country-code CC]
    python3 weather_data.py forecast --lat-long LAT,LON [--date DATE]
        [--aqi yes/no] [--alerts yes/no]
    python3 weather_data.py history --lat-long LAT,LON --date DATE
    python3 weather_data.py alerts --query QUERY
    python3 weather_data.py air-quality --query QUERY
    python3 weather_data.py astronomy --query QUERY [--date DATE]
    python3 weather_data.py timezone --query QUERY
    python3 weather_data.py sports --query QUERY
    python3 weather_data.py show

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


def cmd_search_location(args):
    """Search for a city's latitude and longitude."""
    return _call_tool("weather_search_lat_long", {
        "ascii_city": args.city,
        "two_letter_country_code": args.country_code,
    })


def cmd_forecast(args):
    """Get weather forecast for a location."""
    tool_args = {
        "lat_long": args.lat_long,
        "date": args.date,
    }
    if args.aqi:
        tool_args["aqi"] = args.aqi
    if args.alerts:
        tool_args["alerts"] = args.alerts
    return _call_tool("weather_forecast_future", tool_args)


def cmd_history(args):
    """Get historical weather for a specific date."""
    tool_args = {
        "lat_long": args.lat_long,
        "date": args.date,
    }
    return _call_tool("weather_history", tool_args)


def cmd_alerts(args):
    """Get weather alerts for a location."""
    return _call_tool("weather_alerts", {"q": args.query})


def cmd_air_quality(args):
    """Get air quality data for a location."""
    return _call_tool("weather_airquality", {"q": args.query})


def cmd_astronomy(args):
    """Get astronomy data (sunrise, sunset, moon phase) for a location."""
    return _call_tool("weather_astronomy", {
        "q": args.query,
        "dt": args.date,
    })


def cmd_timezone(args):
    """Get timezone info for a location."""
    return _call_tool("weather_timezone", {"q": args.query})


def cmd_sports(args):
    """Get sports events near a location."""
    return _call_tool("weather_sports", {"q": args.query})


# --- Utility ---

def cmd_show(args):
    """Show raw weather data."""
    return _call_tool("weather_show_data", {
        "offset": args.offset,
        "limit": args.limit,
    })


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(description="Weather Data")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- Location Search ---

    # search-location
    p = sub.add_parser("search-location", help="Search for a city's coordinates")
    p.add_argument("--city", type=str, required=True, help="City name (ASCII)")
    p.add_argument("--country-code", type=str, required=True, help="Two-letter country code (e.g. GB, US)")
    p.set_defaults(func=cmd_search_location)

    # --- Forecast ---

    # forecast
    p = sub.add_parser("forecast", help="Get weather forecast")
    p.add_argument("--lat-long", type=str, required=True, help="Coordinates as 'lat,lon'")
    p.add_argument("--date", type=str, required=True, help="Date (YYYY-MM-DD)")
    p.add_argument("--aqi", type=str, help="Include air quality index (yes/no)")
    p.add_argument("--alerts", type=str, help="Include alerts (yes/no)")
    p.set_defaults(func=cmd_forecast)

    # --- Weather History ---

    # history
    p = sub.add_parser("history", help="Get historical weather")
    p.add_argument("--lat-long", type=str, required=True, help="Coordinates as 'lat,lon'")
    p.add_argument("--date", type=str, required=True, help="Date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_history)

    # --- Alerts ---

    # alerts
    p = sub.add_parser("alerts", help="Get weather alerts")
    p.add_argument("--query", type=str, required=True, help="Location query (city name)")
    p.set_defaults(func=cmd_alerts)

    # --- Air Quality ---

    # air-quality
    p = sub.add_parser("air-quality", help="Get air quality data")
    p.add_argument("--query", type=str, required=True, help="Location query (city name)")
    p.set_defaults(func=cmd_air_quality)

    # --- Astronomy ---

    # astronomy
    p = sub.add_parser("astronomy", help="Get astronomy data")
    p.add_argument("--query", type=str, required=True, help="Location query (city name)")
    p.add_argument("--date", type=str, required=True, help="Date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_astronomy)

    # --- Timezone ---

    # timezone
    p = sub.add_parser("timezone", help="Get timezone info")
    p.add_argument("--query", type=str, required=True, help="Location query (city name)")
    p.set_defaults(func=cmd_timezone)

    # --- Sports Events ---

    # sports
    p = sub.add_parser("sports", help="Get sports events")
    p.add_argument("--query", type=str, required=True, help="Location query (city name)")
    p.set_defaults(func=cmd_sports)

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
