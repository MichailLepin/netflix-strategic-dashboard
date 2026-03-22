# Requirements: Netflix Strategic Dashboard

**Defined:** 2026-03-22
**Core Value:** Enable data-driven decisions about content strategy and user retention by surfacing engagement, recommendation effectiveness, and churn risks.

## v1 Requirements

### Dashboard Core

- [ ] **DASH-01**: Dashboard displays concise title and Netflix logo
- [ ] **DASH-02**: Single-screen layout (no scrolling required for key information)
- [ ] **DASH-03**: Dashboard deployed to Streamlit Cloud with public URL

### KPIs

- [ ] **KPI-01**: User sees Average Daily Watch Time (hours) as scorecard tile
- [ ] **KPI-02**: User sees Content Completion Rate (%) as scorecard tile
- [ ] **KPI-03**: User sees Recommendation Click-Through Rate (%) as scorecard tile
- [ ] **KPI-04**: User sees Churn Rate (%) as scorecard tile

### Visualizations

- [ ] **VIZ-01**: Line chart showing engagement trends over time
- [ ] **VIZ-02**: Horizontal bar chart showing top genres by watch time
- [ ] **VIZ-03**: Pie/donut chart showing device type distribution
- [ ] **VIZ-04**: Scatter plot showing watch time vs content rating

### Filters

- [ ] **FLT-01**: User can filter by genre
- [ ] **FLT-02**: User can filter by subscription type (Basic/Standard/Premium)
- [ ] **FLT-03**: User can filter by device type
- [ ] **FLT-04**: User can filter by time period (date range)

### Data Pipeline

- [ ] **DATA-01**: Download and load Netflix 2025 User Behavior Dataset (6 tables)
- [ ] **DATA-02**: Clean data (handle missing values, duplicates, outliers)
- [ ] **DATA-03**: Join tables with validated keys

### Deliverables

- [ ] **DLVR-01**: Alarm descriptions documented (triggers + thresholds)
- [ ] **DLVR-02**: Word file with business requirements, data prep notes, screenshot, link, alarm description

## v2 Requirements

### Enhanced Visualizations

- **VIZ-05**: Heatmap showing viewing patterns by hour/day
- **VIZ-06**: Funnel chart showing recommendation → click → watch → complete

### Additional KPIs

- **KPI-05**: Monthly Active Users (MAU)
- **KPI-06**: Revenue per User (ARPU)
- **KPI-07**: Search-to-Watch Conversion Rate

### Additional Filters

- **FLT-05**: Region filter (USA/Canada)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Predictive ML models | Assignment focuses on monitoring dashboard, not prediction |
| Real-time data updates | Using static Kaggle dataset |
| Mobile-responsive design | Desktop-first, single-screen focus |
| Peer review of another dashboard | Separate task done outside this project |
| Alarm implementation (code) | Assignment only requires description, not implementation |
| Multi-page navigation | Assignment specifies single-screen dashboard |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DASH-01 | Phase 3 | Pending |
| DASH-02 | Phase 3 | Pending |
| DASH-03 | Phase 4 | Pending |
| KPI-01 | Phase 2 | Pending |
| KPI-02 | Phase 2 | Pending |
| KPI-03 | Phase 2 | Pending |
| KPI-04 | Phase 2 | Pending |
| VIZ-01 | Phase 3 | Pending |
| VIZ-02 | Phase 3 | Pending |
| VIZ-03 | Phase 3 | Pending |
| VIZ-04 | Phase 3 | Pending |
| FLT-01 | Phase 2 | Pending |
| FLT-02 | Phase 2 | Pending |
| FLT-03 | Phase 2 | Pending |
| FLT-04 | Phase 2 | Pending |
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DLVR-01 | Phase 4 | Pending |
| DLVR-02 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-22*
*Last updated: 2026-03-22 after initial definition*
