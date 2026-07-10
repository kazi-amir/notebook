---
name: reminder
description: Add, view, and delete reminders with optional repetition. Check which reminders are currently due. Use when the user asks to set a reminder, see upcoming reminders, or manage existing ones.
---

# Reminder

Add, view, and delete reminders with optional repetition. Data is pre-loaded. No setup needed.

## Viewing Reminders

```bash
# Get all reminders
python3 {baseDir}/reminder_data.py list

# Get only reminders that are currently due
python3 {baseDir}/reminder_data.py due

# Show raw data
python3 {baseDir}/reminder_data.py show --offset 0 --limit 100
```

## Adding Reminders

```bash
# Add a one-time reminder
python3 {baseDir}/reminder_data.py add \
    --title "Call contractor" \
    --due "2026-04-01 09:00:00" \
    --description "Follow up on the roof repair quote"

# Add a repeating reminder (every day)
python3 {baseDir}/reminder_data.py add \
    --title "Check rent payments" \
    --due "2026-04-05 08:00:00" \
    --description "Review outstanding rent payments" \
    --repeat-unit day \
    --repeat-value 1

# Add a weekly reminder
python3 {baseDir}/reminder_data.py add \
    --title "Weekly property walkthrough" \
    --due "2026-04-07 10:00:00" \
    --description "Inspect common areas" \
    --repeat-unit week \
    --repeat-value 1
```

### Reminder Fields

| Field | Flag | Required | Format |
|-------|------|----------|--------|
| Title | `--title` | Yes | Text |
| Due date | `--due` | Yes | `"YYYY-MM-DD HH:MM:SS"` |
| Description | `--description` | Yes | Text |
| Repeat unit | `--repeat-unit` | No | `second`, `minute`, `hour`, `day`, `week`, `month` |
| Repeat value | `--repeat-value` | No | Integer (e.g. `1` for every 1 unit) |

## Deleting Reminders

```bash
# Delete a specific reminder
python3 {baseDir}/reminder_data.py delete --id REMINDER_ID

# Delete all reminders
python3 {baseDir}/reminder_data.py delete-all
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What reminders do I have?" | `list` |
| "Are there any reminders due right now?" | `due` |
| "Remind me to call the plumber tomorrow at 9am" | `add --title "Call plumber" --due "..." --description "..."` |
| "Set a daily reminder to check emails" | `add --repeat-unit day --repeat-value 1 ...` |
| "Delete the reminder about the plumber" | `delete --id <id>` |
| "Clear all my reminders" | `delete-all` |

## Notes

- `due_datetime` in responses is a Unix timestamp; set it with `"YYYY-MM-DD HH:MM:SS"` strings
- Both `--repeat-unit` and `--repeat-value` must be provided together for repeating reminders
- `reminder_id` is a hex UUID string — get it from `list` or `due`
