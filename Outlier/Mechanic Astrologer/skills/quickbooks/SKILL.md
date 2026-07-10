---
name: quickbooks
description: Manage customers, vendors, invoices, bills, and accounts via the QuickBooks accounting platform. Use when the user asks about accounting, invoices, bills, vendors, customers, chart of accounts, or financial records.
---

# QuickBooks

Manage customers, vendors, invoices, bills, and accounts. Data is pre-loaded. No API key or setup needed.

## Customers

```bash
# Search customers (all)
python3 {baseDir}/quickbooks_data.py search-customers --fetch-all

# Search customers with criteria
python3 {baseDir}/quickbooks_data.py search-customers \
    --criteria '[{"field": "DisplayName", "value": "Corp", "operator": "LIKE"}]'

# Search customers with limit and sorting
python3 {baseDir}/quickbooks_data.py search-customers --limit 10 --desc Balance

# Get a specific customer by ID
python3 {baseDir}/quickbooks_data.py get-customer --id CUST-1001

# Create a new customer
python3 {baseDir}/quickbooks_data.py create-customer --display-name "Jane Smith" \
    --given-name Jane --family-name Smith --email jane@example.com --phone 555-1234
```

## Vendors

```bash
# Search vendors (all)
python3 {baseDir}/quickbooks_data.py search-vendors --fetch-all

# Search vendors with criteria
python3 {baseDir}/quickbooks_data.py search-vendors \
    --criteria '[{"field": "CompanyName", "value": "Supply", "operator": "LIKE"}]'

# Get a specific vendor by ID
python3 {baseDir}/quickbooks_data.py get-vendor --id VEND-2001

# Create a new vendor
python3 {baseDir}/quickbooks_data.py create-vendor --display-name "Acme Supply Co" \
    --company-name "Acme Supply Co" --email acme@example.com
```

## Invoices

```bash
# Search invoices (all)
python3 {baseDir}/quickbooks_data.py search-invoices

# Search invoices with criteria (open balances)
python3 {baseDir}/quickbooks_data.py search-invoices \
    --criteria '{"Balance": {"$gt": 0}}'

# Get a specific invoice
python3 {baseDir}/quickbooks_data.py get-invoice --id INV-3001

# Create an invoice
python3 {baseDir}/quickbooks_data.py create-invoice \
    --customer-ref '{"value": "CUST-1001"}' \
    --line-items '[{"Description": "Consulting", "Amount": 500, "DetailType": "SalesItemLineDetail"}]' \
    --txn-date 2026-04-01
```

## Bills

```bash
# Search bills (all)
python3 {baseDir}/quickbooks_data.py search-bills --fetch-all

# Search bills with criteria
python3 {baseDir}/quickbooks_data.py search-bills \
    --criteria '[{"field": "TotalAmt", "value": 1000, "operator": ">="}]'

# Get a specific bill
python3 {baseDir}/quickbooks_data.py get-bill --id BILL-4001

# Create a bill
python3 {baseDir}/quickbooks_data.py create-bill \
    --vendor-ref '{"value": "VEND-2001"}' \
    --line '[{"Description": "Office Supplies", "Amount": 250, "DetailType": "AccountBasedExpenseLineDetail"}]' \
    --due-date 2026-05-01
```

## Accounts

```bash
# Search accounts (all)
python3 {baseDir}/quickbooks_data.py search-accounts --fetch-all

# Search accounts by type
python3 {baseDir}/quickbooks_data.py search-accounts \
    --criteria '[{"field": "AccountType", "value": ["Bank", "Expense"], "operator": "IN"}]'

# Create an account
python3 {baseDir}/quickbooks_data.py create-account \
    --name "Office Supplies" --type Expense --sub-type OfficeGeneralAdministrativeExpenses

# Update an account
python3 {baseDir}/quickbooks_data.py update-account --id ACCT-5001 \
    --patch '{"Name": "Updated Office Supplies"}'
```

## Utility

```bash
# Show raw data
python3 {baseDir}/quickbooks_data.py show --offset 0 --limit 100

# Reset to initial state
python3 {baseDir}/quickbooks_data.py reset
```

## Search Criteria

Search tools accept `--criteria` as a JSON array of objects with the following operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal (default) | `{"field": "Active", "value": true}` |
| `<` | Less than | `{"field": "Balance", "value": 1000, "operator": "<"}` |
| `>` | Greater than | `{"field": "Balance", "value": 0, "operator": ">"}` |
| `<=` | Less than or equal | `{"field": "TotalAmt", "value": 5000, "operator": "<="}` |
| `>=` | Greater than or equal | `{"field": "TotalAmt", "value": 100, "operator": ">="}` |
| `LIKE` | Contains (case-insensitive) | `{"field": "DisplayName", "value": "Corp", "operator": "LIKE"}` |
| `IN` | In list | `{"field": "AccountType", "value": ["Bank", "Expense"], "operator": "IN"}` |

## Account Types

| Type | Classification |
|------|----------------|
| Bank | Asset |
| Other Current Asset | Asset |
| Fixed Asset | Asset |
| Accounts Receivable | Asset |
| Accounts Payable | Liability |
| Credit Card | Liability |
| Long Term Liability | Liability |
| Equity | Equity |
| Income | Revenue |
| Other Income | Revenue |
| Expense | Expense |
| Other Expense | Expense |
| Cost of Goods Sold | Expense |

## Data Entities

The QuickBooks system holds:

- **Customers** -- entities billed for goods/services (Id, DisplayName, GivenName, FamilyName, Balance, BillAddr, etc.)
- **Vendors** -- suppliers and service providers (Id, DisplayName, CompanyName, Balance, Vendor1099, etc.)
- **Invoices** -- amounts owed by customers (Id, DocNumber, CustomerRef, TxnDate, DueDate, TotalAmt, Balance, Line items)
- **Bills** -- amounts owed to vendors (Id, DocNumber, VendorRef, TxnDate, DueDate, TotalAmt, Balance, Line items)
- **Accounts** -- chart of accounts (Id, Name, AccountType, Classification, CurrentBalance, Active)
- **Items** -- products/services used on invoice and bill line items (Id, Name, UnitPrice, Taxable)

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all customers" | `search-customers --fetch-all` |
| "Look up customer CUST-1001" | `get-customer --id CUST-1001` |
| "Find customers named Chen" | `search-customers --criteria '[{"field": "DisplayName", "value": "Chen", "operator": "LIKE"}]'` |
| "What invoices are open?" | `search-invoices` then filter on balance > 0 |
| "Show me vendor bills" | `search-bills --fetch-all` |
| "What accounts do we have?" | `search-accounts --fetch-all` |
| "Create an invoice for customer X" | `create-invoice --customer-ref '{"value": "X"}' --line-items '[...]'` |
| "What's the total amount owed?" | `search-invoices` then sum balances |
