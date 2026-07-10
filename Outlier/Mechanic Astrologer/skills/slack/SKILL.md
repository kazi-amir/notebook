---
name: slack
description: Browse Slack channels and DMs, read message history, search across conversations, and post messages or replies. Use when the user asks about Slack messages, channels, or wants to send a Slack message.
---

# Slack

Browse channels and DMs, read message history, search messages, and post. Data is pre-loaded. No setup needed.

## Listing Channels

```bash
# List all public channels
python3 {baseDir}/slack_data.py channels

# List specific types (public_channel, private_channel, im, mpim)
python3 {baseDir}/slack_data.py channels --types public_channel,private_channel

# List DMs only
python3 {baseDir}/slack_data.py channels --types im

# Limit results
python3 {baseDir}/slack_data.py channels --limit 50
```

## Reading Messages

```bash
# Get recent messages in a channel (use channel ID or #channel-name or @username for DMs)
python3 {baseDir}/slack_data.py history --channel C1234567890
python3 {baseDir}/slack_data.py history --channel "#general"
python3 {baseDir}/slack_data.py history --channel "@alice"

# Limit by time window
python3 {baseDir}/slack_data.py history --channel "#general" --limit "1d"
python3 {baseDir}/slack_data.py history --channel "#general" --limit "1w"
python3 {baseDir}/slack_data.py history --channel "#general" --limit "30d"

# Limit by message count
python3 {baseDir}/slack_data.py history --channel "#general" --limit "50"

# Get a thread (replies to a message)
python3 {baseDir}/slack_data.py thread --channel C1234567890 --ts 1234567890.123456
```

## Searching Messages

```bash
# Search by keyword
python3 {baseDir}/slack_data.py search --query "budget report"

# Search in a specific channel
python3 {baseDir}/slack_data.py search --query "invoice" --in-channel C1234567890

# Search in a DM
python3 {baseDir}/slack_data.py search --query "meeting" --in-dm C_DM_ID

# Filter by date
python3 {baseDir}/slack_data.py search --query "deployment" --after "2026-03-01"
python3 {baseDir}/slack_data.py search --query "deployment" --before "2026-04-01"

# Filter by sender
python3 {baseDir}/slack_data.py search --query "update" --from-user U1234567890

# Threads only
python3 {baseDir}/slack_data.py search --query "followup" --threads-only

# Limit results
python3 {baseDir}/slack_data.py search --query "report" --limit 20
```

## Posting Messages

```bash
# Post to a channel
python3 {baseDir}/slack_data.py post --channel C1234567890 \
    --content "The report is ready."

# Post as a specific user
python3 {baseDir}/slack_data.py post --channel C1234567890 \
    --content "Approved." --user-id U1234567890

# Reply in a thread (use the parent message's ts)
python3 {baseDir}/slack_data.py post --channel C1234567890 \
    --content "Thanks for the update!" --thread-ts 1234567890.123456

# Post markdown
python3 {baseDir}/slack_data.py post --channel "#general" \
    --content "**Reminder:** standup at 10am" --content-type markdown
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What channels are there?" | `channels` |
| "Show me recent messages in #general" | `history --channel "#general"` |
| "What did Alice say this week?" | `search --query "" --from-user <alice_id> --limit "1w"` (or use `history` on DM) |
| "Find messages about the budget" | `search --query "budget"` |
| "Send a message to #announcements" | `post --channel "#announcements" --content "..."` |
| "Reply to this thread" | `post --channel C... --thread-ts <ts> --content "..."` |
| "Show me this thread" | `thread --channel C... --ts <ts>` |

## Notes

- Channel identifiers: use channel ID (`C1234567890`), `#channel-name`, or `@username` for DMs
- `--ts` is the message timestamp (e.g. `1234567890.123456`) — visible in `history` and `search` responses
- `--limit` for `history` accepts time windows (`1d`, `1w`, `30d`, `90d`) or a count string (`"50"`)
- `--content-type` for `post` accepts `markdown` or `plain` (default: `markdown`)
