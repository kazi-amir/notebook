---
name: fintrack
description: Manage users, bank accounts, transactions, and subscriptions for a personal finance tracker. Use when the user asks about account balances, transaction history, spending analysis, or subscription management.
---

# FinTrack Personal Finance

Manage users, accounts, transactions, and subscriptions for personal finance tracking. Data is pre-loaded. No setup needed.

## Users

```bash
# List all users
python3 {baseDir}/fintrack_data.py users

# Get a specific user
python3 {baseDir}/fintrack_data.py user --id U001

# Search users by name or email
python3 {baseDir}/fintrack_data.py search-users --query "John"
```

## Accounts

```bash
# List all accounts
python3 {baseDir}/fintrack_data.py accounts

# Get a specific account
python3 {baseDir}/fintrack_data.py account --id A001

# Get all accounts for a user
python3 {baseDir}/fintrack_data.py accounts-by-user --user-id U001

# Search accounts by institution, type, or status
python3 {baseDir}/fintrack_data.py search-accounts --institution "Chase" --type "checking" --status "active"
```

### Account Filters

| Filter | Flag | Example |
|--------|------|---------|
| Institution | `--institution` | `--institution "Chase"` |
| Type | `--type` | `--type "checking"` |
| Status | `--status` | `--status "active"` |
| Limit | `--limit` | `--limit 20` |

## Transactions

```bash
# List all transactions
python3 {baseDir}/fintrack_data.py transactions --limit 50

# Get a specific transaction
python3 {baseDir}/fintrack_data.py transaction --id T001

# Get transactions for a user
python3 {baseDir}/fintrack_data.py transactions-by-user --user-id U001 --limit 20

# Search transactions by merchant, category, date, or amount
python3 {baseDir}/fintrack_data.py search-transactions --merchant "Amazon" --category "Shopping"
python3 {baseDir}/fintrack_data.py search-transactions --start "2026-03-01" --end "2026-03-15"
python3 {baseDir}/fintrack_data.py search-transactions --min-amount 100 --max-amount 500
python3 {baseDir}/fintrack_data.py search-transactions --user-id U001 --category "Groceries"

# Get spending breakdown by category for a user
python3 {baseDir}/fintrack_data.py spending-by-category --user-id U001
python3 {baseDir}/fintrack_data.py spending-by-category --user-id U001 --start "2026-02-01" --end "2026-02-28"
```

### Transaction Filters

| Filter | Flag | Example |
|--------|------|---------|
| Merchant | `--merchant` | `--merchant "Amazon"` |
| Category | `--category` | `--category "Groceries"` |
| Date range | `--start`, `--end` | `--start "2026-03-01" --end "2026-03-15"` |
| Amount range | `--min-amount`, `--max-amount` | `--min-amount 50 --max-amount 200` |
| User | `--user-id` | `--user-id U001` |
| Limit | `--limit` | `--limit 20` |

## Subscriptions

```bash
# List all subscriptions
python3 {baseDir}/fintrack_data.py subscriptions

# Get a specific subscription
python3 {baseDir}/fintrack_data.py subscription --id S001

# Get subscriptions for a user
python3 {baseDir}/fintrack_data.py subscriptions-by-user --user-id U001

# Get all active subscriptions
python3 {baseDir}/fintrack_data.py active-subscriptions

# Get upcoming billings within N days
python3 {baseDir}/fintrack_data.py upcoming-billings --days 7
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all users" | `users` |
| "What accounts does user U001 have?" | `accounts-by-user --user-id U001` |
| "Show my Chase accounts" | `search-accounts --institution "Chase"` |
| "What did I spend at Amazon?" | `search-transactions --merchant "Amazon"` |
| "How much did I spend on groceries?" | `search-transactions --category "Groceries"` |
| "Spending breakdown for March" | `spending-by-category --user-id U001 --start "2026-03-01" --end "2026-03-31"` |
| "Transactions over $500" | `search-transactions --min-amount 500` |
| "What subscriptions do I have?" | `subscriptions-by-user --user-id U001` |
| "What bills are coming up?" | `upcoming-billings --days 7` |
| "Show active subscriptions" | `active-subscriptions` |
