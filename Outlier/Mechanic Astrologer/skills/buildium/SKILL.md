---
name: buildium
description: Manage rental properties, units, tenants, leases, work orders, vendors, and applicants. Use when the user asks about property management, maintenance, tenant info, or lease tracking.
---

# Buildium

Manage a rental property portfolio — properties, units, tenants, leases, maintenance work orders, vendors, and applicants. Data is pre-loaded. No API key needed.

## Properties

```bash
# List all rental properties
python3 {baseDir}/buildium_data.py properties

# Get a specific property with its units
python3 {baseDir}/buildium_data.py property --id 1

# Get preferred vendors for a property
python3 {baseDir}/buildium_data.py property-vendors --id 1
```

## Units

```bash
# List all units (optionally filter)
python3 {baseDir}/buildium_data.py units --status occupied --property-id 1

# Get a specific unit with current tenant
python3 {baseDir}/buildium_data.py unit --id 5

# Search vacant units with minimum bedrooms
python3 {baseDir}/buildium_data.py units --status vacant --min-beds 2 --max-rent 1500
```

### Unit Filters

| Filter | Flag | Example |
|--------|------|---------|
| Status | `--status` | `--status vacant` |
| Property | `--property-id` | `--property-id 3` |
| Min bedrooms | `--min-beds` | `--min-beds 2` |
| Max rent | `--max-rent` | `--max-rent 1800` |
| Limit | `--limit` | `--limit 20` |

## Tenants

```bash
# List all tenants
python3 {baseDir}/buildium_data.py tenants

# Filter by status or property
python3 {baseDir}/buildium_data.py tenants --status active --property-id 2

# Get a specific tenant
python3 {baseDir}/buildium_data.py tenant --id 10

# Search tenants by name or email
python3 {baseDir}/buildium_data.py search-tenants --query "Smith"
```

## Leases

```bash
# List all leases
python3 {baseDir}/buildium_data.py leases

# Get a specific lease
python3 {baseDir}/buildium_data.py lease --id 5

# Get leases expiring within N days
python3 {baseDir}/buildium_data.py expiring-leases --within-days 90
```

## Work Orders (Maintenance)

```bash
# List work orders with filters
python3 {baseDir}/buildium_data.py work-orders --status open --priority high

# Get a specific work order
python3 {baseDir}/buildium_data.py work-order --id 3

# Search work orders
python3 {baseDir}/buildium_data.py search-work-orders --query "plumbing"

# Get work order statistics
python3 {baseDir}/buildium_data.py work-order-stats
```

### Work Order Filters

| Filter | Flag | Example |
|--------|------|---------|
| Status | `--status` | `--status open` (open, in_progress, scheduled, completed) |
| Priority | `--priority` | `--priority urgent` (low, normal, high, urgent) |
| Category | `--category` | `--category plumbing` |
| Property | `--property-id` | `--property-id 1` |
| Limit | `--limit` | `--limit 10` |

## Vendors

```bash
# List all vendors
python3 {baseDir}/buildium_data.py vendors

# Filter by category
python3 {baseDir}/buildium_data.py vendors --category plumbing

# Get a specific vendor
python3 {baseDir}/buildium_data.py vendor --id 2

# List vendor categories
python3 {baseDir}/buildium_data.py vendor-categories
```

## Applicants

```bash
# List applicants
python3 {baseDir}/buildium_data.py applicants --status pending

# Get a specific applicant
python3 {baseDir}/buildium_data.py applicant --id 1
```

## Dashboard

```bash
# Get portfolio overview stats
python3 {baseDir}/buildium_data.py dashboard
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How many properties do we manage?" | `dashboard` |
| "Show me all vacant units" | `units --status vacant` |
| "Who lives in unit 301?" | `unit --id N` or search tenants |
| "Any leases expiring soon?" | `expiring-leases --within-days 60` |
| "What open maintenance requests do we have?" | `work-orders --status open` |
| "Show me urgent work orders" | `work-orders --priority urgent` |
| "Find a plumber" | `vendors --category plumbing` |
| "What's the status of work order MR-2015?" | `search-work-orders --query "MR-2015"` |
| "Any pending rental applications?" | `applicants --status pending` |
| "Details on tenant John Smith" | `search-tenants --query "John Smith"` |
