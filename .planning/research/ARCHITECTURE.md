# Architecture Research

**Domain:** Single-screen Streamlit + Plotly analytics dashboard (static dataset, Streamlit Cloud)
**Researched:** 2026-03-22
**Confidence:** HIGH (Streamlit official docs + verified community patterns)

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  KPI Row     │  │  Chart Grid  │  │  Data Table  │              │
│  │ (st.metric)  │  │(st.columns)  │  │(st.dataframe)│              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Sidebar: Filters (time period, genre, device, region, plan) │   │
│  └──────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                        TRANSFORM LAYER                              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  filter.py   │  │  kpis.py     │  │  charts.py   │              │
│  │ (apply mask) │  │(compute KPIs)│  │(build figs)  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
├─────────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  data_loader.py  (@st.cache_data — loads + cleans all CSVs)  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐   │
│  │ users.csv│  │ movies.csv   │  │watch_hist.csv│  │ ...3 more │   │
│  └──────────┘  └──────────────┘  └──────────────┘  └───────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Communicates With |
|-----------|----------------|-------------------|
| `app.py` | Entry point; layout orchestration; sidebar filter widgets | All modules |
| `data_loader.py` | Load CSVs, merge tables, clean/type-cast, return master DataFrames | `app.py` (receives DataFrames) |
| `filter.py` | Apply sidebar filter values to DataFrames via boolean masks | `app.py` passes raw DFs + filter values; returns filtered DFs |
| `kpis.py` | Compute 3-7 scalar KPI values from filtered DataFrames | `app.py` passes filtered DFs; returns dict of KPI values |
| `charts.py` | Build Plotly figure objects from filtered DataFrames | `app.py` passes filtered DFs; returns `go.Figure` objects |
| `assets/` | Logo image, theme config | `app.py` loads logo via `st.image()` |
| `.streamlit/config.toml` | App title, theme colors (Netflix red `#E50914`) | Streamlit runtime |
| `requirements.txt` | Python dependencies for Streamlit Cloud | Streamlit Cloud build |

## Recommended Project Structure

```
dashboard/                       # repo root
├── app.py                       # entry point — layout + sidebar only
├── requirements.txt             # pinned deps for Cloud deployment
├── data/
│   ├── users.csv
│   ├── movies.csv
│   ├── watch_history.csv
│   ├── recommendation_logs.csv
│   ├── search_logs.csv
│   └── reviews.csv
├── src/
│   ├── data_loader.py           # load + clean + merge all 6 tables
│   ├── filter.py                # apply sidebar selections to DataFrames
│   ├── kpis.py                  # compute KPI scalars (engagement, churn, rec)
│   └── charts.py                # build Plotly figures
├── assets/
│   └── netflix_logo.png         # logo for dashboard header
└── .streamlit/
    └── config.toml              # theme, page title, layout="wide"
```

### Structure Rationale

- **`app.py` at root:** Streamlit Cloud expects the entrypoint at the repo root (or a path you specify); keeping it there avoids configuration friction.
- **`src/` for logic:** Separating data, filter, KPI, and chart logic from the layout file keeps `app.py` readable and each module independently testable. This is the pattern recommended by the Streamlit team for apps beyond trivial examples.
- **`data/` flat:** With a static dataset (no DB), flat CSV files checked into the repo are simplest. Streamlit Cloud serves them alongside the app without extra infrastructure.
- **`.streamlit/config.toml`:** Controls `layout = "wide"` (required for single-screen density), theme colors, and page title declaratively rather than in code.

## Architectural Patterns

### Pattern 1: Cache at the Load Boundary

**What:** Apply `@st.cache_data` only to the data loading and cleaning function, not to filtering or KPI computation.

**When to use:** Always — with a 210K-row static dataset, loading without cache causes 2-5 second delays on every user interaction because Streamlit reruns the entire script on each widget change.

**Trade-offs:** Cache invalidates on function signature changes. For a static dataset this is fine — no TTL needed. If data were live, set `ttl=3600`.

**Example:**
```python
# src/data_loader.py
import streamlit as st
import pandas as pd

@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    users = pd.read_csv("data/users.csv", parse_dates=["join_date"])
    movies = pd.read_csv("data/movies.csv")
    watch = pd.read_csv("data/watch_history.csv", parse_dates=["watch_date"])
    recs = pd.read_csv("data/recommendation_logs.csv")
    # ... clean, type-cast, merge as needed
    return {"users": users, "movies": movies, "watch": watch, "recs": recs}
```

### Pattern 2: Sidebar → Filter → Render (Reactive Pipeline)

**What:** Sidebar widgets emit values; those values flow into filter functions; filtered DataFrames feed KPI and chart functions. No global state, no callbacks — Streamlit's re-execution model handles reactivity.

**When to use:** Standard pattern for any Streamlit filter dashboard. Matches Streamlit's execution model exactly.

**Trade-offs:** Entire script reruns on each widget change. Acceptable because data load is cached; filter + KPI + chart computation on 210K rows is fast (< 200ms typical).

**Example:**
```python
# app.py (structure sketch)
data = load_data()                          # cached — instant after first run

with st.sidebar:
    genre = st.multiselect("Genre", options=data["movies"]["genre"].unique())
    device = st.selectbox("Device", ["All", "TV", "Mobile", "Web"])
    # ... other filters

filtered = apply_filters(data, genre=genre, device=device)  # src/filter.py
kpis = compute_kpis(filtered)                               # src/kpis.py
figs = build_charts(filtered)                               # src/charts.py

# Render
st.metric("Avg Watch Time", kpis["avg_watch_time"])
st.plotly_chart(figs["engagement_trend"], use_container_width=True)
```

### Pattern 3: Wide Layout with Column Grid

**What:** Use `st.set_page_config(layout="wide")` plus `st.columns()` to achieve a dense single-screen layout. KPIs go in a top row of N equal columns; charts go in a 2-column or 3-column grid below.

**When to use:** Required for single-screen constraint. Without `layout="wide"`, content stacks vertically and forces scrolling.

**Trade-offs:** Fixed column ratios (e.g., `st.columns([1,1,1])`) can look unbalanced on narrow screens, but the assignment is desktop-only so this is acceptable.

**Example:**
```python
# config.toml
[server]
[theme]
primaryColor = "#E50914"   # Netflix red

# app.py
st.set_page_config(page_title="Netflix Strategic Dashboard", layout="wide")

# KPI row — 5 metrics across
k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.metric("Avg Engagement Score", kpis["engagement"])
# ...

# Chart row 1 — 2 charts side by side
c1, c2 = st.columns(2)
with c1: st.plotly_chart(figs["content_performance"], use_container_width=True)
with c2: st.plotly_chart(figs["recommendation_ctr"], use_container_width=True)
```

## Data Flow

### Request Flow (on each user filter interaction)

```
User changes sidebar widget
        ↓
Streamlit reruns app.py top-to-bottom
        ↓
load_data()  →  cache hit (instant) → returns raw DataFrames
        ↓
apply_filters(data, **sidebar_values)  →  boolean mask → filtered DataFrames
        ↓
compute_kpis(filtered)  →  scalar values (avg, count, ratio)
build_charts(filtered)  →  Plotly Figure objects
        ↓
st.metric() / st.plotly_chart() → renders to browser
```

### Data Pipeline (one-time, first load)

```
6 CSV files (data/)
        ↓
data_loader.py: pd.read_csv → parse types → merge on keys
        ↓
@st.cache_data stores result in memory
        ↓
Dict of clean DataFrames available to rest of app
```

### Key Data Flows

1. **Load → Cache:** CSVs are read once per session (or per Streamlit Cloud restart). All 6 tables are loaded, type-cast, and merged into a coherent set of DataFrames that share user_id and movie_id keys.

2. **Filter → KPI:** Filtered DataFrames are passed to `compute_kpis()`, which computes scalar values (e.g., mean watch duration, recommendation click-through rate, churn-risk count). KPIs do not hold references to the DataFrame — they return plain dicts.

3. **Filter → Charts:** Filtered DataFrames are passed to `build_charts()`, which constructs Plotly `go.Figure` objects. Figures are stateless — rebuilt on each rerun from current filtered data.

## Scaling Considerations

This project is a static dataset dashboard for a university assignment — scaling to many users is not a concern. The table below documents realistic limits for Streamlit Community Cloud as context.

| Scale | Architecture Adjustment |
|-------|-------------------------|
| 1 user (assignment demo) | No changes needed. Current architecture is correct. |
| ~10-50 concurrent (shared class link) | `@st.cache_data` handles this — all users share the same cached DataFrame. No changes needed. |
| 100k+ concurrent | Would require moving data load out of Streamlit entirely (pre-computed Parquet, external DB). Not relevant here. |

### Scaling Priorities (for reference only)

1. **First bottleneck:** CSV load time — already solved with `@st.cache_data`.
2. **Second bottleneck:** Plotly figure serialization on large DataFrames — solve by pre-aggregating before charting (always aggregate in `kpis.py`/`charts.py`, never pass raw 210K rows to Plotly).

## Anti-Patterns

### Anti-Pattern 1: Caching Filter Functions

**What people do:** Apply `@st.cache_data` to `apply_filters()` or `compute_kpis()` as well as the loader.

**Why it's wrong:** Filter functions take sidebar values as arguments and change on every interaction. Caching them adds overhead (cache key computation + serialization) with no benefit — they already run in milliseconds.

**Do this instead:** Cache only the I/O-bound loader. Let filter and KPI functions run uncached on every rerun.

### Anti-Pattern 2: Computing KPIs Inside Chart Functions

**What people do:** Build chart figures and compute KPI numbers in the same function, or compute aggregations inline in `app.py`.

**Why it's wrong:** Makes the layout file cluttered and makes KPI values unavailable for `st.metric()` display without re-running aggregations. Also makes unit testing impossible.

**Do this instead:** `kpis.py` computes all scalar KPIs and returns a dict. `charts.py` receives filtered DataFrames and builds figures. `app.py` only calls these and renders outputs.

### Anti-Pattern 3: No `layout="wide"` Configuration

**What people do:** Forget to set `layout="wide"` in `st.set_page_config()` or `config.toml`, then try to cram charts into the narrow center column.

**Why it's wrong:** Streamlit's default layout uses a narrow centered column. Charts shrink, KPI rows wrap, and the single-screen goal fails.

**Do this instead:** Set `layout = "wide"` in `.streamlit/config.toml` so it applies before any Python runs. Also call `st.set_page_config(layout="wide")` as the very first Streamlit command in `app.py`.

### Anti-Pattern 4: Committing `data/` CSVs Without Checking File Size Limits

**What people do:** Assume large CSVs will deploy to Streamlit Cloud without issue.

**Why it's wrong:** GitHub has a 100MB per-file limit and Streamlit Community Cloud mirrors the repo. The Netflix dataset (210K+ records, 6 tables) may exceed this depending on column count.

**Do this instead:** Check file sizes before committing (`ls -lh data/`). If any file exceeds 50MB, pre-filter to needed columns before saving. Alternatively, store data in a public Google Drive / Kaggle and download at runtime (adds startup latency but avoids size limits).

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Streamlit Community Cloud | Push to GitHub; connect repo in Streamlit Cloud UI; auto-deploys on push | Free tier; app sleeps after inactivity — first load after sleep takes ~30s |
| GitHub | Source of truth for all files | `.streamlit/secrets.toml` must be in `.gitignore`; no secrets needed for this project |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `app.py` → `data_loader.py` | Direct Python import; function call returns dict of DataFrames | DataFrames are the contract between layers |
| `app.py` → `filter.py` | Passes raw DataFrames + sidebar values; receives filtered DataFrames | Filter functions are pure — no side effects |
| `app.py` → `kpis.py` | Passes filtered DataFrames; receives `dict[str, float \| int \| str]` | KPIs are plain scalars — easy to display with `st.metric()` |
| `app.py` → `charts.py` | Passes filtered DataFrames; receives `dict[str, go.Figure]` | Figures rendered with `st.plotly_chart(fig, use_container_width=True)` |

## Suggested Build Order

Build in dependency order — each phase only uses components the previous phase established.

1. **Data layer first:** `data_loader.py` + verify all 6 CSVs load and merge correctly. This is the foundation everything else depends on.
2. **Filter layer second:** `filter.py` with sidebar widgets. Verify that filtering returns correct subsets before computing anything on top.
3. **KPI layer third:** `kpis.py` computing each metric. Validate values against raw data manually before displaying.
4. **Chart layer fourth:** `charts.py` building each Plotly figure. Each chart depends on filtered data being correct.
5. **Layout last:** `app.py` wiring all components into the column grid. Only assemble layout once all components return correct outputs.
6. **Deployment:** Add `requirements.txt`, `.streamlit/config.toml`, verify on Streamlit Cloud.

## Sources

- [Streamlit Caching Overview — Official Docs](https://docs.streamlit.io/develop/concepts/architecture/caching) — HIGH confidence
- [st.cache_data Reference](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data) — HIGH confidence
- [App Dependencies for Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — HIGH confidence
- [Secrets Management for Community Cloud](https://docs.streamlit.io/develop/concepts/connections/secrets-management) — HIGH confidence
- [Streamlit Best Practices for App Structure — Medium/Shintani](https://medium.com/@johnpascualkumar077/best-practices-for-developing-streamlit-applications-a-guide-to-efficient-and-maintainable-code-4ae279b6ea4e) — MEDIUM confidence
- [Streamlit + Plotly Dashboard Patterns — KDnuggets](https://www.kdnuggets.com/how-to-combine-streamlit-pandas-and-plotly-for-interactive-data-apps) — MEDIUM confidence
- [Building a Dashboard in Python with Streamlit — Streamlit Blog](https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/amp/) — MEDIUM confidence

---
*Architecture research for: Netflix Strategic Dashboard (Streamlit + Plotly, Streamlit Cloud)*
*Researched: 2026-03-22*
