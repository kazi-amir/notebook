---
name: health-guardian
description: Proactive health monitoring using Apple Health data. Track heart rate, HRV, sleep, steps, workouts, VO2 Max, and body metrics. Detect patterns, anomalies, and generate health summaries. Use when the user asks about their health, vitals, sleep quality, fitness, activity levels, or wants a health analysis.
---

# Health Guardian

Proactive health intelligence from Apple Health. Track vitals, detect patterns, alert on anomalies.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/health_data.py login --email your@email.com
```

## Fetching Data

Use `health_data.py` to get JSON data:

```bash
# Heart rate (last 7 days default)
python3 {baseDir}/health_data.py heart-rate --days 14

# Resting heart rate
python3 {baseDir}/health_data.py resting-hr --days 30

# HRV (Heart Rate Variability SDNN)
python3 {baseDir}/health_data.py hrv --days 30

# Sleep analysis (grouped by night, with stages)
python3 {baseDir}/health_data.py sleep --days 14

# Step count (aggregated by day)
python3 {baseDir}/health_data.py steps --days 7

# Workouts (all types: running, cycling, yoga, etc.)
python3 {baseDir}/health_data.py workouts --days 30

# VO2 Max (cardio fitness)
python3 {baseDir}/health_data.py vo2max --days 90

# Body measurements (weight history + height)
python3 {baseDir}/health_data.py body --days 90

# Daily activity summary (calories, exercise minutes, stand hours, distance)
python3 {baseDir}/health_data.py activity --days 7

# Combined summary with averages across all metrics
python3 {baseDir}/health_data.py summary --days 7

# Custom date range
python3 {baseDir}/health_data.py sleep --start 2025-12-18 --end 2026-01-17

# User profile
python3 {baseDir}/health_data.py profile
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How did I sleep?" | `python3 {baseDir}/health_data.py sleep --days 7`, report hours + stages + efficiency |
| "What's my heart rate been like?" | `python3 {baseDir}/health_data.py resting-hr --days 14`, report trend |
| "How's my HRV?" | `python3 {baseDir}/health_data.py hrv --days 30`, analyze trend |
| "How many steps today?" | `python3 {baseDir}/health_data.py steps --days 1` |
| "Show me my workouts" | `python3 {baseDir}/health_data.py workouts --days 30` |
| "Am I getting fitter?" | `python3 {baseDir}/health_data.py vo2max --days 90`, analyze trend |
| "Give me a health summary" | `python3 {baseDir}/health_data.py summary --days 7` |
| "Any health concerns?" | `python3 {baseDir}/health_data.py summary --days 14` |
| "How active have I been?" | `python3 {baseDir}/health_data.py activity --days 7` |
| "What's my weight trend?" | `python3 {baseDir}/health_data.py body --days 90` |

## Available Metrics

| Metric | Source | Frequency | Key Insight |
|--------|--------|-----------|-------------|
| **Heart Rate** | Apple Watch | ~50/day | Real-time cardiovascular response |
| **Resting Heart Rate** | Apple Watch | 1/day | Cardiovascular fitness indicator |
| **HRV (SDNN)** | Apple Watch | 1/day | Autonomic nervous system balance |
| **Sleep** | Apple Watch | Nightly | Sleep stages (Core, Deep, REM, Awake) |
| **Steps** | Apple Watch + iPhone | Continuous | Daily movement |
| **Active Energy** | Apple Watch | Continuous | Calories from movement |
| **Exercise Minutes** | Apple Watch | Per session | Dedicated exercise time |
| **Stand Hours** | Apple Watch | Hourly | Sedentary behavior |
| **VO2 Max** | Apple Watch | ~Weekly | Cardiorespiratory fitness |
| **Body Mass** | iPhone Health app | ~Weekly | Weight tracking |
| **Workouts** | Apple Watch | Per session | Detailed workout data with duration, calories, distance |

## Anomaly Detection

The analyzer checks for:
- **Heart rate anomalies**: Elevated average HR, unusually low HR
- **Resting HR trends**: Rising resting heart rate over time
- **HRV decline**: Dropping HRV indicating stress or overtraining
- **Sleep degradation**: Recent nights significantly worse than baseline
- **Low activity**: Below-threshold daily steps
- **VO2 Max decline**: Cardiovascular fitness dropping
- **Weight changes**: Significant weight gain or loss

## Health Analysis

When the user asks about their health, trends, or wants insights, use `{baseDir}/references/health_metrics.md` for:
- Normal ranges for heart rate, HRV, sleep, VO2 Max by age and fitness
- Pattern interpretation (what do changes mean?)
- Actionable recommendations
- Red flags that suggest medical consultation

### Analysis workflow
1. Fetch data: `python3 {baseDir}/health_data.py summary --days N`
2. Read `{baseDir}/references/health_metrics.md` for interpretation framework
3. Synthesize findings into personalized insights
4. Always include disclaimer that this is not medical advice

## References

- `{baseDir}/references/health_metrics.md` -- health metric interpretation guide with normal ranges and recommendations
