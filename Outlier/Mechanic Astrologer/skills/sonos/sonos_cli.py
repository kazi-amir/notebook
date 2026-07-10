#!/usr/bin/env python3
"""
Sonos CLI - Control Sonos speakers via the Sonos MCP server

Usage:
    python3 sonos_cli.py login --email EMAIL
    python3 sonos_cli.py discover
    python3 sonos_cli.py status --name "Living Room"
    python3 sonos_cli.py play --name "Kitchen"
    python3 sonos_cli.py pause --name "Kitchen"
    python3 sonos_cli.py stop --name "Kitchen"
    python3 sonos_cli.py next --name "Kitchen"
    python3 sonos_cli.py prev --name "Kitchen"
    python3 sonos_cli.py volume get --name "Living Room"
    python3 sonos_cli.py volume set 40 --name "Living Room"
    python3 sonos_cli.py group status
    python3 sonos_cli.py group join --name "Kitchen" --to "Living Room"
    python3 sonos_cli.py group unjoin --name "Kitchen"
    python3 sonos_cli.py group party --to "Living Room"
    python3 sonos_cli.py group solo --name "Kitchen"
    python3 sonos_cli.py favorites list
    python3 sonos_cli.py favorites open --index 1 --name "Living Room"
    python3 sonos_cli.py queue list --name "Living Room"
    python3 sonos_cli.py queue clear --name "Living Room"

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


def login(email):
    """Log in to Sonos with your email."""
    return _call_tool("sonos_login", {"email": email})


def main():
    parser = argparse.ArgumentParser(description="Sonos speaker control")
    sub = parser.add_subparsers(dest="command")

    # login
    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    # discover
    sub.add_parser("discover")

    # status / now
    for cmd in ["status", "now"]:
        p = sub.add_parser(cmd)
        p.add_argument("--name", required=True, help="Speaker/room name")

    # play / pause / stop / next / prev
    for cmd in ["play", "pause", "stop", "next", "prev"]:
        p = sub.add_parser(cmd)
        p.add_argument("--name", required=True, help="Speaker/room name")

    # volume
    volume_p = sub.add_parser("volume")
    volume_sub = volume_p.add_subparsers(dest="volume_action")
    vol_get = volume_sub.add_parser("get")
    vol_get.add_argument("--name", required=True)
    vol_set = volume_sub.add_parser("set")
    vol_set.add_argument("level", type=int, help="Volume level (0-100)")
    vol_set.add_argument("--name", required=True)

    # group
    group_p = sub.add_parser("group")
    group_sub = group_p.add_subparsers(dest="group_action")
    group_sub.add_parser("status")
    gj = group_sub.add_parser("join")
    gj.add_argument("--name", required=True)
    gj.add_argument("--to", required=True)
    gu = group_sub.add_parser("unjoin")
    gu.add_argument("--name", required=True)
    gp = group_sub.add_parser("party")
    gp.add_argument("--to", required=True)
    gs = group_sub.add_parser("solo")
    gs.add_argument("--name", required=True)

    # favorites
    fav_p = sub.add_parser("favorites")
    fav_sub = fav_p.add_subparsers(dest="favorites_action")
    fav_sub.add_parser("list")
    fo = fav_sub.add_parser("open")
    fo.add_argument("--index", type=int, required=True, help="Favorite index")
    fo.add_argument("--name", required=True)

    # queue
    queue_p = sub.add_parser("queue")
    queue_sub = queue_p.add_subparsers(dest="queue_action")
    ql = queue_sub.add_parser("list")
    ql.add_argument("--name", required=True)
    qc = queue_sub.add_parser("clear")
    qc.add_argument("--name", required=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Map subcommands to MCP tool calls
    if args.command == "login":
        result = login(args.email)
    elif args.command == "discover":
        result = _call_tool("sonos_discover_speakers")
    elif args.command in ("status", "now"):
        result = _call_tool("sonos_get_speaker_status", {"name": args.name})
    elif args.command == "play":
        result = _call_tool("sonos_play", {"name": args.name})
    elif args.command == "pause":
        result = _call_tool("sonos_pause", {"name": args.name})
    elif args.command == "stop":
        result = _call_tool("sonos_stop", {"name": args.name})
    elif args.command == "next":
        result = _call_tool("sonos_next_track", {"name": args.name})
    elif args.command == "prev":
        result = _call_tool("sonos_previous_track", {"name": args.name})
    elif args.command == "volume":
        if args.volume_action == "get":
            result = _call_tool("sonos_get_volume", {"name": args.name})
        elif args.volume_action == "set":
            result = _call_tool("sonos_set_volume", {"name": args.name, "level": args.level})
        else:
            volume_p.print_help()
            sys.exit(1)
    elif args.command == "group":
        if args.group_action == "status":
            result = _call_tool("sonos_get_groups")
        elif args.group_action == "join":
            result = _call_tool("sonos_join_group", {"name": args.name, "to": getattr(args, "to")})
        elif args.group_action == "unjoin":
            result = _call_tool("sonos_unjoin_group", {"name": args.name})
        elif args.group_action == "party":
            result = _call_tool("sonos_party_mode", {"to": getattr(args, "to")})
        elif args.group_action == "solo":
            result = _call_tool("sonos_solo_speaker", {"name": args.name})
        else:
            group_p.print_help()
            sys.exit(1)
    elif args.command == "favorites":
        if args.favorites_action == "list":
            result = _call_tool("sonos_list_favorites")
        elif args.favorites_action == "open":
            result = _call_tool("sonos_play_favorite", {"index": args.index, "name": args.name})
        else:
            fav_p.print_help()
            sys.exit(1)
    elif args.command == "queue":
        if args.queue_action == "list":
            result = _call_tool("sonos_get_queue", {"name": args.name})
        elif args.queue_action == "clear":
            result = _call_tool("sonos_clear_queue", {"name": args.name})
        else:
            queue_p.print_help()
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
