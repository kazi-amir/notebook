---
name: walmart
description: Access Walmart shopping data — search products, view order history, analyze spending patterns, browse departments and categories, and find frequently purchased items. Use when the user asks about Walmart orders, spending, product search, purchase history, or shopping habits.
---

# Walmart

Query the Walmart product catalog, order history, and spending analytics.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/walmart_data.py login --email your@email.com
```

## Fetching Data

Use `walmart_data.py` to get JSON data:

```bash
# Search products
python3 {baseDir}/walmart_data.py search "bananas"
python3 {baseDir}/walmart_data.py search "laptop" --department "Electronics" --max-price 500
python3 {baseDir}/walmart_data.py search "dog food" --category "Pets" --brand "Purina"
python3 {baseDir}/walmart_data.py search "milk" --in-stock-only --limit 10

# List all categories
python3 {baseDir}/walmart_data.py categories

# List all departments
python3 {baseDir}/walmart_data.py departments

# List brands (optionally by category or department)
python3 {baseDir}/walmart_data.py brands
python3 {baseDir}/walmart_data.py brands --department "Grocery & Essentials" --limit 20
python3 {baseDir}/walmart_data.py brands --category "Electronics"

# Get product details by product ID
python3 {baseDir}/walmart_data.py product WMT00000001

# Order history (last 90 days default)
python3 {baseDir}/walmart_data.py orders --days 30
python3 {baseDir}/walmart_data.py orders --status delivered --limit 5
python3 {baseDir}/walmart_data.py orders --start 2025-11-01 --end 2025-12-31

# Single order details
python3 {baseDir}/walmart_data.py order WMT-M4WAOXHX

# Spending analytics
python3 {baseDir}/walmart_data.py spending --days 30
python3 {baseDir}/walmart_data.py spending --start 2025-10-01 --end 2026-01-31

# Frequently purchased products
python3 {baseDir}/walmart_data.py favorites --days 180 --limit 10

# User profile
python3 {baseDir}/walmart_data.py profile

# Account summary
python3 {baseDir}/walmart_data.py summary --days 90
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What did I buy at Walmart recently?" | `walmart_data.py orders --days 30` |
| "How much have I spent at Walmart?" | `walmart_data.py spending --days 90` |
| "Find me cheap groceries" | `walmart_data.py search "groceries" --department "Grocery & Essentials" --max-price 10` |
| "What are my most purchased items?" | `walmart_data.py favorites --days 180` |
| "What brands do I buy most?" | `walmart_data.py spending --days 180` check `by_brand` |
| "Give me a Walmart account summary" | `walmart_data.py summary --days 90` |
| "What departments are available?" | `walmart_data.py departments` |
| "Show me pet supplies" | `walmart_data.py search "pet" --category "Pets"` |
| "Show me details for a product" | `walmart_data.py product <product_id>` |
| "What categories does Walmart have?" | `walmart_data.py categories` |
| "What grocery brands are there?" | `walmart_data.py brands --department "Grocery & Essentials"` |
| "Show me my delivered orders" | `walmart_data.py orders --status delivered` |
| "How much did I spend per month?" | `walmart_data.py spending --days 180` check `by_month` |
| "What's my most expensive order?" | `walmart_data.py spending --days 180` check `most_expensive_order` |
| "What department do I spend most on?" | `walmart_data.py spending --days 180` check `by_department` |
| "What category do I spend most on?" | `walmart_data.py spending --days 180` check `by_category` |

## Key Data

- **2,309 products** across multiple categories from 9 source stores (Grocery, Electronics, Fashion, Toys, Pets, Pharmacy, Bakery, Sporting Goods, Home Appliances)
- **Departments** include Grocery & Essentials, Electronics, Home, Clothing, Toys, Pets, Pharmacy, Sports & Outdoors, and more
- **Orders** include status (delivered, shipped, pending, cancelled), creation/shipping/delivery timestamps, and line items with purchase prices
- **Spending** breakdowns available by month, by category, by department, and by brand
- **Ratings** from 0.0 to 5.0 with review counts for every product
- **Savings** shown when products have original prices higher than current price

## Analysis Tips

When the user asks about their Walmart shopping habits, consider:

- **Spending trends**: Compare monthly totals via `spending` to spot increases or decreases. The `by_month` breakdown shows spending trajectory.
- **Department vs category**: Departments are broader groupings (e.g., "Grocery & Essentials"), while categories are more specific (e.g., "Grocery", "Bakery"). Use `by_department` for a high-level view and `by_category` for details.
- **Grocery patterns**: If the user shops for groceries at Walmart, check `favorites` to see staple items. This can help with meal planning or budgeting.
- **Brand loyalty**: The `by_brand` breakdown shows if the user gravitates toward specific brands. Suggest store brands as a savings opportunity.
- **Order frequency**: Check order count over time. Frequent grocery orders may mean the user visits weekly vs monthly stock-up trips.
- **Price sensitivity**: Products with `savings` and `savings_percent` fields show discounted items. Cross-reference with `favorites` to find deals on frequently purchased items.
- **Order status**: A high cancellation rate may suggest impulse shopping or price sensitivity. Check `summary` for the full status breakdown.

## Reference

- `{baseDir}/references/shopping_guide.md` — Walmart shopping reference with department overview, savings tips, and spending analysis guidance
