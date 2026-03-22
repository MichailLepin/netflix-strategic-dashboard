# Phase 2: Dashboard Skeleton, Filters, and KPIs - Research

**Researched:** 2026-03-22
**Domain:** Streamlit layout, sidebar filters, KPI metrics, custom CSS theming
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Netflix red (#E50914) as accent color throughout
- Netflix logo displayed at top-left (PNG or text-based "NETFLIX" in red)
- Dashboard title: "Netflix Strategic Dashboard"
- Subtitle: "Content Strategy & User Engagement Analytics"
- Dark theme (dark background, light text) to match Netflix aesthetic
- `st.set_page_config(layout="wide")` — mandatory for single-screen
- Top row: Logo + title + subtitle
- Below: 4 KPI tiles in a single row using `st.columns(4)`
- Below KPIs: placeholder area for Phase 3 charts (2x2 grid using nested `st.columns`)
- Sidebar: all 4 filters stacked vertically
- Genre filter: `st.multiselect` using `genre_primary` from movies table (joined via watch_history)
- Subscription type filter: `st.multiselect` using `subscription_plan` from users table
- Device type filter: `st.multiselect` using `device_type` from watch_history table
- Time period filter: `st.date_input` range picker using `watch_date` from watch_history
- All filters default to "all" (no filtering) on initial load
- Filters apply to all KPIs simultaneously
- KPI-01: Mean of `watch_duration_minutes`, converted to hours, displayed as "X.X hrs"
- KPI-02: % of watch_history rows where `progress_percentage >= 90`, displayed as "XX.X%"
- KPI-03: % of recommendation_logs rows where `was_clicked == True`, displayed as "XX.X%"
- KPI-04: % of users where `is_active == False`, displayed as "XX.X%"
- Each KPI tile uses `st.metric()` with delta indicator (vs overall average when filtered)
- Alarm coloring via `st.markdown` with custom CSS:
  - Churn Rate: green < 15%, yellow 15-25%, red > 25%
  - Completion Rate: green > 60%, yellow 40-60%, red < 40%
  - Rec CTR: green > 20%, yellow 10-20%, red < 10%
  - Watch Time: green > 2hrs, yellow 1-2hrs, red < 1hr
- KPI functions must be pure functions taking filtered DataFrames as input

### Claude's Discretion

- Exact CSS styling and spacing
- Loading state while data loads
- Error handling for edge cases (empty filter results)
- Specific font choices within Streamlit constraints

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DASH-01 | Dashboard displays concise title and Netflix logo | st.image() for logo + st.title()/st.markdown() for title; header column layout verified |
| DASH-02 | Single-screen layout (no scrolling for key information) | st.set_page_config(layout="wide") + st.columns() confirmed; config.toml theme approach documented |
| KPI-01 | Avg Daily Watch Time (hours) as scorecard tile | watch_duration_minutes / 60 from watch_history; st.metric() API confirmed |
| KPI-02 | Content Completion Rate (%) as scorecard tile | progress_percentage >= 90 boolean mask on watch_history; st.metric() API confirmed |
| KPI-03 | Recommendation CTR (%) as scorecard tile | CRITICAL: column is `was_clicked` not `clicked` in recommendation_logs |
| KPI-04 | Churn Rate (%) as scorecard tile | is_active == False on users table; st.metric() API confirmed |
| FLT-01 | Filter by genre | st.multiselect on genre_primary (20 unique values confirmed); join watch->movies needed |
| FLT-02 | Filter by subscription type | st.multiselect on subscription_plan (4 values: Basic/Standard/Premium/Premium+) |
| FLT-03 | Filter by device type | st.multiselect on device_type from watch_history (5 values confirmed) |
| FLT-04 | Filter by time period | st.date_input range picker on watch_date column (range: 2024-01-01 to 2025-12-31) |
</phase_requirements>

---

## Summary

Phase 2 builds the visible shell of the dashboard: page config, Netflix dark branding, sidebar filters, and 4 KPI scorecard tiles. The data layer (Phase 1) is complete and validated; this phase only reads from it. All Streamlit APIs needed are confirmed in current docs (Streamlit 1.55.0). The architecture already planned (app.py + src/filter.py + src/kpis.py) maps cleanly to the Streamlit reactive execution model.

Two critical data-level corrections were found by inspecting the actual CSVs: the recommendation_logs column for clicks is `was_clicked` (not `clicked` as mentioned in CONTEXT.md), and watch_history uses `watch_date` (not `timestamp`). The subscription_plan column has 4 distinct values including "Premium+" which is not mentioned in the CONTEXT.md spec. These must be reflected in filter logic.

The main implementation risk is CSS selector instability for styled metric tiles. Streamlit's generated CSS class names change between versions. The safer approach is CSS via `[data-testid]` attributes rather than hashed class names, or using `st.metric(border=True)` plus `delta_color` for alarm signaling without brittle CSS.

**Primary recommendation:** Build in dependency order — config.toml + page config first, then sidebar filters, then KPI computation functions (kpis.py), then tile rendering in app.py. Validate KPI values against raw pandas before wiring to UI.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| streamlit | 1.55.0 | Dashboard framework, widgets, layout | Already pinned; `st.metric`, `st.multiselect`, `st.date_input`, `st.columns` all confirmed present |
| pandas | 2.3.3 | DataFrame filtering and KPI computation | Already pinned; boolean mask filtering is idiomatic and fast on 210K rows |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| datetime | stdlib | Convert st.date_input return values to pd.Timestamp for filtering | Always needed for date range filter |
| os | stdlib | Resolve assets path for Netflix logo PNG | Used in data_loader.py already; same pattern for assets/ |

**No new packages needed.** All phase 2 work uses the existing pinned stack.

---

## Architecture Patterns

### Recommended File Structure for Phase 2
```
dashboard/
├── app.py                        # Entry point — NEW this phase
├── src/
│   ├── data_loader.py            # Already exists (Phase 1)
│   ├── filter.py                 # NEW this phase — pure filter functions
│   └── kpis.py                   # NEW this phase — pure KPI computation
├── assets/
│   └── netflix_logo.png          # NEW this phase (or text fallback)
└── .streamlit/
    └── config.toml               # NEW this phase — dark theme declaration
```

### Pattern 1: .streamlit/config.toml for Dark Theme

**What:** Declare theme declaratively in config.toml so it applies before any Python runs. Prevents flash of light theme on load.

**When to use:** Always set theme in config.toml, not only in set_page_config.

```toml
# .streamlit/config.toml
[theme]
base = "dark"
primaryColor = "#E50914"
backgroundColor = "#141414"
secondaryBackgroundColor = "#1F1F1F"
textColor = "#FFFFFF"
font = "sans serif"
```

Source: [Streamlit Theming Docs](https://docs.streamlit.io/develop/concepts/configuration/theming) — HIGH confidence

### Pattern 2: st.set_page_config (must be first Streamlit call)

```python
# app.py — must be the very first st.* call
import streamlit as st
from src.data_loader import load_data

st.set_page_config(
    page_title="Netflix Strategic Dashboard",
    page_icon="assets/netflix_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

Source: [st.set_page_config API Docs](https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config) — HIGH confidence

### Pattern 3: Header Row (Logo + Title)

```python
# Logo + title using columns
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("assets/netflix_logo.png", width=80)
with col_title:
    st.markdown("## Netflix Strategic Dashboard")
    st.caption("Content Strategy & User Engagement Analytics")
```

Text fallback if PNG is unavailable:
```python
with col_logo:
    st.markdown('<h1 style="color:#E50914;font-weight:900;">NETFLIX</h1>',
                unsafe_allow_html=True)
```

### Pattern 4: Sidebar Filters

```python
with st.sidebar:
    st.header("Filters")

    # Genre filter — populate from movies table
    all_genres = sorted(data["movies"]["genre_primary"].cat.categories.tolist())
    selected_genres = st.multiselect("Genre", options=all_genres, default=[],
                                     placeholder="All genres")

    # Subscription filter
    all_plans = sorted(data["users"]["subscription_plan"].cat.categories.tolist())
    selected_plans = st.multiselect("Subscription Type", options=all_plans, default=[],
                                    placeholder="All plans")

    # Device type filter (from watch_history)
    all_devices = sorted(data["watch"]["device_type"].cat.categories.tolist())
    selected_devices = st.multiselect("Device Type", options=all_devices, default=[],
                                      placeholder="All devices")

    # Date range filter
    import datetime
    date_min = data["watch"]["watch_date"].min().date()
    date_max = data["watch"]["watch_date"].max().date()
    date_range = st.date_input("Time Period",
                               value=(date_min, date_max),
                               min_value=date_min,
                               max_value=date_max)
```

Source: [st.multiselect API Docs](https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect) — HIGH confidence
Source: [st.date_input API Docs](https://docs.streamlit.io/develop/api-reference/widgets/st.date_input) — HIGH confidence

### Pattern 5: KPI Tile Row with st.metric and delta_color for Alarms

```python
# Compute KPIs
kpi_vals = compute_kpis(filtered_data)
kpi_overall = compute_kpis(data)  # unfiltered baseline for delta

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_watch = kpi_vals["avg_watch_hours"] - kpi_overall["avg_watch_hours"]
    # Alarm: green > 2hrs, yellow 1-2hrs, red < 1hr
    watch_color = _watch_color(kpi_vals["avg_watch_hours"])
    st.metric("Avg Watch Time", f"{kpi_vals['avg_watch_hours']:.1f} hrs",
              delta=f"{delta_watch:+.2f} hrs",
              delta_color=watch_color)
```

**For alarm coloring without brittle CSS selectors**, use `delta_color` parameter with named colors. Streamlit 1.55.0 supports "green", "red", "yellow", "orange" as named colors for `delta_color`. This is stable across versions.

Source: [st.metric API Docs](https://docs.streamlit.io/develop/api-reference/data/st.metric) — HIGH confidence

### Pattern 6: CSS Injection for Tile Background (optional enhancement)

Use `st.markdown` with `unsafe_allow_html=True` to inject CSS. Prefer `[data-testid]` selectors over hashed class names — data-testid attributes are stable across Streamlit versions.

```python
st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #1F1F1F;
    border-radius: 8px;
    padding: 16px;
    border-left: 4px solid #E50914;
}
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)
```

Source: [Streamlit FAQ - custom style](https://discuss.streamlit.io/t/faq-how-to-customize-the-style-or-appearance-of-your-streamlit-app/63878) — MEDIUM confidence (community forum, verified with CSS data-testid pattern)

### Pattern 7: Filter Logic in filter.py (pure functions)

```python
# src/filter.py
import pandas as pd
import datetime

def apply_filters(
    data: dict[str, pd.DataFrame],
    genres: list[str],
    plans: list[str],
    devices: list[str],
    date_range: tuple,
) -> dict[str, pd.DataFrame]:
    """Return filtered copies of all DataFrames. Pure function — no side effects."""
    watch = data["watch"].copy()
    users = data["users"].copy()
    recs  = data["recs"].copy()

    # Date range filter on watch_history (column: watch_date)
    if len(date_range) == 2:
        start, end = date_range
        start_ts = pd.Timestamp(start)
        end_ts   = pd.Timestamp(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        watch = watch[(watch["watch_date"] >= start_ts) & (watch["watch_date"] <= end_ts)]

    # Device filter on watch_history
    if devices:
        watch = watch[watch["device_type"].isin(devices)]

    # Genre filter — requires join: watch -> movies -> genre_primary
    if genres:
        genre_movie_ids = data["movies"].loc[
            data["movies"]["genre_primary"].isin(genres), "movie_id"
        ]
        watch = watch[watch["movie_id"].isin(genre_movie_ids)]

    # Subscription plan filter on users, then filter watch+recs by user_id
    if plans:
        users = users[users["subscription_plan"].isin(plans)]
        filtered_user_ids = users["user_id"]
        watch = watch[watch["user_id"].isin(filtered_user_ids)]
        recs  = recs[recs["user_id"].isin(filtered_user_ids)]

    return {"users": users, "watch": watch, "recs": recs}
```

### Pattern 8: KPI Computation in kpis.py (pure functions)

```python
# src/kpis.py
import pandas as pd

def compute_kpis(filtered: dict[str, pd.DataFrame]) -> dict[str, float]:
    """Compute all 4 KPI scalars from filtered DataFrames."""
    watch = filtered["watch"]
    users = filtered["users"]
    recs  = filtered["recs"]

    # KPI-01: Avg Watch Time in hours
    avg_watch_hours = (watch["watch_duration_minutes"].mean() / 60.0) if len(watch) > 0 else 0.0

    # KPI-02: Content Completion Rate
    completion_rate = (
        (watch["progress_percentage"] >= 90).sum() / len(watch) * 100
        if len(watch) > 0 else 0.0
    )

    # KPI-03: Recommendation CTR — COLUMN IS was_clicked (not clicked)
    rec_ctr = (
        recs["was_clicked"].sum() / len(recs) * 100
        if len(recs) > 0 else 0.0
    )

    # KPI-04: Churn Rate
    churn_rate = (
        (~users["is_active"]).sum() / len(users) * 100
        if len(users) > 0 else 0.0
    )

    return {
        "avg_watch_hours": round(avg_watch_hours, 1),
        "completion_rate": round(completion_rate, 1),
        "rec_ctr":         round(rec_ctr, 1),
        "churn_rate":      round(churn_rate, 1),
    }
```

### Anti-Patterns to Avoid

- **Caching filter.py or kpis.py:** These run in milliseconds on 210K rows; caching adds overhead with zero benefit. Cache only data_loader.py.
- **Hardcoding filter option lists:** Always pull from `data[...][col].cat.categories` so options stay in sync with actual data. Genre filter has 20 values; subscription_plan has 4 (not 3 — "Premium+" exists).
- **Using `clicked` for Rec CTR:** The actual column in recommendation_logs is `was_clicked`. Using `clicked` will raise a KeyError.
- **Using `timestamp` for date filter:** The actual column in watch_history is `watch_date`. `timestamp` does not exist in this dataset.
- **st.date_input returns tuple of length 1 when user picks only start date:** Always guard with `if len(date_range) == 2` before unpacking.
- **Calling st.set_page_config anywhere except the very first st.* call:** Streamlit raises an error if anything else runs before it.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reactive filter → rerender | Custom callback system | Streamlit's re-execution model | Entire script reruns top-to-bottom on widget change; just read widget values and compute |
| Dark theme | Inline bgcolor on every element | config.toml `base = "dark"` | One declaration applies globally; overrides cascade correctly |
| Multi-select with "All" option | Custom "All" checkbox logic | Empty list default = no filter | `if genres:` applies filter, empty list skips it — built-in semantics |
| Metric tile borders/backgrounds | Full custom HTML component | `st.metric(border=True)` + CSS via `[data-testid]` | st.metric has border param in 1.55.0; custom CSS via data-testid is stable |

---

## Common Pitfalls

### Pitfall 1: Wrong Column Name for Recommendation CTR
**What goes wrong:** `recs["clicked"]` raises `KeyError: 'clicked'`.
**Why it happens:** CONTEXT.md says `clicked == True` but the actual CSV column is `was_clicked`.
**How to avoid:** Use `recs["was_clicked"]` everywhere. Verified by inspecting recommendation_logs.csv header.
**Warning signs:** KeyError on first app run.

### Pitfall 2: Wrong Column Name for Time Period Filter
**What goes wrong:** Date range filter raises `KeyError: 'timestamp'`.
**Why it happens:** CONTEXT.md says "using `timestamp` from watch_history" but the actual column is `watch_date`.
**How to avoid:** Use `watch["watch_date"]` for all date filtering. Verified by inspecting watch_history.csv header.
**Warning signs:** KeyError on first app run.

### Pitfall 3: Subscription Plan Has 4 Values Including "Premium+"
**What goes wrong:** Filter description says Basic/Standard/Premium (3 values); actual data has Basic/Standard/Premium/Premium+ (4 values).
**Why it happens:** Dataset has a Premium+ tier not described in project context.
**How to avoid:** Always populate filter options dynamically from `data["users"]["subscription_plan"].cat.categories`. Never hardcode the list.
**Warning signs:** "Premium+" records silently excluded from all KPIs when filter is active.

### Pitfall 4: st.date_input Returns Incomplete Tuple While User Is Selecting
**What goes wrong:** `start, end = date_range` raises `ValueError: too many/few values to unpack` when user has only clicked the start date.
**Why it happens:** The widget returns a 1-element tuple during selection, before the end date is chosen.
**How to avoid:** Guard: `if len(date_range) == 2: start, end = date_range` else skip date filtering.
**Warning signs:** App crashes as soon as user clicks one date in the range picker.

### Pitfall 5: Genre Filter Requires a Table Join
**What goes wrong:** `watch["genre_primary"]` raises KeyError — genre is not in watch_history.
**Why it happens:** `genre_primary` lives in the movies table; watch_history only has `movie_id`.
**How to avoid:** Filter by finding `movie_id` values that match the selected genres in the movies table, then filter watch by those `movie_id` values.
**Warning signs:** KeyError on genre filter apply; or incorrectly filtering on a non-existent column.

### Pitfall 6: Brittle CSS Class Name Selectors for Metric Tiles
**What goes wrong:** CSS like `div.css-12w0qpk` stops working after a Streamlit patch update.
**Why it happens:** Streamlit generates hashed class names that change with builds.
**How to avoid:** Use semantic `[data-testid="stMetric"]` selectors which are stable across versions.
**Warning signs:** Styled tiles suddenly become unstyled after `pip install --upgrade streamlit`.

### Pitfall 7: Empty Filter Result Causes Division by Zero in KPIs
**What goes wrong:** `ZeroDivisionError` or `NaN` displayed in `st.metric` when filters produce 0 rows.
**Why it happens:** KPI formulas divide by `len(watch)` or `len(recs)` which can be 0.
**How to avoid:** Guard every KPI with `if len(df) > 0 else 0.0`. Display "N/A" or 0 instead of erroring.
**Warning signs:** Streamlit shows error message on screen when an obscure filter combination is selected.

---

## Code Examples

### Alarm Color Helper
```python
# src/kpis.py
def watch_time_alarm_color(hours: float) -> str:
    """Returns delta_color string for st.metric alarm styling."""
    if hours > 2.0:
        return "green"
    elif hours >= 1.0:
        return "yellow"
    else:
        return "red"

def churn_alarm_color(pct: float) -> str:
    if pct < 15.0:
        return "green"
    elif pct <= 25.0:
        return "yellow"
    else:
        return "red"

def completion_alarm_color(pct: float) -> str:
    if pct > 60.0:
        return "green"
    elif pct >= 40.0:
        return "yellow"
    else:
        return "red"

def ctr_alarm_color(pct: float) -> str:
    if pct > 20.0:
        return "green"
    elif pct >= 10.0:
        return "yellow"
    else:
        return "red"
```

### Date Range Filter Application
```python
# Pandas datetime comparison — dates from st.date_input are datetime.date objects
# Must convert to pd.Timestamp for comparison with datetime64[ns] column
start_ts = pd.Timestamp(start_date)
end_ts   = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
mask = (watch["watch_date"] >= start_ts) & (watch["watch_date"] <= end_ts)
watch_filtered = watch[mask]
```

### Phase 3 Chart Placeholder
```python
# Below KPI row — placeholder for Phase 3
st.markdown("---")
st.subheader("Content & Engagement Analytics")
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.info("Chart: Engagement Trends Over Time (Phase 3)")
with chart_col2:
    st.info("Chart: Top Genres by Watch Time (Phase 3)")
chart_col3, chart_col4 = st.columns(2)
with chart_col3:
    st.info("Chart: Device Type Distribution (Phase 3)")
with chart_col4:
    st.info("Chart: Watch Time vs Content Rating (Phase 3)")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@st.experimental_memo` | `@st.cache_data` | Streamlit 1.18+ | Old decorator removed; must use cache_data |
| CSS class selectors (hashed) | `[data-testid]` attribute selectors | Ongoing since ~1.20 | Class names change; testid attributes are stable |
| `delta_color="normal"/"inverse"` only | Named colors: "red","green","yellow","orange","blue" etc. | Streamlit 1.55.0 | Alarm coloring without any CSS |

**Deprecated/outdated:**
- `@st.experimental_memo`: Removed. Use `@st.cache_data`.
- `@st.experimental_singleton`: Removed. Use `@st.cache_resource`.
- `st.beta_columns`: Old name. Use `st.columns`.

---

## Open Questions

1. **Netflix logo availability**
   - What we know: CONTEXT.md says "download Netflix logo PNG or use text-based fallback"
   - What's unclear: No logo file exists in assets/ yet; license restrictions on Netflix logo for academic use
   - Recommendation: Create assets/ dir with a text-based NETFLIX header in red as default; add real PNG as optional enhancement

2. **delta indicator value for unfiltered state**
   - What we know: CONTEXT.md says "delta = vs overall average when filtered"
   - What's unclear: When no filter is applied, the filtered = overall, making delta always 0.0
   - Recommendation: Show delta as 0 with `delta_color="off"` when no filters are active; only show meaningful delta when at least one filter is applied

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none (discovered at runtime via pytest default) |
| Quick run command | `pytest tests/test_kpis.py tests/test_filter.py -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DASH-01 | App has page title and logo area | smoke | `streamlit run app.py` (manual verify) | manual-only |
| DASH-02 | Single-screen layout set | smoke | inspect app.py for `layout="wide"` | manual-only |
| KPI-01 | compute_kpis returns avg_watch_hours > 0 on full dataset | unit | `pytest tests/test_kpis.py::test_avg_watch_hours -x` | ❌ Wave 0 |
| KPI-02 | compute_kpis returns completion_rate in [0,100] | unit | `pytest tests/test_kpis.py::test_completion_rate -x` | ❌ Wave 0 |
| KPI-03 | compute_kpis returns rec_ctr using was_clicked column | unit | `pytest tests/test_kpis.py::test_rec_ctr -x` | ❌ Wave 0 |
| KPI-04 | compute_kpis returns churn_rate using is_active==False | unit | `pytest tests/test_kpis.py::test_churn_rate -x` | ❌ Wave 0 |
| FLT-01 | Genre filter reduces watch rows to genre-matching movies only | unit | `pytest tests/test_filter.py::test_genre_filter -x` | ❌ Wave 0 |
| FLT-02 | Subscription filter reduces users to selected plans | unit | `pytest tests/test_filter.py::test_subscription_filter -x` | ❌ Wave 0 |
| FLT-03 | Device filter reduces watch rows to selected devices | unit | `pytest tests/test_filter.py::test_device_filter -x` | ❌ Wave 0 |
| FLT-04 | Date range filter reduces watch to rows within range | unit | `pytest tests/test_filter.py::test_date_filter -x` | ❌ Wave 0 |
| KPI-01..04 | Empty filter results return 0.0 not NaN/error | unit | `pytest tests/test_kpis.py::test_empty_dataframe_guard -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_kpis.py tests/test_filter.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_kpis.py` — covers KPI-01, KPI-02, KPI-03, KPI-04, empty guard
- [ ] `tests/test_filter.py` — covers FLT-01, FLT-02, FLT-03, FLT-04
- [ ] `tests/conftest.py` — already exists with `data` session fixture; reusable for new tests
- [ ] `assets/` directory — needed for logo (or text fallback)
- [ ] `.streamlit/config.toml` — needed for dark theme declaration

---

## Sources

### Primary (HIGH confidence)
- [st.multiselect — Streamlit Docs](https://docs.streamlit.io/develop/api-reference/widgets/st.multiselect) — full signature, placeholder, default parameters
- [st.date_input — Streamlit Docs](https://docs.streamlit.io/develop/api-reference/widgets/st.date_input) — range picker behavior, tuple return
- [st.metric — Streamlit Docs](https://docs.streamlit.io/develop/api-reference/data/st.metric) — delta_color named colors, border parameter
- [st.set_page_config — Streamlit Docs](https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config) — layout="wide", page_icon parameters
- [Streamlit Theming — Official Docs](https://docs.streamlit.io/develop/concepts/configuration/theming) — config.toml structure, dark base theme
- Actual CSV inspection (`watch_history.csv`, `recommendation_logs.csv`, `users.csv`, `movies.csv`) — exact column names and filter option values

### Secondary (MEDIUM confidence)
- [Streamlit FAQ - Custom Style](https://discuss.streamlit.io/t/faq-how-to-customize-the-style-or-appearance-of-your-streamlit-app/63878) — data-testid CSS selectors (community, corroborated by multiple sources)
- [How to Style Streamlit Metrics in Custom CSS — DEV Community](https://dev.to/barrisam/how-to-style-streamlit-metrics-in-custom-css-4h14) — CSS selector patterns for metric tiles
- [Streamlit 2026 Release Notes](https://docs.streamlit.io/develop/quick-reference/release-notes/2026) — named delta_color values confirmed

### Tertiary (LOW confidence — not required; using above instead)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all APIs confirmed against current official Streamlit docs
- Architecture: HIGH — follows established patterns from ARCHITECTURE.md, verified with current docs
- Pitfalls: HIGH — column name corrections verified directly against actual CSV files; CSS pitfall pattern well-documented across multiple sources
- Filter option values: HIGH — verified by direct CSV inspection (genres, plans, devices, date range)

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable library — 30 days)
