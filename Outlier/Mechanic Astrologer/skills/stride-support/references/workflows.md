# Stride Shoes — Support Workflow Procedures

## Procedure: Customer Complaint Investigation

**Trigger**: New support email or ticket received.

1. **Identify the customer**
   - Extract email address or name from the email/ticket.
   - Run `shopify_search_customers` with the email or name.
   - Note the `customer_id` for subsequent lookups.

2. **Pull order context**
   - If an order number (STR-NNNNN) appears in the subject or body, run `shopify_get_order_by_number`.
   - Otherwise, run `shopify_get_orders_by_customer` to see all orders.

3. **Check for existing tickets**
   - Search zendesk tickets for the same customer (via `custom_fields.shopify_customer_id`).
   - Avoid creating duplicate tickets.

4. **Assess the issue**
   - Compare the customer's claim (email body) against order data (status, dates, tracking).
   - Determine the category: wrong item, never received, defective, refund request, general inquiry.

---

## Procedure: Refund Request Verification

**Trigger**: Customer requests a refund.

1. **Get the order** — `shopify_get_order_by_number` with the order number from the email.
2. **Check eligibility**:
   - Order status must be `delivered`, `returned`, or `refund_requested`.
   - Orders with status `pending`, `confirmed`, or `cancelled` are not refund-eligible (cancel instead, or already cancelled).
   - Orders with status `shipped` but not yet delivered should wait for delivery.
3. **Review dates**: Check `order_date`, `shipped_date`, `delivered_date` to understand timeline.
4. **Update status**: If approved, use `shopify_update_order_status` to set status to `refund_requested`.

---

## Procedure: "Wrong Item Received" Resolution

**Trigger**: Customer reports receiving the wrong product.

1. **Get order details** — `shopify_get_order_by_number`.
2. **Get product info** — If the customer names the product they received, search with `shopify_search_products` to confirm it exists in catalog.
3. **Compare**: The customer typically states "I ordered X but received Y" — verify X matches the order record.
4. **Check for pattern**: Run `shopify_get_orders_by_customer` to see if this customer has had prior issues.

---

## Procedure: "Never Received" Resolution

**Trigger**: Customer claims order was not delivered.

1. **Get order** — `shopify_get_order_by_number`.
2. **Check status and dates**:
   - If `status` is `shipped` and `delivered_date` is null → order genuinely not delivered yet.
   - If `status` is `delivered` and `delivered_date` is set → carrier marked it delivered.
3. **Check tracking** — Note the `tracking_number` for carrier verification.
4. **Check calendar** — Search calendar events for the order number to see delivery event details.
5. **Determine resolution**: If carrier says delivered but customer disagrees, this may require escalation.

---

## Procedure: Daily Ticket Triage

**Trigger**: Start of support shift.

1. **Get open tickets** — Use zendesk tools to list tickets with status `open`.
2. **Sort by priority** — Handle `urgent` and `high` priority first.
3. **For each ticket**:
   - Read `custom_fields` to get `shopify_customer_id` and `shopify_order_id`.
   - Pull customer and order context from Shopify.
   - Check if related emails exist for additional context.
4. **Update ticket status** as you work through them.

---

## Data Cross-Reference Quick Guide

| Starting point | To find | Use |
|---------------|---------|-----|
| Email sender address | Customer record | `shopify_search_customers` with email |
| Order number in email | Order details | `shopify_get_order_by_number` |
| Customer ID | All their orders | `shopify_get_orders_by_customer` |
| Customer ID | Their contact info | `contacts_*` search by name/email |
| Order shipped/delivered date | Calendar event | `calendar_*` search by order number |
| Zendesk ticket | Shopify data | Read `custom_fields.shopify_customer_id` and `custom_fields.shopify_order_id` |
