---
name: email
description: Read, send, reply, forward, search, and manage emails across inbox, sent, draft, and trash folders. Use when the user asks about emails, sending messages, checking inbox, or email communication.
---

# Email

Read, send, reply to, forward, search, and organize emails. Data is pre-loaded. No email account setup needed.

## Reading Emails

```bash
# List inbox emails (paginated)
python3 {baseDir}/email_data.py list --folder INBOX --offset 0 --limit 10

# List sent emails
python3 {baseDir}/email_data.py list --folder SENT --limit 20

# Get a specific email by ID
python3 {baseDir}/email_data.py get --id abc123def456

# Get an email by its position in a folder
python3 {baseDir}/email_data.py get-by-index --index 0 --folder INBOX
```

### Folders

| Folder | Description |
|--------|-------------|
| `INBOX` | Received emails (default) |
| `SENT` | Sent emails |
| `DRAFT` | Draft emails |
| `TRASH` | Deleted emails |

## Sending Emails

```bash
# Send a new email
python3 {baseDir}/email_data.py send --sender "me@example.com" \
    --recipients '["tenant@example.com"]' \
    --subject "Rent Reminder" \
    --content "This is a reminder that rent is due on the 1st."

# Send with CC
python3 {baseDir}/email_data.py send --sender "me@example.com" \
    --recipients '["tenant@example.com"]' \
    --cc '["manager@example.com"]' \
    --subject "Lease Update" \
    --content "Please review the updated terms."
```

## Replying & Forwarding

```bash
# Reply to an email
python3 {baseDir}/email_data.py reply --id abc123 --sender "me@example.com" \
    --content "Thank you for reporting this. We will address it shortly."

# Forward an email
python3 {baseDir}/email_data.py forward --id abc123 --sender "me@example.com" \
    --recipients '["contractor@example.com"]' \
    --content "Please see the tenant's maintenance request below."
```

## Searching

```bash
# Search emails by keyword (searches subject and content)
python3 {baseDir}/email_data.py search --query "plumbing" --folder INBOX --limit 10
```

## Managing Emails

```bash
# Move an email to another folder
python3 {baseDir}/email_data.py move --id abc123 --from-folder INBOX --to-folder TRASH

# Delete an email
python3 {baseDir}/email_data.py delete --id abc123 --folder INBOX
```

## JMAP & Mailboxes

```bash
# List mailboxes with email counts
python3 {baseDir}/email_data.py mailboxes

# Get a specific mailbox
python3 {baseDir}/email_data.py mailbox --id INBOX

# List JMAP-formatted emails
python3 {baseDir}/email_data.py jmap-list --mailbox-id INBOX --limit 10

# Get JMAP email by ID
python3 {baseDir}/email_data.py jmap-get --id abc123

# Get email thread
python3 {baseDir}/email_data.py thread --id thread123
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Check my inbox" | `list --folder INBOX` |
| "Any new emails?" | `list --folder INBOX --limit 5` (check unread) |
| "Read email from Maria" | `search --query "Maria"` then `get --id <id>` |
| "Send a reminder about rent" | `send --sender ... --recipients ... --subject ... --content ...` |
| "Reply to that maintenance email" | `reply --id <id> --sender ... --content ...` |
| "Forward this to the plumber" | `forward --id <id> --sender ... --recipients ... --content ...` |
| "Search for emails about leaking" | `search --query "leaking"` |
| "Delete that spam email" | `delete --id <id> --folder INBOX` |
| "What emails have I sent?" | `list --folder SENT` |
| "How many unread emails?" | `mailboxes` (check unreadEmails count) |

## Notes

- Reading an email by ID or index automatically marks it as read
- Replies auto-populate the `Re:` subject prefix and send to the original sender
- Forwards auto-populate the `Fwd:` subject prefix
- The `sender` field should be the current user's email address
