# Phase 3: Charts and Complete Layout - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** Auto-analyzed from codebase + requirements

<domain>
## Phase Boundary

Replace the 4 placeholder `st.info()` blocks in app.py with real Plotly charts. All charts must respond to sidebar filters and fit on one screen alongside the KPI row. No new filters or KPIs — only visualizations.

</domain>

<decisions>
## Implementation Decisions

### Chart 1: Engagement Trends (VIZ-01) — Line Chart
- X-axis: time (watch_date, aggregated by week or month)
- Y-axis: average watch duration (hours) per period
- Use `plotly.express.line()` — not graph_objects
- Color by subscription_plan for segment comparison
- Must respond to all 4 sidebar filters
- Position: top-left of 2x2 grid (chart_col1)

### Chart 2: Top Genres (VIZ-02) — Horizontal Bar Chart
- Show top 10 genres by total watch time (hours)
- Use `plotly.express.bar()` with `orientation="h"`
- Sort descending (highest at top)
- Color by genre with Netflix-themed palette
- Must respond to filters
- Position: top-right (chart_col2)

### Chart 3: Device Distribution (VIZ-03) — Donut Chart
- Show device_type distribution by watch session count
- Use `plotly.express.pie()` with `hole=0.4` for donut
- Netflix color palette: reds, grays, whites
- Must respond to filters
- Position: bottom-left (chart_col3)

### Chart 4: Watch Time vs Rating (VIZ-04) — Scatter Plot
- X-axis: imdb_rating (from movies table, joined via movie_id)
- Y-axis: average watch_duration_minutes per movie
- Dot size: number of watch sessions per movie
- Color by genre_primary
- Use `plotly.express.scatter()`
- Must respond to filters
- Position: bottom-right (chart_col4)

### Chart Styling
- Dark theme: `template="plotly_dark"` on all charts
- Consistent Netflix color scheme across all charts
- Compact height — all 4 charts + KPI row must fit in ~900px viewport
- Chart height: approximately 300px each
- Remove chart margins where possible for space efficiency
- `use_container_width=True` on all `st.plotly_chart()` calls

### Claude's Discretion
- Exact aggregation granularity (weekly vs monthly for line chart)
- Hover tooltip content
- Legend placement
- Animation/transition settings
- Exact color hex values beyond #E50914

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/data_loader.py`: `load_data()` returns dict with keys: users, movies, watch, recs, searches, reviews
- `src/filter.py`: `apply_filters()` returns filtered dict with keys: users, watch, recs
- `src/kpis.py`: `compute_kpis()` and `get_alarm_level()` — pattern for pure computation functions

### Established Patterns
- Pure functions in `src/` modules, imported into `app.py`
- Data flows: `load_data() → apply_filters() → compute/chart functions`
- Charts should follow the same pattern: create a `src/charts.py` module with pure functions

### Integration Points
- `app.py` lines 173-183: Replace the 4 `st.info()` placeholders with `st.plotly_chart()` calls
- The 2x2 grid is already set up: `chart_col1, chart_col2` and `chart_col3, chart_col4`
- Filtered data dict is available as `filtered` variable in app.py
- For scatter chart, need to join watch with movies on movie_id for imdb_rating access
- The `data["movies"]` is available in app.py scope for joining

### Key Column Names (from Phase 1)
- watch: `watch_date` (datetime), `watch_duration_minutes`, `device_type`, `user_id`, `movie_id`, `progress_percentage`
- movies: `movie_id`, `genre_primary`, `imdb_rating`, `content_type`, `duration_minutes`
- users: `subscription_plan`

</code_context>

<specifics>
## Specific Ideas

- Charts should feel professional — like a Netflix internal analytics tool
- Keep it clean: no unnecessary gridlines or decorations
- Charts should tell a story at a glance — titles should describe the insight, not just the data

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-charts-and-complete-layout*
*Context gathered: 2026-03-22 via auto-analysis*
