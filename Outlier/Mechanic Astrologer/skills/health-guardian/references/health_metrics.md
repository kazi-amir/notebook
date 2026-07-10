# Apple Health Metrics Interpretation Guide

Science-backed reference for interpreting Apple Health data. Use this guide when analyzing health trends or providing insights.

## Heart Rate

### Resting Heart Rate (RHR)
The heart rate measured at rest, typically first thing in the morning.

| Range (bpm) | Interpretation |
|-------------|----------------|
| < 50 | Athletic / very fit (or bradycardia if symptomatic) |
| 50-59 | Excellent fitness |
| 60-69 | Good / normal |
| 70-79 | Average |
| 80-89 | Below average |
| 90+ | Elevated (consider stress, deconditioning, illness) |

**Trends to watch:**
- Sudden RHR increase (5+ bpm above baseline): possible illness, stress, overtraining, dehydration
- Gradual RHR decrease over weeks: improving cardiovascular fitness
- Day-to-day variation of 3-5 bpm is normal

### Heart Rate During Activity
- Motion context "active" readings reflect exercise intensity
- Motion context "sedentary" readings reflect resting state
- Maximum heart rate estimate: ~220 minus age

## Heart Rate Variability (HRV SDNN)

HRV measures the variation in time between heartbeats. Higher HRV generally indicates better cardiovascular fitness and recovery.

| Age Group | Low (ms) | Average (ms) | Good (ms) | Excellent (ms) |
|-----------|----------|--------------|-----------|----------------|
| 18-25 | < 30 | 30-50 | 50-80 | > 80 |
| 26-35 | < 25 | 25-45 | 45-70 | > 70 |
| 36-45 | < 20 | 20-40 | 40-60 | > 60 |
| 46-55 | < 18 | 18-35 | 35-50 | > 50 |
| 56-65 | < 15 | 15-30 | 30-45 | > 45 |
| 65+ | < 12 | 12-25 | 25-40 | > 40 |

**What affects HRV:**
- Sleep quality (poor sleep = lower HRV)
- Alcohol consumption (lowers HRV for 24-48h)
- Stress (acute and chronic)
- Exercise (improves baseline HRV over time, temporarily lowers after intense sessions)
- Illness (HRV drops before symptoms often appear)

**Key insight:** Track the trend, not individual readings. A consistent 15%+ decline over 1-2 weeks warrants attention.

## Sleep

### Sleep Stages
| Stage | Typical % | Purpose |
|-------|-----------|---------|
| **Core (Light)** | 45-55% | Memory consolidation, motor learning |
| **Deep (SWS)** | 15-25% | Physical recovery, immune function, growth hormone |
| **REM** | 20-25% | Emotional processing, creativity, memory |
| **Awake** | 5-10% | Normal micro-awakenings |

### Sleep Duration by Age
| Age | Recommended (hours) |
|-----|-------------------|
| 14-17 | 8-10 |
| 18-25 | 7-9 |
| 26-64 | 7-9 |
| 65+ | 7-8 |

### Sleep Efficiency
- **> 85%**: Good
- **75-85%**: Acceptable
- **< 75%**: Poor (excessive awake time in bed)

**Red flags:**
- Consistently < 6 hours total sleep
- Deep sleep < 10% of total
- Sleep efficiency < 70%
- Sudden change in sleep patterns

## Steps & Activity

### Daily Step Guidelines
| Steps/day | Category |
|-----------|----------|
| < 5,000 | Sedentary |
| 5,000-7,499 | Low active |
| 7,500-9,999 | Somewhat active |
| 10,000-12,499 | Active |
| > 12,500 | Highly active |

### Exercise Minutes
- WHO recommends: 150-300 min moderate OR 75-150 min vigorous per week
- That's roughly 21-43 min/day moderate activity
- Apple Watch "exercise minutes" typically tracks moderate+ intensity

### Stand Hours
- Goal: 12 hours/day with at least 1 minute of standing
- Prolonged sitting (> 8 hours/day) associated with health risks regardless of exercise

## VO2 Max

Maximal oxygen consumption — the gold standard for cardiovascular fitness.

| Fitness Level | Male (mL/min/kg) | Female (mL/min/kg) |
|---------------|-------------------|---------------------|
| Poor | < 30 | < 25 |
| Below Average | 30-35 | 25-30 |
| Average | 35-40 | 30-35 |
| Above Average | 40-45 | 35-40 |
| Good | 45-50 | 40-45 |
| Excellent | 50-55 | 45-50 |
| Elite | > 55 | > 50 |

**Key insight:** VO2 Max is one of the strongest predictors of all-cause mortality. Even small improvements (2-3 mL/min/kg) are clinically meaningful.

**Apple Watch accuracy:** Estimates within ~1-2 mL/min/kg of lab testing for walking/running. Less accurate for other activities.

## Body Mass

### BMI Reference (weight in kg / height in m^2)
| BMI | Category |
|-----|----------|
| < 18.5 | Underweight |
| 18.5-24.9 | Normal |
| 25.0-29.9 | Overweight |
| 30.0+ | Obese |

**Weight tracking tips:**
- Weekly weigh-ins more useful than daily (less noise)
- Weight fluctuates 1-2 kg day-to-day (water, food, etc.)
- Trend over 4+ weeks more meaningful than any single reading
- Unintentional weight loss > 5% in 6-12 months: medical evaluation recommended

## Workout Analysis

### Calories Burned Interpretation
- **Basal energy**: Calories burned at rest (typically 1,200-2,000 kcal/day)
- **Active energy**: Additional calories from movement and exercise
- **Total energy** = Basal + Active
- Average METs value indicates workout intensity (1 = resting, 3-6 = moderate, 6+ = vigorous)

### Common Workout Metrics
| Activity | Typical Duration | Typical kcal/30min | Expected HR Zone |
|----------|-----------------|-------------------|-----------------|
| Walking | 30-60 min | 100-200 | 50-65% max HR |
| Running | 20-60 min | 250-400 | 65-85% max HR |
| Cycling | 30-90 min | 200-350 | 60-80% max HR |
| Yoga | 30-60 min | 100-200 | 40-60% max HR |
| Strength | 30-60 min | 150-300 | 50-75% max HR |
| Swimming | 20-45 min | 200-350 | 60-80% max HR |
| Basketball | 30-60 min | 250-400 | 65-85% max HR |

## Pattern Detection

### Overtraining Signals
Watch for this combination:
- Rising resting HR (> 5 bpm above baseline)
- Declining HRV (> 15% below baseline)
- Worsening sleep quality
- Decreased workout performance

### Illness Early Warning
Often appears 1-2 days before symptoms:
- RHR spike (> 10 bpm above baseline)
- HRV drop (> 20% below baseline)
- Sleep disruption
- Decreased step count / activity

### Stress Indicators
- Elevated RHR without exercise
- Reduced HRV
- Poor sleep efficiency
- Increased awake time during sleep

## Red Flags (Suggest Medical Consultation)

- Resting HR consistently > 100 bpm or < 40 bpm (without athletic background)
- HRV consistently < 10 ms
- Sleep < 5 hours for > 1 week
- Unintentional weight change > 5% in a month
- VO2 Max declining > 10% over 3 months without explanation
- Heart rate not recovering after exercise (> 20 min to return to resting)

---

*This guide is for informational purposes only and does not constitute medical advice. Always consult a healthcare professional for health concerns.*
