# Feature Research

**Domain:** Streaming analytics / Netflix BI management dashboard (university assignment)
**Researched:** 2026-03-22
**Confidence:** HIGH (assignment constraints are explicit; KPI domain is well-documented)

---

## Context

This is a single-screen Streamlit dashboard for a university BI assignment. Hard constraints from the assignment spec drive all categorization:

- 3-7 KPIs
- 3-6 chart types
- 2-5 interactive filters
- Single screen, no scrolling
- Business problem: content strategy optimization (engagement + recommendation effectiveness + churn risk)
- Dataset: Kaggle "Netflix 2025 User Behavior Dataset" — tables: users, movies, watch_history, recommendation_logs, search_logs, reviews

All features are evaluated against: (1) assignment requirements, (2) what a BI grader expects to see, (3) what is actually computable from the dataset.

---

## Feature Landscape

### Table Stakes (Users/Graders Expect These)

Missing any of these makes the dashboard feel incomplete or fails assignment criteria.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| KPI scorecards at the top | Standard BI layout — executive-level summary first | LOW | 3-7 KPIs shown as large number tiles with label and unit. Graders check this box first. |
| Average Watch Time per User | Core engagement metric; Netflix's own north star proxy | LOW | `watch_history.watch_duration` / distinct users. Segment by filter. |
| Churn Rate (or Churn Risk %) | Retention is a primary Netflix business concern | LOW-MEDIUM | Derive from `users` table — users with no watch activity in last N days, or subscription status if present. |
| Recommendation Click-Through Rate (CTR) | Assignment asks for recommendation engine effectiveness | MEDIUM | `recommendation_logs`: clicks / recommendations shown per user. |
| Content Completion Rate | Whether users finish what they start — quality signal | LOW | `watch_history`: watch_duration / movie_duration. |
| Active Users (DAU or MAU) | Baseline engagement health metric | LOW | Count distinct users in `watch_history` within time window. |
| Time-series line chart | Shows trends over time — expected in any BI dashboard | LOW | Watch hours or active users by week/month. |
| Bar chart for content/genre ranking | Categorical comparison — most watched genres or top titles | LOW | Aggregate `watch_history` joined to `movies` by genre. |
| Interactive filters (sidebar) | Assignment requires 2-5 filters; Streamlit sidebar is standard | LOW | Genre, subscription type, device type, time period at minimum. |
| Dashboard title + Netflix logo | Assignment explicitly requires this | LOW | Static image + `st.title()`. |
| Alarm/threshold descriptions | Assignment requires describing what triggers action | LOW | Text annotations or colored KPI tiles (red/yellow/green). |

### Differentiators (Assignment Score Boosters)

Features beyond the minimum that elevate the dashboard from "passes" to "impressive." Not required, but high grader value.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Recommendation Effectiveness by Genre | Shows which genres benefit most from the recommender — actionable insight | MEDIUM | Join `recommendation_logs` + `movies`; CTR or watch rate post-recommendation by genre. |
| Cohort-style retention heatmap | Shows retention across user signup cohorts — visually impressive, analytically rigorous | HIGH | Requires cohort bucketing by join month; pivot table rendered as heatmap. May be too complex for single screen. |
| KPI delta indicators (vs. prior period) | Shows trend direction — standard in professional dashboards | LOW-MEDIUM | Compare current window to previous window; show +/- % change in KPI tile. |
| Scatter plot: Watch Time vs. Rating | Reveals whether high-rated content drives engagement — hypothesis testing visual | LOW-MEDIUM | Join `watch_history` + `reviews`; one dot per movie/genre. |
| Content Diversity Score | Measures how varied a user's viewing is — captures breadth vs. depth | MEDIUM | Entropy or unique genre count per user; shown as a histogram or single KPI. |
| Device-type breakdown donut/pie | Shows platform usage mix (mobile vs. TV vs. desktop) | LOW | `watch_history.device_type` aggregated; pie or donut chart. |
| Search-to-Watch conversion rate | How often search leads to content consumption — search quality metric | MEDIUM | Join `search_logs` + `watch_history` by user+time proximity. |

### Anti-Features (Deliberately Exclude)

Features that seem appealing but should not be built given constraints.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Multi-page / tabbed dashboard | Seems like it allows more content | Violates "single screen" assignment requirement; risks losing grader attention | Prioritize ruthlessly — keep everything on one screen with sidebar filters |
| Predictive ML churn model | Feels sophisticated and impressive | Assignment explicitly scopes this out; adds complexity without deliverable value; dataset is synthetic and unsuitable | Use threshold-based churn definition (e.g., inactive 30 days) as a proxy KPI |
| Real-time data streaming / live updates | Makes dashboard feel dynamic | Dataset is static Kaggle file; implementing fake real-time adds complexity with zero benefit | Static load on startup; filters re-aggregate in-memory |
| User-level drill-down tables | Product managers want individual user detail | Too granular for a strategic management dashboard; loses the "executive at a glance" framing; performance risk on 210K rows | Segment-level aggregations (by genre, device, subscription tier) |
| NPS / survey-based sentiment KPIs | NPS is a real Netflix KPI | Dataset does not contain NPS data; fabricating it is academically dishonest | Use `reviews` star ratings as a satisfaction proxy |
| Geographic / choropleth map | Visually impressive, often expected | Only useful if `users` table has reliable region data; adds a chart slot that competes with more data-rich options | Use region as a filter dropdown rather than a map visualization |
| Animated transitions / custom CSS | Polish feels professional | Streamlit's default theme is acceptable; custom CSS is fragile and time-expensive given today's deadline | Use Plotly's built-in themes consistently |

---

## Feature Dependencies

```
[Interactive Filters (sidebar)]
    └──drives──> [All KPI scorecards]  (all KPIs must respect filter state)
    └──drives──> [All chart visualizations]

[watch_history table]
    └──required by──> [Average Watch Time KPI]
    └──required by──> [Active Users KPI]
    └──required by──> [Content Completion Rate KPI]
    └──required by──> [Time-series line chart]

[recommendation_logs table]
    └──required by──> [Recommendation CTR KPI]
    └──required by──> [Recommendation Effectiveness by Genre chart]

[movies table]
    └──required by──> [Genre bar chart]
    └──joined by──> [watch_history] for content-level analysis

[users table]
    └──required by──> [Churn Rate KPI]
    └──provides──> [subscription_type filter]
    └──provides──> [device_type filter] (or watch_history)

[reviews table]
    └──optional join──> [Scatter: Watch Time vs Rating]

[KPI scorecards]
    └──enhanced by──> [KPI delta indicators] (prior period comparison)
    └──enhanced by──> [Alarm thresholds] (color coding)

[Churn Rate KPI] ──conflicts with──> [Predictive ML Model]
    (assignment scopes out prediction; use simple threshold definition)
```

### Dependency Notes

- **All KPIs require filters to propagate:** Every aggregation must be wrapped in filter-aware Pandas operations. Define filters first, then compute all metrics from filtered DataFrames.
- **recommendation_logs is the riskiest table:** It may have quality or join issues. Validate this join early — if it fails, Recommendation CTR must be dropped or approximated.
- **Churn Rate definition is a design choice:** With a static dataset, "churn" must be defined operationally (e.g., no watch event in last 30 days of dataset window, or subscription_status == 'cancelled'). Choose one definition and document it in the Word deliverable.
- **Genre filter depends on movies.genre being clean:** May need normalization (lowercase, deduplication) during data prep.

---

## MVP Definition

Given the hard deadline of today (March 22, 2026, 23:59 MSK), this is the only version.

### Launch With (v1 = Final Deliverable)

- [ ] **5 KPI scorecards** — Average Watch Time, Active Users, Recommendation CTR, Content Completion Rate, Churn Rate. Covers all three business areas (engagement, recommendation, retention). Stays within 3-7 limit.
- [ ] **4 chart types** — (1) Line chart: watch hours over time. (2) Horizontal bar: top genres by watch time. (3) Pie/donut: device type distribution. (4) Scatter: watch time vs. avg rating. Covers 3-6 requirement with visible variety.
- [ ] **3-4 interactive filters** — Time period (date range or month selector), Genre (multiselect), Subscription type (dropdown), Device type (dropdown). Meets 2-5 requirement.
- [ ] **KPI delta badges** — Prior period comparison shown as +/-% under each KPI tile. LOW complexity, HIGH grader impression.
- [ ] **Alarm thresholds documented** — Color KPI tiles red/yellow/green based on thresholds. Described in Word file.
- [ ] **Netflix logo + dashboard title** — Required by assignment.

### Add After Validation (v1.x)

Not applicable — single-submission assignment.

### Future Consideration (v2+)

Not applicable — this is a one-time deliverable.

---

## Feature Prioritization Matrix

| Feature | Assignment Value | Implementation Cost | Priority |
|---------|-----------------|---------------------|----------|
| 5 KPI scorecards | HIGH | LOW | P1 |
| Interactive sidebar filters (4 filters) | HIGH | LOW | P1 |
| Line chart (watch time over time) | HIGH | LOW | P1 |
| Bar chart (top genres) | HIGH | LOW | P1 |
| Churn Rate KPI | HIGH | MEDIUM | P1 |
| Recommendation CTR KPI | HIGH | MEDIUM | P1 |
| Netflix logo + title | HIGH | LOW | P1 |
| Alarm threshold coloring on KPI tiles | HIGH | LOW | P1 |
| Pie/donut (device breakdown) | MEDIUM | LOW | P2 |
| Scatter plot (watch time vs. rating) | MEDIUM | LOW | P2 |
| KPI delta indicators (vs. prior period) | MEDIUM | LOW | P2 |
| Recommendation effectiveness by genre | MEDIUM | MEDIUM | P2 |
| Cohort retention heatmap | LOW | HIGH | P3 |
| Search-to-watch conversion rate | LOW | MEDIUM | P3 |
| Geographic filter / map | LOW | MEDIUM | P3 |

**Priority key:**
- P1: Must have for assignment submission
- P2: Include if time allows — raises grade
- P3: Skip given today's deadline

---

## Competitor / Reference Feature Analysis

These are real streaming analytics dashboards that inform what "good" looks like.

| Feature | Vimeo OTT Analytics | Netflix Internal (public statements) | This Dashboard |
|---------|---------------------|--------------------------------------|----------------|
| Watch time trend | Line chart, daily | Internal metric, not public | Line chart by week/month |
| Content performance ranking | Title-level table | Engagement report (hours viewed) | Genre-level bar chart |
| Audience segmentation filters | Geography, device, date | Age, region, device | Genre, device, subscription type, date |
| Churn / retention | Subscriber gain/loss | Churn rate (~1.8% gross) | Churn Rate KPI (threshold-based) |
| Recommendation metrics | Not exposed | CTR, hit rate, view duration post-rec | Recommendation CTR KPI |
| Alarm / alerting | Not in self-serve | Internal SLA thresholds | Color-coded KPI tiles + Word description |

---

## KPI Recommended Shortlist (Final 5)

These 5 KPIs cover all three business pillars required by the assignment and are all computable from the dataset.

| # | KPI | Business Pillar | Formula | Alarm Threshold (example) |
|---|-----|----------------|---------|--------------------------|
| 1 | Average Watch Time (min/user) | Engagement | SUM(watch_duration) / COUNT(DISTINCT user_id) | Red if < 60 min/month |
| 2 | Monthly Active Users (MAU) | Engagement | COUNT(DISTINCT user_id) in selected period | Red if month-over-month decline > 5% |
| 3 | Content Completion Rate (%) | Engagement | AVG(watch_duration / movie_duration) * 100 | Red if < 50% |
| 4 | Recommendation CTR (%) | Recommendation Effectiveness | SUM(clicks) / SUM(recommendations_shown) * 100 | Red if < 10% |
| 5 | Churn Rate (%) | Retention | COUNT(churned_users) / COUNT(total_users) * 100 | Red if > 5% monthly |

---

## Sources

- [Netflix content engagement KPI - The Content Technologist](https://www.content-technologist.com/netflix-content-engagement-kpi/)
- [OTT Platform Analytics: 15 KPIs - MwareTV](https://mwaretv.com/en/blog/ott-platform-analytics-guide)
- [How Netflix Recommendation System Works - HelloPM](https://hellopm.co/netflix-content-recommendation-system-product-analytics-case-study/)
- [Measuring Netflix Recommendation Engine - PM Exercises](https://www.productmanagementexercises.com/4092/how-would-you-measure-success-netflix-recommendation-engine)
- [Guide to Video Analytics for OTT Platforms - FastPix](https://www.fastpix.io/blog/guide-to-video-analytics-for-ott-platform-key-metrics)
- [OTT KPIs: Executive Guide - ExecViva](https://execviva.com/executive-hub/ott-kpis)
- [Understanding Vimeo OTT Streaming Analytics Dashboard](https://help.vimeo.com/hc/en-us/articles/36503541895697-Understanding-the-Vimeo-OTT-Streaming-Analytics-dashboard)
- [Netflix Retention Strategy: Proven Tactics - Propel](https://www.trypropel.ai/resources/customer-retention-strategies-proven-netflix-techniques-to-reduce-churn)
- [BI Dashboard Design Best Practices 2025 - Julius AI](https://julius.ai/articles/business-intelligence-dashboard-design-best-practices)
- [What Metrics Show Value for Netflix's Recommendation Algorithm - Medium/Tharunya, Jan 2026](https://medium.com/@Tharunya/what-metrics-show-value-for-netflixs-content-recommendation-algorithm-ee5f46823334)

---

*Feature research for: Netflix Strategic Dashboard (university BI assignment)*
*Researched: 2026-03-22*
