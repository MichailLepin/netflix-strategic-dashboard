# Stack Research

**Domain:** Streamlit analytics dashboard (BI assignment, static dataset)
**Researched:** 2026-03-22
**Confidence:** HIGH — versions verified against PyPI on research date

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12 | Runtime | Streamlit Cloud default; avoid 3.13 (newer ecosystem, less stable on Cloud) |
| Streamlit | 1.55.0 | Dashboard framework | Current stable (March 3, 2026 release); `st.set_page_config(layout="wide")` enables full-width single-screen layout; `@st.cache_data` prevents re-running data loading on every widget interaction |
| Plotly | 6.6.0 | Interactive charts | Current stable (March 2, 2026); first-class Streamlit integration via `st.plotly_chart(fig, use_container_width=True)`; produces rich HTML charts with hover, zoom, legend toggle — mandatory for an interactive dashboard |
| pandas | 2.3.3 | Data loading and transformation | Last stable 2.x release (September 2025); safe for this project — pandas 3.0.1 (Jan 2026) has breaking Copy-on-Write semantics and new string dtype that can silently break existing data pipelines; use 2.3.3 to avoid migration risk on a deadline |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| plotly-express (bundled with plotly) | 6.6.0 | High-level chart API | Use `px.bar`, `px.line`, `px.scatter`, `px.pie` for fast chart creation — fewer lines than `go.*` constructors, same output quality |
| numpy | 2.x (pinned by pandas) | Numerical operations | Needed transitively by pandas; don't pin explicitly — let pandas pull the compatible version |
| kagglehub | latest | Dataset download from Kaggle | Use `kagglehub.dataset_download()` to pull the Netflix 2025 dataset programmatically; alternative is manual CSV download and commit to repo |
| openpyxl | 3.x | Excel file reading | Only needed if the Kaggle dataset ships as `.xlsx` files; pandas uses it as the engine for `pd.read_excel()` |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pip + requirements.txt | Dependency declaration for Streamlit Cloud | Streamlit Cloud reads `requirements.txt` at deploy time; pin major+minor versions (e.g., `streamlit==1.55.0`) to prevent surprise upgrades |
| Streamlit Community Cloud | Free public hosting | Connects to a public GitHub repo; deploys automatically on push; provides a public URL — required for the assignment deliverable |
| VS Code with Python extension | Local development | Run `streamlit run app.py` locally; hot-reloads on file save |

## Installation

```bash
# Core dashboard stack
pip install streamlit==1.55.0 plotly==6.6.0 pandas==2.3.3

# Optional: programmatic Kaggle download
pip install kagglehub

# Optional: only if dataset contains .xlsx files
pip install openpyxl
```

**requirements.txt for Streamlit Cloud:**
```
streamlit==1.55.0
plotly==6.6.0
pandas==2.3.3
# kagglehub  # add if using programmatic download
# openpyxl   # add if loading .xlsx files
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Plotly 6.6.0 | Altair / Vega-Lite | If you need grammar-of-graphics declarative syntax and the team knows Vega-Altair; Plotly is better here because the assignment stack is already decided and Plotly has broader chart type coverage |
| Plotly 6.6.0 | Matplotlib / Seaborn | Never for this project — Matplotlib produces static images; Plotly produces interactive HTML; interactive filters require interactive charts |
| Streamlit | Dash (plotly) | If you need full custom layout control, multi-page apps with URL routing, or production enterprise deployment; overkill for a single-screen BI assignment |
| Streamlit | Gradio | Gradio is optimized for ML model demos, not analytics dashboards; wrong domain |
| pandas 2.3.3 | pandas 3.0.1 | Use 3.0 on new projects without legacy code; avoid here because CoW semantics can silently break chained assignment patterns on a tight deadline |
| Streamlit Cloud | Hugging Face Spaces | Valid alternative for free hosting; Streamlit Cloud is simpler and native — no Docker config needed |
| Streamlit Cloud | Heroku / Render | Fine but require more config (Procfile, buildpacks); Streamlit Cloud is zero-config for Streamlit apps |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `st.cache_resource` for DataFrames | Designed for shared global resources (DB connections, ML models); mutating cached DataFrames across sessions causes bugs | `@st.cache_data` — copies data per session, safe for DataFrames |
| `@st.experimental_memo` / `@st.experimental_singleton` | Removed in Streamlit 1.18+; legacy decorators from pre-1.x | `@st.cache_data` and `@st.cache_resource` respectively |
| pandas 3.0.1 | Released January 2026 with breaking Copy-on-Write (CoW) semantics — chained assignment (`df[col][mask] = val`) silently fails; new string dtype changes dtype equality checks | pandas 2.3.3 — stable, no breaking changes for typical dashboard code |
| `plotly.graph_objects` (go.*) for all charts | Verbose; 3-5x more code than `plotly.express` for standard charts | `plotly.express` (px.*) for standard charts; only drop to `go.*` for custom traces or subplots |
| Bokeh | Streamlit's native Bokeh support was dropped; requires a third-party component (`streamlit-bokeh`) — added complexity | Plotly — natively supported via `st.plotly_chart()` |
| Streamlit multipage app structure | The assignment requires a single-screen dashboard; `st.navigation` / `st.Page` adds routing overhead | Single `app.py` with `st.set_page_config(layout="wide")` and `st.columns()` for layout |

## Stack Patterns by Variant

**For the assignment (single-screen, static dataset, deploy today):**
- One `app.py` file
- Load and cache data at top with `@st.cache_data`
- `st.set_page_config(layout="wide", page_title="Netflix Dashboard")`
- Sidebar for all filters (`st.sidebar.selectbox`, `st.sidebar.multiselect`, `st.sidebar.date_input`)
- Main area split with `st.columns([1,1,1])` for KPI metrics and charts
- `st.plotly_chart(fig, use_container_width=True)` on every chart

**If the dataset is too large to load in memory (>500MB):**
- Pre-aggregate the 6 CSV tables into a single summary parquet with a one-time script
- Load the parquet in the dashboard — pandas `read_parquet` is 5-10x faster than `read_csv` for repeated loads

**If deployment to Streamlit Cloud fails due to dependency conflicts:**
- Drop explicit pinning from requirements.txt (let Cloud resolve) then re-add one pin at a time
- The most common conflict is numpy version incompatible with the pinned pandas version

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| streamlit==1.55.0 | plotly>=5.0, pandas>=1.3 | No known conflicts with plotly 6.6.0 or pandas 2.3.3 |
| pandas==2.3.3 | numpy>=1.26.4, <3 | Streamlit Cloud Python 3.12 satisfies these; do not use pandas 3.0+ on this project |
| plotly==6.6.0 | Python>=3.8 | Fully compatible with Python 3.12 and streamlit 1.55.0 |
| Python 3.12 | All above packages | Streamlit Cloud default; use the same version locally |

## Sources

- [streamlit 1.55.0 on PyPI](https://pypi.org/project/streamlit/) — version verified March 22, 2026 (HIGH confidence)
- [plotly 6.6.0 on PyPI](https://pypi.org/project/plotly/) — version verified March 22, 2026 (HIGH confidence)
- [pandas 2.3.3 / 3.0.1 release notes](https://pandas.pydata.org/docs/whatsnew/index.html) — breaking changes in 3.0 verified (HIGH confidence)
- [Streamlit 2025 release notes](https://docs.streamlit.io/develop/quick-reference/release-notes/2025) — feature verification (HIGH confidence)
- [Streamlit Community Cloud deployment docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — Python 3.12 default confirmed (HIGH confidence)
- [WebSearch: streamlit plotly dashboard best practices 2025] — layout patterns and caching recommendations (MEDIUM confidence — corroborated by official Streamlit docs)
- [pandas 3.0 CoW migration guide — Real Python, February 2026](https://realpython.com/python-news-february-2026/) — breaking changes rationale (HIGH confidence)

---
*Stack research for: Netflix Strategic Dashboard (Streamlit + Plotly, BI assignment)*
*Researched: 2026-03-22*
