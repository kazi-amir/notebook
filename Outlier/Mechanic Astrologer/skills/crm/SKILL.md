---
name: crm
description: Manage contacts, companies, deals, leads, and engagements via the CRM platform. Use when the user asks about sales pipeline, deals, leads, client relationships, companies, engagement history, or customer relationship management.
---

# CRM

Manage contacts, companies, deals, leads, and engagements. Data is pre-loaded. No API key or setup needed.

## Contacts

```bash
# Search contacts by name
python3 {baseDir}/crm_data.py search-contacts --full-name "Lisa Chen"

# Get a specific contact by ID
python3 {baseDir}/crm_data.py get-contact --id CON-1001

# Create a new contact
python3 {baseDir}/crm_data.py create-contact --full-name "Jane Doe" --email jane@example.com \
    --company-id COMP-2001 --phone 555-1234 --jobtitle "Marketing Director"

# Delete a contact
python3 {baseDir}/crm_data.py delete-contact --id CON-1001
```

## Companies

```bash
# Search companies by name
python3 {baseDir}/crm_data.py search-companies --name "Acme"

# Get a specific company by ID
python3 {baseDir}/crm_data.py get-company --id COMP-2001

# Create a new company
python3 {baseDir}/crm_data.py create-company --name "Acme Corp" \
    --industry Technology --domain acme.com --phone 555-0100

# Delete a company
python3 {baseDir}/crm_data.py delete-company --id COMP-2001
```

## Deals

```bash
# Search deals by name
python3 {baseDir}/crm_data.py search-deals --dealname "Chen"

# Search deals by company
python3 {baseDir}/crm_data.py search-deals --company-id COMP-2001

# Get a specific deal by ID
python3 {baseDir}/crm_data.py get-deal --id DEAL-3001

# Create a new deal
python3 {baseDir}/crm_data.py create-deal --dealname "Enterprise License" \
    --dealstage qualifiedtobuy --company-id COMP-2001 --amount 50000 \
    --closedate 2026-06-30

# Update deal stage
python3 {baseDir}/crm_data.py update-deal-stage --id DEAL-3001 --dealstage closedwon

# Delete a deal
python3 {baseDir}/crm_data.py delete-deal --id DEAL-3001
```

### Deal Stages

| Stage | Description |
|-------|-------------|
| `appointmentscheduled` | Initial appointment scheduled |
| `qualifiedtobuy` | Lead qualified as potential buyer |
| `presentationscheduled` | Demo/presentation scheduled |
| `decisionmakerboughtin` | Decision maker approval obtained |
| `contractsent` | Contract sent to customer |
| `closedwon` | Deal won |
| `closedlost` | Deal lost |

## Leads

```bash
# Search leads by name
python3 {baseDir}/crm_data.py search-leads --full-name "Smith"

# Search leads by company
python3 {baseDir}/crm_data.py search-leads --company-id COMP-2001

# Get a specific lead by ID
python3 {baseDir}/crm_data.py get-lead --id LEAD-4001

# Create a new lead
python3 {baseDir}/crm_data.py create-lead --full-name "Bob Smith" --email bob@example.com \
    --company "Acme Corp" --rating hot --leadsource "Website"

# Delete a lead
python3 {baseDir}/crm_data.py delete-lead --id LEAD-4001
```

### Lead Ratings

| Rating | Description |
|--------|-------------|
| `hot` | High priority lead |
| `warm` | Medium priority lead |
| `cold` | Low priority lead |

## Engagements

```bash
# Create an email engagement
python3 {baseDir}/crm_data.py create-engagement --engagement-type EMAIL \
    --body "Follow-up on proposal" --contact-ids '["CON-1001"]' --title "Proposal Follow-up"

# Create a call engagement
python3 {baseDir}/crm_data.py create-engagement --engagement-type CALL \
    --body "Discussed pricing" --contact-ids '["CON-1001"]' --company-ids '["COMP-2001"]'

# Create a note
python3 {baseDir}/crm_data.py create-engagement --engagement-type NOTE \
    --body "Client prefers quarterly billing"

# List engagements (optionally filter)
python3 {baseDir}/crm_data.py list-engagements
python3 {baseDir}/crm_data.py list-engagements --contact-ids '["CON-1001"]'
python3 {baseDir}/crm_data.py list-engagements --company-ids '["COMP-2001"]'

# Delete an engagement
python3 {baseDir}/crm_data.py delete-engagement --id ENG-5001
```

### Engagement Types

| Type | Description |
|------|-------------|
| `EMAIL` | Email communication |
| `CALL` | Phone call |
| `NOTE` | Internal note |

## Utility

```bash
# Show raw data
python3 {baseDir}/crm_data.py show --offset 0 --limit 100

# Reset to initial state
python3 {baseDir}/crm_data.py reset
```

## Data Entities

The CRM system holds:

- **Contacts** -- individual people (id, full_name, email, phone, company_id, jobtitle, address, etc.)
- **Companies** -- organizations (id, name, industry, contact_ids, domain, annualrevenue, numberofemployees, etc.)
- **Deals** -- sales opportunities (id, dealname, dealstage, company_id, amount, closedate, pipeline, etc.)
- **Leads** -- prospective clients (id, full_name, email, company_id, rating, leadsource, notes, etc.)
- **Engagements** -- interaction records (id, engagement_type, body, contact_ids, company_ids, title, etc.)

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all companies" | `show` or `search-companies --name ""` |
| "Find contact Lisa Chen" | `search-contacts --full-name "Lisa Chen"` |
| "What deals are in the pipeline?" | `search-deals --dealname ""` |
| "Show me the Chen Family deal" | `search-deals --dealname "Chen"` |
| "What's the status of the Alvarez deal?" | `search-deals --dealname "Alvarez"` |
| "Log a call with a client" | `create-engagement --engagement-type CALL --body "..."` |
| "Move deal to closed won" | `update-deal-stage --id DEAL-X --dealstage closedwon` |
| "Who are our hot leads?" | `search-leads` then filter by rating |
| "Show engagement history for Chen" | `list-engagements --company-ids '["COMP-X"]'` |
