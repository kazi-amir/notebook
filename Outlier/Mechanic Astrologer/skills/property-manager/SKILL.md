---
name: property-manager
description: Orchestrate property management workflows across Buildium, Stripe, email, contacts, and calendar. Use when the user asks about rent collection, maintenance coordination, lease renewals, tenant onboarding, or any task that spans multiple property management systems.
---

# Property Manager

Orchestrate tenant and property workflows across five systems:

| System | What it holds | Skill script |
|--------|---------------|--------------|
| **Buildium** | Properties, units, tenants, leases, work orders, vendors, applicants | `buildium_data.py` |
| **Stripe** | Customers, invoices, payments, charges, payment methods | `stripe_data.py` |
| **Email** | Tenant/contractor correspondence (inbox + sent) | Email MCP tools |
| **Contacts** | Tenant and contractor contact info | Contacts MCP tools |
| **Calendar** | Maintenance visits, lease expiration reminders | Calendar MCP tools |

## Cross-System Correlation

### Linking records across systems

Stripe stores linkage metadata on every customer and invoice:

```
customer.metadata: { tenant_id, unit_id, unit_number, property_id, property_name }
invoice.metadata:  { payment_id, tenant_id, unit_id, unit_number, property_id, property_name, payment_method, original_status }
```

**Buildium → Stripe**: Look up tenant in Buildium (get tenant_id), then search Stripe customers by metadata or by tenant name/email.

**Stripe → Buildium**: Read invoice metadata to get `tenant_id` / `unit_id`, then look up in Buildium.

**Email → Tenant**: Match email sender address against Buildium tenant email or Contacts entries.

**Calendar → Buildium**: Calendar event locations contain unit/property names. Work order numbers appear in maintenance event descriptions.

### Maintaining metadata when creating records

**IMPORTANT**: When creating or updating records in any system, always include cross-reference identifiers so the agent (or a future agent) can correlate records across systems without fuzzy matching.

#### Stripe — always set metadata on customers and invoices

When creating a Stripe customer for a tenant, include metadata linking back to Buildium:

```json
{
  "metadata": {
    "tenant_id": "5",
    "unit_id": "12",
    "unit_number": "301",
    "property_id": "3",
    "property_name": "Riverside Commons"
  }
}
```

When creating a Stripe invoice, include the same plus payment context:

```json
{
  "metadata": {
    "tenant_id": "5",
    "unit_id": "12",
    "unit_number": "301",
    "property_id": "3",
    "property_name": "Riverside Commons",
    "payment_method": "online_portal",
    "original_status": "pending"
  }
}
```

#### Calendar — use structured titles, locations, and descriptions

When creating calendar events, embed identifiers in the fields so they are searchable:

- **Title**: Include the type and key detail, e.g., `"Maintenance: Leaking faucet"` or `"Lease Expiration: Maria Garcia"`
- **Location**: Always include unit and property, e.g., `"Unit 301, Riverside Commons, 4210 Riverside Dr"`
- **Description**: Include work order number, tenant name, priority, contractor — any details that help cross-reference, e.g., `"Work Order: MR-2015\nPriority: high\nContractor: Mike's Plumbing"`
- **Tag**: Use consistent tags: `"Maintenance"`, `"Lease"`
- **Attendees**: Include contractor/vendor name or tenant name

#### Contacts — use description for role context

When adding contacts, include their role and location in the `description` field:

- Tenants: `"Tenant at Riverside Commons, Unit 301"`
- Contractors: `"Contractor — Plumbing, water heaters, leaks"`

This allows `contacts search` to find people by property name or trade.

#### Email — use subject lines for traceability

When sending emails, use structured subjects that reference the unit/property:

- `"Rent Reminder — Unit 301, Riverside Commons — March 2026"`
- `"Maintenance Update — MR-2015 — Leaking faucet, Unit 301"`
- `"Lease Renewal Offer — Unit 204, Oak Hill Apartments"`

This ensures `email search` can find all correspondence related to a unit, property, or work order.

## Workflows

### 1. Rent Collection — Check overdue payments

```bash
# Step 1: Get open (unpaid) invoices from Stripe
python3 {baseDir}/../stripe/stripe_data.py invoices --status open

# Step 2: For each overdue invoice, get tenant details from metadata
# The invoice metadata has tenant_id, unit_number, property_name

# Step 3: Look up tenant contact info in Buildium
python3 {baseDir}/../buildium/buildium_data.py tenant --id <tenant_id>

# Step 4: Check if a reminder email was already sent
# Search emails by tenant's email address using Email MCP tools
```

### 2. Maintenance Request — End to end

```bash
# Step 1: Review open work orders
python3 {baseDir}/../buildium/buildium_data.py work-orders --status open --priority high

# Step 2: Find the right vendor for the category
python3 {baseDir}/../buildium/buildium_data.py vendors --category plumbing

# Step 3: Check tenant's email about the issue
# Search emails by tenant email address or subject keywords

# Step 4: Check calendar for scheduling conflicts
# Search calendar events for the unit/property
```

### 3. Lease Renewal — Expiring leases

```bash
# Step 1: Get leases expiring within 60 days
python3 {baseDir}/../buildium/buildium_data.py expiring-leases --within-days 60

# Step 2: Check tenant payment history (are they a good tenant?)
python3 {baseDir}/../stripe/stripe_data.py invoices --customer-id <cus_id>

# Step 3: Check for any open maintenance complaints
python3 {baseDir}/../buildium/buildium_data.py work-orders --status open

# Step 4: Check calendar for the lease expiration event
# Review calendar events tagged "Lease"

# Step 5: Draft renewal email to tenant
# Compose via Email MCP tools
```

### 4. Tenant Onboarding — New move-in

```bash
# Step 1: Review the applicant
python3 {baseDir}/../buildium/buildium_data.py applicant --id <applicant_id>

# Step 2: Check the unit is actually vacant
python3 {baseDir}/../buildium/buildium_data.py unit --id <unit_id>

# Step 3: After approval, create tenant + lease in Buildium
# Note the tenant_id and unit_id returned

# Step 4: Create Stripe customer WITH metadata (critical for cross-referencing)
# Include: tenant_id, unit_id, unit_number, property_id, property_name

# Step 5: Add tenant to contacts with role description
# Description: "Tenant at <property_name>, Unit <unit_number>"

# Step 6: Send welcome email with structured subject
# Subject: "Welcome — Unit <unit_number>, <property_name>"

# Step 7: Schedule move-in event on calendar
# Title: "Move-in: <tenant_name>"
# Location: "Unit <unit_number>, <property_name>, <address>"
```

### 5. Vacancy Management — Fill empty units

```bash
# Step 1: Find all vacant units
python3 {baseDir}/../buildium/buildium_data.py units --status vacant

# Step 2: Check pending applications for those units
python3 {baseDir}/../buildium/buildium_data.py applicants --status pending

# Step 3: Review applicant financials (credit score, income)
python3 {baseDir}/../buildium/buildium_data.py applicant --id <applicant_id>
```

### 6. Portfolio Overview — Dashboard

```bash
# Property/tenant summary
python3 {baseDir}/../buildium/buildium_data.py dashboard

# Work order statistics
python3 {baseDir}/../buildium/buildium_data.py work-order-stats

# Revenue overview (paid invoices)
python3 {baseDir}/../stripe/stripe_data.py invoices --status paid --limit 50

# Upcoming lease expirations
python3 {baseDir}/../buildium/buildium_data.py expiring-leases --within-days 90
```

## Answering Questions

| User asks | Workflow |
|-----------|----------|
| "Who owes rent?" | Stripe: `invoices --status open` → read metadata for tenant/unit |
| "Handle maintenance for unit 301" | Buildium: `work-orders` for unit → find vendor → check emails → schedule |
| "Any leases expiring soon?" | Buildium: `expiring-leases --within-days 60` → check payment history → draft renewal |
| "Onboard new tenant Sam Chen" | Buildium: `applicant --id N` → verify unit → create tenant/lease → Stripe customer → welcome email |
| "Give me a portfolio summary" | Buildium: `dashboard` + `work-order-stats` → Stripe: revenue → leases expiring |
| "What's the status of the plumbing issue at Riverside?" | Buildium: `search-work-orders --query plumbing` → check emails → check calendar |
| "How is tenant Maria Garcia doing?" | Buildium: `search-tenants --query "Maria Garcia"` → Stripe: payment history → emails |
| "Show me all vacant units" | Buildium: `units --status vacant` → check pending applicants |
| "Any urgent maintenance?" | Buildium: `work-orders --priority urgent --status open` |
| "Revenue this month?" | Stripe: `invoices --status paid` → filter by due_date → sum amounts |

## References

- `{baseDir}/references/workflows.md` — step-by-step procedures for common property management tasks
