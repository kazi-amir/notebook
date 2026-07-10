---
name: stripe
description: Manage customers, invoices, payments, subscriptions, refunds, and billing via the Stripe platform. Use when the user asks about payments, invoices, billing, subscriptions, or financial transactions.
---

# Stripe

Manage customers, invoices, payments, subscriptions, and billing. Data is pre-loaded. No Stripe API key needed.

## Customers

```bash
# List customers
python3 {baseDir}/stripe_data.py customers --limit 20

# Get a specific customer
python3 {baseDir}/stripe_data.py customer --id cus_abc123

# Search customers by name or email
python3 {baseDir}/stripe_data.py search-customers --query "Smith"

# Get customer's payment methods
python3 {baseDir}/stripe_data.py payment-methods --customer-id cus_abc123
```

## Invoices

```bash
# List invoices (optionally filter)
python3 {baseDir}/stripe_data.py invoices --status paid --customer-id cus_abc123

# Get a specific invoice
python3 {baseDir}/stripe_data.py invoice --id in_abc123

# Get invoice line items
python3 {baseDir}/stripe_data.py invoice-items --invoice-id in_abc123
```

### Invoice Filters

| Filter | Flag | Example |
|--------|------|---------|
| Status | `--status` | `--status paid` (draft, open, paid, void, uncollectible) |
| Customer | `--customer-id` | `--customer-id cus_abc123` |
| Limit | `--limit` | `--limit 50` |

## Payments

```bash
# List payment intents
python3 {baseDir}/stripe_data.py payments --customer-id cus_abc123 --status succeeded

# Get a specific payment intent
python3 {baseDir}/stripe_data.py payment --id pi_abc123

# List charges
python3 {baseDir}/stripe_data.py charges --customer-id cus_abc123
```

## Products & Prices

```bash
# List products
python3 {baseDir}/stripe_data.py products

# Get a specific product
python3 {baseDir}/stripe_data.py product --id prod_abc123

# List prices for a product
python3 {baseDir}/stripe_data.py prices --product-id prod_abc123
```

## Subscriptions

```bash
# List subscriptions
python3 {baseDir}/stripe_data.py subscriptions --customer-id cus_abc123 --status active

# Get a specific subscription
python3 {baseDir}/stripe_data.py subscription --id sub_abc123
```

## Refunds & Disputes

```bash
# List refunds
python3 {baseDir}/stripe_data.py refunds --charge-id ch_abc123

# List disputes
python3 {baseDir}/stripe_data.py disputes --status warning_needs_response
```

## Account & Balance

```bash
# Get account info
python3 {baseDir}/stripe_data.py account

# List balance transactions
python3 {baseDir}/stripe_data.py balance-transactions --limit 20
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all unpaid invoices" | `invoices --status open` |
| "How much does tenant X owe?" | `search-customers --query "X"` then `invoices --customer-id ID --status open` |
| "Show payment history for unit 301" | `search-customers --query "301"` (metadata has unit info) then `invoices --customer-id ID` |
| "Any overdue rent payments?" | `invoices --status open` |
| "What payment method does tenant use?" | `payment-methods --customer-id ID` |
| "Total revenue this month?" | `charges --status succeeded` and sum amounts |
| "Show me invoice details" | `invoice --id in_xxx` then `invoice-items --invoice-id in_xxx` |
| "Any refunds issued?" | `refunds` |
| "What products do we bill for?" | `products` |

## Metadata

Customer and invoice records contain `metadata` with cross-references to the property management system:

- **Customer metadata**: `tenant_id`, `unit_id`, `unit_number`, `property_id`, `property_name`
- **Invoice metadata**: `payment_id`, `tenant_id`, `unit_id`, `unit_number`, `property_id`, `property_name`, `payment_method`, `original_status`

Use these to correlate payment data with Buildium property/tenant records.
