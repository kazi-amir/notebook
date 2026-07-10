---
name: weather
description: Check weather forecasts, history, alerts, air quality, astronomy, and sports events. Use when the user asks about weather, forecasts, temperature, rain, alerts, air quality, sunrise, sunset, moon phase, or sports events.
---

# Weather

Check weather forecasts, history, alerts, air quality, astronomy, and sports events. Data is pre-loaded. No API key or setup needed.

**Important:** Many commands require lat,lon coordinates. Use `search-location` first to get coordinates, then pass them to forecast/history commands.

## Location Search

```bash
# Search for a city's coordinates (both --city and --country-code are required)
python3 {baseDir}/weather_data.py search-location --city "London" --country-code GB

python3 {baseDir}/weather_data.py search-location --city "Tokyo" --country-code JP
```

## Forecast

```bash
# Get weather forecast (requires lat,lon and date)
python3 {baseDir}/weather_data.py forecast --lat-long "51.51,-0.13" --date 2026-04-20

# Forecast with air quality and alerts
python3 {baseDir}/weather_data.py forecast --lat-long "51.51,-0.13" --date 2026-04-20 --aqi yes --alerts yes
```

## Weather History

```bash
# Get historical weather for a specific date
python3 {baseDir}/weather_data.py history --lat-long "51.51,-0.13" --date 2026-04-01
```

## Alerts

```bash
# Get weather alerts for a location
python3 {baseDir}/weather_data.py alerts --query "London"
```

## Air Quality

```bash
# Get air quality data for a location
python3 {baseDir}/weather_data.py air-quality --query "London"
```

## Astronomy

```bash
# Get sunrise, sunset, moonrise, moonset, moon phase (--date is required)
python3 {baseDir}/weather_data.py astronomy --query "London" --date 2026-04-20
```

## Timezone

```bash
# Get timezone info for a location
python3 {baseDir}/weather_data.py timezone --query "London"
```

## Sports Events

```bash
# Get sports events near a location
python3 {baseDir}/weather_data.py sports --query "London"
```

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What's the weather in Paris?" | `search-location --city "Paris"`, then `forecast --lat-long LAT,LON` |
| "Will it rain tomorrow in NYC?" | `search-location --city "New York"`, then `forecast --lat-long LAT,LON --date TOMORROW` |
| "What was the weather last week?" | `search-location --city CITY`, then `history --lat-long LAT,LON --date DATE` |
| "Any weather alerts in Miami?" | `alerts --query "Miami"` |
| "What's the air quality in Beijing?" | `air-quality --query "Beijing"` |
| "What time is sunrise tomorrow?" | `astronomy --query CITY --date DATE` |
| "What timezone is Tokyo in?" | `timezone --query "Tokyo"` |
| "Any sports events near London?" | `sports --query "London"` |
| "Show all weather data" | `show` |

## Data Entities

The weather system provides:

- **Location** -- name, region, country, lat, lon, tz_id, localtime
- **Forecast** -- location, forecastday[] with date, day (maxtemp_c, mintemp_c, avgtemp_c, maxwind_kph, totalprecip_mm, avghumidity, condition), hour[]
- **Alert** -- headline, severity, urgency, areas, category, event, effective, expires, desc, instruction
- **AirQuality** -- co, no2, o3, so2, pm2_5, pm10, us_epa_index, gb_defra_index
- **Astro** -- sunrise, sunset, moonrise, moonset, moon_phase, moon_illumination
- **SportsEvent** -- stadium, country, region, tournament, start, match

## Notes

- `lat_long` format is `"lat,lon"` (e.g. `"51.51,-0.13"`)
- Date format is `YYYY-MM-DD`
- The `--query` parameter accepts city names directly (no coordinates needed)

## Utility

```bash
# Show raw data
python3 {baseDir}/weather_data.py show
```
