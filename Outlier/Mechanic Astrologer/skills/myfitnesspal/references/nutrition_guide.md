# Nutrition Analysis Guide

Reference for interpreting MyFitnessPal nutrition data and providing dietary insights.

## Calorie Management

### Daily Energy Balance

```
Net Calories = Food Calories - Exercise Calories
Calorie Balance = Net Calories - Daily Goal
```

- **Deficit** (under goal): Supports weight loss (~500 kcal/day deficit = ~0.45 kg/week loss)
- **Surplus** (over goal): Supports weight/muscle gain (~250-500 kcal/day surplus for lean gain)
- **Maintenance**: Net calories close to goal (+/- 100 kcal)

### Calorie Estimates by Goal

| Goal | Typical Range | Deficit/Surplus |
|------|--------------|----------------|
| Weight Loss | 1200-1800 kcal | 500-750 kcal deficit |
| Maintenance | 1800-2500 kcal | Neutral |
| Muscle Gain | 2200-3200 kcal | 250-500 kcal surplus |

## Macronutrient Guidelines

### Recommended Distributions

| Goal | Protein | Carbs | Fat |
|------|---------|-------|-----|
| General Health | 15-25% | 45-55% | 25-35% |
| Weight Loss | 25-35% | 35-45% | 25-30% |
| Muscle Building | 25-35% | 40-50% | 20-30% |
| Endurance | 15-20% | 55-65% | 20-30% |

### Protein

- **Minimum**: 0.8 g/kg body weight (sedentary adults)
- **Active adults**: 1.2-1.6 g/kg body weight
- **Strength athletes**: 1.6-2.2 g/kg body weight
- **Calorie content**: 4 kcal per gram
- **Key roles**: Muscle repair, satiety, immune function

### Carbohydrates

- **Minimum**: 130 g/day (brain function)
- **Moderate activity**: 3-5 g/kg body weight
- **High activity**: 5-7 g/kg body weight
- **Calorie content**: 4 kcal per gram
- **Fiber target**: 25-30 g/day (promotes digestive health, satiety)
- **Sugar limit**: <25g added sugar (WHO), <50g total sugar preferred

### Fat

- **Minimum**: 20% of total calories (hormone production)
- **Optimal**: 25-35% of total calories
- **Calorie content**: 9 kcal per gram
- **Saturated fat**: <10% of total calories (~22g on 2000 kcal diet)
- **Trans fat**: As close to 0g as possible

## Micronutrient Reference

### Key Minerals

| Nutrient | Daily Value | Concern Level |
|----------|------------|---------------|
| Sodium | <2300 mg | Over is common; linked to blood pressure |
| Potassium | 2600-3400 mg | Under is common; important for heart |
| Calcium | 1000-1200 mg | Important for bone health |
| Iron | 8-18 mg | Higher for women; deficiency causes fatigue |

### Cholesterol

- **Dietary guideline**: <300 mg/day
- **Heart health**: <200 mg/day preferred
- **Note**: Dietary cholesterol has less impact than previously thought; saturated fat matters more

## Hydration Guidelines

### Daily Water Needs

| Category | Amount |
|----------|--------|
| Sedentary adult | 2000-2500 ml |
| Active adult | 2500-3500 ml |
| High activity/heat | 3000-4000+ ml |

### Hydration Indicators

- **On track**: >80% of daily goal by evening
- **Behind**: <60% of goal by afternoon
- **Key times**: Morning (rehydrate), before meals, during/after exercise

### Water Intake Conversion

| Unit | Equivalent |
|------|-----------|
| 1 cup | 236.6 ml |
| 1 oz | 29.6 ml |
| 1 liter | 1000 ml |

## Pattern Detection

When analyzing multi-day data (`date_range`), look for:

1. **Consistent deficit/surplus**: Average daily calories vs goal over the period
2. **Protein adequacy**: Average protein vs goal -- shortfall impacts recovery
3. **Macro balance**: Distribution trending too far in any direction
4. **Sodium patterns**: Consistently over 2300mg → flag
5. **Fiber gap**: Average <20g/day → suggest more vegetables, whole grains
6. **Water consistency**: Days with <50% goal met → hydration concern
7. **Exercise regularity**: Frequency and calories burned per session
8. **Weekend vs weekday**: Calorie spikes on weekends are common

## Meal Timing Patterns

When reviewing meal breakdowns:

- **Breakfast skipping**: If no breakfast entries → may lead to overeating later
- **Heavy dinners**: >50% of daily calories at dinner → suggest redistribution
- **Snack impact**: Snack calories often underestimated; highlight if >25% of daily total
- **Pre/post workout**: Note exercise timing relative to meals

## Red Flags

Flag these patterns to the user:

- Daily intake consistently <1200 kcal (women) or <1500 kcal (men) without medical supervision
- Protein consistently <0.6g/kg body weight
- Fat intake <15% of calories (hormone disruption risk)
- Sodium consistently >3000mg/day
- Zero fiber days
- No water logged for a full day
- Extreme calorie swings (>1000 kcal variation day-to-day)

## Recommendation Guidelines

When providing nutrition insights:
- Be specific: "You averaged 95g protein vs your 137g goal -- a 31% shortfall"
- Frame positively: "You hit your fiber goal on 4 of 7 days"
- Connect to goals: "At this deficit, you're on track for ~0.3 kg/week loss"
- Suggest actionable changes: "Adding a Greek yogurt snack would add 18g protein"
- Always include: "This is informational only and not dietary advice. Consult a registered dietitian for personalized nutrition plans."
