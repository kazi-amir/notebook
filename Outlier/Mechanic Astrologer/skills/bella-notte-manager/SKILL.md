---
name: bella-notte-manager
description: Orchestrate restaurant management workflows for Bella Notte Ristorante across QuickBooks, CRM, Stripe, Airtable, Notion, Slack, email, contacts, calendar, reminders, Instacart, Amazon Fresh, and Shopping. Use when the user asks about catering events, vendor orders, staff scheduling, financial reporting, register discrepancies, health inspections, menu planning, weekly P&L reports, food costs, supply ordering, payroll, or anything about running Bella Notte — even if the question only touches one system, this skill knows how to correlate data across all 13 connected systems. Also use when the user mentions specific people like Giancarlo, Carmen, Tony, or specific clients like Chen Wedding, Johnson Corp, or Alvarez.
---

# Bella Notte Restaurant Manager

Orchestrate restaurant operations for Bella Notte Ristorante — a fine-dining Italian restaurant in Milwaukee, WI. Victor Reyes is the General Manager, reporting to semi-retired owner Giancarlo Moretti.

## Systems Overview

| System | What it holds | Access via |
|--------|---------------|------------|
| **QuickBooks** | Restaurant financials: customers, vendors, invoices, bills, payroll, chart of accounts | QuickBooks MCP tools |
| **CRM** | Catering pipeline: companies, contacts, deals (stages + amounts), engagement history | CRM MCP tools |
| **Stripe** | Catering deposit payments, gift card sales, reservation deposits | Stripe MCP tools |
| **Airtable** | Staff schedules, register close-out logs, temperature logs | Airtable MCP tools |
| **Notion** | Daily manager log (covers, revenue, incidents), kitchen SOPs, catering event tracker | Notion MCP tools |
| **Slack** | Team communications: #kitchen, #front-of-house, #management, #catering, #general | Slack MCP tools |
| **Email** | Vendor contracts, catering proposals, health inspection results, owner correspondence | Email MCP tools |
| **Contacts** | Staff, vendors, suppliers, catering clients, health inspector | Contacts MCP tools |
| **Calendar** | Owner calls, staff meetings, health inspections, catering events | Calendar MCP tools |
| **Reminder** | Recurring restaurant tasks: Sysco orders, payroll, P&L reports, license renewals | Reminder MCP tools |
| **Instacart** | Emergency restaurant supply orders (when Sysco is late/short) | Instacart MCP tools |
| **Amazon Fresh** | Backup bulk supply orders (dairy, pasta, produce for Sysco gaps) | Amazon Fresh MCP tools |
| **Shopping** | Operational supplies: gloves, sanitizer, receipt paper, thermometers, cleaning products | Shopping MCP tools |

## Cross-System Correlation

### Catering clients across systems

A single catering client (e.g., Chen Wedding, Johnson Corp, Alvarez Quinceañera) appears in:
- **CRM**: Deal pipeline with stage, amount, engagement history
- **Stripe**: Deposit payment (amounts in cents) with `metadata.invoice_id` linking to QuickBooks
- **QuickBooks**: Invoice records (deposits + final balances) and customer records
- **Contacts**: Personal contact info for the client
- **Email**: Proposal and correspondence threads

Match across systems by **client name** or **email address**.

### Vendors across systems

Each vendor (Sysco, US Foods, Capital Wine, Milwaukee Bread, Linen & Things) appears in:
- **Contacts**: Rep's direct phone/email and account number in description (e.g., "Account SYSC-4412")
- **QuickBooks**: Vendor account with balance, bills, payment terms
- **Email**: Contract renewals, price negotiations, delivery issues
- **Instacart / Amazon Fresh**: Emergency backup orders when primary vendor is short

Match by **vendor name** or **account number** (SYSC-4412, CWI-1155, USF-7890, MBC-0302, LTC-5567).

### Staff across systems

Each staff member appears in:
- **Contacts**: Personal info, phone, notes (scheduling constraints, sensitive info)
- **Slack**: User profile and team communications
- **Airtable**: Shift schedules and register close-out records
- **Notion**: Manager log entries referencing performance and incidents

Match by **full name** (Slack `real_name` = Contacts `first_name` + `last_name`).

### Key identifiers

| Entity | Identifier | Found in |
|--------|-----------|----------|
| Catering clients | Email address | CRM contacts, Stripe customers, QuickBooks customers, Contacts |
| Vendors | Account number | Contacts description, QuickBooks vendor records, Email threads |
| Staff | Full name | Contacts, Slack users, Airtable schedules, Notion logs |
| Invoices | Invoice ID (INV-3001, etc.) | QuickBooks invoices, Stripe payment_intent metadata |

## Workflows

### 1. Weekly Owner Reporting (Giancarlo Moretti)

Every Thursday, Victor sends a P&L summary before the 2 PM owner call.

```
Step 1: QuickBooks — Pull revenue, COGS, and expense accounts for the week
        → quickbooks_search_accounts
Step 2: Notion — Review daily manager logs for the week (covers, revenue, 86'd items, incidents)
        → Notion MCP tools (search "Daily Manager Log" database)
Step 3: CRM — Check catering pipeline updates (new deals, deposits received)
        → crm_search_deals
Step 4: Email — Draft and send P&L summary to giancarlo.moretti@gmail.com
        → Email MCP tools
Step 5: Calendar — Confirm Thursday 2 PM call is on schedule
        → calendar_search_events (query "Giancarlo")
```

### 2. Catering Event Lifecycle

From inquiry through event completion.

```
INQUIRY:
Step 1: CRM — Create company + contact, log engagement (CALL or EMAIL)
Step 2: CRM — Create deal with stage "appointmentscheduled"
Step 3: Email — Send catering proposal to client

DEPOSIT:
Step 4: Stripe — Verify deposit payment received
Step 5: QuickBooks — Create invoice, mark as paid
Step 6: CRM — Update deal stage to "contractsent"
Step 7: Slack — Post update to #catering channel

EVENT PREP:
Step 8: Notion — Create catering event entry with menu, timeline, staffing plan
Step 9: Airtable — Schedule extra staff shifts for the event
Step 10: Calendar — Add event with all staff attendees

POST-EVENT:
Step 11: QuickBooks — Invoice final balance
Step 12: CRM — Update deal stage to "closedwon", log completion engagement
Step 13: Notion — Log event recap in manager log
```

### 3. Vendor Order Management

When Sysco or another primary vendor is late or short on delivery.

```
Step 1: Slack — Check #kitchen for delivery issue reports
Step 2: Email — Check vendor correspondence about the shortage
Step 3: Contacts — Look up vendor rep contact info for follow-up
Step 4: Instacart or Amazon Fresh — Place emergency backup order
        (Instacart for produce/dairy/herbs, Amazon Fresh for bulk staples/pasta)
Step 5: QuickBooks — Check vendor bill status and outstanding balances
Step 6: Notion — Log the supply issue in the daily manager log
```

### 4. Staff Scheduling & Register Investigation

```
SCHEDULING:
Step 1: Airtable — View/update staff schedule in "Staff Schedule" table
Step 2: Contacts — Check scheduling constraints in contact notes
        (e.g., Jessica and Ryan must not be scheduled together)
Step 3: Slack — Post schedule updates to #front-of-house or #general

REGISTER INVESTIGATION:
Step 4: Airtable — Pull register close-out log entries, filter by closer name
Step 5: Notion — Review daily manager log entries flagged with register issues
Step 6: Notion — Update investigation notes with running totals and pattern analysis
```

### 5. Health Inspection Preparation

Quarterly inspections by James Okonkwo, Milwaukee Health Department.

```
Step 1: Calendar — Check inspection date window
        → calendar_search_events (query "health inspection")
Step 2: Airtable — Verify walk-in cooler and freezer temperature logs are current
Step 3: Notion — Review kitchen SOPs (opening/closing checklists, HACCP procedures)
Step 4: Slack — Post prep reminders to #kitchen and #management
Step 5: Shopping — Order compliance supplies (thermometers, sanitizer, labels, first aid)
        → shopping_search_product, shopping_add_to_cart, shopping_checkout
Step 6: Contacts — Confirm inspector contact info
        → contacts_search_contacts (query "Okonkwo")
```

### 6. Financial Overview

```
RESTAURANT FINANCES:
Step 1: QuickBooks — Pull account balances (operating checking, AR, AP, catering deposits held)
        → quickbooks_search_accounts
Step 2: QuickBooks — Review open invoices (final balances due from catering clients)
        → quickbooks_search_invoices
Step 3: QuickBooks — Review unpaid vendor bills
        → quickbooks_search_bills
Step 4: Stripe — Check recent deposit payments and gift card sales
        → stripe_list_payment_intents, stripe_list_charges

PAYROLL:
Step 5: QuickBooks — Review payroll records (biweekly, 25 employees)
Step 6: Reminder — Check next payroll processing date
Step 7: Airtable — Cross-reference staff hours from schedule
```

### 7. Supply Procurement

Three channels for restaurant supplies, each serving a different need.

```
ROUTINE (Sysco / US Foods):
Step 1: Reminder — Check weekly Sysco order reminder (Sundays)
Step 2: QuickBooks — Review recent Sysco/US Foods bills for spending trends
Step 3: Email — Check for pricing changes or delivery schedule updates

EMERGENCY (Instacart / Amazon Fresh):
Step 4: Instacart — Search catalog and order perishables (cream, herbs, cheese, spirits)
Step 5: Amazon Fresh — Order bulk staples (olive oil, canned tomatoes, pasta, eggs)
        Restaurant orders deliver to: 2215 N. Farwell Ave

OPERATIONAL (Shopping):
Step 6: Shopping — Order non-food supplies (gloves, sanitizer, receipt paper, cleaning products)
Step 7: Shopping — Check order history for reorder timing
```

## Answering Questions

| User asks | Workflow |
|-----------|----------|
| "What catering events are coming up?" | CRM: search deals → Calendar: search events → QuickBooks: check invoices |
| "Did the Chen wedding deposit come in?" | Stripe: search customers/payments → QuickBooks: check invoice INV-3001 |
| "How's the restaurant doing financially?" | QuickBooks: accounts + revenue → Notion: manager log → CRM: pipeline total |
| "What happened at the restaurant this week?" | Notion: daily manager logs → Slack: recent messages → Airtable: register log |
| "Is there a Sysco delivery issue?" | Slack: #kitchen messages → Email: Sysco correspondence → Instacart/Amazon Fresh: recent orders |
| "Who's working tonight?" | Airtable: staff schedule for today's date |
| "Any register discrepancies?" | Airtable: register close-out log → Notion: investigation notes |
| "When is the health inspection?" | Calendar: search "health inspection" → Airtable: temp logs current? |
| "What supplies do we need to order?" | Slack: #kitchen requests → Shopping: recent orders → Instacart: order history |
| "How's the quinceañera prep going?" | CRM: Alvarez deal → Notion: catering tracker → Slack: #catering → Calendar: March 22 |
| "Give me the P&L for Giancarlo" | QuickBooks: revenue/expenses → Notion: weekly covers/revenue → Email: draft to Giancarlo |
| "Any urgent staff issues?" | Slack: #management → Notion: manager log (recent) → Contacts: staff notes |
| "What vendor payments are due?" | QuickBooks: search bills (Open) → Contacts: vendor rep info |
| "How's the fish fry series going?" | CRM: St. Boniface deal → Notion: manager log entries → Slack: #catering updates |
| "What's our food cost this month?" | QuickBooks: COGS account → QuickBooks: revenue account → calculate percentage |
| "When's the next owner call?" | Calendar: search "Giancarlo" → Reminder: P&L send reminder |

## Key People (Restaurant)

| Person | Role | Key Systems |
|--------|------|-------------|
| **Victor Reyes** | General Manager (you) | All systems — the logged-in user |
| **Giancarlo Moretti** | Owner (semi-retired, Scottsdale) | Email (weekly P&L), Calendar (Thu 2 PM calls) |
| **Carmen Diaz** | Shift Lead | Slack, Airtable (register closes), Contacts |
| **Tony Aguilar** | Sous Chef | Slack (#kitchen), Notion (SOPs), Calendar (events) |
| **Maria Kowalski** | Head Bartender | Slack, Email (wine vendor CC'd) |
| **Daniela Perez** | FOH Manager | Slack (#front-of-house), Airtable (schedules) |
| **Luis Ochoa** | Line Cook | Slack (#kitchen), Airtable (schedules) |
| **Marco Villareal** | Line Cook | Slack (#kitchen), Airtable (schedules) |
| **Dan Mallory** | Sysco Rep | Email, Contacts (SYSC-4412), QuickBooks (vendor) |
| **Robert Fontaine** | Capital Wine Rep | Email, Contacts (CWI-1155), QuickBooks (vendor) |
| **James Okonkwo** | Health Inspector | Email, Contacts, Calendar (inspections) |

## Operational Notes

- **Scheduling conflict** _(relevant to Workflow 4)_: Jessica Hartmann and Ryan Engel (her ex) must not be scheduled on the same shifts. Check Contacts notes before adjusting schedules.
- **Register investigation** _(relevant to Workflow 4)_: Ongoing pattern of shortages on Carmen Diaz's closes. Documented in Notion manager log and Airtable register close-out log. Not yet reported to owner — handle discreetly.
- **Catering deposits** _(relevant to Workflows 2, 6)_: Held in trust per Wisconsin law. QuickBooks tracks these in "Catering Deposits Held" liability account (ACCT-2100). Must not be commingled with operating funds.
- **Fish fry series** _(relevant to Workflow 2)_: 7-Friday Lenten series for St. Boniface Church (Feb 20 – Apr 3). Tracked in CRM as a deal and in Notion as catering events.
- **Liquor license** _(relevant to Workflow 5)_: WI-MLW-2024-08841, renewal due July 2026. Reminder set for May 1 to start paperwork.
