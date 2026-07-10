---
name: zendesk
description: Manage support tickets, users, organizations, groups, and comments for a Zendesk-style help desk. Use when the user asks about support tickets, customer issues, agent assignments, or help desk operations.
---

# Zendesk Help Desk

Manage tickets, users, organizations, groups, and comments for a help desk system. Data is pre-loaded. No setup needed.

## Tickets

```bash
# List all tickets (with optional filters)
python3 {baseDir}/zendesk_data.py list-tickets
python3 {baseDir}/zendesk_data.py list-tickets --status "open" --priority "high"
python3 {baseDir}/zendesk_data.py list-tickets --assignee-id 3 --limit 10
python3 {baseDir}/zendesk_data.py list-tickets --organization-id 1 --sort-by "priority" --sort-order "asc"

# Get a specific ticket
python3 {baseDir}/zendesk_data.py get-ticket --id 42

# Create a new ticket
python3 {baseDir}/zendesk_data.py create-ticket --subject "Login broken" --description "Cannot log in since update" --requester-id 5
python3 {baseDir}/zendesk_data.py create-ticket --subject "Billing issue" --description "Double charged" --requester-id 5 --priority "urgent" --type "problem" --tags "billing,urgent"

# Update a ticket
python3 {baseDir}/zendesk_data.py update-ticket --id 42 --status "solved" --priority "low"
python3 {baseDir}/zendesk_data.py update-ticket --id 42 --assignee-id 3 --tags "escalated,reviewed"

# Delete a ticket
python3 {baseDir}/zendesk_data.py delete-ticket --id 42
```

### Ticket Filters

| Filter | Flag | Example |
|--------|------|---------|
| Status | `--status` | `--status "open"` |
| Priority | `--priority` | `--priority "urgent"` |
| Assignee | `--assignee-id` | `--assignee-id 3` |
| Requester | `--requester-id` | `--requester-id 5` |
| Organization | `--organization-id` | `--organization-id 1` |
| Group | `--group-id` | `--group-id 2` |
| Sort field | `--sort-by` | `--sort-by "priority"` |
| Sort direction | `--sort-order` | `--sort-order "asc"` |
| Limit | `--limit` | `--limit 10` |
| Offset | `--offset` | `--offset 25` |

## Users

```bash
# List all users (with optional filters)
python3 {baseDir}/zendesk_data.py list-users
python3 {baseDir}/zendesk_data.py list-users --role "agent"
python3 {baseDir}/zendesk_data.py list-users --email "john" --active true

# Get a specific user
python3 {baseDir}/zendesk_data.py get-user --id 5

# Create a new user
python3 {baseDir}/zendesk_data.py create-user --name "Jane Doe" --email "jane@example.com"
python3 {baseDir}/zendesk_data.py create-user --name "Agent Smith" --email "smith@company.com" --role "agent" --phone "+1234567890"

# Update a user
python3 {baseDir}/zendesk_data.py update-user --id 5 --role "agent" --verified true
python3 {baseDir}/zendesk_data.py update-user --id 5 --active false
```

### User Filters

| Filter | Flag | Example |
|--------|------|---------|
| Role | `--role` | `--role "agent"` |
| Email | `--email` | `--email "john@"` |
| Organization | `--organization-id` | `--organization-id 1` |
| Active | `--active` | `--active true` |
| Limit | `--limit` | `--limit 10` |
| Offset | `--offset` | `--offset 25` |

## Organizations

```bash
# List all organizations
python3 {baseDir}/zendesk_data.py list-organizations
python3 {baseDir}/zendesk_data.py list-organizations --name "Acme" --domain "acme.com"

# Get a specific organization
python3 {baseDir}/zendesk_data.py get-organization --id 1

# Create a new organization
python3 {baseDir}/zendesk_data.py create-organization --name "Acme Corp" --domain-names "acme.com,acme.io" --details "Enterprise customer"
python3 {baseDir}/zendesk_data.py create-organization --name "Shared Org" --shared-tickets --shared-comments
```

## Comments

```bash
# List comments for a ticket
python3 {baseDir}/zendesk_data.py list-ticket-comments --ticket-id 42
python3 {baseDir}/zendesk_data.py list-ticket-comments --ticket-id 42 --include-private

# Add a comment to a ticket
python3 {baseDir}/zendesk_data.py add-ticket-comment --ticket-id 42 --body "Working on this now"
python3 {baseDir}/zendesk_data.py add-ticket-comment --ticket-id 42 --body "Internal note" --public false --author-id 3
```

## Groups

```bash
# List all agent groups
python3 {baseDir}/zendesk_data.py list-groups

# Create a new group
python3 {baseDir}/zendesk_data.py create-group --name "Tier 2 Support" --description "Escalation team"
python3 {baseDir}/zendesk_data.py create-group --name "Internal Team" --is-public false
```

## Search & Stats

```bash
# Search across tickets, users, and organizations
python3 {baseDir}/zendesk_data.py search --query "login issue"
python3 {baseDir}/zendesk_data.py search --query "billing" --type "ticket" --limit 10

# Get system statistics
python3 {baseDir}/zendesk_data.py stats
```

## Response Format

All commands return **flat JSON objects** to stdout. For example, `create-ticket` returns:

```json
{"id": 41, "subject": "Login broken", "status": "open", "priority": "normal", ...}
```

**Not** nested like `{"ticket": {"id": 41}}`. Read fields directly from the top-level object.

## Tags

Tags are passed as **comma-separated strings** on the CLI: `--tags "billing,urgent,escalated"`. The script splits them into an array automatically.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all open tickets" | `list-tickets --status "open"` |
| "What urgent tickets are there?" | `list-tickets --priority "urgent"` |
| "Show ticket #42" | `get-ticket --id 42` |
| "Create a ticket for login issue" | `create-ticket --subject "Login issue" --description "..." --requester-id ID` |
| "Close ticket 42" | `update-ticket --id 42 --status "closed"` |
| "Assign ticket 42 to agent 3" | `update-ticket --id 42 --assignee-id 3` |
| "What comments are on ticket 42?" | `list-ticket-comments --ticket-id 42` |
| "Add a note to ticket 42" | `add-ticket-comment --ticket-id 42 --body "..." --public false` |
| "List all agents" | `list-users --role "agent"` |
| "Show user 5" | `get-user --id 5` |
| "Create a new customer" | `create-user --name "..." --email "..."` |
| "What organizations do we have?" | `list-organizations` |
| "Search for billing tickets" | `search --query "billing" --type "ticket"` |
| "How many tickets do we have?" | `stats` |
| "What groups exist?" | `list-groups` |
| "Tickets assigned to agent 3" | `list-tickets --assignee-id 3` |
| "High priority pending tickets" | `list-tickets --status "pending" --priority "high"` |
