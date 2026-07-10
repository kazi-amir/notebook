---
name: mock-shopping
description: Browse products, manage cart, apply discount codes, and place orders via the mock shopping platform. Use when the user asks about purchasing supplies, product catalog, cart, checkout, discount codes, or order status.
---

# Shopping

Browse product catalog, manage shopping cart, apply discounts, and place orders. Data is pre-loaded. No API key or setup needed.

## Products

```bash
# List all products
python3 {baseDir}/shopping_data.py list-products

# List with pagination
python3 {baseDir}/shopping_data.py list-products --offset 0 --limit 20

# Get full product details including variants
python3 {baseDir}/shopping_data.py get-product --product-id PROD-001

# Search products by name
python3 {baseDir}/shopping_data.py search-product --product-name "gloves"
python3 {baseDir}/shopping_data.py search-product --product-name "sanitizer" --limit 5
```

## Cart

```bash
# Add an item to the cart
python3 {baseDir}/shopping_data.py add-to-cart --item-id ITEM-001
python3 {baseDir}/shopping_data.py add-to-cart --item-id ITEM-001 --quantity 3

# Remove an item from the cart
python3 {baseDir}/shopping_data.py remove-from-cart --item-id ITEM-001
python3 {baseDir}/shopping_data.py remove-from-cart --item-id ITEM-001 --quantity 2

# List cart contents
python3 {baseDir}/shopping_data.py list-cart
```

## Checkout & Orders

```bash
# Checkout (create order from cart)
python3 {baseDir}/shopping_data.py checkout

# Checkout with a discount code
python3 {baseDir}/shopping_data.py checkout --discount-code SAVE10

# List all placed orders
python3 {baseDir}/shopping_data.py list-orders

# Get order details
python3 {baseDir}/shopping_data.py get-order --order-id ORD-001

# Cancel an order (must be processed or shipped)
python3 {baseDir}/shopping_data.py cancel-order --order-id ORD-001
```

## Discount Codes

```bash
# Get items and percentages for a discount code
python3 {baseDir}/shopping_data.py get-discount-code --discount-code SAVE10

# List all available discount codes
python3 {baseDir}/shopping_data.py get-all-discount-codes
```

## Utility

```bash
# Show raw data
python3 {baseDir}/shopping_data.py show --offset 0 --limit 100

# Reset to initial state
python3 {baseDir}/shopping_data.py reset
```

## Order Statuses

| Status | Description |
|--------|-------------|
| `processed` | Order received, awaiting shipment |
| `shipped` | Order has been shipped |
| `delivered` | Order has been delivered |
| `cancelled` | Order has been cancelled |

## Discount Code Rules

- Discount codes apply a percentage discount to specific items
- When checking out with a discount code, the code **must** be valid for **ALL** items in the cart
- Checkout will fail if any cart item does not support the provided discount code
- This is a strict all-or-nothing discount policy
- Use `get-discount-code` to check which items a code applies to before checkout
- Use `get-all-discount-codes` to see all available codes

## Data Entities

The shopping system holds:

- **Products** -- catalog items with variants (product_id, name, variants dict)
- **Items** -- product variants with specific options (item_id, price, available, options like color/size/storage)
- **Cart** -- in-memory shopping cart (item_id to quantity/price/options mapping)
- **Orders** -- placed orders (order_id, order_status, order_date, order_total, order_items)
- **Discount Codes** -- codes mapping to item-specific discount percentages

## Typical Workflow

```
1. Browse:    list-products or search-product
2. Details:   get-product to see variants and prices
3. Add:       add-to-cart with the desired item_id
4. Review:    list-cart to verify cart contents
5. Discount:  get-all-discount-codes to find applicable codes
6. Checkout:  checkout (optionally with --discount-code)
7. Track:     list-orders / get-order
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What products are available?" | `list-products` |
| "Search for gloves" | `search-product --product-name "gloves"` |
| "Show me details for product X" | `get-product --product-id X` |
| "Add sanitizer to the cart" | Search for product, get item_id from variants, then `add-to-cart --item-id X` |
| "What's in my cart?" | `list-cart` |
| "Remove item from cart" | `remove-from-cart --item-id X` |
| "Any discount codes available?" | `get-all-discount-codes` |
| "Place the order" | `checkout` |
| "Place order with discount SAVE10" | `checkout --discount-code SAVE10` |
| "Show my orders" | `list-orders` |
| "Cancel order X" | `cancel-order --order-id X` |
| "What's the status of my order?" | `get-order --order-id X` |
