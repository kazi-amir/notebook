---
name: whoop
description: Access Whoop wearable health data (sleep, recovery, strain, HRV, workouts) and generate interactive charts. Use when the user asks about sleep quality, recovery scores, strain levels, HRV trends, workout data, or wants health visualizations/graphs from their Whoop band.
---

# Whoop

Query health metrics from the Whoop wearable and generate interactive HTML charts.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/whoop_data.py login --email your@email.com
```

## Fetching Data

Use `whoop_data.py` to get JSON data:

```bash
# Sleep (last 7 days default)
python3 {baseDir}/whoop_data.py sleep --days 14

# Recovery scores
python3 {baseDir}/whoop_data.py recovery --days 30

# Strain/cycles
python3 {baseDir}/whoop_data.py cycles --days 7

# Workouts
python3 {baseDir}/whoop_data.py workouts --days 30

# Combined summary with averages
python3 {baseDir}/whoop_data.py summary --days 7

# Custom date range
python3 {baseDir}/whoop_data.py sleep --start 2026-01-01 --end 2026-01-15

# User profile / body measurements
python3 {baseDir}/whoop_data.py profile
python3 {baseDir}/whoop_data.py body
```

Output is JSON to stdout. Parse it to answer user questions.

## Generating Charts

Use `whoop_chart.py` for interactive HTML visualizations:

```bash
# Sleep analysis (performance + stages)
python3 {baseDir}/whoop_chart.py sleep --days 30

# Recovery bars (color-coded green/yellow/red)
python3 {baseDir}/whoop_chart.py recovery --days 30

# Strain & calories trend
python3 {baseDir}/whoop_chart.py strain --days 90

# HRV & resting heart rate trend
python3 {baseDir}/whoop_chart.py hrv --days 90

# Full dashboard (all 4 charts)
python3 {baseDir}/whoop_chart.py dashboard --days 30

# Save to specific file
python3 {baseDir}/whoop_chart.py dashboard --days 90 --output ~/Desktop/whoop.html
```

Charts open automatically in the default browser. They use ApexCharts with dark theme, stat cards, and tooltips.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How did I sleep?" | `{baseDir}/whoop_data.py summary --days 7`, report sleep performance + hours |
| "How's my recovery?" | `{baseDir}/whoop_data.py recovery --days 7`, report scores + trend |
| "Show me a chart for the last month" | `{baseDir}/whoop_chart.py dashboard --days 30` |
| "Is my HRV improving?" | `{baseDir}/whoop_data.py recovery --days 30`, analyze trend |
| "How much did I train this week?" | `{baseDir}/whoop_data.py workouts --days 7`, list activities |

## Key Metrics

- **Recovery** (0-100%): Green >=67%, Yellow 34-66%, Red <34%
- **Strain** (0-21): Daily exertion score based on HR
- **Sleep Performance**: Actual sleep vs. sleep needed
- **HRV** (ms): Higher = better recovery, track trend over time
- **RHR** (bpm): Lower = better cardiovascular fitness

## Health Analysis

When the user asks about their health, trends, or wants insights, use `{baseDir}/references/health_analysis.md` for:
- Science-backed interpretation of HRV, RHR, sleep stages, recovery, strain, SpO2
- Normal ranges by age and fitness level
- Pattern detection (day-of-week effects, sleep debt, overtraining signals)
- Actionable recommendations based on data
- Red flags that suggest medical consultation

### Analysis workflow
1. Fetch data: `python3 {baseDir}/whoop_data.py summary --days N`
2. Read `{baseDir}/references/health_analysis.md` for interpretation framework
3. Apply the 5-step analysis: Status -> Trends -> Patterns -> Insights -> Flags
4. Always include disclaimer that this is not medical advice

## References

- `{baseDir}/references/health_analysis.md` -- science-backed health data interpretation guide
