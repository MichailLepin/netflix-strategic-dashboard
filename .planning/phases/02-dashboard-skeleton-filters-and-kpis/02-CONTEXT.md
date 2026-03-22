# Phase 2: Dashboard Skeleton, Filters, and KPIs - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** Auto-analyzed from codebase + requirements

<domain>
## Phase Boundary

Build the running Streamlit app shell with Netflix branding (logo + title), 4 sidebar filters wired to live data, and 4 KPI scorecard tiles that update when filters change. Single-screen layout using `st.set_page_config(layout="wide")` and `st.columns()`. Charts are Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Netflix Branding
- Use Netflix red (#E50914) as accent color throughout
- Netflix logo displayed at top-left of the app (download Netflix logo PNG or use text-based "NETFLIX" in red)
- Dashboard title: "Netflix Strategic Dashboard" — concise, in dark text next to logo
- Dark theme preferred (dark background, light text) to match Netflix aesthetic

### Layout Structure
- `st.set_page_config(layout="wide")` — mandatory for single-screen
- Top row: Logo + title + subtitle ("Content Strategy & User Engagement Analytics")
- Below: 4 KPI tiles in a single row using `st.columns(4)`
- Below KPIs: placeholder area for Phase 3 charts (2x2 grid using nested `st.columns`)
- Sidebar: all 4 filters stacked vertically

### Filter Design
- Genre filter: `st.multiselect` using `genre_primary` from movies table (joined via watch_history)
- Subscription type filter: `st.multiselect` using `subscription_plan` from users table (values: Basic, Standard, Premium)
- Device type filter: `st.multiselect` using `device_type` from watch_history table
- Time period filter: `st.date_input` range picker using `timestamp` from watch_history
- All filters default to "all" (no filtering) on initial load
- Filters apply to all KPIs simultaneously

### KPI Computation
- **Avg Watch Time (KPI-01)**: Mean of `watch_duration_minutes` from watch_history, converted to hours. Display as "X.X hrs"
- **Content Completion Rate (KPI-02)**: % of watch_history rows where `progress_percentage >= 90`. Display as "XX.X%"
- **Recommendation CTR (KPI-03)**: % of recommendation_logs where `clicked == True`. Display as "XX.X%"
- **Churn Rate (KPI-04)**: % of users where `is_active == False`. Display as "XX.X%"

### KPI Tile Styling
- Each tile uses `st.metric()` with delta indicator (vs overall average when filtered)
- Alarm coloring: green (good), yellow (warning), red (critical)
  - Churn Rate: green < 15%, yellow 15-25%, red > 25%
  - Completion Rate: green > 60%, yellow 40-60%, red < 40%
  - Rec CTR: green > 20%, yellow 10-20%, red < 10%
  - Watch Time: green > 2hrs, yellow 1-2hrs, red < 1hr
- Use `st.markdown` with custom CSS for colored backgrounds on tiles

### Claude's Discretion
- Exact CSS styling and spacing
- Loading state while data loads
- Error handling for edge cases (empty filter results)
- Specific font choices within Streamlit constraints

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/data_loader.py`: `load_data()` returns dict with keys: users, movies, watch, recs, searches, reviews
- All DataFrames are cleaned, typed, and cached via `@st.cache_data`
- Total memory: 73.3MB — well within limits

### Established Patterns
- Data dir resolved via `os.path.dirname(os.path.abspath(__file__))` — relative to module
- Category dtypes on: `subscription_plan`, `country`, `primary_device`, `gender`, `device_type`, `genre_primary`, `content_type`
- Join keys validated: user_id (100% match), movie_id (100% match)

### Integration Points
- `app.py` (new) will import `from src.data_loader import load_data`
- Filters will operate on the cached DataFrames — no re-loading needed
- KPI functions should be pure functions taking filtered DataFrames as input

### Key Column Names (verified from actual data)
- Users: `user_id`, `subscription_plan`, `country`, `primary_device`, `gender`, `age`, `is_active`, `monthly_spend`
- Movies: `movie_id`, `genre_primary`, `content_type`, `imdb_rating`, `duration_minutes`
- Watch: `session_id`, `user_id`, `movie_id`, `device_type`, `watch_duration_minutes`, `progress_percentage`, `timestamp`
- Recs: `user_id`, `movie_id`, `clicked` (+ other fields)

</code_context>

<specifics>
## Specific Ideas

- Netflix dark theme feel — the dashboard should feel like a Netflix internal tool
- KPI tiles should be prominent and immediately readable at a glance
- Filters should feel responsive — no lag when switching

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-dashboard-skeleton-filters-and-kpis*
*Context gathered: 2026-03-22 via auto-analysis*
