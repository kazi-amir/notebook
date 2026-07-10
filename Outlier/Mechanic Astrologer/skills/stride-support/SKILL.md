---
name: stride-support
description: Customer support workflows for Stride Shoes online store. Use when handling customer complaints, refund requests, order issues, or support ticket triage across email, shopify, zendesk, contacts, and calendar systems.
---

# Stride Shoes — Customer Support Workflows

Stride Shoes is a small online shoe store. Customer support data is spread across multiple systems:

| System | Data | Key tool prefix |
|--------|------|----------------|
| **Shopify** | Customers, orders, products | `shopify_*` |
| **Email** | 215 inbound support emails | `email_*` |
| **Zendesk** | 40 support tickets | `zendesk_*` |
| **Contacts** | 1,900 customer contacts | `contacts_*` |
| **Calendar** | Delivery tracking events | `calendar_*` |

## Cross-System Correlation

Emails and tickets contain `customer_id` and `order_id` fields that map directly to Shopify:
- Email `customer_id` → Shopify customer ID
- Email `order_id` → Shopify order ID
- Ticket `customer_id` → Shopify customer ID
- Ticket `order_id` → Shopify order ID
- Zendesk ticket `custom_fields.shopify_customer_id` → Shopify customer ID
- Zendesk ticket `custom_fields.shopify_order_id` → Shopify order ID
- Zendesk ticket `custom_fields.order_number` → Shopify order number

Order numbers follow the pattern `STR-NNNNN` (e.g., STR-50001) and appear in email subjects and ticket subjects.

## Workflows

### 1. Look Up a Customer Complaint

When a customer emails about an issue:

1. **Read the email** — `email_*` tools to get the email content. Note the sender address, subject, and any order number mentioned.
2. **Find the customer** — Use `shopify_search_customers` with the sender's email or name.
3. **Check their orders** — Use `shopify_get_orders_by_customer` with the customer ID.
4. **Check existing tickets** — Search zendesk for the customer to see if a ticket already exists.
5. **Review the specific order** — If an order number is mentioned (STR-NNNNN), use `shopify_get_order_by_number`.

### 2. Verify a Refund Claim

When a customer requests a refund:

1. **Get the order** — Use `shopify_get_order_by_number` or `shopify_get_order` to check order status.
2. **Check order status** — Valid refund candidates typically have status `delivered`, `returned`, or `refund_requested`.
3. **Check delivery date** — The `delivered_date` field shows when it arrived.
4. **Check tracking** — The `tracking_number` field can verify delivery.
5. **Review the customer's claim** in the email body against the order details.

### 3. Handle "Wrong Item" Claims

When a customer says they received the wrong item:

1. **Get the order details** — `shopify_get_order_by_number` to see what was ordered.
2. **Check the product** — If the email mentions a specific product, use `shopify_search_products` to verify product details.
3. **Cross-reference** — Compare what the customer says they received vs. what the order shows.
4. **Check the email body** — The customer typically states both what they ordered and what they received.

### 4. Handle "Never Received" Claims

When a customer says their order never arrived:

1. **Get the order** — `shopify_get_order_by_number` to check status and dates.
2. **Check tracking** — The `tracking_number` field can be used to verify delivery.
3. **Check dates** — Compare `shipped_date` and `delivered_date`. If `delivered_date` is set, the carrier marked it delivered.
4. **Check calendar** — Search calendar events for the order number to see delivery events.

### 5. Triage Support Tickets

When reviewing open tickets:

1. **List open tickets** — Use zendesk tools to get tickets with status `open` or `pending`.
2. **For each ticket** — Use `custom_fields.shopify_customer_id` and `custom_fields.shopify_order_id` to pull customer and order context from Shopify.
3. **Prioritize** — Tickets with `priority: high` or `urgent` should be handled first.
4. **Check related emails** — Search emails for the same customer or order number.

## Order Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Order placed, not yet confirmed |
| `confirmed` | Payment confirmed, awaiting shipment |
| `shipped` | In transit, has tracking number |
| `delivered` | Carrier confirms delivery |
| `returned` | Customer returned the item |
| `refund_requested` | Customer requested a refund |
| `cancelled` | Order was cancelled |

## Ticket Statuses (Zendesk)

| Status | Meaning |
|--------|---------|
| `open` | Needs agent attention |
| `pending` | Waiting on customer response |
| `solved` | Issue resolved |

## Tips

- Email subjects often contain the order number (e.g., "Return — STR-50885")
- Use order numbers to quickly correlate across all systems
- The shopify `customer_id` is the primary key linking all systems together
- When investigating a complaint, always check both the email content AND the Shopify order data to get both sides of the story
