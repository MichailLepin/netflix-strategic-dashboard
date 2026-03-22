# Pitfalls Research

**Domain:** Streamlit BI Dashboard — Netflix dataset, university assignment, Streamlit Cloud deployment
**Researched:** 2026-03-22
**Confidence:** HIGH (Streamlit-specific issues verified via official docs and community forum; dataset issues verified via Kaggle dataset page)

---

## Critical Pitfalls

### Pitfall 1: 210K-Row CSV Loaded Raw on Every Rerun Kills Performance

**What goes wrong:**
Streamlit reruns the entire script on every widget interaction. Without caching, loading and merging 6 CSVs totaling 210K+ rows happens on every filter change — turning each selectbox interaction into a 5-10 second freeze.

**Why it happens:**
New Streamlit users treat it like a script, not an app. They call `pd.read_csv()` at the top of the file without `@st.cache_data`, not realizing the entire file executes from top to bottom on every widget event.

**How to avoid:**
Wrap ALL data loading and expensive joins in `@st.cache_data`. The loading function should return the fully merged and pre-cleaned DataFrame once, then every filter just slices the cached result. Structure:
```python
@st.cache_data
def load_data():
    users = pd.read_csv("users.csv")
    watch = pd.read_csv("watch_history.csv")
    # ... merge, clean, type-cast
    return merged_df

df = load_data()  # cached after first run
filtered = df[df["genre"] == selected_genre]  # fast slice
```

**Warning signs:**
- Dashboard takes >3 seconds to respond to a filter change
- CPU spikes on every widget interaction in browser dev tools
- No `@st.cache_data` decorator visible in the code

**Phase to address:** Data preparation / data loading phase (first coding phase)

---

### Pitfall 2: Streamlit Cloud 1GB Memory Limit Crashes the App

**What goes wrong:**
Streamlit Community Cloud hard-limits apps to ~1GB RAM. A 210K-row multi-table dataset loaded naively as Python objects with object-dtype columns can consume 300-600MB. Add Plotly figure objects, cached DataFrame copies, and the app crashes mid-demo with "This app has gone over its resource limits."

**Why it happens:**
Pandas defaults to `object` dtype for string columns, which is memory-inefficient. Six merged tables with string columns (genre, country, device, subscription_type) balloon memory. Each cached DataFrame copy also adds overhead.

**How to avoid:**
- Cast string columns to `category` dtype immediately after loading — reduces memory by 50-70%
- Cast integer columns to `int32` or `int16` where values fit
- For the dataset's join: merge only needed columns, not all 6 tables fully
- Use `st.cache_resource` instead of `st.cache_data` for the base DataFrame if mutating is not needed (avoids serialization copy overhead)
- Test memory locally with `df.info(memory_usage='deep')` before deploying

```python
df["genre"] = df["genre"].astype("category")
df["subscription_type"] = df["subscription_type"].astype("category")
df["device_type"] = df["device_type"].astype("category")
```

**Warning signs:**
- `df.info(memory_usage='deep')` shows >200MB for the merged DataFrame
- App works locally but crashes 30-60 seconds after deploying to Streamlit Cloud
- "Oh no. Error running app" / resource limit message on Cloud

**Phase to address:** Data preparation phase (optimize before deploying, not after)

---

### Pitfall 3: GitHub Rejects Large CSV Files, Blocking Deployment

**What goes wrong:**
GitHub's file size soft limit is 50MB (warning) and hard limit is 100MB per file. A 210K-row CSV can be 30-80MB+ depending on column count. Pushing raw CSVs to GitHub blocks the Streamlit Cloud deployment pipeline entirely — git push fails, or the repo is rejected at clone time.

**Why it happens:**
Students download Kaggle CSVs and commit them directly to the repo without checking file sizes. The error only surfaces at `git push`, often 30 minutes into deployment.

**How to avoid:**
- Check file sizes before committing: `ls -lh data/`
- If files are >50MB: convert to Parquet format (typically 5-10x smaller than CSV) before committing
- Alternative: Use `.gitignore` to exclude raw CSVs and load from Kaggle API or a public URL at startup (adds complexity — avoid for deadline work)
- The Kaggle dataset has ~210K total rows across 6 tables. Individual files (users.csv: 10K rows, watch_history.csv: 105K rows) are likely under 100MB — but verify before assuming

**Warning signs:**
- `git push` returns "this exceeds GitHub's file size limit"
- Individual CSV is larger than 50MB when checked with `ls -lh`
- Deployment build log shows "fatal: repository not found" or clone failure

**Phase to address:** Repository setup phase, before first commit of data files

---

### Pitfall 4: Synthetic Dataset Join Keys Don't Actually Join Cleanly

**What goes wrong:**
The dataset documentation confirms 10-20% missing values and 3-6% duplicate records. Join keys (`user_id`, `movie_id`) across tables may not be referentially consistent in a synthetic dataset — watch_history rows may reference user_ids that don't exist in users.csv, or vice versa. A naive `pd.merge()` silently drops rows (inner join) or creates NaN-filled rows (outer join) without warning, producing charts that misrepresent the data.

**Why it happens:**
Synthetic data generators often create each table independently and don't enforce strict foreign-key constraints. Students assume the multi-table dataset is normalized when it isn't.

**How to avoid:**
- Before merging, validate join key cardinality:
```python
assert watch_history["user_id"].isin(users["user_id"]).mean() > 0.95, "High orphan rate!"
print(f"Unmatched user_ids in watch_history: {(~watch_history['user_id'].isin(users['user_id'])).sum()}")
```
- Use `how="inner"` intentionally and log the row count before/after to detect silent drops
- Check for duplicate user_ids in the users table before using as join anchor
- Document the join loss rate in the Word deliverable data preparation notes

**Warning signs:**
- Row count after merge is significantly lower than the smaller table's row count
- KPI numbers seem implausibly low or high after joining
- NaN columns appear in merged DataFrame where they shouldn't exist

**Phase to address:** Data cleaning / EDA phase

---

### Pitfall 5: Single-Screen Layout Overflows and Requires Scrolling

**What goes wrong:**
The assignment requires a single-screen dashboard with no scrolling. Streamlit's default layout stacks everything vertically. Adding 3-6 charts plus 2-5 filter widgets without explicit column layout produces a page that requires significant scrolling — failing the assignment constraint directly.

**Why it happens:**
Streamlit defaults to vertical stacking. Developers build charts one by one and assume layout can be fixed "at the end," but retrofitting column layouts after charts are built requires restructuring the entire script.

**How to avoid:**
- Design the grid layout FIRST before writing any chart code
- Use `st.columns()` for side-by-side charts from the start
- For a single-screen strategic dashboard: filter row at top, then a 3-column KPI metric row, then a 2-column chart row, then a full-width chart at bottom
- Set `page_title` and `layout="wide"` in `st.set_page_config()` immediately:
```python
st.set_page_config(page_title="Netflix Dashboard", layout="wide")
```
- Test at 1080p resolution (standard laptop screen) with browser at 100% zoom

**Warning signs:**
- Scrollbar appears on the right side of the browser
- Charts are displayed one per full-width row
- `layout="wide"` is not set in `st.set_page_config()`

**Phase to address:** Dashboard layout / UI structure phase (before charts are built)

---

### Pitfall 6: Plotly Charts Re-Render Slowly on Every Filter Change

**What goes wrong:**
Combining Plotly with Streamlit filter widgets (selectbox, multiselect, date range) causes full chart re-renders on every interaction. With 210K rows, even a simple bar chart aggregation on an unoptimized DataFrame takes 2-4 seconds per filter change, making the dashboard feel broken.

**Why it happens:**
The chart-generation code is inside the main script body, so it re-executes on every rerun. The data aggregation (groupby, pivot, merge) happens fresh each time because it's not cached separately from the raw data load.

**How to avoid:**
- Cache the data loading separately from chart generation
- Pre-aggregate data in the loading/cleaning phase where possible (compute common groupby aggregations upfront)
- Cache filter-dependent aggregations with `@st.cache_data` that takes filter values as arguments:
```python
@st.cache_data
def get_genre_engagement(df_hash, genre):
    return df[df["genre"] == genre].groupby("month")["watch_time"].mean()
```
- Avoid passing full DataFrames to cached functions (use a hash or subset)

**Warning signs:**
- 2+ second delay between filter selection and chart update
- CPU maxes out during filter interaction
- Chart code includes `groupby()` or `merge()` calls outside of cached functions

**Phase to address:** Chart implementation phase

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Load all 6 CSVs fully, merge everything | Simpler code | Memory bloat, possible Cloud limit hit | Never — this is a single-day project, optimize upfront |
| Keep string columns as `object` dtype | No extra code | 2-3x memory overhead | Never — `astype("category")` is a one-liner |
| Use `st.cache_data` without TTL | Data stays fresh | Cache grows unbounded on Cloud | Acceptable for static dataset with no updates |
| Skip join validation, trust the dataset | Faster to build | KPIs silently wrong, word deliverable inaccurate | Never for graded work |
| Build full-width layout, fix at end | Charts built faster | Single-screen constraint fails | Never — layout must come first |
| Hard-code filter options instead of reading from data | Simpler code | Breaks if dataset has unexpected values | Acceptable for MVP with known controlled dataset |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Streamlit Cloud + GitHub | Commit raw CSVs without checking size | Check `ls -lh data/` before `git add`; convert oversized files to Parquet |
| Streamlit Cloud + requirements.txt | Include built-in Python libs (os, math) or exclude third-party libs | Only list non-stdlib packages: `streamlit`, `pandas`, `plotly`, `openpyxl` |
| Streamlit Cloud + Python version | Develop on Python 3.12, Cloud defaults to older | Pin Python version in `.python-version` or `runtime.txt` file |
| Kaggle dataset download | Manually download and commit CSVs | Acceptable for single-assignment; verify file sizes before commit |
| Plotly + Streamlit | Use `st.plotly_chart(fig)` without `use_container_width=True` | Always pass `use_container_width=True` to fill column width |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| No `@st.cache_data` on data load | Every filter causes full CSV reload | Add decorator to all `pd.read_csv()` + merge functions | Immediately — first filter interaction |
| `object` dtype string columns in 210K row merge | Memory >400MB, Cloud crash | `astype("category")` on all categorical columns | At Cloud deployment |
| Groupby inside main script body (not cached) | 2-4s per filter change | Move aggregations into cached functions or pre-compute | At first user interaction |
| Displaying raw `st.dataframe(df)` with all 210K rows | Browser freezes, tab crash | Show aggregated summaries, not raw data; limit to `df.head(100)` if table needed | Immediately on page load |
| Multiple `st.columns()` nested inside loops | Layout breaks at certain screen widths | Define column structure once at the top level | At different screen resolutions |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Too many KPIs (>7) on a single screen | Visual overload, grader can't identify focus | Limit to 3-5 KPIs shown as `st.metric()` tiles in a single row |
| Unclear chart titles ("Chart 1", "Chart 2") | Grader doesn't understand what business question is answered | Every chart gets a specific title: "Average Watch Time by Genre (Last 30 Days)" |
| No alarm thresholds visible | Assignment requires alarm descriptions — missing = lost marks | Add annotation lines or colored zones on KPI charts showing the threshold |
| Filters with no "All" default option | Dashboard loads with no data if default filter value doesn't exist in dataset | Always include "All" as first option in selectbox: `["All"] + sorted(df["genre"].unique().tolist())` |
| Company logo absent or wrong size | Fails assignment layout requirement (must include logo) | Add Netflix logo at top using `st.image()` with controlled width parameter |

---

## "Looks Done But Isn't" Checklist

- [ ] **Caching:** Every `pd.read_csv()` and merge call is inside a `@st.cache_data` function — verify no CSV load in main script body
- [ ] **Memory:** `df.info(memory_usage='deep')` shows <200MB for the merged DataFrame before deploying
- [ ] **Single screen:** At 1080p resolution, no vertical scrollbar appears — verify by resizing browser
- [ ] **Filters:** All selectbox/multiselect widgets have an "All" option as default — verify first load shows all data
- [ ] **Alarm description:** Each KPI has a documented threshold visible on the dashboard or in the Word doc — verify against assignment rubric
- [ ] **Word deliverable:** Screenshot of deployed app (not localhost) is in the Word file — verify URL in screenshot shows Streamlit Cloud domain
- [ ] **Public link:** App is accessible without login — verify in incognito/private browser window
- [ ] **Logo:** Netflix logo is displayed — verify it renders on Streamlit Cloud (not just localhost, as local paths break)
- [ ] **requirements.txt:** All non-stdlib dependencies are listed — verify by deploying to a fresh branch/environment
- [ ] **KPI count:** Between 3 and 7 KPIs are defined — verify against assignment constraint

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| App crashes on Cloud (memory limit) | MEDIUM | Add `astype("category")` to all string columns; restart app via Cloud dashboard; re-deploy |
| GitHub rejects large file | LOW | Remove file from git history with `git rm --cached data/large.csv`; convert to Parquet; re-add |
| Dashboard scrolls (not single-screen) | LOW | Wrap all charts in `st.columns()` layout; set `layout="wide"` in `set_page_config()` |
| Charts slow on filter change | MEDIUM | Move all aggregations into `@st.cache_data` functions with filter params as arguments |
| Join produces wrong KPI numbers | HIGH | Re-validate all join keys; check merge row counts; re-examine which join type is correct |
| Deployment fails (requirements error) | LOW | Check Streamlit Cloud build logs; add missing package to requirements.txt; redeploy |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| No caching — slow on every rerun | Phase 1: Data loading setup | Run app, change a filter, confirm response <1 second |
| Memory limit exceeded on Cloud | Phase 1: Data loading setup | `df.info(memory_usage='deep')` shows <200MB |
| GitHub file size limit | Phase 0: Repo setup | `ls -lh data/` confirms all files <50MB |
| Synthetic dataset join key issues | Phase 2: Data cleaning/EDA | Print row counts before and after every merge |
| Single-screen layout overflows | Phase 3: Dashboard layout design | No scrollbar at 1080p before any chart is added |
| Plotly re-renders slowly on filter | Phase 4: Chart implementation | Each filter interaction responds in <1 second |
| Missing assignment requirements | Phase 5: Final checklist | Walk through "Looks Done But Isn't" checklist above |

---

## Sources

- [Streamlit FAQ: Large Data Performance](https://discuss.streamlit.io/t/faq-how-to-improve-performance-of-apps-with-large-data/64007) — HIGH confidence (official Streamlit forum FAQ)
- [Streamlit Docs: Caching Overview](https://docs.streamlit.io/develop/concepts/architecture/caching) — HIGH confidence (official docs)
- [Streamlit Docs: Resource Limits](https://docs.streamlit.io/knowledge-base/deploy/resource-limits) — HIGH confidence (official docs, confirms 1GB limit)
- [Streamlit Blog: Common App Problems — Resource Limits](https://blog.streamlit.io/common-app-problems-resource-limits/) — HIGH confidence (official Streamlit blog)
- [Streamlit Docs: App Dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — HIGH confidence (official docs)
- [Streamlit FAQ: Large Files in Streamlit Apps](https://discuss.streamlit.io/t/faq-how-to-use-large-files-in-your-streamlit-app/64621) — HIGH confidence (official Streamlit forum FAQ)
- [Streamlit: st.selectbox session state bug (Dec 2025)](https://github.com/streamlit/streamlit/issues/13435) — HIGH confidence (confirmed GitHub issue)
- [Kaggle: Netflix 2025 User Behavior Dataset](https://www.kaggle.com/datasets/sayeeduddin/netflix-2025user-behavior-dataset-210k-records) — HIGH confidence (primary dataset, intentional quality issues documented by creator)
- [Perceptual Edge: Common Pitfalls in Dashboard Design](https://www.perceptualedge.com/articles/Whitepapers/Common_Pitfalls.pdf) — MEDIUM confidence (authoritative BI design reference)
- [Streamlit Plotly Performance Issues Despite Caching](https://discuss.streamlit.io/t/plotly-performance-issues-despite-caching/110491) — MEDIUM confidence (community forum, verified pattern)

---
*Pitfalls research for: Streamlit Netflix BI Dashboard (university assignment)*
*Researched: 2026-03-22*
