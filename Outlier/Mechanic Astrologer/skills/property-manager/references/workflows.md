# Property Management Workflows

## Rent Collection — Check overdue payments

1. Find open (unpaid) invoices: `stripe_data.py invoices --status open`
2. Read invoice `metadata` to get `tenant_id`, `unit_number`, `property_name`
3. Look up tenant contact info: `buildium_data.py tenant --id <tenant_id>`
4. Check if a reminder was already sent: search emails by tenant's email address
5. If needed, send reminder email with structured subject referencing the unit/property

## Maintenance Coordination

1. Review open work orders: `buildium_data.py work-orders --status open`
2. Get work order details: `buildium_data.py work-order --id <N>`
3. Find a vendor matching the category: `buildium_data.py vendors --category <category>`
4. Check tenant's original email about the issue: search emails by tenant email or keywords
5. Check calendar for scheduling conflicts: search calendar events for the unit/property
6. Schedule the visit: create a calendar event with tag `"Maintenance"`, location including unit/property, contractor as attendee
7. After completion: update work order status and actual cost in Buildium

## Lease Renewal

1. Identify expiring leases: `buildium_data.py expiring-leases --within-days 60`
2. For each tenant, check payment history: `stripe_data.py invoices --customer-id <cus_id>`
3. Check for open maintenance complaints: `buildium_data.py work-orders --status open`
4. Check calendar for the lease expiration event: search by tag `"Lease"`
5. Send renewal offer or non-renewal notice via email
6. Update lease status and dates in Buildium upon agreement

## Tenant Onboarding

1. Review application: `buildium_data.py applicant --id <N>` — check credit score, income
2. Verify unit is vacant: `buildium_data.py unit --id <unit_id>`
3. Update applicant status in Buildium
4. Create tenant and lease records in Buildium — note the returned `tenant_id` and `unit_id`
5. Create Stripe customer with metadata: `tenant_id`, `unit_id`, `unit_number`, `property_id`, `property_name`
6. Add tenant to contacts with description: `"Tenant at <property_name>, Unit <unit_number>"`
7. Send welcome email with structured subject
8. Schedule move-in event on calendar

## Vacancy Management

1. Find vacant units: `buildium_data.py units --status vacant`
2. Check pending applications: `buildium_data.py applicants --status pending`
3. Review applicant details: `buildium_data.py applicant --id <N>`
4. Process top applicants through onboarding workflow above

## Portfolio Overview

1. Get property/tenant summary: `buildium_data.py dashboard`
2. Get work order statistics: `buildium_data.py work-order-stats`
3. Review paid invoices for revenue: `stripe_data.py invoices --status paid --limit 50`
4. Check upcoming lease expirations: `buildium_data.py expiring-leases --within-days 90`
