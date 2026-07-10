---
name: airtable
description: Browse and manage Airtable bases, tables, fields, and records. List, create, update, delete, and search records across bases. Use when the user asks about Airtable data, databases, or structured records.
---

# Airtable

Browse and manage Airtable bases, tables, fields, and records. Data is pre-loaded. No setup needed.

## Bases & Tables

```bash
# List all bases
python3 {baseDir}/airtable_data.py list-bases

# List tables in a base
python3 {baseDir}/airtable_data.py list-tables --base-id appXXXXXXXXXXXXXX

# Describe a table (fields + schema)
python3 {baseDir}/airtable_data.py describe-table \
    --base-id appXXXXXXXXXXXXXX --table-id tblXXXXXXXXXXXXXX

# Create a table
python3 {baseDir}/airtable_data.py create-table \
    --base-id appXXXXXXXXXXXXXX --name "Tenants" \
    --description "Tenant contact information"

# Update a table name or description
python3 {baseDir}/airtable_data.py update-table \
    --base-id appXXXXXXXXXXXXXX --table-id tblXXXXXXXXXXXXXX \
    --name "Residents"
```

## Fields

```bash
# Create a field (field is a JSON object with name and type)
python3 {baseDir}/airtable_data.py create-field \
    --base-id appXXXXXXXXXXXXXX --table-id tblXXXXXXXXXXXXXX \
    --field '{"name": "Phone", "type": "phoneNumber"}'

# Update a field
python3 {baseDir}/airtable_data.py update-field \
    --base-id appXXXXXXXXXXXXXX --table-id tblXXXXXXXXXXXXXX \
    --field-id fldXXXXXXXXXXXXXX \
    --updates '{"name": "Mobile Phone"}'
```

### Field Types

`singleLineText`, `multilineText`, `number`, `checkbox`, `date`, `singleSelect`, `multipleSelect`, `email`, `url`, `phoneNumber`

## Records

```bash
# List records in a table
python3 {baseDir}/airtable_data.py list-records \
    --base-id appXXXXXXXXXXXXXX --table "Tenants" --max 50

# Get a specific record
python3 {baseDir}/airtable_data.py get-record \
    --base-id appXXXXXXXXXXXXXX --table "Tenants" --record-id recXXXXXXXXXXXXXX

# Create a record
python3 {baseDir}/airtable_data.py create-record \
    --base-id appXXXXXXXXXXXXXX --table "Tenants" \
    --fields '{"Name": "Jane Smith", "Email": "jane@example.com", "Unit": "204"}'

# Update records (max 10 per call; each entry needs id + fields)
python3 {baseDir}/airtable_data.py update-records \
    --base-id appXXXXXXXXXXXXXX --table-id tblXXXXXXXXXXXXXX \
    --records '[{"id": "recXXX", "fields": {"Unit": "205"}}]'

# Delete records
python3 {baseDir}/airtable_data.py delete-records \
    --base-id appXXXXXXXXXXXXXX --table-id tblXXXXXXXXXXXXXX \
    --record-ids '["recXXX", "recYYY"]'

# Search records by field value
python3 {baseDir}/airtable_data.py search-records \
    --base-id appXXXXXXXXXXXXXX --table "Tenants" \
    --field "Email" --value "jane@example.com"

# Show raw data
python3 {baseDir}/airtable_data.py show --offset 0 --limit 100
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What bases do I have?" | `list-bases` |
| "What tables are in this base?" | `list-tables --base-id ...` |
| "Show me all tenants" | `list-records --base-id ... --table "Tenants"` |
| "Find the record for Jane Smith" | `search-records --field "Name" --value "Jane Smith"` |
| "Add a new tenant" | `create-record --fields '{"Name": "...", ...}'` |
| "Update the unit number for record X" | `update-records --records '[{"id": "recX", "fields": {"Unit": "..."}}]'` |
| "Delete this record" | `delete-records --record-ids '["recX"]'` |
| "What fields does this table have?" | `describe-table --base-id ... --table-id ...` |

## Notes

- `--base-id` uses the base's app ID (e.g. `appXXXXXXXXXXXXXX`) — get it from `list-bases`
- `--table` (for record operations) accepts the table name string
- `--table-id` (for schema/update operations) accepts the table ID (e.g. `tblXXXXXXXXXXXXXX`) — get it from `list-tables`
- `--fields`, `--field`, `--updates`, `--records`, `--record-ids` all accept JSON strings
