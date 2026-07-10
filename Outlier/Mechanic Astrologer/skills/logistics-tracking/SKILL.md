---
name: logistics-tracking
description: Track packages across carriers -- view shipment status, delivery timeline, carrier details, and batch-track multiple packages. Use when the user asks about package tracking, delivery status, shipping updates, or wants to know where their order is.
---

# Logistics Tracking

Track packages across 3,100+ carriers using tracking numbers from your shopping orders.

Data is pre-loaded from your linked shopping accounts. No API key or setup needed.

## Fetching Data

Use `logistics_data.py` to get JSON data:

```bash
# Track a single package
python3 {baseDir}/logistics_data.py track TBA123456789012
python3 {baseDir}/logistics_data.py track 1ZABC12345678901 --carrier UPS

# Detect carrier from tracking number
python3 {baseDir}/logistics_data.py detect 1ZABC12345678901

# Batch track multiple packages
python3 {baseDir}/logistics_data.py batch TBA123456789012 1ZABCDEF1234567890 9400000000000000000001

# Explain a status code
python3 {baseDir}/logistics_data.py status InTransit
python3 {baseDir}/logistics_data.py status Delivered

# List all my shipments
python3 {baseDir}/logistics_data.py shipments
python3 {baseDir}/logistics_data.py shipments --status Delivered
python3 {baseDir}/logistics_data.py shipments --carrier UPS --limit 10
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Where is my package?" | `logistics_data.py shipments` then `logistics_data.py track <number>` |
| "Track this number: TBA..." | `logistics_data.py track TBA...` |
| "What carrier is this?" | `logistics_data.py detect <number>` |
| "Show all my deliveries" | `logistics_data.py shipments --status Delivered` |
| "Any packages in transit?" | `logistics_data.py shipments --status InTransit` |
| "Track all my recent packages" | `logistics_data.py shipments --limit 10` then batch track |
| "What does InTransit mean?" | `logistics_data.py status InTransit` |
| "Which carrier has my stuff?" | `logistics_data.py shipments --carrier UPS` (or FedEx, USPS, etc.) |

## Tracking Number Formats

| Carrier | Format | Example |
|---------|--------|---------|
| UPS | `1Z` + 16 chars | `1ZABCDEF1234567890` |
| FedEx | 12 digits | `123456789012` |
| USPS | `94` + 20 digits | `9400000000000000000001` |
| DHL | 10 digits | `1234567890` |
| Amazon Logistics | `TBA` + 12 digits | `TBA123456789012` |
| Local Delivery | `LOC` + 10 digits | `LOC1234567890` |
| Instacart | `IC` + 10 digits | `IC1234567890` |

## Status Codes

| Code | Meaning |
|------|---------|
| `InfoReceived` | Carrier has shipping info but hasn't picked up the package |
| `InTransit` | Package is on its way, moving through sorting facilities |
| `OutForDelivery` | Package is on the delivery vehicle, arriving today |
| `Delivered` | Package has been delivered |
| `Exception` | Issue with delivery (delayed, held, requires action) |
| `Returned` | Package is being returned to sender |

## Cross-Service Workflow

To find a tracking number for a specific order:
1. Look up the order in the relevant store (e.g., `amazon_data.py order ORDER-123`)
2. The order response includes `tracking_number` and `carrier` fields
3. Use `logistics_data.py track <tracking_number>` to get the full timeline
