---
name: eight-sleep
description: Access Eight Sleep Pod smart bed data (sleep sessions, temperature control, HRV, heart rate, sleep stages, alarms). Use when the user asks about sleep quality, bed temperature, sleep fitness scores, HRV trends, or alarm settings from their Eight Sleep Pod.
---

# Eight Sleep

Query sleep analytics, temperature settings, and alarm data from the Eight Sleep Pod smart bed.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/eight_sleep_data.py login --email your@email.com
```

## Fetching Data

Use `eight_sleep_data.py` to get JSON data:

```bash
# Sleep sessions (last 7 days default)
python3 {baseDir}/eight_sleep_data.py sleep --days 14

# Sleep fitness trends (averages + daily scores)
python3 {baseDir}/eight_sleep_data.py trends --days 30

# Current bed temperature
python3 {baseDir}/eight_sleep_data.py temperature

# Temperature schedules (bedtime, deep sleep, wake-up)
python3 {baseDir}/eight_sleep_data.py schedules

# Alarms (vibration, thermal, sound settings)
python3 {baseDir}/eight_sleep_data.py alarms

# Device status (Pod model, firmware, water level)
python3 {baseDir}/eight_sleep_data.py device

# User profile
python3 {baseDir}/eight_sleep_data.py profile

# Combined summary with all data
python3 {baseDir}/eight_sleep_data.py summary --days 7

# Set bed temperature (-100 to 100, per side)
python3 {baseDir}/eight_sleep_data.py set-temperature --level 20 --side left
python3 {baseDir}/eight_sleep_data.py set-temperature --level -30 --side right

# Custom date range
python3 {baseDir}/eight_sleep_data.py sleep --start 2026-01-01 --end 2026-01-15
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How did I sleep?" | `{baseDir}/eight_sleep_data.py summary --days 7`, report sleep fitness + stages |
| "What's my sleep score?" | `{baseDir}/eight_sleep_data.py trends --days 14`, report fitness score trend |
| "What temperature is my bed?" | `{baseDir}/eight_sleep_data.py temperature` |
| "Show my sleep trends" | `{baseDir}/eight_sleep_data.py trends --days 30`, analyze patterns |
| "What time do my alarms go off?" | `{baseDir}/eight_sleep_data.py alarms` |
| "Am I getting enough deep sleep?" | `{baseDir}/eight_sleep_data.py sleep --days 14`, check deep_duration_s |
| "How's my HRV?" | `{baseDir}/eight_sleep_data.py trends --days 14`, report avg HRV |
| "Change my bed temperature" | `python3 {baseDir}/eight_sleep_data.py set-temperature --level LEVEL --side SIDE` |

## Key Metrics

- **Sleep Fitness Score** (0-100): Overall sleep quality assessment
- **Duration Score** (0-100): Whether you slept enough relative to your goal
- **Quality Score** (0-100): Sleep stage composition and restfulness
- **Temperature** (-100 to 100): Bed temperature on Eight Sleep scale. Negative = cooling, positive = warming
- **HRV** (ms): Heart rate variability during sleep. Higher = better recovery
- **Sleep Stages**: Awake, Light, Deep, REM durations in seconds

### Sleep Stage Targets (% of total sleep)

| Stage | Healthy Range | Notes |
|-------|--------------|-------|
| Deep | 13-23% | Decreases with age, critical for recovery |
| REM | 20-25% | Important for memory and learning |
| Light | 45-55% | Normal bulk of sleep |
| Awake | <10% | Lower is better |

### Temperature Settings

| Level | Description |
|-------|-------------|
| -100 to -50 | Very cold (deep sleep boost) |
| -50 to -10 | Cool (typical bedtime setting) |
| -10 to 10 | Neutral |
| 10 to 50 | Warm (wake-up warming) |
| 50 to 100 | Very warm |

## Health Analysis

When the user asks about their sleep health, trends, or wants insights, use `{baseDir}/references/sleep_analysis.md` for:
- Science-backed interpretation of sleep stages, HRV, heart rate
- Temperature optimization strategies
- Normal ranges by age
- Pattern detection (consistency, weekend shifts, seasonal effects)
- Actionable recommendations for better sleep

### Analysis workflow
1. Fetch data: `python3 {baseDir}/eight_sleep_data.py summary --days N`
2. Read `{baseDir}/references/sleep_analysis.md` for interpretation framework
3. Apply the 5-step analysis: Status -> Trends -> Patterns -> Insights -> Flags
4. Always include disclaimer that this is not medical advice

## References

- `{baseDir}/references/sleep_analysis.md` -- science-backed sleep data interpretation guide
