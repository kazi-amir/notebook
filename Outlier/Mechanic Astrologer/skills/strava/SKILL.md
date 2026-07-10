---
name: strava
description: Load and analyze Strava activities, stats, and workouts. Use when user asks about their runs, rides, swims, workout history, fitness stats, personal records, or training zones.
---

# Strava

Load and analyze Strava activities, stats, and workouts.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/strava_data.py login --email your@email.com
```

## Fetching Data

Use `strava_data.py` to get JSON data:

### List Recent Activities

```bash
# Last 30 activities (default)
python3 {baseDir}/strava_data.py activities

# With pagination
python3 {baseDir}/strava_data.py activities --per-page 10 --page 1

# Filter by activity type
python3 {baseDir}/strava_data.py activities --type Run
python3 {baseDir}/strava_data.py activities --type Ride
python3 {baseDir}/strava_data.py activities --type Swim

# Filter by date range
python3 {baseDir}/strava_data.py activities --days 30
python3 {baseDir}/strava_data.py activities --after 2026-01-01 --before 2026-01-31

# Combine filters
python3 {baseDir}/strava_data.py activities --type Run --days 14
```

Returns: activity name, type, distance (meters), moving time (seconds), elevation gain, average/max speed, heart rate, calories, kudos, PRs.

Available types: `Run`, `Ride`, `Swim`, `Walk`, `Hike`, `WeightTraining`, `Yoga`, `Workout`

### Get Activity Details

```bash
# Full details for a specific activity (use ID from activities list)
python3 {baseDir}/strava_data.py activity --id ACTIVITY_ID
```

Returns: all activity fields including watts, cadence, elevation high/low, suffer score, gear, device name, and description.

### Get Athlete Profile

```bash
python3 {baseDir}/strava_data.py profile
```

Returns: name, city, state, country, sex, premium status, weight, FTP.

### Get Athlete Statistics

```bash
python3 {baseDir}/strava_data.py stats
```

Returns: year-to-date, all-time, and recent totals for Run, Ride, and Swim (count, distance, moving time, elevation gain, achievements).

### Get Personal Records

```bash
python3 {baseDir}/strava_data.py records
```

Returns: personal bests with activity type, record name, value, unit, and date achieved.

### Get Training Zones

```bash
python3 {baseDir}/strava_data.py zones
```

Returns: heart rate zones (5 zones) and power zones (7 zones) with min/max values.

### Combined Fitness Summary

```bash
# Overview of last 30 days (default)
python3 {baseDir}/strava_data.py summary --days 30

# Last 90 days
python3 {baseDir}/strava_data.py summary --days 90
```

Returns: athlete profile, activity breakdown by type, totals (distance, time, elevation, calories), and all-time stats.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "Show me my last 10 activities" | `python3 {baseDir}/strava_data.py activities --per-page 10` |
| "What runs did I do last week?" | `python3 {baseDir}/strava_data.py activities --type Run --days 7` |
| "Get details for my most recent ride" | List activities with `--type Ride --per-page 1`, then use the ID with `activity --id` |
| "What's my total distance this month?" | `python3 {baseDir}/strava_data.py summary --days 30`, report distance |
| "Show my profile and stats" | `python3 {baseDir}/strava_data.py profile` and `python3 {baseDir}/strava_data.py stats` |
| "What are my personal records?" | `python3 {baseDir}/strava_data.py records` |
| "What are my heart rate zones?" | `python3 {baseDir}/strava_data.py zones` |
| "How active was I this year?" | `python3 {baseDir}/strava_data.py stats`, report YTD totals |

## Common Data Fields

- **distance**: Distance in meters. Divide by 1000 for km, by 1609.34 for miles.
- **moving_time**: Moving time in seconds. Divide by 60 for minutes, by 3600 for hours.
- **elapsed_time**: Total time including stops, in seconds.
- **total_elevation_gain**: Elevation gain in meters. Multiply by 3.281 for feet.
- **average_speed**: Average speed in m/s. Multiply by 3.6 for km/h, by 2.237 for mph.
- **average_heartrate**: Average heart rate in bpm (if available).
- **calories**: Estimated calories burned.
- **suffer_score**: Strava's relative effort score based on heart rate.

## Tips

- Convert m/s to min/km pace: `1000 / (speed * 60)` gives minutes per km
- Convert m/s to min/mile pace: `1609.34 / (speed * 60)` gives minutes per mile
- Activities with `trainer: true` were done on an indoor trainer
- Activities with `commute: true` were flagged as commutes

Output is JSON to stdout. Parse it to answer user questions.
