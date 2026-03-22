# Project Research Summary

**Project:** Netflix Strategic Dashboard (university BI assignment)
**Domain:** Streamlit analytics dashboard — static Kaggle dataset, Streamlit Cloud deployment
**Researched:** 2026-03-22
**Confidence:** HIGH

## Executive Summary

This is a single-screen Streamlit BI dashboard for a university assignment analyzing the Kaggle "Netflix 2025 User Behavior Dataset" (210K records across 6 tables). Experts build this class of dashboard with a three-layer architecture: a cached data loader that reads CSVs once per session, a filtering layer that applies sidebar widget values to DataFrames via boolean masks, and a presentation layer that renders Plotly figures and st.metric KPI tiles in a column grid. The entire stack (Python 3.12, Streamlit 1.55.0, Plotly 6.6.0, pandas 2.3.3) is well-documented, version-stable as of the research date, and has no known compatibility conflicts.

The recommended approach is to build in strict dependency order: data loading and cleaning first, then filter logic, then KPI computation, then chart figures, and layout assembly last. This order is non-negotiable because every upstream layer is a contract for the next — building charts before validating that joins produce correct row counts leads to silently wrong KPI numbers, which is a graded deliverable failure. The assignment has hard constraints (3-7 KPIs, 3-6 chart types, 2-5 filters, single screen no scroll) that drive all feature decisions; every feature choice should be evaluated against these constraints before implementation.

The primary risks are operational, not architectural. Three pitfalls can kill the deliverable entirely: (1) not applying `@st.cache_data` to data loading causes 5-10 second freezes on every filter interaction; (2) loading 6 CSVs with default `object` dtype string columns can push the merged DataFrame over Streamlit Community Cloud's 1GB RAM limit; (3) GitHub's 100MB per-file limit may block deployment if CSVs are committed without checking size first. All three are trivially avoidable if addressed in Phase 1 (repository setup and data loading), but expensive to recover from if discovered at deployment time.

## Key Findings

### Recommended Stack

The stack is fully determined by the assignment constraints and platform. Streamlit 1.55.0 is the current stable release (March 3, 2026); Plotly 6.6.0 (March 2, 2026) integrates natively via `st.plotly_chart()`; pandas 2.3.3 is recommended over the newer 3.0.1 because pandas 3.0's Copy-on-Write semantics silently break chained assignment patterns and the migration risk is not justified for a deadline project. All three are confirmed compatible with Python 3.12 (Streamlit Cloud default).

Deployment uses Streamlit Community Cloud (free tier, zero-config for Streamlit apps, auto-deploys on GitHub push). The alternative Hugging Face Spaces is valid but adds Docker configuration that is unnecessary here.

**Core technologies:**
- Python 3.12: runtime — Streamlit Cloud default, avoid 3.13 (ecosystem less stable on Cloud)
- Streamlit 1.55.0: dashboard framework — `layout="wide"` for single-screen, `@st.cache_data` for performance
- Plotly 6.6.0: interactive charts — first-class Streamlit integration; use `px.*` (plotly.express) not `go.*` to minimize code
- pandas 2.3.3: data transformation — stable 2.x; avoid 3.0.1 (breaking CoW semantics on deadline)
- pip + requirements.txt: dependency pinning for Streamlit Cloud deployment
- Streamlit Community Cloud: free hosting, auto-deploys from GitHub

### Expected Features

The assignment requires 3-7 KPIs, 3-6 chart types, and 2-5 interactive filters on a single non-scrolling screen. Research identified 5 KPIs that cover all three required business pillars (engagement, recommendation effectiveness, retention) and are computable from the available dataset tables.

**Must have (table stakes — P1, required for assignment):**
- 5 KPI scorecards (Average Watch Time, MAU, Content Completion Rate, Recommendation CTR, Churn Rate) — graders check this box first
- Interactive sidebar filters: time period, genre, subscription type, device type — assignment requires 2-5
- Line chart: watch hours over time — trend visualization is expected in any BI dashboard
- Bar chart: top genres by watch time — categorical ranking is expected
- Netflix logo + dashboard title — explicitly required by assignment
- Alarm threshold coloring on KPI tiles (red/yellow/green) — assignment requires describing what triggers action

**Should have (differentiators — P2, raise grade):**
- Pie/donut chart: device type distribution — fills chart variety requirement with low effort
- Scatter plot: watch time vs. average rating — cross-table join; visually differentiating
- KPI delta indicators (prior period +/- %) — standard in professional dashboards; low implementation cost, high grader impression
- Recommendation effectiveness by genre chart — shows recommender insight beyond the CTR KPI

**Defer (P3 — skip given today's deadline):**
- Cohort retention heatmap — high complexity, requires pivot/bucketing; competes with chart slot budget
- Search-to-watch conversion rate — medium complexity join between search_logs and watch_history by time proximity
- Geographic filter or choropleth map — only valuable if users table has reliable region data; adds a chart slot at low analytical return

**Explicit anti-features to exclude:**
- Multi-page / tabbed layout — violates single-screen assignment constraint
- Predictive ML churn model — assignment scopes this out; use threshold-based definition instead
- Real-time data streaming — dataset is static; fake real-time adds complexity with zero benefit
- Custom CSS / animated transitions — fragile, time-expensive, and unnecessary given Plotly's built-in themes

### Architecture Approach

The architecture follows a strict three-layer pattern: data layer (`data_loader.py` with `@st.cache_data`), transform layer (`filter.py`, `kpis.py`, `charts.py` as pure functions), and presentation layer (`app.py` as layout orchestrator only). All 6 CSV files live in `data/` and are loaded once into a dict of clean DataFrames. Filter sidebar widgets in `app.py` emit values that flow into `filter.py`, which returns filtered DataFrames. These filtered DataFrames are passed to `kpis.py` (returns `dict[str, float]`) and `charts.py` (returns `dict[str, go.Figure]`). `app.py` renders outputs with `st.metric()` and `st.plotly_chart()` inside an `st.columns()` grid. Streamlit's re-execution model handles all reactivity — no callbacks or state management needed.

**Major components:**
1. `data_loader.py` — load, type-cast, and merge all 6 CSVs; wrapped in `@st.cache_data`; only function that touches disk
2. `filter.py` — pure function: takes raw DataFrames + sidebar values, returns filtered DataFrames via boolean masks; never cached
3. `kpis.py` — pure function: takes filtered DataFrames, returns dict of scalar KPI values; never cached
4. `charts.py` — pure function: takes filtered DataFrames, returns dict of Plotly Figure objects; never cached
5. `app.py` — layout orchestration only: sets page config, renders sidebar widgets, calls all modules, renders st.metric and st.plotly_chart in columns grid
6. `.streamlit/config.toml` — declares `layout = "wide"` and Netflix red theme (`#E50914`) declaratively

### Critical Pitfalls

1. **No `@st.cache_data` on data loading** — every filter interaction reloads and merges 6 CSVs, causing 5-10 second freezes. Wrap all `pd.read_csv()` and merge calls in a single `@st.cache_data` function before writing any other code.
2. **Streamlit Cloud 1GB memory limit exceeded** — default `object` dtype string columns across 6 merged tables can exceed 400MB. Cast all categorical string columns (genre, subscription_type, device_type) to pandas `category` dtype immediately after loading. Verify with `df.info(memory_usage='deep')` before deploying.
3. **GitHub rejects large CSV files** — individual files >100MB block git push entirely; >50MB triggers warnings. Run `ls -lh data/` before the first `git add` on dataset files; convert oversized files to Parquet (5-10x smaller).
4. **Synthetic dataset join keys do not match across tables** — the dataset has documented 10-20% missing values and 3-6% duplicate records; join keys may not be referentially consistent. Validate key cardinality before merging (`watch_history["user_id"].isin(users["user_id"]).mean() > 0.95`) and log row counts before and after every merge to detect silent drops.
5. **Single-screen layout overflows into scroll** — Streamlit defaults to vertical stacking. Set `layout="wide"` in both `.streamlit/config.toml` and `st.set_page_config()` before writing any chart code, and design the column grid layout first. Test at 1080p with browser at 100% zoom.

## Implications for Roadmap

Based on the research, the natural build order follows strict architectural dependencies. Each phase produces a contract that the next phase depends on. Skipping or reordering phases causes rework.

### Phase 1: Repository and Data Foundation

**Rationale:** Everything else depends on data loading being correct and deployment being unblocked. GitHub file size limits and memory limits must be validated before a single line of dashboard code is written, or they become late-stage blockers.
**Delivers:** Working `data_loader.py` with all 6 CSVs loading, cleaned, type-cast, and merged correctly; validated join key cardinality; memory footprint confirmed under 200MB; all files committed and Streamlit Cloud deployment pipeline unblocked.
**Addresses:** Average Watch Time, MAU, Churn Rate, Recommendation CTR KPIs (computable only after data is clean and joins are validated)
**Avoids:** Pitfalls 1 (no caching), 2 (memory limit), 3 (GitHub file size), 4 (join key mismatches)
**Research flag:** No additional research needed — patterns are well-documented and stack is confirmed.

### Phase 2: Layout Skeleton and Filter Wiring

**Rationale:** The single-screen constraint is a hard grading requirement that fails if the layout is retrofitted after charts are built. Design the column grid first (before any chart code exists) so chart placement is intentional, not accidental.
**Delivers:** Working `app.py` with `layout="wide"`, sidebar filter widgets (time period, genre, subscription type, device type) wired to `filter.py`, column grid structure defined, Netflix logo and dashboard title in place. No KPIs or charts yet — just the skeleton.
**Uses:** Streamlit 1.55.0 sidebar widgets, `st.columns()`, `.streamlit/config.toml` Netflix theme
**Implements:** Presentation layer structure + filter layer (filter.py)
**Avoids:** Pitfall 5 (layout overflow), UX pitfall (missing logo, missing "All" default on filters)
**Research flag:** No additional research needed — standard Streamlit patterns.

### Phase 3: KPI Computation

**Rationale:** KPIs depend on filtered DataFrames being correct (Phase 2) and data being clean (Phase 1). Computing KPIs before charts ensures scalar values are validated against raw data before being visualized.
**Delivers:** Working `kpis.py` returning all 5 KPI values (Average Watch Time, MAU, Content Completion Rate, Recommendation CTR, Churn Rate) with alarm threshold coloring (red/yellow/green) and delta indicators (+/- % vs. prior period) rendered as `st.metric()` tiles in the KPI row.
**Addresses:** Covers all three business pillars required by the assignment (engagement, recommendation, retention). KPI delta badges are P2 but low-cost enough to include in this phase.
**Avoids:** UX pitfall (too many KPIs, unclear thresholds), anti-pattern (computing KPIs inside chart functions)
**Research flag:** No additional research needed — formulas are defined in FEATURES.md; Churn Rate definition needs a documented choice (threshold-based: inactive 30 days OR subscription_status == 'cancelled').

### Phase 4: Chart Implementation

**Rationale:** Charts are the most time-consuming phase. Build them after KPIs are validated so chart aggregations can be cross-checked against known KPI numbers. All chart data flows from the same filtered DataFrames as KPIs.
**Delivers:** Working `charts.py` with 4 chart types: (1) line chart — watch hours over time, (2) horizontal bar — top genres by watch time, (3) pie/donut — device type distribution, (4) scatter — watch time vs. average rating. All charts use `use_container_width=True` and fit within the column grid.
**Addresses:** Meets 3-6 chart type requirement with visible variety; P2 scatter and donut charts included because implementation cost is LOW.
**Avoids:** Pitfall 6 (Plotly re-renders slowly — ensure aggregations happen in charts.py, not inline in app.py), anti-pattern (caching filter functions), anti-pattern (using go.* instead of px.*)
**Research flag:** No additional research needed — all chart types are standard Plotly Express patterns.

### Phase 5: Integration, Verification, and Deployment

**Rationale:** Final integration and deployment must be verified on Streamlit Cloud (not localhost) because the Word deliverable requires a screenshot of the deployed URL. Local testing does not catch Cloud-specific issues (memory limits, path resolution for assets).
**Delivers:** App deployed to Streamlit Cloud at a public URL; Word deliverable screenshot taken from deployed URL; all assignment checklist items verified (KPI count 3-7, chart count 3-6, filter count 2-5, single screen no scroll, logo present, alarm thresholds documented, public link accessible without login, requirements.txt complete).
**Avoids:** Missing requirement pitfalls (logo absent, alarm thresholds not visible, app requires login, localhost screenshot in Word file)
**Research flag:** No additional research needed — deployment steps are documented in ARCHITECTURE.md and STACK.md.

### Phase Ordering Rationale

- Data must precede everything because join validation determines which KPIs are feasible and whether any data preparation steps (Parquet conversion, column pruning) are needed before deployment.
- Layout must precede charts because the column grid structure dictates how many chart slots exist and at what widths — building charts first and then fitting them into a grid causes resizing rework.
- KPIs must precede charts because scalar KPI values provide ground-truth reference numbers; chart aggregations should produce consistent results with KPI computations on the same filtered data.
- Deployment is last but must happen before submission — Streamlit Cloud's first-load behavior (app sleeps after inactivity, ~30s wake) must be accounted for in the demo plan.

### Research Flags

Phases with standard patterns (no additional research-phase needed):
- **Phase 1:** `@st.cache_data`, `pd.read_csv`, `astype("category")` — all standard, well-documented patterns
- **Phase 2:** `st.columns()`, sidebar widgets, `layout="wide"` — official Streamlit docs cover this completely
- **Phase 3:** `st.metric()`, pandas groupby/count/mean — standard patterns; KPI formulas defined in FEATURES.md
- **Phase 4:** `plotly.express` px.line, px.bar, px.pie, px.scatter — all standard patterns in official Plotly docs
- **Phase 5:** Streamlit Cloud deployment — zero-config via GitHub connect; steps documented in official docs

No phase requires `/gsd:research-phase` — this is a well-understood domain with verified stack and established patterns. The only area requiring a design decision (not research) is the operational definition of Churn Rate, which must be chosen and documented before Phase 3.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified against PyPI on 2026-03-22; compatibility confirmed via official Streamlit docs |
| Features | HIGH | Assignment constraints are explicit and non-negotiable; KPI formulas verified against OTT analytics domain sources |
| Architecture | HIGH | Patterns verified against official Streamlit docs; three-layer structure is the Streamlit-team-recommended pattern for apps beyond trivial examples |
| Pitfalls | HIGH | Critical pitfalls verified against official Streamlit docs, official blog, and confirmed GitHub issues; dataset quality issues documented by dataset creator on Kaggle |

**Overall confidence:** HIGH

### Gaps to Address

- **Churn Rate operational definition:** Must choose between "inactive N days" vs. `subscription_status == 'cancelled'` before implementing Phase 3. The choice affects which column is used and must be documented in the Word deliverable. Resolution: inspect the `users.csv` schema in Phase 1 and pick the definition supported by available columns.
- **Kaggle dataset individual file sizes:** Estimated under GitHub's limits based on row counts (10K users, 105K watch_history) but not verified. Resolution: check `ls -lh data/` immediately after downloading in Phase 1 before any `git add`.
- **recommendation_logs join quality:** Documented as a risky table (synthetic data may have poor join key coverage). Resolution: validate with `isin()` cardinality check in Phase 1; if join coverage is below 80%, Recommendation CTR KPI must be dropped or approximated from available columns.
- **Streamlit Cloud Python version pinning:** Streamlit Cloud defaults to Python 3.12 but this should be confirmed by adding a `runtime.txt` file (`python-3.12`) to the repo root in Phase 1 to avoid surprises.

## Sources

### Primary (HIGH confidence)
- [Streamlit 1.55.0 on PyPI](https://pypi.org/project/streamlit/) — version verification
- [Plotly 6.6.0 on PyPI](https://pypi.org/project/plotly/) — version verification
- [Streamlit Caching Overview — Official Docs](https://docs.streamlit.io/develop/concepts/architecture/caching) — caching patterns
- [st.cache_data Reference](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data) — caching API
- [Streamlit Resource Limits](https://docs.streamlit.io/knowledge-base/deploy/resource-limits) — 1GB memory limit
- [Streamlit App Dependencies for Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — Python 3.12 default, requirements.txt
- [pandas 3.0 CoW migration guide — Real Python, February 2026](https://realpython.com/python-news-february-2026/) — breaking change rationale for sticking with pandas 2.3.3
- [Kaggle: Netflix 2025 User Behavior Dataset](https://www.kaggle.com/datasets/sayeeduddin/netflix-2025user-behavior-dataset-210k-records) — dataset schema, known quality issues

### Secondary (MEDIUM confidence)
- [Streamlit Best Practices for App Structure — Medium/Shintani](https://medium.com/@johnpascualkumar077/best-practices-for-developing-streamlit-applications-a-guide-to-efficient-and-maintainable-code-4ae279b6ea4e) — three-layer architecture pattern
- [OTT Platform Analytics: 15 KPIs — MwareTV](https://mwaretv.com/en/blog/ott-platform-analytics-guide) — KPI domain validation
- [Measuring Netflix Recommendation Engine — PM Exercises](https://www.productmanagementexercises.com/4092/how-would-you-measure-success-netflix-recommendation-engine) — Recommendation CTR rationale
- [BI Dashboard Design Best Practices 2025 — Julius AI](https://julius.ai/articles/business-intelligence-dashboard-design-best-practices) — layout and KPI tile patterns
- [Streamlit Plotly Performance Issues Despite Caching — Community Forum](https://discuss.streamlit.io/t/plotly-performance-issues-despite-caching/110491) — Pitfall 6 pattern

### Tertiary (LOW confidence — corroborated by higher-confidence sources)
- WebSearch: streamlit plotly dashboard best practices 2025 — layout patterns, corroborated by official Streamlit docs

---
*Research completed: 2026-03-22*
*Ready for roadmap: yes*
