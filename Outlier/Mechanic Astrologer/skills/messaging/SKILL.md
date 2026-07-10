---
name: messaging
description: Send and receive messages, manage conversations, and search message history. Use when the user asks about messages, conversations, chats, or wants to contact someone.
---

# Messaging

Send messages, browse conversations, and search message history. Data is pre-loaded. No setup needed.

## Viewing Conversations

```bash
# List all conversations (most recently updated first)
python3 {baseDir}/messaging_data.py list

# List with pagination
python3 {baseDir}/messaging_data.py list --offset 0 --limit 20

# Get a conversation with its messages
python3 {baseDir}/messaging_data.py get --conversation-id CONV_ID

# Get with message pagination
python3 {baseDir}/messaging_data.py get --conversation-id CONV_ID --offset 0 --limit 50

# Search conversations (searches title, participant names, message content)
python3 {baseDir}/messaging_data.py search --query "invoice"

# Show raw data
python3 {baseDir}/messaging_data.py show --offset 0 --limit 100
```

## Sending Messages

```bash
# Send a message to a user (creates a new conversation if none exists)
python3 {baseDir}/messaging_data.py send --user-id USER_ID --content "Hello, how are you?"

# Send a message to an existing conversation
python3 {baseDir}/messaging_data.py send-to --conversation-id CONV_ID \
    --content "Following up on the invoice."

# Send with an attachment
python3 {baseDir}/messaging_data.py send --user-id USER_ID \
    --content "Please see the attached report." \
    --attachment "/path/to/report.pdf"
```

## Managing Conversations

```bash
# Create a new conversation with multiple participants
python3 {baseDir}/messaging_data.py create \
    --participant-ids '["user_001", "user_002", "user_003"]' \
    --title "Q1 Budget Review"

# Create without a title (uses participant names)
python3 {baseDir}/messaging_data.py create \
    --participant-ids '["user_001", "user_002"]'

# Add a user to an existing conversation
python3 {baseDir}/messaging_data.py add-user \
    --conversation-id CONV_ID --user-id USER_ID
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me my recent conversations" | `list` |
| "What did we talk about with John?" | `search --query "John"` |
| "Show me the conversation about invoices" | `search --query "invoice"` |
| "Send a message to user_042" | `send --user-id user_042 --content "..."` |
| "Reply to this conversation" | `send-to --conversation-id ... --content "..."` |
| "Start a group chat with Alice and Bob" | `create --participant-ids '["alice_id", "bob_id"]' --title "..."` |
| "Add Carol to this conversation" | `add-user --conversation-id ... --user-id carol_id` |

## Notes

- Conversations are sorted by `last_updated` descending — most recent first
- `send --user-id` will find an existing 1:1 conversation or create a new one
- Message timestamps are Unix timestamps
- `--participant-ids` and similar list arguments take JSON arrays
