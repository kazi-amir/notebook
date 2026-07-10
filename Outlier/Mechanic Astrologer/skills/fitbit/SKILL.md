---
name: fitbit
description: Query Fitbit health data including sleep, heart rate, activity, steps, calories, and body measurements. Use when user asks about their fitness, sleep quality, steps, health metrics, nutrition, or weight from their Fitbit.
---

# Fitbit

Query health and fitness data from Fitbit wearables.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/fitbit_data.py login --email your@email.com
```

## Fetching Data

Use `fitbit_data.py` to get JSON data:

### Sleep Logs

```bash
# Sleep data (last 7 days default)
python3 {baseDir}/fitbit_data.py sleep --days 7

# Specific date range
python3 {baseDir}/fitbit_data.py sleep --start 2026-01-01 --end 2026-01-15
```

Returns: duration, efficiency, sleep stages (deep, light, REM, wake), time in bed.

### Heart Rate

```bash
# Heart rate zones + resting HR (last 7 days default)
python3 {baseDir}/fitbit_data.py heart-rate --days 14

# Custom range
python3 {baseDir}/fitbit_data.py heart-rate --start 2026-01-20 --end 2026-02-04
```

Returns: resting heart rate, heart rate zones (Out of Range, Fat Burn, Cardio, Peak) with minutes and calories per zone.

### Daily Activity

```bash
# Steps, calories, distance, floors, active zone minutes (last 7 days default)
python3 {baseDir}/fitbit_data.py activity --days 7

# Last month
python3 {baseDir}/fitbit_data.py activity --days 30
```

Returns: steps, distance, calories (total/BMR/active), floors, elevation, active zone minutes breakdown, activity minutes (sedentary/lightly active/fairly active/very active), resting heart rate.

### Active Zone Minutes

Active zone minutes are included in the `activity` response under `active_zone_minutes` and `zone_minutes` (fat_burn, cardio, peak).

```bash
python3 {baseDir}/fitbit_data.py activity --days 7
```

### Exercise Activities / Workouts

```bash
# Logged exercises (last 7 days default)
python3 {baseDir}/fitbit_data.py workouts --days 14
```

Returns: activity name, duration, calories, steps, distance, heart rate (avg/max), active zone minutes, pace, speed, elevation gain.

### Body Measurements

```bash
# Weight, BMI, body fat (last 7 days default)
python3 {baseDir}/fitbit_data.py body --days 30
```

Returns: weight, BMI, body fat %, lean mass, measurement source (e.g., Aria scale).

### Food / Nutrition Logs

```bash
# Food logs (most recent date by default)
python3 {baseDir}/fitbit_data.py food

# Specific date
python3 {baseDir}/fitbit_data.py food --date 2026-02-02
```

Returns: meals with food name, brand, amount, and full nutrient breakdown (calories, carbs, fat, fiber, protein, sodium, sugar). Includes daily totals.

### Water Intake

```bash
# Water logs (most recent date by default)
python3 {baseDir}/fitbit_data.py water

# Specific date
python3 {baseDir}/fitbit_data.py water --date 2026-02-02
```

Returns: water entries with amounts in ml. Includes daily totals.

### User Profile

```bash
python3 {baseDir}/fitbit_data.py profile
```

Returns: name, date of birth, gender, height, weight, stride lengths, timezone, member since date.

### Connected Devices

```bash
python3 {baseDir}/fitbit_data.py devices
```

Returns: device name, type, firmware version, battery level, last sync time, features.

### Achievement Badges

```bash
python3 {baseDir}/fitbit_data.py badges
```

Returns: earned badges with type, description, date earned, value, and times achieved.

### Lifetime Statistics

```bash
python3 {baseDir}/fitbit_data.py lifetime
```

Returns: all-time totals (steps, distance, floors, calories, active minutes) and personal bests with dates.

### Combined Summary

```bash
# Health overview (last 7 days default)
python3 {baseDir}/fitbit_data.py summary --days 7

# Last month
python3 {baseDir}/fitbit_data.py summary --days 30
```

Returns: combined sleep, activity, heart rate, and workout data with computed averages.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "How did I sleep?" | `python3 {baseDir}/fitbit_data.py sleep --days 7`, report efficiency + stages |
| "How many steps today/this week?" | `python3 {baseDir}/fitbit_data.py activity --days 7`, report steps |
| "What's my heart rate been like?" | `python3 {baseDir}/fitbit_data.py heart-rate --days 7`, report RHR + zones |
| "How active was I last month?" | `python3 {baseDir}/fitbit_data.py activity --days 30`, report steps + active zones |
| "Is my Fitbit synced?" | `python3 {baseDir}/fitbit_data.py devices`, report battery + last sync |
| "What's my weight trend?" | `python3 {baseDir}/fitbit_data.py body --days 30`, report weight changes |
| "What did I eat?" | `python3 {baseDir}/fitbit_data.py food`, report meals + macros |
| "How much water did I drink?" | `python3 {baseDir}/fitbit_data.py water`, report daily total |
| "Give me an overview" | `python3 {baseDir}/fitbit_data.py summary --days 7`, report key metrics |

## Key Metrics

- **Sleep Efficiency** (0-100%): Time asleep vs time in bed. >85% is good.
- **Sleep Stages**: Deep (recovery), REM (memory), Light (transitions), Wake
- **Resting Heart Rate** (bpm): Lower = better cardiovascular fitness
- **Active Zone Minutes**: Weekly target is 150 min (WHO recommendation)
- **Heart Rate Zones**: Fat Burn (moderate), Cardio (vigorous), Peak (max effort)
- **Steps**: 10,000/day is a common goal; 7,000-8,000 is linked to health benefits

## Date Parameters

- `--days N`: Last N days from today
- `--start DATE`: Start date (ISO format, e.g., `2026-01-01`)
- `--end DATE`: End date (ISO format, e.g., `2026-01-31`)
- `--date DATE`: Specific date (for food and water logs)

Output is JSON to stdout. Parse it to answer user questions.
