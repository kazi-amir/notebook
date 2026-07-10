---
name: shopify
description: Access Shopify e-commerce data — customers, orders, and products. Use when the user asks about customers, orders, order status, products, tracking, or e-commerce operations.
---

# Shopify

Query Shopify e-commerce data including customers, orders, and products.

Data is pre-loaded from your Shopify store. No API key or setup needed.

## Fetching Data

Use `shopify_data.py` to get JSON data:

```bash
# Customers
python3 {baseDir}/shopify_data.py customers
python3 {baseDir}/shopify_data.py customer <id>
python3 {baseDir}/shopify_data.py search-customers "John Smith"

# Orders
python3 {baseDir}/shopify_data.py orders
python3 {baseDir}/shopify_data.py order <id>
python3 {baseDir}/shopify_data.py order-by-number "STR-50001"
python3 {baseDir}/shopify_data.py orders-by-customer <customer_id>
python3 {baseDir}/shopify_data.py search-orders --status delivered --date-from "2026-01-01" --date-to "2026-03-01"
python3 {baseDir}/shopify_data.py search-orders --min-amount 100 --max-amount 500

# Products
python3 {baseDir}/shopify_data.py products
python3 {baseDir}/shopify_data.py product <id>
python3 {baseDir}/shopify_data.py product-by-sku "NK-AM90"
python3 {baseDir}/shopify_data.py search-products --brand Nike --category running --gender men
python3 {baseDir}/shopify_data.py search-products --min-price 50 --max-price 150

# Order Updates
python3 {baseDir}/shopify_data.py update-order-status <order_id> <status>
python3 {baseDir}/shopify_data.py update-order-status <order_id> <status> --notes "Reason for update"
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me all customers" | `shopify_data.py customers` |
| "Look up customer #42" | `shopify_data.py customer 42` |
| "Find customer by name/email" | `shopify_data.py search-customers "query"` |
| "Show all orders" | `shopify_data.py orders` |
| "Look up order #STR-50001" | `shopify_data.py order-by-number "STR-50001"` |
| "Show orders for customer #42" | `shopify_data.py orders-by-customer 42` |
| "Show delivered orders" | `shopify_data.py search-orders --status delivered` |
| "Show orders over $200" | `shopify_data.py search-orders --min-amount 200` |
| "What products do we have?" | `shopify_data.py products` |
| "Show Nike products" | `shopify_data.py search-products --brand Nike` |
| "Show running shoes" | `shopify_data.py search-products --category running` |
| "Find product by SKU" | `shopify_data.py product-by-sku "NK-AM90"` |
| "Mark order as shipped" | `shopify_data.py update-order-status <id> shipped` |

## Key Data

- **Customers** with contact info, shipping address, payment method on file, and loyalty status/points
- **Orders** with order number, status (pending/confirmed/shipped/delivered/returned/refund_requested/cancelled), dates, totals, and tracking numbers
- **Products** with brand, model, SKU, category, gender, price, and description

## Analysis Tips

- **Order lifecycle**: Track orders through pending → confirmed → shipped → delivered. Check shipped_date and delivered_date for timing.
- **Customer history**: Use `orders-by-customer` to see a customer's full purchase history.
- **Tracking**: Orders with tracking_number can be cross-referenced with shipping carriers.
- **Refunds/Returns**: Filter by status `returned` or `refund_requested` to identify problem orders.
- **Product catalog**: Search by brand, category, gender, or price range to find specific items.
- **Loyalty program**: Customers with `loyalty_member=1` accumulate loyalty_points.
