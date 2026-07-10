---
name: hotel-management
description: Manage hotel rooms, guests, reservations, occupancy metrics, and OTA rate parity. Use when the user asks about room availability, guest lookups, reservations, check-ins/check-outs, occupancy stats, or rate comparisons.
---

# Hotel Management

Manage rooms, guests, reservations, occupancy, and OTA pricing for a hotel. Data is pre-loaded. No setup needed.

## Rooms

```bash
# List all rooms
python3 {baseDir}/hotel_data.py rooms

# Get a specific room
python3 {baseDir}/hotel_data.py room --number 301

# Search rooms by type, floor, or view
python3 {baseDir}/hotel_data.py search-rooms --room-type "Ocean View King" --floor 3 --view "Ocean"

# Get available rooms for a date range
python3 {baseDir}/hotel_data.py available-rooms --start "2026-03-10" --end "2026-03-14"
python3 {baseDir}/hotel_data.py available-rooms --start "2026-03-10" --end "2026-03-14" --room-type "Junior Suite"
```

### Room Filters

| Filter | Flag | Example |
|--------|------|---------|
| Room type | `--room-type` | `--room-type "Deluxe King"` |
| Floor | `--floor` | `--floor 3` |
| View | `--view` | `--view "Ocean"` |

Room types: Standard King, Standard Double, Deluxe King, Deluxe Double, Ocean View King, Ocean View Double, Junior Suite, Executive Suite, Presidential Suite

## Guests

```bash
# List all guests
python3 {baseDir}/hotel_data.py guests

# Get a specific guest
python3 {baseDir}/hotel_data.py guest --id G001

# Search guests by name or email
python3 {baseDir}/hotel_data.py search-guests --query "Sarah Mitchell"
```

## Reservations

```bash
# List all reservations
python3 {baseDir}/hotel_data.py reservations --status "Checked-In" --limit 20

# Get a specific reservation by confirmation code
python3 {baseDir}/hotel_data.py reservation --code APH-2401

# Search reservations by guest, status, or dates
python3 {baseDir}/hotel_data.py search-reservations --guest-id G001
python3 {baseDir}/hotel_data.py search-reservations --status "Confirmed"
python3 {baseDir}/hotel_data.py search-reservations --start "2026-03-05" --end "2026-03-10"

# Today's check-ins and check-outs
python3 {baseDir}/hotel_data.py todays-checkins
python3 {baseDir}/hotel_data.py todays-checkouts
```

### Reservation Filters

| Filter | Flag | Example |
|--------|------|---------|
| Status | `--status` | `--status "Checked-In"` |
| Guest | `--guest-id` | `--guest-id G018` |
| Date range | `--start`, `--end` | `--start "2026-03-01" --end "2026-03-07"` |
| Limit | `--limit` | `--limit 20` |

Statuses: Checked-In, Confirmed, Checked-Out, No-Show, Cancelled

## Guest Emails

```bash
# List all hotel emails
python3 {baseDir}/hotel_data.py emails

# Get a specific email
python3 {baseDir}/hotel_data.py email --id E034

# Search emails by keyword
python3 {baseDir}/hotel_data.py search-emails --query "AC not working"

# Get emails for a specific reservation
python3 {baseDir}/hotel_data.py emails-by-reservation --code APH-2421
```

## Occupancy & Revenue

```bash
# Get occupancy data for a date range
python3 {baseDir}/hotel_data.py occupancy --start "2026-02-01" --end "2026-02-28"

# Get occupancy summary (averages)
python3 {baseDir}/hotel_data.py occupancy-summary --start "2026-02-01" --end "2026-02-28"
```

Returns: occupancy %, rooms sold, ADR (average daily rate), RevPAR, revenue.

## OTA Rate Comparison

```bash
# Get OTA pricing for a room type and date
python3 {baseDir}/hotel_data.py ota-pricing --room-type "Standard King" --date "2026-03-05"

# Get rate comparison across all OTAs for a date
python3 {baseDir}/hotel_data.py rate-comparison --date "2026-03-05"
python3 {baseDir}/hotel_data.py rate-comparison --date "2026-03-05" --room-type "Junior Suite"
```

Returns: direct price vs Booking.com, Expedia, Hotels.com with commission percentages.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Any rooms available next week?" | `available-rooms --start ... --end ...` |
| "Look up reservation APH-2421" | `reservation --code APH-2421` |
| "Who's checking in today?" | `todays-checkins` |
| "What's our occupancy this month?" | `occupancy-summary --start ... --end ...` |
| "Show me ocean view rooms on floor 3" | `search-rooms --view "Ocean" --floor 3` |
| "Any emails about AC problems?" | `search-emails --query "AC"` |
| "Guest Sarah Mitchell's details" | `search-guests --query "Sarah Mitchell"` |
| "Are our rates competitive?" | `rate-comparison --date "2026-03-15"` |
| "What reservations does guest G018 have?" | `search-reservations --guest-id G018` |
| "Revenue for February?" | `occupancy-summary --start "2026-02-01" --end "2026-02-28"` |
