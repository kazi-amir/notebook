---
name: system
description: Get current time and wait for notifications. Use when the user asks about the current time, current date, what day it is, or needs to wait/pause for a specified duration.
---

# System

Get current time and wait for notifications. This is a utility service with no persistent entities.

## Current Time

```bash
# Get the current time, date, and weekday
python3 {baseDir}/system_data.py current-time
```

Returns: `current_timestamp`, `current_datetime`, `current_weekday`

## Wait

```bash
# Wait for a notification with a timeout (in seconds)
python3 {baseDir}/system_data.py wait --timeout 30

# Wait up to 60 seconds
python3 {baseDir}/system_data.py wait --timeout 60
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What time is it?" | `current-time` |
| "What day is it today?" | `current-time`, report `current_weekday` |
| "What's today's date?" | `current-time`, report `current_datetime` |
| "Wait 30 seconds" | `wait --timeout 30` |
| "Pause for a minute" | `wait --timeout 60` |

## Notes

- This is a utility service with no persistent entities
- The `wait` command blocks until a notification is received or the timeout expires
- Timeout is specified in seconds as an integer

## Utility

```bash
# Show raw data
python3 {baseDir}/system_data.py show
```
