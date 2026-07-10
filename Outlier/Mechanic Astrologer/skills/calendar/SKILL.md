---
name: calendar
description: View, create, edit, search, and delete calendar events. Filter by date range, tag, or keyword. Use when the user asks about schedules, appointments, events, reminders, or anything time-related.
---

# Calendar

View, create, edit, search, and delete calendar events. Data is pre-loaded. No setup needed.

## Viewing Events

```bash
# Get today's events
python3 {baseDir}/calendar_data.py today

# Get events in a date range
python3 {baseDir}/calendar_data.py range \
    --start "2026-03-01 00:00:00" --end "2026-03-31 23:59:59" \
    --limit 20

# Get a specific event by ID
python3 {baseDir}/calendar_data.py get --id abc123def456

# Show all events (raw data)
python3 {baseDir}/calendar_data.py show --offset 0 --limit 100
```

## Filtering by Tag

```bash
# List all tags
python3 {baseDir}/calendar_data.py tags

# Get events by tag
python3 {baseDir}/calendar_data.py by-tag --tag "Maintenance"
python3 {baseDir}/calendar_data.py by-tag --tag "Lease"
```

## Searching Events

```bash
# Search by keyword (searches title, description, location, attendees)
python3 {baseDir}/calendar_data.py search --query "plumbing"
python3 {baseDir}/calendar_data.py search --query "Riverside Commons"
```

## Creating Events

```bash
# Create a new event
python3 {baseDir}/calendar_data.py add \
    --title "Maintenance: Fix leaky faucet" \
    --start "2026-03-20 09:00:00" \
    --end "2026-03-20 11:00:00" \
    --tag "Maintenance" \
    --description "Plumber scheduled to fix kitchen faucet in unit 301" \
    --location "Unit 301, Riverside Commons" \
    --attendees '["Mike'\''s Plumbing"]'

# Minimal event (defaults: start=now, end=1hr later)
python3 {baseDir}/calendar_data.py add --title "Quick meeting"
```

### Event Fields

| Field | Flag | Required | Format |
|-------|------|----------|--------|
| Title | `--title` | No (defaults to "Event") | Text |
| Start | `--start` | No (defaults to now) | `"YYYY-MM-DD HH:MM:SS"` |
| End | `--end` | No (defaults to start+1hr) | `"YYYY-MM-DD HH:MM:SS"` |
| Tag | `--tag` | No | Text (e.g., "Maintenance", "Lease") |
| Description | `--description` | No | Text |
| Location | `--location` | No | Text |
| Attendees | `--attendees` | No | JSON array: `'["name1", "name2"]'` |

## Editing Events

```bash
# Edit an event (only specified fields are updated)
python3 {baseDir}/calendar_data.py edit --id abc123 \
    --start "2026-03-21 10:00:00" \
    --end "2026-03-21 12:00:00" \
    --description "Rescheduled to Thursday"
```

## Deleting Events

```bash
# Delete an event
python3 {baseDir}/calendar_data.py delete --id abc123
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What's on my calendar today?" | `today` |
| "Any events this week?" | `range --start "YYYY-MM-DD 00:00:00" --end "YYYY-MM-DD 23:59:59"` |
| "Show maintenance events" | `by-tag --tag "Maintenance"` |
| "When is the lease expiring for unit 301?" | `search --query "301"` or `by-tag --tag "Lease"` |
| "Schedule a plumber visit" | `add --title "..." --start "..." --end "..." --tag "Maintenance" ...` |
| "Reschedule the meeting to Thursday" | `edit --id <id> --start "..." --end "..."` |
| "Cancel that appointment" | `delete --id <id>` |
| "What tags are available?" | `tags` |
| "Search for events about Riverside" | `search --query "Riverside"` |

## Notes

- Datetime fields in responses are Unix timestamps (e.g., `1737018000.0`)
- Human-readable versions are in `start_strftime` and `end_strftime` fields
- When creating/editing, always pass datetimes as `"YYYY-MM-DD HH:MM:SS"` strings
- Start time must be before end time
