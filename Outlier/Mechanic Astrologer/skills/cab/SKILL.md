---
name: cab
description: Book rides, get quotations, manage ride status, and browse ride history via the cab ride-hailing service. Use when the user asks about rides, cabs, taxis, transportation, booking a car, or ride history.
---

# Cab

Book rides, get quotations, check ride status, and browse ride history. Data is pre-loaded. No API key or setup needed.

## Quotations

```bash
# Get a price quote for a ride
python3 {baseDir}/cab_data.py get-quotation --start-location "Downtown" --end-location "Airport" --service-type Default --ride-time "2026-04-15 10:00:00"

# Only start and end locations are required
python3 {baseDir}/cab_data.py get-quotation --start-location "Home" --end-location "Office"
```

## Booking

```bash
# List available rides between two locations
python3 {baseDir}/cab_data.py list-rides --start-location "Downtown" --end-location "Airport"
python3 {baseDir}/cab_data.py list-rides --start-location "Home" --end-location "Office" --ride-time "2026-04-15 14:00:00"

# Order a ride
python3 {baseDir}/cab_data.py order-ride --start-location "Downtown" --end-location "Airport" --service-type Premium
python3 {baseDir}/cab_data.py order-ride --start-location "Home" --end-location "Office" --service-type Default --ride-time "2026-04-15 09:00:00"
```

## Ride Status

```bash
# Check current ride status
python3 {baseDir}/cab_data.py ride-status

# Cancel the current ride
python3 {baseDir}/cab_data.py cancel-ride
```

## Ride History

```bash
# Get a specific ride by index in history
python3 {baseDir}/cab_data.py get-ride --idx 0

# List ride history with pagination
python3 {baseDir}/cab_data.py ride-history --offset 0 --limit 10

# Get total number of rides in history
python3 {baseDir}/cab_data.py ride-history-length
```

## Service Types

| Type | Description |
|------|-------------|
| `Default` | Standard ride at the lowest price |
| `Premium` | Higher-end vehicle with premium features |
| `Van` | Larger vehicle for groups or extra luggage |

## Ride Statuses

| Status | Description |
|--------|-------------|
| `BOOKED` | Ride has been booked and is active |
| `COMPLETED` | Ride has been completed |
| `CANCELLED` | Ride has been cancelled |

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How much is a ride to the airport?" | `get-quotation --start-location "Current" --end-location "Airport"` |
| "What rides are available?" | `list-rides --start-location X --end-location Y` |
| "Book me a cab to downtown" | `order-ride --start-location X --end-location "Downtown" --service-type Default` |
| "I want a premium ride" | `order-ride --start-location X --end-location Y --service-type Premium` |
| "Where is my ride?" | `ride-status` |
| "Cancel my ride" | `cancel-ride` |
| "Show my ride history" | `ride-history` |
| "How many rides have I taken?" | `ride-history-length` |
| "Show me my last ride" | `get-ride --idx 0` |
| "Compare prices for different service types" | Run `get-quotation` for Default, Premium, and Van |

## Data Entities

The cab system holds:

- **Rides** -- ride records (ride_id, status, service_type, start_location, end_location, price, duration, time_stamp, distance_km, delay, delay_history)
- **Service Types** -- Default, Premium, Van
- **Ride Statuses** -- BOOKED, COMPLETED, CANCELLED

## Utility

```bash
# Show raw data
python3 {baseDir}/cab_data.py show
```
