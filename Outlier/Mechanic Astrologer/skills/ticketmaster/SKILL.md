---
name: ticketmaster
description: Search events, browse venues and attractions, check ticket availability, manage a shopping cart, and purchase tickets across concerts, sports, theater, comedy, and family shows nationwide. Use when the user asks about concerts, sports games, theater tickets, events near them, or wants to buy tickets.
---

# Ticketmaster

Discover and purchase tickets for concerts, sports, theater, comedy, and family events at venues across the United States.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/ticketmaster_data.py login --email your@email.com
```

## Fetching Data

Use `ticketmaster_data.py` to get JSON data:

```bash
# Search events
python3 {baseDir}/ticketmaster_data.py search "Taylor Swift"
python3 {baseDir}/ticketmaster_data.py search --segment "Music" --city "New York"
python3 {baseDir}/ticketmaster_data.py search --genre "Rock" --status "on_sale" --sort-by "date"
python3 {baseDir}/ticketmaster_data.py search --segment "Sports" --genre "NBA" --max-price 200
python3 {baseDir}/ticketmaster_data.py search --date-from "2026-06-01" --date-to "2026-08-31"
python3 {baseDir}/ticketmaster_data.py search --segment "Comedy" --city "Nashville"

# Event details (includes venue, performers, ticket types)
python3 {baseDir}/ticketmaster_data.py event EVT001

# Browse venues
python3 {baseDir}/ticketmaster_data.py venues
python3 {baseDir}/ticketmaster_data.py venues --city "Los Angeles" --venue-type "arena"
python3 {baseDir}/ticketmaster_data.py venues --state "NY"

# Venue details with upcoming events
python3 {baseDir}/ticketmaster_data.py venue VEN001

# Search attractions (artists, bands, teams, comedians, companies)
python3 {baseDir}/ticketmaster_data.py attractions "Beyonce"
python3 {baseDir}/ticketmaster_data.py attractions --type "band" --genre "Rock"
python3 {baseDir}/ticketmaster_data.py attractions --type "comedian"

# Attraction details with upcoming events
python3 {baseDir}/ticketmaster_data.py attraction ATT001

# Classification hierarchy (Segment > Genre > Sub-Genre)
python3 {baseDir}/ticketmaster_data.py classifications

# Ticket availability for an event
python3 {baseDir}/ticketmaster_data.py availability EVT001

# Section-based seat map
python3 {baseDir}/ticketmaster_data.py seatmap EVT001

# Add tickets to cart (event_id, ticket_type_id, quantity)
python3 {baseDir}/ticketmaster_data.py add-to-cart EVT001 TKT001 2

# View cart with fee breakdown
python3 {baseDir}/ticketmaster_data.py cart

# Remove from cart
python3 {baseDir}/ticketmaster_data.py remove-from-cart 1

# Checkout (complete purchase)
python3 {baseDir}/ticketmaster_data.py checkout

# Order history
python3 {baseDir}/ticketmaster_data.py orders

# Order details (by order ID or confirmation code)
python3 {baseDir}/ticketmaster_data.py order ORD001
python3 {baseDir}/ticketmaster_data.py order TM-A7B3K9

# User profile
python3 {baseDir}/ticketmaster_data.py profile

# Spending analytics
python3 {baseDir}/ticketmaster_data.py spending

# Account summary
python3 {baseDir}/ticketmaster_data.py summary
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Find me concerts in New York" | `ticketmaster_data.py search --segment "Music" --city "New York"` |
| "When is Taylor Swift playing?" | `ticketmaster_data.py search "Taylor Swift"` |
| "What NBA games are coming up?" | `ticketmaster_data.py search --segment "Sports" --genre "NBA"` |
| "Show me comedy shows" | `ticketmaster_data.py search --segment "Comedy"` |
| "What's playing at Madison Square Garden?" | `ticketmaster_data.py venue VEN001` |
| "Are there tickets for Hamilton?" | `ticketmaster_data.py search "Hamilton"` then `availability <event_id>` |
| "What venues are in Chicago?" | `ticketmaster_data.py venues --city "Chicago"` |
| "Show me rock bands touring" | `ticketmaster_data.py attractions --type "band" --genre "Rock"` |
| "How much are tickets for this event?" | `ticketmaster_data.py availability <event_id>` |
| "Which sections are available?" | `ticketmaster_data.py seatmap <event_id>` |
| "Add 2 VIP tickets to my cart" | `ticketmaster_data.py add-to-cart <event_id> <ticket_type_id> 2` |
| "What's in my cart?" | `ticketmaster_data.py cart` |
| "Complete my purchase" | `ticketmaster_data.py checkout` |
| "Show my ticket orders" | `ticketmaster_data.py orders` |
| "Look up confirmation TM-A7B3K9" | `ticketmaster_data.py order TM-A7B3K9` |
| "How much have I spent on tickets?" | `ticketmaster_data.py spending` |
| "Give me a Ticketmaster summary" | `ticketmaster_data.py summary` |
| "What events are this summer?" | `ticketmaster_data.py search --date-from 2026-06-01 --date-to 2026-08-31` |
| "Find family shows under $100" | `ticketmaster_data.py search --segment "Family" --max-price 100` |
| "What types of events are there?" | `ticketmaster_data.py classifications` |

## Key Data

- **90 events** across 5 segments: Music (~35 concerts), Sports (~25 games), Arts & Theater (~15 shows), Comedy (~10 shows), Family (~7 shows)
- **18 venues** nationwide: Madison Square Garden, SoFi Stadium, Red Rocks, Fenway Park, United Center, Ryman Auditorium, and more
- **45 attractions**: Artists (Taylor Swift, Beyonce, Kendrick Lamar), bands (Foo Fighters, Radiohead), sports teams (Lakers, Yankees), comedians (John Mulaney, Trevor Noah), theater companies (Hamilton, Wicked)
- **Classification hierarchy**: Segment > Genre > Sub-Genre (e.g., Music > Pop > Pop, Sports > NBA > NBA)
- **Ticket types**: 3-5 tiers per event (GA, Reserved, Premium, VIP) with section labels
- **Status lifecycle**: presale > on_sale > limited > sold_out (also cancelled, postponed)
- **Fees**: 25% service fee + $5.95 order processing fee per order
- **Ticket limits**: 4-8 per event, enforced at cart addition

## Purchase Flow

1. **Browse**: Search events, check venue schedules, or find attractions
2. **Select**: Get event details with `event` to see all performers and ticket types
3. **Check availability**: Use `availability` or `seatmap` to see what's open
4. **Add to cart**: Use `add-to-cart` with the event ID, ticket type ID, and quantity
5. **Review**: Check `cart` to see items with fee breakdown
6. **Purchase**: Run `checkout` to complete the order and get confirmation codes
7. **Verify**: Check `orders` or look up by confirmation code with `order`

## Analysis Tips

- **Spending breakdown**: The `spending` command shows total spent, average per order, and breakdowns by event segment and venue
- **Upcoming events**: The `summary` command lists upcoming events from your order history
- **Price comparison**: Use `availability` on multiple events to compare ticket tiers and prices
- **Status tracking**: Use `search --status limited` to find events selling fast
- **Fee awareness**: All prices shown on tickets are pre-fee. The cart shows the full breakdown including the 25% service fee and $5.95 processing fee

## Reference

- `{baseDir}/references/event_guide.md` — Event types, venue guide, and ticket buying tips
