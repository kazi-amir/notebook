---
name: city
description: Look up crime rate data by zip code, check API usage limits, and view raw data. Use when the user asks about crime rates, neighborhood safety, zip code safety data, or city crime statistics.
---

# City

Look up crime rate data (violent and property crime rates per 1,000 residents) by zip code.

Data is served from a rate-limited API. No setup needed.

## Crime Rates

```bash
# Get crime rate for a zip code
python3 {baseDir}/city_data.py get-crime-rate --zip-code 90210
```

Returns: `zip_code`, `violent_crime` (rate per 1,000), `property_crime` (rate per 1,000).

## API Limits

The API allows **100 calls per 30-minute window**.

```bash
# Check how many API calls you've made
python3 {baseDir}/city_data.py api-call-count

# Check the API call limit
python3 {baseDir}/city_data.py api-call-limit
```

## Utility

```bash
# Show raw crime data
python3 {baseDir}/city_data.py show
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Is 90210 safe?" | `get-crime-rate --zip-code 90210` |
| "What's the crime rate in zip 60614?" | `get-crime-rate --zip-code 60614` |
| "Compare safety of two neighborhoods" | `get-crime-rate` for each zip, compare violent + property rates |
| "How many API calls do I have left?" | `api-call-count` then `api-call-limit`, subtract |
| "Show all crime data" | `show` |

## Data Entities

### CrimeData

| Field | Description |
|-------|-------------|
| `zip_code` | 5-digit US zip code |
| `violent_crime` | Violent crime rate per 1,000 residents |
| `property_crime` | Property crime rate per 1,000 residents |
