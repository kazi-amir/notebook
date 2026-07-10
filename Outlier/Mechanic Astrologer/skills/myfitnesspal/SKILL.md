---
name: myfitnesspal
description: Access MyFitnessPal nutrition and fitness tracking data (daily food logs, meal breakdowns, macros, exercise, water intake, nutrition goals). Use when the user asks about calories, meals, macros, protein intake, what they ate, exercise logs, water intake, diet progress, or nutrition goals.
---

# MyFitnessPal

Query nutrition and fitness tracking data from MyFitnessPal. Data is loaded from your account. Log in first, then query your data.

## Login

Log in with your account email before querying data:

```bash
python3 {baseDir}/mfp_data.py login --email your@email.com
```

## Fetching Data

Use `mfp_data.py` to get JSON data:

```bash
# Daily summary (calories in/out, macros, exercise, water, remaining budget)
python3 {baseDir}/mfp_data.py daily_summary --date 2026-01-20

# Meal-by-meal breakdown (per-item nutrition for each meal)
python3 {baseDir}/mfp_data.py meals --date 2026-01-20

# Detailed macro/micronutrient breakdown with goal comparison
python3 {baseDir}/mfp_data.py macros --date 2026-01-20

# Exercise activities for a day
python3 {baseDir}/mfp_data.py exercise --date 2026-01-20

# Water intake with progress toward goal
python3 {baseDir}/mfp_data.py water --date 2026-01-20

# Aggregate stats across a date range (totals + daily averages)
python3 {baseDir}/mfp_data.py date_range --start 2026-01-07 --end 2026-02-05

# Search the food database
python3 {baseDir}/mfp_data.py search_foods --query chicken

# Search exercises
python3 {baseDir}/mfp_data.py search_exercises --query running

# User profile and nutrition goals
python3 {baseDir}/mfp_data.py profile
```

Output is JSON to stdout. Parse it to answer user questions.

## Answering Questions

| User asks | Action |
|-----------|--------|
| "What did I eat today?" | `python3 {baseDir}/mfp_data.py meals --date DATE` |
| "How many calories have I had?" | `python3 {baseDir}/mfp_data.py daily_summary --date DATE` |
| "What's my remaining calorie budget?" | `python3 {baseDir}/mfp_data.py daily_summary --date DATE`, check `remaining.calories` |
| "Am I hitting my protein goal?" | `python3 {baseDir}/mfp_data.py macros --date DATE`, check protein vs goal |
| "Show my macro breakdown" | `python3 {baseDir}/mfp_data.py macros --date DATE` |
| "How much water did I drink?" | `python3 {baseDir}/mfp_data.py water --date DATE` |
| "What exercise did I do?" | `python3 {baseDir}/mfp_data.py exercise --date DATE` |
| "How's my diet this week?" | `python3 {baseDir}/mfp_data.py date_range --start START --end END` |
| "What foods have chicken?" | `python3 {baseDir}/mfp_data.py search_foods --query chicken` |
| "What's my calorie goal?" | `python3 {baseDir}/mfp_data.py profile` |

## Key Metrics

- **Calories**: Food calories in - exercise calories = net calories. Compare to daily goal.
- **Macros**: Protein (4 cal/g), Carbs (4 cal/g), Fat (9 cal/g). Check distribution %.
- **Protein**: Critical for muscle maintenance. Goal varies by persona (50-210g).
- **Fiber**: Target 25-30g/day. Important for digestive health.
- **Water**: Track ml consumed vs. daily goal (2000-3500ml).
- **Net Calories**: `food calories - exercise calories`. Under goal = calorie deficit.

## Nutrition Analysis

When the user asks about their diet, trends, or wants insights, use `{baseDir}/references/nutrition_guide.md` for:
- Recommended macro distributions for different goals
- Micronutrient daily value guidelines
- Interpreting calorie surplus/deficit for weight management
- Hydration guidelines
- Common nutritional imbalances to flag

### Analysis workflow
1. Fetch data: `python3 {baseDir}/mfp_data.py daily_summary --date DATE` or `date_range`
2. Read `{baseDir}/references/nutrition_guide.md` for interpretation
3. Compare actual intake against goals
4. Identify gaps (under on protein, over on sodium, etc.)
5. Always include disclaimer that this is not medical/dietary advice

## References

- `{baseDir}/references/nutrition_guide.md` -- nutrition analysis and interpretation guide
