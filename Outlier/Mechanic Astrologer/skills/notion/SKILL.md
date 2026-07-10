---
name: notion
description: Browse and manage Notion workspace data including pages, databases, users, blocks, and comments. Use when the user asks about Notion pages, databases, wiki content, knowledge base, project tracking, or workspace management.
---

# Notion

Browse and manage Notion workspace pages, databases, blocks, comments, and users. Data is pre-loaded. No API key or setup needed.

## Users

```bash
# Get the authenticated bot user
python3 {baseDir}/notion_data.py get-self

# Get a user by ID
python3 {baseDir}/notion_data.py get-user --user-id USR-001

# List all users
python3 {baseDir}/notion_data.py get-users
python3 {baseDir}/notion_data.py get-users --page-size 10 --start-cursor abc123

# Create a new user
python3 {baseDir}/notion_data.py create-user --name "Jane Doe" --email jane@example.com
```

## Databases

```bash
# Get a database by ID
python3 {baseDir}/notion_data.py retrieve-database --database-id DB-001

# Create a new database
python3 {baseDir}/notion_data.py create-database \
    --parent '{"page_id": "PAGE-001"}' \
    --properties '{"Name": {"title": {}}, "Status": {"select": {"options": [{"name": "Active"}]}}}' \
    --title "My Database"

# Update a database
python3 {baseDir}/notion_data.py update-database --database-id DB-001 \
    --title "Updated Title" --description "New description"

# Query pages in a database
python3 {baseDir}/notion_data.py query-database --database-id DB-001

# Query with filters
python3 {baseDir}/notion_data.py query-database --database-id DB-001 \
    --filter '{"and": [{"property": "Status", "status": {"equals": "In Progress"}}]}'

# Query with sorts
python3 {baseDir}/notion_data.py query-database --database-id DB-001 \
    --sorts '[{"property": "Date", "direction": "descending"}]'
```

## Pages

```bash
# Get a page by ID
python3 {baseDir}/notion_data.py retrieve-page --page-id PAGE-001

# Create a new page in a database
python3 {baseDir}/notion_data.py create-page \
    --parent '{"database_id": "DB-001"}' \
    --properties '{"Name": {"title": [{"text": {"content": "New Page"}}]}}'

# Create a child page
python3 {baseDir}/notion_data.py create-page \
    --parent '{"page_id": "PAGE-001"}'

# Update a page
python3 {baseDir}/notion_data.py update-page --page-id PAGE-001 \
    --properties '{"Status": {"status": {"name": "Done"}}}'

# Archive a page
python3 {baseDir}/notion_data.py update-page --page-id PAGE-001 --archived

# Get a specific property value
python3 {baseDir}/notion_data.py retrieve-page-property \
    --page-id PAGE-001 --property-id PROP-001
```

## Blocks & Comments

```bash
# Get a block by ID (also works with page IDs)
python3 {baseDir}/notion_data.py retrieve-block --block-id BLOCK-001

# Get comments for a block or page
python3 {baseDir}/notion_data.py retrieve-comments --block-id PAGE-001

# Create a comment on a page
python3 {baseDir}/notion_data.py create-comment \
    --parent '{"page_id": "PAGE-001"}' \
    --rich-text '[{"text": {"content": "This looks great!"}}]'
```

## Search

```bash
# Search all pages and databases
python3 {baseDir}/notion_data.py search

# Search by title
python3 {baseDir}/notion_data.py search --query "SOP"

# Search only databases
python3 {baseDir}/notion_data.py search \
    --filter '{"property": "object", "value": "database"}'

# Search only pages
python3 {baseDir}/notion_data.py search \
    --filter '{"property": "object", "value": "page"}'
```

## Utility

```bash
# Show raw data
python3 {baseDir}/notion_data.py show --offset 0 --limit 100

# Reset to initial state
python3 {baseDir}/notion_data.py reset
```

## Property Types

When creating or updating pages, property values use type-specific formats:

| Type | Format Example |
|------|----------------|
| `title` | `{"Title": {"title": [{"text": {"content": "Page name"}}]}}` |
| `rich_text` | `{"Notes": {"rich_text": [{"text": {"content": "text"}}]}}` |
| `number` | `{"Price": {"number": 99.99}}` |
| `checkbox` | `{"Done": {"checkbox": true}}` |
| `select` | `{"Status": {"select": {"name": "Active"}}}` |
| `status` | `{"Status": {"status": {"name": "In Progress"}}}` |
| `date` | `{"Due": {"date": {"start": "2024-01-15"}}}` |

## Query Filtering

The `query-database` command supports compound filters via `--filter`:

```json
{
  "and": [
    {"property": "Status", "status": {"equals": "In Progress"}},
    {"property": "Priority", "select": {"equals": "High"}}
  ]
}
```

Supported filter conditions by property type:

- **date**: `equals`, `before`, `after`, `on_or_before`, `on_or_after`, `is_empty`, `is_not_empty`
- **number**: `equals`, `does_not_equal`, `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`, `is_empty`, `is_not_empty`
- **rich_text**: `equals`, `does_not_equal`, `contains`, `does_not_contain`, `starts_with`, `ends_with`, `is_empty`, `is_not_empty`
- **select/status**: `equals`, `does_not_equal`, `is_empty`, `is_not_empty`
- **checkbox**: `equals`, `does_not_equal`

## Data Entities

The Notion workspace holds:

- **Users** -- workspace members (id, name, email, type: person or bot)
- **Databases** -- structured collections with property schemas (id, title, description, properties, parent)
- **Pages** -- individual records within databases or standalone pages (id, properties, parent, archived)
- **Properties** -- schema definitions for database columns (id, name, type, configuration)
- **Property Values** -- per-page property data (id, page_id, property_id, type, value)
- **Blocks** -- content blocks within pages (paragraph, heading, list, code, etc.)
- **Comments** -- discussion threads on pages or blocks

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all databases" | `search --filter '{"property": "object", "value": "database"}'` |
| "Find pages about SOPs" | `search --query "SOP"` |
| "What's in the Daily Manager Log?" | `search` for the database, then `query-database` to list entries |
| "Show me today's log entry" | `query-database` with date filter on the manager log database |
| "Create a new page in the tracker" | `create-page` with database parent and properties matching the schema |
| "Update the status of a page" | `update-page --page-id X --properties '{"Status": ...}'` |
| "Who are the workspace users?" | `get-users` |
| "Add a comment to this page" | `create-comment --parent '{"page_id": "X"}' --rich-text '[...]'` |
| "Show me all catering events" | `search --query "Catering Events"` then `query-database` |
