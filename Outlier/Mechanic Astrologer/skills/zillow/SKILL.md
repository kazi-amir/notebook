---
name: zillow
description: Search real estate listings, get Zestimates, analyze market trends, calculate mortgages, and evaluate investment properties. Use when the user asks about buying or renting homes, property values, market conditions, or real estate investments.
---

# Zillow

Search properties, get Zestimates, analyze markets, and calculate mortgages. Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/zillow_data.py login --email your@email.com
```

## Searching Properties

```bash
# Search by location (city, state, or zip)
python3 {baseDir}/zillow_data.py search --location "San Francisco"

# Filter by price range and bedrooms
python3 {baseDir}/zillow_data.py search --city "Austin" --min-price 300000 --max-price 600000 --min-beds 3

# Filter by home type and status
python3 {baseDir}/zillow_data.py search --state CA --home-type "Single Family" --status "For Sale"

# Sort by price descending, limit results
python3 {baseDir}/zillow_data.py search --state NY --sort-by price --sort-order DESC --limit 10

# Combine multiple filters
python3 {baseDir}/zillow_data.py search --city "Seattle" --min-beds 2 --max-price 800000 --min-sqft 1200 --max-hoa 500
```

### Search Filters

| Filter | Flag | Example |
|--------|------|---------|
| Location (general) | `--location` | `--location "Portland OR"` |
| City | `--city` | `--city "Denver"` |
| State | `--state` | `--state CO` |
| ZIP code | `--zip` | `--zip 94122` |
| Price range | `--min-price`, `--max-price` | `--min-price 200000 --max-price 500000` |
| Bedrooms | `--min-beds`, `--max-beds` | `--min-beds 3 --max-beds 5` |
| Bathrooms | `--min-baths`, `--max-baths` | `--min-baths 2` |
| Square footage | `--min-sqft`, `--max-sqft` | `--min-sqft 1500` |
| Home type | `--home-type` | `--home-type "Condo"` |
| Status | `--status` | `--status "For Sale"` |
| Year built | `--min-year` | `--min-year 2000` |
| Max HOA | `--max-hoa` | `--max-hoa 300` |
| Sort | `--sort-by`, `--sort-order` | `--sort-by price --sort-order DESC` |
| Limit | `--limit` | `--limit 10` |

Sort options: `price`, `days_on_zillow`, `bedrooms`, `bathrooms`, `sqft`, `year_built`, `zestimate`

## Property Details & Valuation

```bash
# Get full property details
python3 {baseDir}/zillow_data.py details --id 42

# Get Zestimate (Zillow's estimated market value)
python3 {baseDir}/zillow_data.py zestimate --id 42

# Get comparable properties (similar location, price, features)
python3 {baseDir}/zillow_data.py comps --id 42 --limit 5
```

## Market Analysis

```bash
# Get market trends for a region
python3 {baseDir}/zillow_data.py market --region "San Francisco"

# Get market trends by state
python3 {baseDir}/zillow_data.py market --state TX

# Get top markets by metric
python3 {baseDir}/zillow_data.py top-markets --metric price_change_yoy --limit 10
```

Top market metrics: `median_home_price`, `price_change_yoy`, `inventory`, `homes_sold`

## Mortgage Calculator

```bash
# Basic mortgage calculation
python3 {baseDir}/zillow_data.py mortgage --price 500000

# Full calculation with custom terms
python3 {baseDir}/zillow_data.py mortgage --price 750000 --down-payment 25 --rate 6.25 --term 30 --tax-rate 1.2 --insurance 1500 --hoa 350
```

## Investment Analysis

```bash
# Analyze a property as rental investment
python3 {baseDir}/zillow_data.py invest-analyze --id 42

# Custom investment assumptions
python3 {baseDir}/zillow_data.py invest-analyze --id 42 --down-payment 25 --rate 7.0 --vacancy 10 --expense-ratio 50
```

Returns: cap rate, cash-on-cash return, gross rent multiplier, 1% rule check, DSCR.

## Saved Properties & Tours

```bash
# Get your saved/bookmarked properties
python3 {baseDir}/zillow_data.py saved

# Get your scheduled property tours
python3 {baseDir}/zillow_data.py tours
```

## Discovery

```bash
# List all available cities and states
python3 {baseDir}/zillow_data.py locations

# List all home types
python3 {baseDir}/zillow_data.py home-types

# Get your profile info
python3 {baseDir}/zillow_data.py profile
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Find homes in Austin under $500K" | `search --city Austin --max-price 500000 --status "For Sale"` |
| "What's this property worth?" | `zestimate --id N` |
| "Show me 3-bedroom condos in Seattle" | `search --city Seattle --min-beds 3 --home-type Condo` |
| "What are market trends in California?" | `market --state CA` |
| "How much would my mortgage be?" | `mortgage --price N --down-payment N --rate N` |
| "Is this a good investment property?" | `invest-analyze --id N` then review cap rate, cash-on-cash, DSCR |
| "Show me similar properties" | `comps --id N` |
| "What properties have I saved?" | `saved` |
| "What tours do I have scheduled?" | `tours` |
| "What cities have listings?" | `locations` |

## Reference Guides

- **Investment analysis**: See `{baseDir}/references/investing.md` for cap rate targets, expense estimation, and market quality checklist
- **Pricing strategy**: See `{baseDir}/references/pricing.md` for buyer/seller pricing guidance and Zestimate caveats
