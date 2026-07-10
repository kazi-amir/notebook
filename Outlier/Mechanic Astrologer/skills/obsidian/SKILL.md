---
name: obsidian
description: Work with Obsidian vaults (plain Markdown notes). Search notes, read content, create/edit/move/delete notes, explore tags and wikilinks. Use when the user asks about their notes, wants to find information in their vault, create new notes, or organize their knowledge base.
---

# Obsidian

Work with the user's Obsidian vault — a folder of plain Markdown notes with wikilinks.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/vault_tool.py login --email your@email.com
```

## Vault Structure

An Obsidian vault is a normal folder on disk:
- **Notes**: `*.md` (plain Markdown with `[[wikilinks]]`)
- **Config**: `.obsidian/` (workspace + plugin settings; don't modify)
- **Folders**: `Daily Notes/`, `Personal/`, `Projects/`, `Reference/`, `Templates/`
- **Dashboard**: `Home.md` (the vault's landing page with links to key areas)

## Using the Vault Tool

Use `vault_tool.py` to interact with the vault. All output is JSON.

### Discover the vault

```bash
# Show vault path, stats, and folder structure
python3 {baseDir}/vault_tool.py info

# Show folder tree
python3 {baseDir}/vault_tool.py tree
```

Always run `info` first to understand the vault layout before searching or creating notes.

### Search for notes

```bash
# Search by note name
python3 {baseDir}/vault_tool.py search "shopping"

# Full-text search inside notes (shows matching lines with context)
python3 {baseDir}/vault_tool.py search-content "budget"
```

### Read notes

```bash
# Read a specific note (path relative to vault root, no .md extension needed)
python3 {baseDir}/vault_tool.py read "Home"
python3 {baseDir}/vault_tool.py read "Personal/Shopping List"
python3 {baseDir}/vault_tool.py read "Daily Notes/2026-01-17"
```

### List notes

```bash
# List all notes in the vault
python3 {baseDir}/vault_tool.py list

# List notes in a specific folder
python3 {baseDir}/vault_tool.py list "Personal"
python3 {baseDir}/vault_tool.py list "Daily Notes"
```

### Create notes

```bash
# Create a new note with content
python3 {baseDir}/vault_tool.py create "Personal/New Note" --content "# My Note\n\nContent here."

# Create in a new folder (folder is created automatically)
python3 {baseDir}/vault_tool.py create "Ideas/Project Brainstorm" --content "# Brainstorm\n\n- Idea 1"
```

### Move/rename notes

```bash
# Move a note (automatically updates all [[wikilinks]] across the vault)
python3 {baseDir}/vault_tool.py move "Personal/Old Name" "Personal/New Name"

# Move to a different folder
python3 {baseDir}/vault_tool.py move "Personal/Note" "Projects/Note"
```

This is the main advantage over manual `mv` — wikilinks in other notes are automatically updated.

### Delete notes

```bash
python3 {baseDir}/vault_tool.py delete "Personal/Old Note"
```

### Explore connections

```bash
# List all tags used in the vault
python3 {baseDir}/vault_tool.py tags

# Show outgoing wikilinks from a note
python3 {baseDir}/vault_tool.py links "Home"

# Show which notes link TO a given note (backlinks)
python3 {baseDir}/vault_tool.py backlinks "Personal/Shopping List"

# Show recently modified notes
python3 {baseDir}/vault_tool.py recent --days 30
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What's in my vault?" | `python3 {baseDir}/vault_tool.py info` then `python3 {baseDir}/vault_tool.py tree` |
| "Find notes about X" | `python3 {baseDir}/vault_tool.py search-content "X"` |
| "Show me my shopping list" | `python3 {baseDir}/vault_tool.py read "Personal/Shopping List"` |
| "What did I write today?" | `python3 {baseDir}/vault_tool.py list "Daily Notes"` then read the latest |
| "Create a note about Y" | `python3 {baseDir}/vault_tool.py create "path/to/note" --content "..."` |
| "Rename this note" | `python3 {baseDir}/vault_tool.py move "old/name" "new/name"` |
| "What links to X?" | `python3 {baseDir}/vault_tool.py backlinks "X"` |
| "What tags do I use?" | `python3 {baseDir}/vault_tool.py tags` |

## Direct File Editing

For simple edits to existing notes, you can also read and modify the markdown files directly. The vault is just a folder — any file changes are immediately reflected.

1. Read the note: `python3 {baseDir}/vault_tool.py read "path/to/note"`
2. Edit the file at the path shown in the response
3. The vault tool will see the changes on next read

Use the `move` command instead of manual file moves when renaming, so wikilinks stay intact.

## Note Format

Notes use standard Markdown with Obsidian extensions:
- **Wikilinks**: `[[Note Name]]` or `[[Folder/Note Name]]` or `[[Note|Display Text]]`
- **Tags**: `#tag` inline or in a `Tags:` line at the end
- **Tasks**: `- [ ] Todo item` / `- [x] Done item`
- **Templates**: Notes in `Templates/` folder use `{{date}}` and `{{title}}` placeholders
