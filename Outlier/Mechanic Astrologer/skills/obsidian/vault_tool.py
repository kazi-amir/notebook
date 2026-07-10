#!/usr/bin/env python3
"""
Obsidian Vault Tool - MCP API client for Obsidian vault access.

Calls the @mauricio.wolff/mcp-obsidian MCP server via the agent-environment
/step API.

Usage:
    python3 vault_tool.py login --email EMAIL            # Log in with your email
    python3 vault_tool.py info                          # Show vault path and stats
    python3 vault_tool.py list [folder]                 # List notes (optionally in a folder)
    python3 vault_tool.py search "query"                # Search note names
    python3 vault_tool.py search-content "query"        # Full-text search inside notes
    python3 vault_tool.py read "path/to/note"           # Read a note's content
    python3 vault_tool.py create "path/to/note" --content "..."  # Create a new note
    python3 vault_tool.py move "old/path" "new/path"    # Move/rename with wikilink updates
    python3 vault_tool.py delete "path/to/note"         # Delete a note
    python3 vault_tool.py tags                          # List all tags used in the vault
    python3 vault_tool.py links "path/to/note"          # Show outgoing wikilinks from a note
    python3 vault_tool.py backlinks "path/to/note"      # Show notes that link to a given note
    python3 vault_tool.py recent [--days N]             # Show recently modified notes
    python3 vault_tool.py tree                          # Show vault folder structure

All note paths are relative to the vault root and omit the .md extension.
Output: JSON to stdout.
"""

import argparse
import json
import os
import re
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


# ---- Wikilink / Tag Parsing Utilities ----

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def _extract_wikilinks(content: str) -> list:
    """Extract all wikilink targets from markdown content."""
    return WIKILINK_RE.findall(content)


def _extract_tags(content: str) -> list:
    """Extract all #tags from markdown content."""
    return re.findall(r"(?:^|\s)#([a-zA-Z][a-zA-Z0-9_/-]*)", content)


def _ensure_md_ext(path: str) -> str:
    """Ensure a note path has .md extension."""
    if not path.endswith(".md"):
        return path + ".md"
    return path


def _strip_md_ext(path: str) -> str:
    """Strip .md extension from a note path for display."""
    if path.endswith(".md"):
        return path[:-3]
    return path


# ---- Commands ----


def cmd_info():
    """Show vault info and stats by listing the root directory."""
    listing = _call_tool("obsidian_list", {})
    if "error" in listing:
        return listing

    notes = listing.get("notes", [])
    directories = listing.get("directories", [])

    return {
        "total_notes": len(notes),
        "total_folders": len(directories),
        "folders": directories,
        "root_notes": [n["path"] if isinstance(n, dict) else n for n in notes],
    }


def cmd_list(folder=None):
    """List notes, optionally filtered to a folder."""
    args = {"folder": folder} if folder else {}
    result = _call_tool("obsidian_list", args)
    if "error" in result:
        return result

    notes = result.get("notes", [])
    directories = result.get("directories", [])

    return {
        "notes": notes,
        "directories": directories,
        "count": len(notes),
    }


def cmd_search(query):
    """Search note names (case-insensitive)."""
    result = _call_tool("obsidian_search", {
        "query": query,
    })
    if "error" in result:
        return result

    # The search results may use abbreviated keys (p, t, ex, mc)
    raw_results = result if isinstance(result, list) else result.get("results", result.get("r", []))
    if not isinstance(raw_results, list):
        raw_results = []

    matches = []
    for r in raw_results:
        path = r.get("path", r.get("p", ""))
        title = r.get("title", r.get("t", ""))
        matches.append({
            "path": _strip_md_ext(path),
            "title": title,
        })

    return {"query": query, "matches": matches, "count": len(matches)}


def cmd_search_content(query):
    """Full-text search inside notes."""
    result = _call_tool("obsidian_search_content", {
        "query": query,
    })
    if "error" in result:
        return result

    raw_results = result if isinstance(result, list) else result.get("results", result.get("r", []))
    if not isinstance(raw_results, list):
        raw_results = []

    results = []
    for r in raw_results:
        path = r.get("path", r.get("p", ""))
        excerpt = r.get("excerpt", r.get("ex", ""))
        match_count = r.get("matchCount", r.get("mc", 0))
        results.append({
            "path": _strip_md_ext(path),
            "excerpt": excerpt,
            "match_count": match_count,
        })

    total = sum(r["match_count"] for r in results)
    return {"query": query, "results": results, "total_matches": total}


def cmd_read(note_path):
    """Read a note's full content."""
    filepath = _ensure_md_ext(note_path)
    result = _call_tool("obsidian_read", {"note_path": filepath})
    if "error" in result:
        return result

    content = result.get("content", result.get("c", ""))
    return {
        "path": _strip_md_ext(note_path),
        "content": content,
        "size_bytes": len(content.encode("utf-8")),
        "lines": content.count("\n") + 1,
    }


def cmd_create(note_path, content=""):
    """Create a new note."""
    filepath = _ensure_md_ext(note_path)
    # Interpret escaped newlines from shell arguments
    content = content.replace("\\n", "\n")

    result = _call_tool("obsidian_create", {
        "note_path": filepath,
        "content": content,
    })
    if "error" in result:
        return result

    return {
        "success": True,
        "path": _strip_md_ext(note_path),
        "size_bytes": len(content.encode("utf-8")),
    }


def cmd_move(old_path, new_path):
    """Move/rename a note."""
    old_filepath = _ensure_md_ext(old_path)
    new_filepath = _ensure_md_ext(new_path)

    result = _call_tool("obsidian_move", {
        "old_path": old_filepath,
        "new_path": new_filepath,
    })
    if "error" in result:
        return result

    return {
        "success": True,
        "old_path": _strip_md_ext(old_path),
        "new_path": _strip_md_ext(new_path),
    }


def cmd_delete(note_path):
    """Delete a note."""
    filepath = _ensure_md_ext(note_path)
    result = _call_tool("obsidian_delete", {
        "note_path": filepath,
    })
    if "error" in result:
        return result

    return {"success": True, "deleted": _strip_md_ext(note_path)}


def cmd_tags():
    """List all tags used across the vault with counts.

    Fetches the vault file listing, then reads each note to parse tags.
    """
    # Get all files in the vault
    listing = _call_tool("obsidian_list", {})
    if "error" in listing:
        return listing

    notes = listing.get("notes", [])
    note_paths = [n["path"] if isinstance(n, dict) else n for n in notes]

    # Read each note individually to extract tags
    tag_counts = {}
    for note_path in note_paths:
        note_result = _call_tool("obsidian_read", {"note_path": note_path})
        if "error" in note_result:
            continue
        content = note_result.get("content", note_result.get("c", ""))
        if content:
            for tag in _extract_tags(content):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])
    return {
        "tags": [{"tag": t, "count": c} for t, c in sorted_tags],
        "total_unique_tags": len(sorted_tags),
    }


def cmd_links(note_path):
    """Show outgoing wikilinks from a note."""
    filepath = _ensure_md_ext(note_path)
    result = _call_tool("obsidian_read", {"note_path": filepath})
    if "error" in result:
        return result

    content = result.get("content", result.get("c", ""))
    links = _extract_wikilinks(content)

    return {
        "path": _strip_md_ext(note_path),
        "outgoing_links": links,
        "count": len(links),
    }


def cmd_backlinks(note_path):
    """Find all notes that link to the given note via search."""
    note_name = note_path.split("/")[-1].removesuffix(".md")

    # Search for the note name across all content
    result = _call_tool("obsidian_search_content", {
        "query": f"[[{note_name}]]",
    })
    if "error" in result:
        return result

    raw_results = result if isinstance(result, list) else result.get("results", result.get("r", []))
    if not isinstance(raw_results, list):
        raw_results = []

    backlinks = []
    for r in raw_results:
        path = r.get("path", r.get("p", ""))
        # Exclude the note itself from backlinks
        if _strip_md_ext(path) == _strip_md_ext(note_path):
            continue
        backlinks.append({
            "path": _strip_md_ext(path),
            "link_text": note_name,
        })

    return {
        "target": _strip_md_ext(note_path),
        "backlinks": backlinks,
        "count": len(backlinks),
    }


def cmd_recent(days=7):
    """Show recently modified notes using obsidian_recent."""
    result = _call_tool("obsidian_recent", {"days": days})
    if "error" in result:
        return result

    # The server already returns the right structure; normalize paths
    notes = result.get("notes", [])
    for note in notes:
        if "path" in note:
            note["path"] = _strip_md_ext(note["path"])

    return {"days": days, "notes": notes, "count": len(notes)}


def cmd_tree():
    """Show vault folder structure as a tree.

    Recursively lists directories to build the tree.
    """
    def _list_dir(path):
        args = {"folder": path} if path else {}
        result = _call_tool("obsidian_list", args)
        if "error" in result:
            return [], []
        dirs = result.get("directories", [])
        notes = result.get("notes", [])
        note_paths = [n["path"] if isinstance(n, dict) else n for n in notes]
        return dirs, note_paths

    def _build_tree(path, prefix=""):
        dirs, notes = _list_dir(path)
        tree = {}
        for d in sorted(dirs):
            if d.startswith("."):
                continue
            subpath = f"{path}/{d}" if path else d
            tree[d] = _build_tree_node(subpath)
        for n in sorted(notes):
            tree[n] = None  # leaf node
        return tree

    def _build_tree_node(path):
        dirs, notes = _list_dir(path)
        node = {}
        for d in sorted(dirs):
            if d.startswith("."):
                continue
            subpath = f"{path}/{d}"
            node[d] = _build_tree_node(subpath)
        for n in sorted(notes):
            node[n] = None
        return node

    tree = _build_tree("")

    def format_tree(node, prefix=""):
        lines = []
        items = sorted(node.items(), key=lambda x: (x[1] is not None, x[0]))
        for i, (name, children) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
            display_name = name.removesuffix(".md") if children is None else name + "/"
            lines.append(prefix + connector + display_name)
            if children is not None:
                extension = "    " if is_last else "\u2502   "
                lines.extend(format_tree(children, prefix + extension))
        return lines

    tree_lines = ["vault/"] + format_tree(tree)
    return {"tree": "\n".join(tree_lines)}


def login(email):
    """Log in to Obsidian with your email."""
    return _call_tool("obsidian_login", {"email": email})


# ---- Main ----


def main():
    parser = argparse.ArgumentParser(description="Obsidian Vault Tool")
    sub = parser.add_subparsers(dest="command")

    login_p = sub.add_parser("login", help="Log in with your email")
    login_p.add_argument("--email", type=str, required=True)

    sub.add_parser("info")

    list_p = sub.add_parser("list")
    list_p.add_argument("folder", nargs="?", help="Folder to list (optional)")

    search_p = sub.add_parser("search")
    search_p.add_argument("query", help="Search query for note names")

    search_content_p = sub.add_parser("search-content")
    search_content_p.add_argument("query", help="Search query for note content")

    read_p = sub.add_parser("read")
    read_p.add_argument("note", help="Note path (e.g., 'Personal/Shopping List')")

    create_p = sub.add_parser("create")
    create_p.add_argument("note", help="Note path to create")
    create_p.add_argument("--content", default="", help="Initial content")

    move_p = sub.add_parser("move")
    move_p.add_argument("old", help="Current note path")
    move_p.add_argument("new", help="New note path")

    delete_p = sub.add_parser("delete")
    delete_p.add_argument("note", help="Note path to delete")

    sub.add_parser("tags")

    links_p = sub.add_parser("links")
    links_p.add_argument("note", help="Note path")

    backlinks_p = sub.add_parser("backlinks")
    backlinks_p.add_argument("note", help="Note path")

    recent_p = sub.add_parser("recent")
    recent_p.add_argument("--days", type=int, default=7, help="Days to look back")

    sub.add_parser("tree")

    args = parser.parse_args()

    commands = {
        "login": lambda: login(args.email),
        "info": cmd_info,
        "list": lambda: cmd_list(args.folder),
        "search": lambda: cmd_search(args.query),
        "search-content": lambda: cmd_search_content(args.query),
        "read": lambda: cmd_read(args.note),
        "create": lambda: cmd_create(args.note, args.content),
        "move": lambda: cmd_move(args.old, args.new),
        "delete": lambda: cmd_delete(args.note),
        "tags": cmd_tags,
        "links": lambda: cmd_links(args.note),
        "backlinks": lambda: cmd_backlinks(args.note),
        "recent": lambda: cmd_recent(args.days),
        "tree": cmd_tree,
    }

    if args.command in commands:
        result = commands[args.command]()
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
