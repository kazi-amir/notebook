# Ticketmaster Event Guide

## Event Segments

| Segment | Genres | Typical Venues |
|---------|--------|----------------|
| Music | Pop, Rock, Hip-Hop, R&B, Country, Electronic | Arenas, stadiums, amphitheaters, clubs |
| Sports | NBA, NFL, MLB | Arenas, stadiums |
| Arts & Theater | Musical, Play | Theaters |
| Comedy | Stand-Up | Theaters, clubs |
| Family | Show | Arenas, theaters |

## Venue Types

| Type | Description | Capacity Range | Examples |
|------|-------------|----------------|----------|
| Arena | Indoor multi-purpose venue | 15,000-21,000 | Madison Square Garden, United Center, Chase Center |
| Stadium | Large outdoor/retractable roof | 37,000-70,000 | SoFi Stadium, Fenway Park, Wrigley Field |
| Theater | Seated performance venue | 1,800-6,000 | Ryman Auditorium, Fox Theatre, Radio City Music Hall |
| Club | Intimate indoor venue | 1,800-6,000 | The Wiltern, The Anthem |
| Outdoor | Open-air amphitheater | 9,500-27,500 | Red Rocks Amphitheatre, Gorge Amphitheatre |

## Ticket Tiers

| Tier | Description | Price Range |
|------|-------------|-------------|
| General Admission (GA) | Standing or unassigned seating, often floor level | $25-$100 |
| Reserved Seating | Assigned seats, various levels (upper, lower, field) | $30-$285 |
| Premium Reserved | Better location — club level, pavilion, premium rows | $69-$450 |
| VIP Package | Best seats plus perks — suite, courtside, VIP lounge | $89-$650 |

## Event Status Lifecycle

```
presale → on_sale → limited → sold_out
                              ↘ cancelled
                              ↘ postponed
```

- **presale**: Tickets available to select groups (fan clubs, credit cards)
- **on_sale**: General public can purchase
- **limited**: Low availability across most ticket types
- **sold_out**: No tickets remaining
- **cancelled**: Event will not take place
- **postponed**: Event delayed, new date TBD

## Fee Structure

| Component | Calculation |
|-----------|-------------|
| Subtotal | price per ticket x quantity |
| Service fee | 25% of subtotal |
| Order processing fee | $5.95 flat per order |
| **Total** | subtotal + service fee + processing fee |

**Example:** 2 tickets at $89.50 each
- Subtotal: $179.00
- Service fee: $44.75 (25%)
- Processing: $5.95
- **Total: $229.70**

## Ticket Limits

Each event has a per-event ticket limit (typically 4-8 tickets). This limit applies to the total number of tickets in your cart for that event, regardless of ticket type.

## Tips for Finding Events

- **By artist/team**: Search by name (e.g., `search "Taylor Swift"`)
- **By genre**: Use segment + genre filters (e.g., `--segment "Music" --genre "Rock"`)
- **By location**: Filter by city or state (e.g., `--city "Nashville"` or `--state "TX"`)
- **By date**: Use date range (e.g., `--date-from 2026-06-01 --date-to 2026-08-31`)
- **By budget**: Set price limits (e.g., `--max-price 100`)
- **Selling fast**: Check `--status limited` for events with low availability
- **Coming soon**: Check `--status presale` for upcoming releases

## Venue Highlights

| Venue | City | Known For |
|-------|------|-----------|
| Madison Square Garden | New York, NY | World's most famous arena — concerts, NBA, NHL |
| SoFi Stadium | Los Angeles, CA | NFL stadium, mega concerts |
| Red Rocks Amphitheatre | Morrison, CO | Iconic outdoor venue with natural acoustics |
| Fenway Park | Boston, MA | Historic MLB park, summer concerts |
| Ryman Auditorium | Nashville, TN | Mother Church of Country Music |
| Radio City Music Hall | New York, NY | Art Deco theater, Rockettes, Broadway |
| Gorge Amphitheatre | George, WA | Stunning outdoor venue overlooking Columbia River |
