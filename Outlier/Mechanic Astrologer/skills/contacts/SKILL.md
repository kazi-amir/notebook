---
name: contacts
description: Browse, search, add, edit, and delete contacts with name, email, phone, address, job, and demographic info. Use when the user asks about contact details, phone numbers, email addresses, or managing their address book.
---

# Contacts

Browse, search, add, edit, and delete contacts. Data is pre-loaded. No setup needed.

## Browsing Contacts

```bash
# List contacts (paginated)
python3 {baseDir}/contacts_data.py list --offset 0

# Show all contacts (raw data)
python3 {baseDir}/contacts_data.py show --offset 0 --limit 100
```

## Looking Up Contacts

```bash
# Get a specific contact by ID
python3 {baseDir}/contacts_data.py get --id abc123def456

# Search by name, email, or phone
python3 {baseDir}/contacts_data.py search --query "Smith"
python3 {baseDir}/contacts_data.py search --query "mike@mikesplumbing"
python3 {baseDir}/contacts_data.py search --query "512-555"
```

## Adding Contacts

```bash
# Add a new contact (first_name and last_name required)
python3 {baseDir}/contacts_data.py add \
    --first-name "John" --last-name "Smith" \
    --email "john@example.com" \
    --phone "+1-512-555-9999" \
    --job "Electrician" \
    --city "Austin" --country "US" \
    --status "Employed" \
    --description "Licensed electrician, referral from Mike"

# Minimal add
python3 {baseDir}/contacts_data.py add --first-name "Jane" --last-name "Doe"
```

### Contact Fields

| Field | Flag | Required | Example |
|-------|------|----------|---------|
| First name | `--first-name` | Yes | `--first-name "John"` |
| Last name | `--last-name` | Yes | `--last-name "Smith"` |
| Email | `--email` | No | `--email "john@example.com"` |
| Phone | `--phone` | No | `--phone "+1-512-555-1234"` |
| Job | `--job` | No | `--job "Software Engineer"` |
| City | `--city` | No | `--city "Austin"` |
| Country | `--country` | No | `--country "US"` |
| Address | `--address` | No | `--address "123 Main St, Austin, TX"` |
| Gender | `--gender` | No | `--gender "Male"` (Male, Female, Other, Unknown) |
| Age | `--age` | No | `--age 35` (1-100) |
| Nationality | `--nationality` | No | `--nationality "American"` |
| Status | `--status` | No | `--status "Employed"` (Student, Employed, Unemployed, Retired, Unknown) |
| Description | `--description` | No | `--description "Tenant at unit 301"` |

## Editing Contacts

```bash
# Update specific fields
python3 {baseDir}/contacts_data.py edit --id abc123 \
    --updates '{"phone": "+1-512-555-0000", "email": "new@example.com"}'
```

## Deleting Contacts

```bash
# Delete a contact
python3 {baseDir}/contacts_data.py delete --id abc123
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What's Maria's phone number?" | `search --query "Maria"` |
| "Find the plumber's contact" | `search --query "plumber"` or `search --query "plumbing"` |
| "Add a new contractor contact" | `add --first-name ... --last-name ... --phone ... --email ...` |
| "Update John's email" | `search --query "John"` then `edit --id <id> --updates '{"email": "..."}'` |
| "Show me all contacts" | `list` or `show --limit 100` |
| "Delete the old contractor" | `search --query "..."` then `delete --id <id>` |
| "Who is contact abc123?" | `get --id abc123` |
