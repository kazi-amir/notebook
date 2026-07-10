---
name: stayncook
description: Search vacation rental listings and check availability. Use when the user asks about vacation rentals, holiday homes, accommodation, lodging, Airbnb-style listings, or places to stay.
---

# StayNCook

Search vacation rental listings and check availability. Data is pre-loaded. No API key or setup needed.

## Searching Listings

```bash
# Search listings in a city
python3 {baseDir}/stayncook_data.py search --city "Paris" --country-code FR

# Search with dates and guest count
python3 {baseDir}/stayncook_data.py search --city "London" --country-code GB --checkin 2026-05-01 --checkout 2026-05-07 --adults 2

# Search with price range and pagination
python3 {baseDir}/stayncook_data.py search --city "Tokyo" --country-code JP --min-price 50 --max-price 200 --offset 0 --limit 10

# Search with children, infants, and pets
python3 {baseDir}/stayncook_data.py search --city "Barcelona" --country-code ES --adults 2 --children 1 --infants 1 --pets 1
```

## Listing Details

```bash
# Get detailed info for a specific listing
python3 {baseDir}/stayncook_data.py listing-details --id "listing-123"

# Check availability for specific dates and guests
python3 {baseDir}/stayncook_data.py listing-details --id "listing-123" --checkin 2026-05-01 --checkout 2026-05-07 --adults 2 --children 1
```

## Property Types

| Type | Description |
|------|-------------|
| `Apartment` | Standard apartment unit |
| `House` | Full standalone house |
| `Condo` | Condominium unit |
| `Townhouse` | Multi-floor townhouse |
| `Loft` | Open-plan loft space |
| `Villa` | Luxury villa property |
| `Cottage` | Small countryside cottage |
| `Cabin` | Rustic cabin property |
| `Bungalow` | Single-story bungalow |
| `Studio` | Compact studio unit |
| `Guest suite` | Private guest suite |
| `Entire floor` | Full floor of a building |

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Find me a place to stay in Paris" | `search --city "Paris" --country-code FR` |
| "Any pet-friendly rentals in London?" | `search --city "London" --country-code GB --pets 1` |
| "I need a place for 4 adults and 2 kids" | `search --city CITY --adults 4 --children 2` |
| "Show me listings under $100/night" | `search --city CITY --max-price 100` |
| "Is this listing available next week?" | `listing-details --id ID --checkin DATE --checkout DATE --adults N` |
| "Tell me more about listing X" | `listing-details --id X` |
| "Show me the next page of results" | `search --city CITY --offset 10 --limit 10` |
| "Show all listing data" | `show` |

## Data Entities

The StayNCook system provides:

- **ListingSummary** -- listing_id, title, city, country_code, state_or_region, price_per_night, max_guests, bedrooms, beds, bathrooms, property_type, amenities[], description, host_name, rating, num_reviews, images[], allows_pets, instant_book, total_price
- **ListingDetails** -- (extends ListingSummary) available_dates[], is_available, num_nights, can_accommodate_guests, requested_guests, pets_allowed

## Notes

- Dates must be in `YYYY-MM-DD` format
- `country_code` is a 2-letter ISO country code (e.g. `FR`, `GB`, `US`, `JP`)
- All search parameters are optional; omit any to get unfiltered results
- Use `offset` and `limit` for pagination through large result sets

## Utility

```bash
# Show raw data
python3 {baseDir}/stayncook_data.py show
```
