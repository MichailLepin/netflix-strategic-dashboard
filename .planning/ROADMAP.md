# Roadmap: Netflix Strategic Dashboard

## Overview

Four phases build strictly in dependency order: data loading and validation first (nothing else is possible without clean, joined DataFrames), then the dashboard skeleton with filters and KPI tiles (the interactive frame), then all four charts assembled into the complete single-screen layout, and finally deployment plus Word deliverable completion. Each phase produces a verifiable artifact that the next phase contracts against.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Data Foundation** - Load, clean, type-cast, join, and validate all 6 CSV tables; confirm memory footprint and GitHub file size safety (completed 2026-03-22)
- [x] **Phase 2: Dashboard Skeleton, Filters, and KPIs** - Build the app shell with Netflix branding, sidebar filters, and all 4 KPI scorecard tiles wired to live data (completed 2026-03-22)
- [ ] **Phase 3: Charts and Complete Layout** - Implement all 4 Plotly charts inside the column grid to produce the finished single-screen dashboard
- [ ] **Phase 4: Deploy and Word Deliverable** - Deploy to Streamlit Cloud, verify all assignment checklist items, and complete the Word file

## Phase Details

### Phase 1: Data Foundation
**Goal**: All 6 CSV tables are loaded, cleaned, correctly typed, and joined into a single cached DataFrame that downstream code can query without worrying about data quality or memory limits.
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria** (what must be TRUE):
  1. Running `data_loader.py` standalone prints row counts for all 6 tables and the merged DataFrame without errors
  2. `df.info(memory_usage='deep')` shows total memory under 400MB after categorical dtype casting
  3. Join key cardinality check passes: at least 80% of watch_history user_ids exist in users table
  4. `ls -lh data/` shows no individual CSV file exceeds 90MB (safe for GitHub)
  5. `@st.cache_data` wraps all loading logic so repeated calls return immediately without re-reading disk
**Plans**: 1 plan

Plans:
- [ ] 01-01-PLAN.md — Project setup, dataset download, data loading with cleaning/validation/caching

### Phase 2: Dashboard Skeleton, Filters, and KPIs
**Goal**: A running Streamlit app showing the Netflix logo, dashboard title, sidebar filters wired to live data, and 4 KPI scorecard tiles that update correctly when filters change.
**Depends on**: Phase 1
**Requirements**: DASH-01, DASH-02, KPI-01, KPI-02, KPI-03, KPI-04, FLT-01, FLT-02, FLT-03, FLT-04
**Success Criteria** (what must be TRUE):
  1. Netflix logo and dashboard title are visible at the top of the app
  2. Sidebar shows 4 filter widgets (genre, subscription type, device type, date range) and selecting any filter instantly updates the displayed values
  3. All 4 KPI tiles (Average Daily Watch Time, Content Completion Rate, Recommendation CTR, Churn Rate) display computed scalar values with alarm threshold coloring (red/yellow/green)
  4. The column grid layout renders without vertical scrolling on a 1080p screen at 100% zoom
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — App shell, config.toml dark theme, Netflix branding, and layout skeleton
- [ ] 02-02-PLAN.md — Filter sidebar, KPI computation with tests, and alarm-colored tile rendering

### Phase 3: Charts and Complete Layout
**Goal**: All 4 Plotly charts are implemented and placed in the column grid, producing the finished single-screen dashboard that meets every visual assignment requirement.
**Depends on**: Phase 2
**Requirements**: VIZ-01, VIZ-02, VIZ-03, VIZ-04
**Success Criteria** (what must be TRUE):
  1. Line chart showing watch hours over time renders and responds to active filters
  2. Horizontal bar chart showing top genres by watch time renders and responds to active filters
  3. Pie/donut chart showing device type distribution renders and responds to active filters
  4. Scatter plot showing watch time vs. content rating renders and responds to active filters
  5. All charts fit on one screen with no scrolling alongside the KPI row at 1080p 100% zoom
**Plans**: 1 plan

Plans:
- [ ] 03-01-PLAN.md — Create charts.py module with 4 Plotly chart functions and wire into app.py layout

### Phase 4: Deploy and Word Deliverable
**Goal**: The dashboard is publicly accessible on Streamlit Cloud and the Word file contains all required sections with a screenshot of the deployed URL.
**Depends on**: Phase 3
**Requirements**: DASH-03, DLVR-01, DLVR-02
**Success Criteria** (what must be TRUE):
  1. Streamlit Cloud URL opens the dashboard without login from a fresh browser session
  2. App loads within 60 seconds from a cold start (account for Streamlit Community Cloud sleep behavior)
  3. Alarm thresholds are documented in the dashboard (visible descriptions or legend) and in the Word file
  4. Word file contains: business requirements, data preparation notes, dashboard screenshot taken from the deployed URL (not localhost), public link, and alarm description
**Plans**: TBD

Plans:
- [ ] 04-01: Deploy to Streamlit Cloud and complete Word deliverable

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Foundation | 0/1 | Complete    | 2026-03-22 |
| 2. Dashboard Skeleton, Filters, and KPIs | 2/2 | Complete    | 2026-03-22 |
| 3. Charts and Complete Layout | 0/1 | Not started | - |
| 4. Deploy and Word Deliverable | 0/1 | Not started | - |
