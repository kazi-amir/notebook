---
name: target
description: Access Target shopping data — search products, view order history, analyze spending patterns, browse departments, categories, and Circle deals. Use when the user asks about Target orders, spending, product search, purchase history, Circle deals, or shopping habits.
---

# Target

Query the Target product catalog, order history, Circle deals, and spending analytics.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/target_data.py login --email your@email.com
```

## Fetching Data

Use `target_data.py` to get JSON data:

```bash
# Search products
python3 {baseDir}/target_data.py search "headphones"
python3 {baseDir}/target_data.py search "throw pillow" --department "Home" --max-price 50
python3 {baseDir}/target_data.py search "baby monitor" --category "Baby" --brand "Owlet"
python3 {baseDir}/target_data.py search "shampoo" --in-stock-only --limit 10
python3 {baseDir}/target_data.py search "snacks" --circle-deals-only

# List all categories
python3 {baseDir}/target_data.py categories

# List all departments
python3 {baseDir}/target_data.py departments

# List brands (optionally by category or department)
python3 {baseDir}/target_data.py brands
python3 {baseDir}/target_data.py brands --department "Electronics" --limit 20
python3 {baseDir}/target_data.py brands --category "Beauty"

# Get Circle member deals
python3 {baseDir}/target_data.py circle-deals --limit 20

# Get product details by product ID
python3 {baseDir}/target_data.py product TGT00000001

# Order history (last 90 days default)
python3 {baseDir}/target_data.py orders --days 30
python3 {baseDir}/target_data.py orders --status delivered --limit 5
python3 {baseDir}/target_data.py orders --start 2025-11-01 --end 2025-12-31

# Single order details
python3 {baseDir}/target_data.py order TGT-M4WAOXHX

# Spending analytics
python3 {baseDir}/target_data.py spending --days 30
python3 {baseDir}/target_data.py spending --start 2025-10-01 --end 2026-01-31

# Frequently purchased products
python3 {baseDir}/target_data.py favorites --days 180 --limit 10

# User profile
python3 {baseDir}/target_data.py profile

# Account summary
python3 {baseDir}/target_data.py summary --days 90
```

## User Question → Command Mapping

| Question | Command |
|----------|---------|
| "Find me a good laptop under $500" | `search "laptop" --max-price 500 --in-stock-only` |
| "What Circle deals are available?" | `circle-deals` |
| "Show my recent Target orders" | `orders --days 30` |
| "How much have I spent at Target?" | `spending --days 90` |
| "What do I buy most often?" | `favorites` |
| "What departments does Target have?" | `departments` |
| "Show me baby products" | `search "baby" --department "Baby"` |

## Key Data Insights

- **~3,600 products** across 11 departments sourced from multiple specialty stores
- **Departments**: Electronics, Home, Grocery & Essentials, Clothing & Accessories, Beauty, Baby, Toys & Games, Sports & Outdoors, Entertainment, Pharmacy & Health, Pets
- **Target Circle**: ~30% of products have Circle member deals with special pricing
- **Fulfillment**: Products support delivery, store pickup, and Drive Up options

## Analysis Tips

### Spending Trends
- Use `spending --days 30` vs `spending --days 90` to compare recent vs longer-term patterns
- Monthly breakdown shows seasonal trends (holidays, back-to-school)

### Department Balance
- Compare spending across departments to understand shopping habits
- Check if the user shops specific departments disproportionately

### Circle Deals
- Use `circle-deals` to find savings opportunities
- Cross-reference with `favorites` to find deals on frequently purchased items

### Order Frequency Patterns
- Weekly shoppers: 4+ orders per month
- Biweekly: 2-3 orders per month
- Monthly: 1 order per month
