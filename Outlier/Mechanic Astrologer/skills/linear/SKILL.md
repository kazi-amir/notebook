---
name: linear
description: Manage users, teams, projects, issues, and comments via the Linear project tracker. Use when the user asks about project management, issues, tickets, sprints, teams, or issue tracking.
---

# Linear

Manage users, teams, projects, issues, and comments. Data is pre-loaded. No API key or setup needed.

## Users

```bash
# List users (optionally filter by query, team)
python3 {baseDir}/linear_data.py list-users --query "Lisa"

# Get a specific user by ID, name, email, or "me"
python3 {baseDir}/linear_data.py get-user --id "me"
python3 {baseDir}/linear_data.py get-user --id USR-1001

# Create a new user
python3 {baseDir}/linear_data.py create-user --email jane@example.com --name "Jane Doe"
```

## Teams

```bash
# List teams (optionally filter)
python3 {baseDir}/linear_data.py list-teams --query "Engineering"

# Get a specific team by ID
python3 {baseDir}/linear_data.py get-team --id TEAM-2001

# Create a new team
python3 {baseDir}/linear_data.py create-team --name "Platform"
```

## Projects

```bash
# List projects (optionally filter by team, member, state)
python3 {baseDir}/linear_data.py list-projects --team TEAM-2001
python3 {baseDir}/linear_data.py list-projects --state started --member USR-1001

# Get a specific project by ID
python3 {baseDir}/linear_data.py get-project --id PROJ-3001

# Create a new project
python3 {baseDir}/linear_data.py create-project --name "Q3 Roadmap" --team TEAM-2001 \
    --description "Quarterly planning" --lead USR-1001 --priority 1 --state planned \
    --start-date 2026-07-01 --target-date 2026-09-30 --labels '["roadmap","q3"]'

# Update a project
python3 {baseDir}/linear_data.py update-project --id PROJ-3001 --state started \
    --summary "Kicked off July 1"
```

### Project States

| State | Description |
|-------|-------------|
| `backlog` | Not yet scheduled |
| `planned` | Scheduled for future work |
| `started` | Currently in progress |
| `paused` | Temporarily on hold |
| `completed` | Finished |
| `canceled` | Canceled |

## Issues

```bash
# List issues (optionally filter by team, project, assignee, state, label, cycle)
python3 {baseDir}/linear_data.py list-issues --project PROJ-3001
python3 {baseDir}/linear_data.py list-issues --assignee USR-1001 --state "In Progress"
python3 {baseDir}/linear_data.py list-issues --team TEAM-2001 --label bug

# Get a specific issue by ID
python3 {baseDir}/linear_data.py get-issue --id ISS-4001

# Create a new issue
python3 {baseDir}/linear_data.py create-issue --team TEAM-2001 --title "Fix login bug" \
    --description "Users cannot log in on mobile" --assignee USR-1001 \
    --project PROJ-3001 --priority 1 --state "In Progress" --due-date 2026-05-15 \
    --labels '["bug","mobile"]' --links '["https://example.com/issue"]'

# Update an issue
python3 {baseDir}/linear_data.py update-issue --id ISS-4001 --state Done \
    --estimate 3 --priority 2

# Create a sub-issue
python3 {baseDir}/linear_data.py create-issue --team TEAM-2001 --title "Sub-task" \
    --parent-id ISS-4001
```

### Issue Priority Levels

| Priority | Description |
|----------|-------------|
| `0` | No priority |
| `1` | Urgent |
| `2` | High |
| `3` | Medium |
| `4` | Low |

## Comments

```bash
# List comments on an issue
python3 {baseDir}/linear_data.py list-comments --issue-id ISS-4001

# Create a comment
python3 {baseDir}/linear_data.py create-comment --issue-id ISS-4001 \
    --body "Looks good, merging now"

# Reply to a comment (threaded)
python3 {baseDir}/linear_data.py create-comment --issue-id ISS-4001 \
    --body "Thanks!" --parent-id CMT-5001
```

## Utility

```bash
# Show raw data
python3 {baseDir}/linear_data.py show --offset 0 --limit 100
```

## Data Entities

The Linear system holds:

- **Users** -- people in the workspace (id, email, name, display_name, avatar_url, is_active, created_at, updated_at)
- **Teams** -- organizational groups (id, name, key, description, is_archived, created_at, updated_at)
- **Projects** -- high-level initiatives (id, team_id, name, summary, description, lead_id, priority, state, start_date, target_date, labels, is_archived)
- **Issues** -- individual work items (id, project_id, team_id, parent_id, assignee_id, state_id, cycle_id, number, title, description, priority, estimate, due_date, labels, links, is_archived)
- **Comments** -- discussion on issues (id, issue_id, author_id, parent_id, body, is_edited)
- **TeamMemberships** -- links users to teams (id, team_id, user_id)

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all teams" | `list-teams` |
| "Who is on the Engineering team?" | `list-users --team TEAM-X` |
| "What projects are in progress?" | `list-projects --state started` |
| "Show issues for the Q3 Roadmap" | `list-issues --project PROJ-X` |
| "What's assigned to me?" | `get-user --id me` then `list-issues --assignee USR-X` |
| "Create a bug ticket" | `create-issue --team TEAM-X --title "..." --labels '["bug"]'` |
| "Move issue to Done" | `update-issue --id ISS-X --state Done` |
| "Add a comment to ISS-4001" | `create-comment --issue-id ISS-4001 --body "..."` |
| "What are the open issues?" | `list-issues --state "In Progress"` or `list-issues` and filter |
| "Show comments on this issue" | `list-comments --issue-id ISS-X` |
| "Who leads this project?" | `get-project --id PROJ-X` then `get-user --id LEAD-ID` |

## Notes

- User IDs, team IDs, project IDs, and issue IDs are used to link entities across the system.
- The `get-user` command accepts an ID, name, email, or the special value `"me"` to retrieve the current user.
- Issues support sub-issues via the `--parent-id` flag.
- Comments support threading via the `--parent-id` flag.
- Labels and links are passed as JSON arrays (e.g., `'["bug","urgent"]'`).
- List commands support pagination with `--limit` and `--offset` (or `--after`/`--before` for cursor-based pagination on users).
- List commands support ordering with `--order-by` and date filtering with `--created-at` / `--updated-at`.
