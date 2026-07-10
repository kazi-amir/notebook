---
name: flights
description: Search flights, compare airfare, and look up airport codes. Use when the user asks about flights, airfare, airports, airline tickets, travel bookings, or flight search.
---

# Flights

Search for flights across airlines and look up airport IATA codes.

## Searching Flights

Search for available flights by origin, destination, and date:

```bash
# One-way flight search
python3 {baseDir}/flights_data.py search-flights --origin JFK --destination LAX --departure-date 2026-06-15

# Round-trip flight search
python3 {baseDir}/flights_data.py search-flights --origin SFO --destination ORD --departure-date 2026-07-01 --trip-type round_trip --return-date 2026-07-08

# Business class, 2 passengers
python3 {baseDir}/flights_data.py search-flights --origin BOS --destination MIA --departure-date 2026-08-10 --cabin-class business --passengers 2

# With baggage options
python3 {baseDir}/flights_data.py search-flights --origin SEA --destination DEN --departure-date 2026-09-01 --carry-on-bag 1 --checked-bags 2

# Paginated results
python3 {baseDir}/flights_data.py search-flights --origin ATL --destination DFW --departure-date 2026-06-20 --offset 10 --limit 5
```

## Airport Lookup

Look up airport IATA codes by city name or partial code:

```bash
# Search by city name
python3 {baseDir}/flights_data.py search-airports --query "San Francisco"

# Search by partial code
python3 {baseDir}/flights_data.py search-airports --query "JFK"

# Filter by country
python3 {baseDir}/flights_data.py search-airports --query "London" --country-code GB

# Limit results
python3 {baseDir}/flights_data.py search-airports --query "New" --limit 5
```

## Cabin Classes

| Class | Description |
|-------|-------------|
| economy | Standard seating |
| business | Premium seating with extra legroom and services |
| first | Top-tier seating with full-service amenities |

## Trip Types

| Type | Description |
|------|-------------|
| one_way | Single direction flight |
| round_trip | Outbound and return flights |

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Find flights from NYC to LA" | `search-flights --origin JFK --destination LAX --departure-date DATE` |
| "What's the cheapest flight to Miami?" | `search-flights --origin ORIGIN --destination MIA --departure-date DATE` |
| "Book a round trip to Chicago" | `search-flights --origin ORIGIN --destination ORD --departure-date DATE --trip-type round_trip --return-date DATE` |
| "Business class to London" | `search-flights --origin ORIGIN --destination LHR --departure-date DATE --cabin-class business` |
| "What's the airport code for Denver?" | `search-airports --query "Denver"` |
| "Show airports in Japan" | `search-airports --query "Japan" --country-code JP` |
| "Show all flight data" | `show` |

## Data Entities

### Flight

| Field | Description |
|-------|-------------|
| flight_id | Unique flight identifier |
| airline | Operating airline name |
| flight_number | Airline flight number |
| origin | Departure airport IATA code |
| destination | Arrival airport IATA code |
| departure_datetime | Departure date and time |
| arrival_datetime | Arrival date and time |
| duration_minutes | Total flight duration in minutes |
| price_per_passenger | Price per passenger in USD |
| cabin_class | economy, business, or first |
| aircraft_type | Aircraft model |
| stops | Number of stops (0 = nonstop) |
| layover_airports | List of layover airport IATA codes |
| legs | List of FlightLeg objects for multi-stop flights |

### FlightLeg

| Field | Description |
|-------|-------------|
| flight_number | Leg flight number |
| airline | Leg operating airline |
| origin | Leg departure airport |
| destination | Leg arrival airport |
| departure_datetime | Leg departure time |
| arrival_datetime | Leg arrival time |
| duration_minutes | Leg duration in minutes |
| aircraft_type | Leg aircraft model |

### Airport

| Field | Description |
|-------|-------------|
| iata_code | 3-letter IATA airport code |
| municipality | City name |
| iso_country | 2-letter country code |
| iso_region | Region/state code |
| latitude_deg | Latitude coordinate |
| longitude_deg | Longitude coordinate |

## Notes

- Always use IATA codes (3-letter codes like JFK, LAX, SFO) for origin and destination.
- Use the airport search tool to find IATA codes when the user provides city names.
- Dates must be in YYYY-MM-DD format.
- For round-trip searches, both `--departure-date` and `--return-date` are required.
- Prices are per passenger in USD.
