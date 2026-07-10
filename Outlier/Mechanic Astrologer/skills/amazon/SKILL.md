---
name: amazon
description: Access Amazon shopping data — search products, view order history, analyze spending patterns, find frequently purchased items, and explore the product catalog. Use when the user asks about Amazon orders, spending, product search, purchase history, or shopping habits.
---

# Amazon

Query the Amazon product catalog, order history, and spending analytics.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/amazon_data.py login --email your@email.com
```

## Fetching Data

Use `amazon_data.py` to get JSON data:

```bash
# Search products
python3 {baseDir}/amazon_data.py search "wireless headphones"
python3 {baseDir}/amazon_data.py search "laptop" --category "Electronics" --max-price 1000
python3 {baseDir}/amazon_data.py search "running shoes" --brand "Nike" --min-rating 4.5
python3 {baseDir}/amazon_data.py search "kitchen" --prime-only --limit 10

# List all categories
python3 {baseDir}/amazon_data.py categories

# List brands (optionally by category)
python3 {baseDir}/amazon_data.py brands
python3 {baseDir}/amazon_data.py brands --category "Electronics" --limit 20

# Get product details by ASIN
python3 {baseDir}/amazon_data.py product B08N5WRWNW

# Order history (last 90 days default)
python3 {baseDir}/amazon_data.py orders --days 30
python3 {baseDir}/amazon_data.py orders --status delivered --limit 5
python3 {baseDir}/amazon_data.py orders --start 2025-11-01 --end 2025-12-31

# Single order details
python3 {baseDir}/amazon_data.py order ORDER-A1B2C3D4

# Spending analytics
python3 {baseDir}/amazon_data.py spending --days 30
python3 {baseDir}/amazon_data.py spending --start 2025-10-01 --end 2026-01-31

# Frequently purchased products
python3 {baseDir}/amazon_data.py favorites --days 180 --limit 10

# User profile
python3 {baseDir}/amazon_data.py profile

# Account summary
python3 {baseDir}/amazon_data.py summary --days 90
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What did I buy on Amazon recently?" | `amazon_data.py orders --days 30` |
| "How much have I spent on Amazon?" | `amazon_data.py spending --days 90` |
| "Find me a laptop under $1000" | `amazon_data.py search "laptop" --max-price 1000` |
| "What are my most purchased items?" | `amazon_data.py favorites --days 180` |
| "What brands do I buy most?" | `amazon_data.py spending --days 180` check `by_brand` |
| "Give me an Amazon account summary" | `amazon_data.py summary --days 90` |
| "Find highly rated headphones" | `amazon_data.py search "headphones" --min-rating 4.5` |
| "Show me details for a product" | `amazon_data.py product <ASIN>` |
| "What categories does Amazon have?" | `amazon_data.py categories` |
| "What electronics brands are there?" | `amazon_data.py brands --category "Electronics"` |
| "Show me my delivered orders" | `amazon_data.py orders --status delivered` |
| "How much did I spend per month?" | `amazon_data.py spending --days 180` check `by_month` |
| "What's my most expensive order?" | `amazon_data.py spending --days 180` check `most_expensive_order` |
| "What category do I spend most on?" | `amazon_data.py spending --days 180` check `by_category` |
| "Show me Prime-eligible items" | `amazon_data.py search "<query>" --prime-only` |

## Key Data

- **2,830 products** across 24 categories (Electronics, Books, Clothing, Home & Kitchen, Sports & Outdoors, Beauty, Toys & Games, and more)
- **1,304 unique brands** (Apple, Samsung, Sony, Nike, Amazon, and many more)
- **Orders** include status (delivered, pending, shipped, cancelled), timestamps for creation/shipping/delivery, and line items with purchase prices
- **Spending** breakdowns available by month, by category, and by brand
- **Ratings** from 4.0 to 4.9 with review counts for every product

## Analysis Tips

When the user asks about their Amazon shopping habits, consider:

- **Spending trends**: Compare monthly totals via `spending` to spot increases or decreases. The `by_month` breakdown shows spending trajectory over time.
- **Category focus**: The `by_category` breakdown reveals where the user's money goes. Heavy Electronics spending may indicate a tech enthusiast; diverse category spread suggests general shopping.
- **Brand loyalty**: The `by_brand` breakdown shows if the user gravitates toward specific brands. This can inform product recommendations.
- **Purchase frequency**: Check order count over time. High-frequency purchasers may benefit from Prime if they don't already have it.
- **Favorites vs variety**: If the same products dominate `favorites`, the user has strong preferences. Low repeat-purchase rates suggest exploration behavior.
- **Order status**: Check `summary` for the status breakdown — a high cancellation rate may indicate indecisiveness or price sensitivity.
- **Price sensitivity**: Compare `avg_per_order` and look at the `cheapest_order` vs `most_expensive_order` spread to understand spending comfort.

## Reference

- `{baseDir}/references/shopping_guide.md` — Amazon shopping reference with category overview, product comparison tips, and spending analysis guidance
