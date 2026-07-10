---
name: garmin-connect
description: Access Garmin Connect health and fitness data (daily activity, sleep, heart rate, HRV, stress, body battery, SpO2, training readiness, workouts, body composition). Use when the user asks about steps, heart rate, sleep quality, stress levels, body battery, training readiness, HRV trends, workout history, weight, or any Garmin health metrics.
---

# Garmin Connect

Query health and fitness data from Garmin Connect. Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/garmin_data.py login --email your@email.com
```

## Fetching Data

Use `garmin_data.py` to get JSON data:

```bash
# Daily activity summary (steps, HR, calories, distance)
python3 {baseDir}/garmin_data.py summary --days 7

# Sleep data (duration, quality, stages)
python3 {baseDir}/garmin_data.py sleep --days 14

# Activities/workouts
python3 {baseDir}/garmin_data.py activities --days 30

# Heart rate (resting, min, max, avg)
python3 {baseDir}/garmin_data.py heart_rate --days 14

# HRV (heart rate variability)
python3 {baseDir}/garmin_data.py hrv --days 30

# Stress levels
python3 {baseDir}/garmin_data.py stress --days 7

# Body battery
python3 {baseDir}/garmin_data.py body_battery --days 7

# SpO2 (blood oxygen)
python3 {baseDir}/garmin_data.py spo2 --days 7

# Respiration rate
python3 {baseDir}/garmin_data.py respiration --days 7

# Body composition (weight, BMI, body fat, muscle mass)
python3 {baseDir}/garmin_data.py body_composition --days 30

# Training readiness scores
python3 {baseDir}/garmin_data.py training_readiness --days 7

# Combined health snapshot with averages
python3 {baseDir}/garmin_data.py health_snapshot --days 7

# Custom date range
python3 {baseDir}/garmin_data.py summary --start 2026-01-01 --end 2026-01-31

# Registered devices
python3 {baseDir}/garmin_data.py devices

# User profile
python3 {baseDir}/garmin_data.py profile
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How many steps did I take?" | `python3 {baseDir}/garmin_data.py summary --days 7`, report steps |
| "How did I sleep?" | `python3 {baseDir}/garmin_data.py sleep --days 7`, report quality + duration |
| "What's my resting heart rate?" | `python3 {baseDir}/garmin_data.py heart_rate --days 7`, report resting HR trend |
| "Is my HRV improving?" | `python3 {baseDir}/garmin_data.py hrv --days 30`, analyze trend |
| "How stressed am I?" | `python3 {baseDir}/garmin_data.py stress --days 7`, report stress levels |
| "What's my body battery?" | `python3 {baseDir}/garmin_data.py body_battery --days 7`, report charge/drain |
| "Am I ready to train?" | `python3 {baseDir}/garmin_data.py training_readiness --days 7`, report readiness |
| "Show my workouts" | `python3 {baseDir}/garmin_data.py activities --days 30`, list activities |
| "What's my weight trend?" | `python3 {baseDir}/garmin_data.py body_composition --days 30`, report weight |
| "Give me a health overview" | `python3 {baseDir}/garmin_data.py health_snapshot --days 7`, full summary |

## Key Metrics

- **Steps**: Daily step count, distance, calories, active minutes
- **Sleep Score** (0-100): Quality rating (fair <75, good 75-89, excellent 90+)
- **Resting Heart Rate** (bpm): Lower = better cardiovascular fitness
- **HRV** (ms): Higher = better recovery capacity; track weekly average trend
- **Stress** (0-100): calm <30, moderate 30-50, high >50
- **Body Battery** (0-100): Morning value indicates recovery quality
- **Training Readiness** (0-100): low <40, moderate 40-65, high 66-85, prime >85
- **SpO2** (%): Normal 95-100%, concern <93%

## Health Analysis

When the user asks about their health, trends, or wants insights, use `{baseDir}/references/health_analysis.md` for:
- Science-backed interpretation of all Garmin metrics
- Normal ranges by age and fitness level
- Pattern detection (overtraining, sleep debt, stress trends)
- Actionable recommendations based on data
- Red flags that suggest medical consultation

### Analysis workflow
1. Fetch data: `python3 {baseDir}/garmin_data.py health_snapshot --days N`
2. Read `{baseDir}/references/health_analysis.md` for interpretation framework
3. Apply the 5-step analysis: Status -> Trends -> Patterns -> Insights -> Flags
4. Always include disclaimer that this is not medical advice

## References

- `{baseDir}/references/health_analysis.md` -- science-backed health data interpretation guide
