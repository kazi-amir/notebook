# Garmin Health Data Analysis Guide

Science-backed reference for interpreting Garmin Connect health metrics.

## 5-Step Analysis Framework

1. **Status**: What do today's numbers say? Is the user in a good/fair/poor state?
2. **Trends**: Compare the last 7 days vs. 30 days. Improving, stable, or declining?
3. **Patterns**: Look for day-of-week effects, workout impact, sleep debt accumulation
4. **Insights**: Connect metrics together (poor sleep → low body battery → high stress)
5. **Flags**: Identify anything unusual that warrants attention

## Resting Heart Rate (RHR)

| Category | Range (bpm) |
|----------|-------------|
| Athlete | 40-55 |
| Excellent | 56-61 |
| Good | 62-65 |
| Above Average | 66-69 |
| Average | 70-73 |
| Below Average | 74-81 |
| Poor | >81 |

**Trend signals:**
- Gradual decrease over weeks → improving fitness
- Sudden increase of 5+ bpm → illness, overtraining, or poor recovery
- Day-to-day variation of 3-5 bpm is normal

## Heart Rate Variability (HRV)

### Normal Ranges by Age

| Age | Low (ms) | Balanced (ms) | High (ms) |
|-----|----------|---------------|-----------|
| 20-29 | <30 | 30-70 | >70 |
| 30-39 | <25 | 25-60 | >60 |
| 40-49 | <20 | 20-50 | >50 |
| 50-59 | <15 | 15-40 | >40 |
| 60+ | <12 | 12-30 | >30 |

**Interpretation:**
- Higher HRV = better autonomic balance, better recovery
- Track the 7-day average trend, not daily fluctuations
- HRV dropping below personal baseline for 3+ days → recovery concern
- Garmin shows `hrv_weekly_avg` (7-day rolling) and `hrv_last_night` (single night)
- Compare `hrv_last_night` against `baseline_low`/`baseline_high` for context

## Sleep Metrics

### Duration Needs (Adults)

| Category | Hours |
|----------|-------|
| Optimal | 7.0-9.0 |
| Acceptable | 6.0-7.0 |
| Short | <6.0 |
| Excessive | >9.5 |

### Sleep Stage Distribution (Healthy)

| Stage | % of Total | Minutes (8h sleep) |
|-------|-----------|-------------------|
| Light | 50-60% | 240-288 |
| Deep | 15-25% | 72-120 |
| REM | 20-25% | 96-120 |

### Sleep Score Zones

| Score | Quality | Meaning |
|-------|---------|---------|
| 90-100 | Excellent | Optimal recovery sleep |
| 75-89 | Good | Adequate recovery |
| 60-74 | Fair | Some recovery compromise |
| <60 | Poor | Significant sleep disruption |

**Key patterns:**
- Deep sleep occurs mostly in first half of night
- REM increases in later sleep cycles
- Awake time >45 minutes suggests sleep fragmentation
- Consistent sleep schedule (start time variance <30 min) improves quality

## Stress Metrics

### Stress Level Zones

| Level | Range | Meaning |
|-------|-------|---------|
| Rest | 0-25 | Body is in recovery/rest mode |
| Low | 26-50 | Normal daily stress |
| Medium | 51-75 | Elevated stress, manageable |
| High | 76-100 | Significant stress, need recovery |

### Stress Qualifiers

| Qualifier | Avg Stress | Interpretation |
|-----------|-----------|----------------|
| Calm | <30 | Mostly resting, good recovery |
| Moderate | 30-50 | Normal day with some activity |
| High | >50 | Stressful day, prioritize recovery |

**Analysis tips:**
- Physical activity registers as stress (not just psychological)
- Compare rest stress duration vs. high stress duration
- Chronic high stress (>50 avg for 5+ days) → burnout risk
- Rest stress >8 hours/day indicates good recovery time

## Body Battery

### Morning Value Interpretation

| Value | Level | Meaning |
|-------|-------|---------|
| 80-100 | High | Well-recovered, ready for intense activity |
| 60-79 | Moderate | Adequately recovered, moderate activity OK |
| 40-59 | Low | Partially recovered, light activity recommended |
| <40 | Critical | Poor recovery, rest recommended |

**Key metrics:**
- `charged` = energy gained (mostly from sleep and rest)
- `drained` = energy used (from activity, stress, daily living)
- Net balance: `charged - drained` shows recovery surplus/deficit
- Morning value is the most reliable indicator of recovery state

## Training Readiness

### Score Zones

| Score | Level | Recommendation |
|-------|-------|---------------|
| 86-100 | Prime | Ready for high-intensity training |
| 66-85 | High | Good for moderate-to-hard training |
| 40-65 | Moderate | Light training or active recovery |
| <40 | Low | Rest day recommended |

**Components:**
- `sleepScore`: How well sleep contributed to readiness
- `recoveryScore`: Overall recovery state
- `hrvStatus`: HRV relative to baseline (low/balanced/high)
- `trainingLoadStatus`: Current training load (optimal/high/very_high)

**Pattern detection:**
- Readiness declining for 3+ days → overtraining risk
- Low readiness + high training load → forced rest needed
- Prime readiness + balanced HRV → ideal training window

## SpO2 (Blood Oxygen Saturation)

| Range | Status | Action |
|-------|--------|--------|
| 95-100% | Normal | No concern |
| 93-95% | Mild concern | Monitor, may indicate altitude or congestion |
| 90-93% | Moderate concern | Consider medical evaluation |
| <90% | Serious | Seek medical attention |

**Notes:**
- Night-time SpO2 dips during sleep are common and usually benign
- Persistent low SpO2 during sleep may indicate sleep apnea
- Altitude significantly affects SpO2 readings

## Respiration Rate

### Normal Ranges

| Context | Range (breaths/min) |
|---------|-------------------|
| Sleeping | 12-16 |
| Waking/Rest | 12-20 |
| Light Activity | 20-30 |

**Signals:**
- Sleeping respiration >18 → possible illness onset
- Sudden increase in waking respiration → stress or illness
- Consistently low sleeping respiration → good fitness indicator

## Body Composition

### BMI Categories

| BMI | Category |
|-----|----------|
| <18.5 | Underweight |
| 18.5-24.9 | Normal |
| 25.0-29.9 | Overweight |
| 30.0+ | Obese |

### Body Fat Percentage (Adults)

| Category | Male | Female |
|----------|------|--------|
| Essential | 2-5% | 10-13% |
| Athletic | 6-13% | 14-20% |
| Fitness | 14-17% | 21-24% |
| Average | 18-24% | 25-31% |
| Above Average | 25%+ | 32%+ |

**Tracking tips:**
- Weight fluctuations of 1-2 kg day-to-day are normal (water, food)
- Track weekly averages, not daily readings
- Body fat % is more informative than weight alone
- Muscle mass increase can offset weight loss on the scale

## Activity & Workout Analysis

### Training Effect Scale (Garmin)

| TE Aerobic | Level | Impact |
|------------|-------|--------|
| 0-1.0 | No Benefit | Too easy |
| 1.0-2.0 | Minor | Recovery pace |
| 2.0-3.0 | Maintaining | Maintains fitness |
| 3.0-4.0 | Improving | Builds fitness |
| 4.0-5.0 | Highly Improving | Significant gains |

### VO2 Max Categories (ml/kg/min)

| Fitness Level | Male (20-39) | Female (20-39) |
|---------------|-------------|----------------|
| Superior | >51 | >45 |
| Excellent | 46-51 | 40-45 |
| Good | 42-45 | 36-39 |
| Fair | 36-41 | 31-35 |
| Poor | <36 | <31 |

## Pattern Detection Checklist

Look for these patterns across multiple metrics:

1. **Overtraining signal**: Declining readiness + rising RHR + low HRV + high stress for 3+ days
2. **Sleep debt**: Sleep <6h for 3+ nights → expect low body battery, high stress, low readiness
3. **Illness onset**: Sudden RHR spike + SpO2 drop + elevated respiration rate
4. **Recovery day needed**: Body battery morning <40 + readiness <40 + HRV below baseline
5. **Peak performance window**: Readiness prime + HRV high + body battery >80 + good sleep
6. **Stress accumulation**: Rising avg stress over a week with decreasing rest duration
7. **Fitness improvement**: Gradual RHR decline + HRV increase + VO2 Max increase over 4+ weeks

## Red Flags (Suggest Medical Consultation)

- Resting heart rate suddenly >100 bpm or <40 bpm (without athletic history)
- SpO2 consistently <93%
- Sleep quality poor (<60) for 7+ consecutive days
- HRV dropping >40% below personal baseline for 5+ days
- Respiration rate consistently elevated during sleep (>20 breaths/min)
- Unexplained weight changes of >3 kg in a week

## Recommendation Guidelines

When providing health insights:
- Be specific: "Your resting HR increased from 62 to 68 bpm over the past week"
- Compare to personal baseline, not just population norms
- Connect related metrics: "Low body battery (35) aligns with your poor sleep (score 58) last night"
- Suggest actionable steps: "Consider a rest day given your low training readiness (38)"
- Always include: "This is informational only and not medical advice. Consult a healthcare provider for medical concerns."
