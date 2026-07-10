---
name: renpho
description: Access Renpho smart scale body composition data (weight, BMI, body fat, muscle mass, visceral fat, metabolic age, water percentage). Use when the user asks about their weight, body composition, BMI, body fat percentage, muscle mass, or weight trends.
---

# Renpho

Query body composition metrics from the Renpho smart scale.

Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/renpho_data.py login --email your@email.com
```

## Fetching Data

Use `renpho_data.py` to get JSON data:

```bash
# Latest measurement (most recent weigh-in)
python3 {baseDir}/renpho_data.py latest

# Detailed body composition with health classifications
python3 {baseDir}/renpho_data.py composition

# Weight trend over N days (default: 30)
python3 {baseDir}/renpho_data.py trend --days 90

# Historical measurements
python3 {baseDir}/renpho_data.py measurements --days 30

# Custom date range
python3 {baseDir}/renpho_data.py measurements --start 2026-01-01 --end 2026-02-01

# User profile (height, gender, goal weight, scale info)
python3 {baseDir}/renpho_data.py profile

# Combined summary with all data
python3 {baseDir}/renpho_data.py summary --days 30
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What's my weight?" | `{baseDir}/renpho_data.py latest`, report weight + BMI |
| "What's my body fat?" | `{baseDir}/renpho_data.py composition`, report body fat + classification |
| "Am I losing weight?" | `{baseDir}/renpho_data.py trend --days 30`, report trend direction |
| "Show my weight history" | `{baseDir}/renpho_data.py measurements --days 90`, list readings |
| "How's my body composition?" | `{baseDir}/renpho_data.py composition`, full breakdown |
| "What's my muscle mass?" | `{baseDir}/renpho_data.py latest`, report muscle mass |
| "Is my visceral fat okay?" | `{baseDir}/renpho_data.py composition`, check visceral fat classification |

## Key Metrics

### Weight & BMI

| BMI | Classification |
|-----|---------------|
| <18.5 | Underweight |
| 18.5-24.9 | Normal |
| 25.0-29.9 | Overweight |
| 30.0+ | Obese |

### Body Fat Percentage

| Category | Male | Female |
|----------|------|--------|
| Essential | 2-5% | 10-13% |
| Athlete | 6-13% | 14-20% |
| Fitness | 14-17% | 21-24% |
| Average | 18-24% | 25-31% |
| Obese | 25%+ | 32%+ |

### Visceral Fat

| Level | Rating | Health Impact |
|-------|--------|--------------|
| 1-9 | Healthy | Normal risk |
| 10-14 | Elevated | Increased risk |
| 15+ | High | Significantly increased risk |

### Other Metrics

- **Muscle Mass**: Typically 30-40% of body weight for men, 25-35% for women
- **Water Percentage**: Healthy range 45-65% (higher for men)
- **Bone Mass**: Typically 3-5% of body weight
- **Metabolic Age**: Ideally at or below actual age
- **BMR**: Basal Metabolic Rate in kcal/day

## Health Analysis

When the user asks about body composition trends or health insights, use `{baseDir}/references/body_composition_guide.md` for:
- Science-backed interpretation of body composition metrics
- Healthy ranges by age, gender, and fitness level
- Weight trend analysis and goal tracking
- Relationships between metrics (e.g., muscle gain vs. weight change)
- Red flags that suggest medical consultation

### Analysis workflow
1. Fetch data: `python3 {baseDir}/renpho_data.py summary --days N`
2. Read `{baseDir}/references/body_composition_guide.md` for interpretation
3. Apply the 5-step analysis: Status -> Trends -> Patterns -> Insights -> Flags
4. Always include disclaimer that this is not medical advice

## References

- `{baseDir}/references/body_composition_guide.md` -- science-backed body composition interpretation guide
