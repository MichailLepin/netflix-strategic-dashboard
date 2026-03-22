# Data Enrichment Prompt for Netflix 2025 User Behavior Dataset

## Context

The base dataset is "Netflix 2025 User Behavior Dataset" from Kaggle (by Sayeeduddin, 210K+ records). Upon exploratory analysis, all metrics were found to be uniformly distributed with no meaningful variance across segments (e.g., churn rate ~15% for all subscription plans, watch time ~1.1 hrs for all devices, CTR ~15% for all recommendation types). This makes the dataset unsuitable for business intelligence dashboards that need to surface actionable insights.

## Objective

Enrich the existing Kaggle dataset by injecting realistic business patterns that reflect known streaming platform dynamics, while preserving the original schema, row counts, and data types. The enrichment must produce data where filtering by different segments yields visibly different KPI values.

## Source Tables to Modify

### 1. users.csv (10,000 rows)
**Target columns:** `is_active` (bool), `monthly_spend` (float)

**Enrichment rules:**
- **Churn rate by subscription plan:**
  - Basic: ~28% churn (is_active=False) — budget users have highest churn
  - Standard: ~16% churn — mid-tier, moderate retention
  - Premium: ~9% churn — invested users stay longer
  - Premium+: ~4% churn — highest commitment, lowest churn
  - *Rationale:* Higher-value subscription plans indicate stronger user commitment and receive more platform features, leading to better retention

- **Age-based churn adjustment:**
  - Users aged 18-25: +8 percentage points additional churn (younger users more price-sensitive, more likely to try alternatives)
  - Users aged 55+: -5 percentage points churn reduction (older users are more habitual, less likely to switch)

- **Monthly spend by plan:**
  - Premium+: multiply by 1.4x (reflects higher plan cost + add-ons)
  - Premium: multiply by 1.15x
  - Basic: multiply by 0.7x (reflects lower plan cost, fewer extras)

### 2. watch_history.csv (100,000 rows)
**Target columns:** `watch_duration_minutes` (float), `progress_percentage` (float)

**Enrichment rules:**

- **Seasonal viewing patterns (by month of watch_date):**
  - December & January: multiply watch_duration_minutes by random(1.2, 1.5) — holiday binge watching
  - July & August: multiply by random(1.05, 1.25) — summer vacation viewing
  - February: multiply by random(0.8, 0.95) — shortest month, post-holiday dip
  - *Rationale:* Streaming viewership follows well-documented seasonal patterns with peaks during holidays and summer

- **Device-based session length:**
  - Mobile: multiply watch_duration_minutes by 0.6x — short mobile sessions (commute, breaks)
  - Smart TV: multiply by 1.4x — lean-back viewing, longer sessions
  - Tablet: multiply by 0.85x — moderate sessions
  - Desktop & Laptop: no change (baseline)
  - *Rationale:* Screen size and viewing context directly affect session duration

- **Subscription tier engagement:**
  - Premium & Premium+ users: multiply watch_duration_minutes by 1.25x — more engaged, access to more content
  - Basic users: multiply by 0.75x — limited catalog access, lower engagement
  - *Rationale:* Premium users self-select as heavy viewers; basic users are more casual

- **Content type completion rates:**
  - Movies (content_type='Movie'): clip progress_percentage lower bound to 30, then multiply by 1.1x — movies are designed for single-sitting completion
  - Documentaries: multiply progress_percentage by 0.75x — documentaries are more commonly abandoned mid-way
  - *Rationale:* Different content formats have different consumption patterns

- **Platform growth trend:**
  - Calculate days_since_start for each row (from earliest watch_date)
  - Apply growth factor: 1 + (days_since_start / max_days) * 0.2 — up to 20% engagement growth over 24 months
  - *Rationale:* Growing platforms show increasing engagement as catalog and features improve

- **Final clipping:**
  - watch_duration_minutes: clip to [5, 300] range
  - progress_percentage: clip to [0, 100] range

### 3. recommendation_logs.csv (50,000 rows)
**Target columns:** `was_clicked` (bool)

**Enrichment rules:**

- **Position-based CTR:**
  - Position 1: ~35% CTR (top of the list gets most attention)
  - Position 20: ~5% CTR (bottom of list rarely seen)
  - Linear decay: click_probability = 0.35 - (position - 1) / max_position * 0.30
  - Re-roll was_clicked using: random() < click_probability
  - *Rationale:* Well-documented position bias in recommendation systems — top positions get disproportionate clicks

- **Recommendation type effectiveness:**
  - personalized: ~28% CTR (tailored to user history, highest relevance)
  - genre_based: ~22% CTR (matches user's genre preferences)
  - trending: ~18% CTR (social proof, but less personalized)
  - new_releases: ~15% CTR (novelty, but not targeted)
  - similar_users: ~12% CTR (collaborative filtering, least personalized)
  - Override was_clicked for each type using the respective probability
  - *Rationale:* More personalized algorithms produce higher-relevance recommendations

- **Algorithm version improvement:**
  - For algorithm_version='v2.0': flip 10% of non-clicks to clicks (v2.0 is improved algorithm)
  - *Rationale:* Newer algorithm versions should show measurable improvement in CTR

## Tables NOT Modified

- **movies.csv** — Content metadata is already realistic (genres, ratings, durations)
- **search_logs.csv** — Search behavior doesn't need enrichment for the dashboard KPIs
- **reviews.csv** — Review sentiment data is not used in dashboard KPIs

## Validation After Enrichment

Run these checks to confirm patterns are visible:

```python
# Churn by plan should show clear gradient
for plan in ['Basic', 'Standard', 'Premium', 'Premium+']:
    rate = (~users[users['subscription_plan']==plan]['is_active']).mean() * 100
    print(f'{plan}: {rate:.1f}%')
# Expected: Basic ~29%, Standard ~17%, Premium ~10%, Premium+ ~6%

# Watch time by device should show clear differences
for dev in watch['device_type'].unique():
    avg = watch[watch['device_type']==dev]['watch_duration_minutes'].mean() / 60
    print(f'{dev}: {avg:.2f} hrs')
# Expected: Smart TV ~1.7hrs, Desktop ~1.3hrs, Mobile ~0.8hrs

# Rec CTR by type should show personalized >> similar_users
for rtype in recs['recommendation_type'].unique():
    ctr = recs[recs['recommendation_type']==rtype]['was_clicked'].mean() * 100
    print(f'{rtype}: {ctr:.1f}%')
# Expected: personalized ~30%, similar_users ~13%
```

## Implementation Notes

- Use numpy random seed (42) for reproducibility
- All modifications are multiplicative or probability-based — they preserve the original distribution shape while shifting means
- No rows are added or removed — only column values are modified
- Schema and data types remain unchanged
- The enrichment script (fix_data.py) can be re-run idempotently on the original Kaggle data
