---
name: amazon-fresh
description: Access Amazon Fresh grocery delivery data — browse products, view order history, track deliveries, analyze spending, and find frequently purchased items. Use when the user asks about grocery orders, spending, product search, delivery status, or shopping habits.
---

# Amazon Fresh

Query grocery product catalog, order history, delivery status, and spending analytics.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/amazon_fresh_data.py login --email your@email.com
```

## Fetching Data

Use `amazon_fresh_data.py` to get JSON data:

```bash
# Search products
python3 {baseDir}/amazon_fresh_data.py search "organic milk"
python3 {baseDir}/amazon_fresh_data.py search "chicken" --category "Meat & Seafood"
python3 {baseDir}/amazon_fresh_data.py search "snacks" --organic --limit 10

# List all categories
python3 {baseDir}/amazon_fresh_data.py categories

# Get product details
python3 {baseDir}/amazon_fresh_data.py product prod_001

# Order history (last 90 days default)
python3 {baseDir}/amazon_fresh_data.py orders --days 30
python3 {baseDir}/amazon_fresh_data.py orders --status delivered --limit 5

# Single order details
python3 {baseDir}/amazon_fresh_data.py order AMF000001

# Spending analytics
python3 {baseDir}/amazon_fresh_data.py spending --days 30
python3 {baseDir}/amazon_fresh_data.py spending --start 2025-11-01 --end 2025-12-31

# Frequently ordered products
python3 {baseDir}/amazon_fresh_data.py favorites --days 90 --limit 10

# Deliveries
python3 {baseDir}/amazon_fresh_data.py deliveries --days 30
python3 {baseDir}/amazon_fresh_data.py deliveries --status pending

# Reorder items from a past order
python3 {baseDir}/amazon_fresh_data.py reorder AMF000001

# User profile
python3 {baseDir}/amazon_fresh_data.py profile

# Account summary
python3 {baseDir}/amazon_fresh_data.py summary --days 30
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What groceries do I usually buy?" | `amazon_fresh_data.py favorites --days 90` |
| "How much did I spend on groceries?" | `amazon_fresh_data.py spending --days 30` |
| "Show my recent orders" | `amazon_fresh_data.py orders --days 30` |
| "Find me organic snacks" | `amazon_fresh_data.py search "snacks" --organic` |
| "When is my delivery?" | `amazon_fresh_data.py deliveries --days 7` |
| "Reorder my last groceries" | `amazon_fresh_data.py orders --limit 1` then `amazon_fresh_data.py reorder <id>` |
| "Give me a grocery summary" | `amazon_fresh_data.py summary --days 30` |
| "What categories are available?" | `amazon_fresh_data.py categories` |
| "Show me details for product X" | `amazon_fresh_data.py product <id>` |
| "How much do I spend per month?" | `amazon_fresh_data.py spending --days 180`, check `by_month` |
| "What's my most expensive order?" | `amazon_fresh_data.py spending --days 90`, check `most_expensive_order` |
| "Am I buying enough produce?" | `amazon_fresh_data.py spending --days 90`, check `by_category` |

## Key Data

- **2200+ products** across 15 categories (Produce, Dairy, Meat & Seafood, Bakery, Beverages, Snacks, Frozen, Pantry, Breakfast, Condiments, Household, Baby, Pet, International, Condiments & Spices)
- **1600+ product variants** (size/quantity options)
- **Orders** include status (delivered, pending, shipped, cancelled), delivery date, delivery slot, and line items
- **Spending** breakdowns available by month and by category

## Analysis Tips

When the user asks about their grocery habits, consider:

- **Spending trends**: Compare monthly totals to spot increases or decreases. The `spending` command provides `by_month` and `by_category` breakdowns.
- **Shopping frequency**: Check order count over time. More than 4 orders/month suggests frequent shopping; fewer than 2 may mean bulk buying.
- **Category balance**: A healthy cart typically has a mix of Produce, Dairy, Meat & Seafood, and Pantry. Heavy Snacks/Frozen spending may indicate room for improvement.
- **Favorites vs variety**: If the same 5-10 items dominate `favorites`, the user has strong preferences. Suggest related products via `search`.
- **Price awareness**: The `reorder` command flags price changes since last purchase — useful for budget-conscious users.
- **Delivery patterns**: Check `deliveries` for preferred time slots and frequency.

## Reference

- `{baseDir}/references/grocery_guide.md` — smart shopping reference with seasonal produce, budget tips, and category balance guidance
