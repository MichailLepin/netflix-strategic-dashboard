# Phase 1: Data Foundation - Research

**Researched:** 2026-03-22
**Domain:** pandas data loading, cleaning, type optimization, and multi-table joining for a 6-table synthetic CSV dataset
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DATA-01 | Download and load Netflix 2025 User Behavior Dataset (6 tables) | Standard pandas read_csv patterns; file-size check before git commit; @st.cache_data wrapping |
| DATA-02 | Clean data (handle missing values, duplicates, outliers) | Cleaning pipeline: dropna/fillna strategy per column role, drop_duplicates on user_id/movie_id, outlier capping |
| DATA-03 | Join tables with validated keys | pd.merge with indicator=True + isin() pre-validation; log row counts before/after every merge |
</phase_requirements>

---

## Summary

Phase 1 produces `src/data_loader.py` — a single cached function that loads all 6 CSV files, cleans them, and returns a dict of clean DataFrames ready for downstream filtering, KPI, and chart code. The caller never touches raw CSVs; it always gets clean, correctly typed data.

The dataset is synthetic (210K+ records across 6 tables) with intentional quality problems: 10-20% missing values, 3-6% duplicate records, and outliers in numeric columns. The two join keys are `user_id` (links users, watch_history, recommendation_logs, search_logs, reviews) and `movie_id` (links movies and watch_history). Referential integrity is NOT guaranteed in synthetic data, so join validation is mandatory before trusting KPI numbers.

The critical constraint for this phase is that the data loader must be wrapped in `@st.cache_data` so Streamlit does not reload 6 CSVs on every widget interaction. Memory optimization via `category` dtype and narrow integer types must also happen here — before any downstream code relies on the column types — to stay under Streamlit Cloud's 1GB RAM limit.

**Primary recommendation:** Build `src/data_loader.py` with one `@st.cache_data` function that loads, cleans, validates joins, and returns a stable dict of DataFrames. All type casting and cleaning happens inside this function, never outside it.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | 2.3.3 | CSV loading, cleaning, merging, type casting | Project decision (locked); last stable 2.x before CoW breaking changes in 3.0 |
| streamlit | 1.55.0 | `@st.cache_data` decorator for caching the loaded DataFrames | Project decision (locked); cache is load-boundary concern, lives in data_loader.py |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | 2.x (resolved by pandas) | Numeric dtype operations | Needed transitively; do not pin explicitly |
| openpyxl | 3.x | Excel engine for pandas | Only if any of the 6 files arrive as .xlsx; likely not needed for this dataset |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pandas 2.3.3 | pandas 3.0.1 | 3.0 has breaking CoW semantics — chained assignment silently fails; not worth risk on deadline |
| flat CSV in data/ | Parquet | Parquet is 5-10x smaller and faster to load; use if any CSV exceeds 50MB after inspection |

**Installation:**
```bash
pip install streamlit==1.55.0 plotly==6.6.0 pandas==2.3.3
```

---

## Architecture Patterns

### Recommended Project Structure (Phase 1 scope)

```
dashboard/
├── data/
│   ├── users.csv                  # 10,300 records
│   ├── movies.csv                 # 1,040 records
│   ├── watch_history.csv          # 105,000 records
│   ├── recommendation_logs.csv    # 52,000 records
│   ├── search_logs.csv            # 26,500 records
│   └── reviews.csv                # 15,450 records
├── src/
│   └── data_loader.py             # load + clean + merge (Phase 1 deliverable)
└── tests/
    └── test_data_loader.py        # Phase 1 test suite (Wave 0 gap — must create)
```

The `app.py`, `filter.py`, `kpis.py`, and `charts.py` files are out of scope for Phase 1. This phase is complete when `load_data()` returns a verified dict of clean DataFrames.

### Pattern 1: Single Cached Loader Function

**What:** One `@st.cache_data` function loads all 6 CSVs, cleans and types each, validates join keys, merges as needed, and returns a dict of DataFrames.

**When to use:** Always — this is the only correct pattern for Streamlit with static datasets. Loading outside this function causes full CSV reloads on every widget event.

**Example:**
```python
# src/data_loader.py
import streamlit as st
import pandas as pd

@st.cache_data
def load_data() -> dict[str, pd.DataFrame]:
    """
    Load, clean, and return all 6 Netflix dataset tables.
    Returns a dict with keys: users, movies, watch, recs, searches, reviews
    """
    users = _load_users()
    movies = _load_movies()
    watch = _load_watch_history()
    recs = _load_recommendation_logs()
    searches = _load_search_logs()
    reviews = _load_reviews()

    # Validate join keys before merging
    _validate_join_keys(users, movies, watch, recs, searches, reviews)

    return {
        "users": users,
        "movies": movies,
        "watch": watch,
        "recs": recs,
        "searches": searches,
        "reviews": reviews,
    }
```

### Pattern 2: Per-Table Private Loader with Explicit Types

**What:** Each of the 6 CSVs gets its own private function that handles type casting and cleaning for that table. The cached public function calls all 6.

**When to use:** Always — separates concerns, makes each table's cleaning logic readable and independently testable.

**Example:**
```python
def _load_users() -> pd.DataFrame:
    df = pd.read_csv("data/users.csv")

    # Drop duplicate users (3-6% expected)
    df = df.drop_duplicates(subset=["user_id"])

    # Fill missing categorical fields with mode
    for col in ["subscription_type", "country", "device_type"]:
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode()[0])

    # Fill missing numeric fields with median (robust to outliers)
    for col in ["age", "monthly_spending"]:
        if col in df.columns and df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # Cap outliers: age must be 13-100 (Netflix minimum age), spending > 0
    if "age" in df.columns:
        df["age"] = df["age"].clip(13, 100)

    # Cast categorical columns to save 50-70% memory
    for col in ["subscription_type", "country", "device_type"]:
        if col in df.columns:
            df[col] = df[col].astype("category")

    # Cast narrow integers where values fit
    if "age" in df.columns:
        df["age"] = df["age"].astype("int16")

    return df
```

### Pattern 3: Join Key Validation Before Merging

**What:** Before executing any `pd.merge()`, validate that join key coverage is above an acceptable threshold (95%+ recommended). Log orphan counts so they appear in the data prep notes for the Word deliverable.

**When to use:** Before every merge in this project. Synthetic datasets do NOT guarantee referential integrity.

**Example:**
```python
# Source: pandas.DataFrame.merge docs + isin() pattern
def _validate_join_keys(users, movies, watch, recs, searches, reviews):
    n_watch = len(watch)
    matched = watch["user_id"].isin(users["user_id"]).sum()
    match_rate = matched / n_watch
    print(f"watch_history user_id match rate: {match_rate:.1%} ({n_watch - matched} orphans)")
    if match_rate < 0.80:
        raise ValueError(
            f"watch_history join quality too low ({match_rate:.1%}) "
            "— Recommendation CTR KPI may be invalid. Inspect dataset."
        )

    n_watch_movies = watch["movie_id"].isin(movies["movie_id"]).sum()
    print(f"watch_history movie_id match rate: {n_watch_movies / n_watch:.1%}")
```

**Merge with indicator for auditing:**
```python
# Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
merged = pd.merge(
    watch, users,
    on="user_id",
    how="inner",
    validate="m:1",   # many watch rows to one user row
    indicator=True,
)
print(merged["_merge"].value_counts())  # "both" count confirms successful match
merged = merged.drop(columns=["_merge"])
```

### Anti-Patterns to Avoid

- **Reading CSVs outside the cached function:** Any `pd.read_csv()` call not inside `@st.cache_data` will re-execute on every widget event. Every CSV read must live inside `load_data()` or its private sub-functions called from `load_data()`.
- **Merging all 6 tables into one mega-DataFrame:** The tables serve different grain levels (per-user, per-movie, per-session). A single flat join explodes row count and balloons memory. Return separate DataFrames per table; only merge what KPI logic actually needs.
- **Skipping join validation:** Silently dropping rows on an inner join (the pandas default) produces wrong KPI numbers without any error. Validate first, merge second.
- **Using `object` dtype for string columns:** pandas defaults to `object` for all string columns. On 210K rows with categorical data, this uses 3-5x more memory than `category` dtype. Cast immediately after loading.
- **Chained assignment on pandas 2.x:** `df[col][mask] = val` triggers a SettingWithCopyWarning in 2.x and will silently fail in 3.x. Use `df.loc[mask, col] = val` always.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Duplicate detection | Custom loop comparing rows | `df.drop_duplicates(subset=["user_id"])` | pandas handles multi-column comparison, NaN equality, and index reset |
| Missing value imputation | Custom mean/mode calculation | `df[col].fillna(df[col].median())` / `.mode()[0]` | pandas methods handle NaN-aware statistics correctly |
| Outlier capping | Custom min/max loop | `df[col].clip(lower, upper)` | Vectorized, one-liner, handles NaN |
| Join validation | Custom set comparison logic | `df_a["id"].isin(df_b["id"])` + `merge(indicator=True)` | pandas built-ins are faster and produce auditable output |
| CSV parsing | Custom file reader | `pd.read_csv()` with `dtype=` and `parse_dates=` args | Handles encoding, line endings, quoting, type inference |

**Key insight:** Every data cleaning operation needed for this dataset has a one- or two-liner pandas equivalent. Custom loops are slower (not vectorized), harder to read, and untested against edge cases pandas already handles.

---

## Common Pitfalls

### Pitfall 1: CSV Files Exceed GitHub's 50MB Limit

**What goes wrong:** watch_history.csv (105K rows) or recommendation_logs.csv (52K rows) may be large enough to trigger GitHub's 50MB soft limit or 100MB hard limit. The error appears at `git push` — after the file is already staged — potentially 30 minutes into work.

**Why it happens:** Students download the Kaggle zip and commit all CSVs without checking sizes first.

**How to avoid:** Run `ls -lh data/` immediately after downloading. If any file exceeds 50MB, convert it to Parquet before committing:
```bash
python -c "import pandas as pd; df = pd.read_csv('data/watch_history.csv'); df.to_parquet('data/watch_history.parquet', index=False)"
```
Then load with `pd.read_parquet()` in `data_loader.py`. This is also 5-10x faster to load.

**Warning signs:** `git push` reports "this exceeds GitHub's file size limit of 100MB."

### Pitfall 2: Synthetic Join Keys Have Low Match Rate

**What goes wrong:** watch_history rows may reference user_ids that don't exist in users.csv. An inner merge silently drops those rows, producing undercount KPIs. An outer merge produces unexpected NaN columns.

**Why it happens:** Synthetic data generators create each table independently without enforcing foreign key constraints.

**How to avoid:** Run `_validate_join_keys()` before any merge. Print match rates to stdout (they'll appear in the Streamlit Cloud logs). If match rate drops below 80%, the Recommendation CTR KPI noted in STATE.md may need to be approximated or dropped.

**Warning signs:** Row count after merge is significantly lower than the smaller input table's count. NaN values appear in columns that should not have missing data after joining.

### Pitfall 3: Memory Exceeds Streamlit Cloud's 1GB Limit

**What goes wrong:** Default pandas `object` dtype on categorical string columns (genre, country, subscription_type, device_type) uses 3-5x more memory than `category` dtype. Six merged tables at object dtype can push the app past 400MB before Plotly figures are added. Streamlit Cloud kills the app mid-demo.

**Why it happens:** Developers don't check `df.info(memory_usage='deep')` before deploying.

**How to avoid:** Cast all low-cardinality string columns to `category` dtype in each per-table loader. Check memory before deploying:
```python
df.info(memory_usage='deep')  # target: <100MB per table, <300MB total
```

**Warning signs:** App works locally but shows "resource limit exceeded" on Streamlit Cloud within 30 seconds of load.

### Pitfall 4: Churn Rate Definition Unknown Until Schema is Inspected

**What goes wrong:** The Churn Rate KPI (KPI-04, Phase 2) cannot be defined without knowing which column in users.csv encodes churn status. STATE.md explicitly flags this as unresolved. If Phase 1 skips the schema inspection step, Phase 2 will block on this.

**Why it happens:** Developers skip exploratory inspection and go straight to cleaning.

**How to avoid:** After loading users.csv, print `users.columns.tolist()` and `users.dtypes` and `users.describe()`. Document which column will serve as the churn proxy (e.g., `is_churned`, `status`, `subscription_end_date`) and record the decision in a code comment.

**Warning signs:** Phase 2 starts and `kpis.py` cannot implement Churn Rate because no one knows which column to use.

### Pitfall 5: `@st.cache_data` Not Applied — Full Reload on Every Widget Change

**What goes wrong:** Without `@st.cache_data`, Streamlit re-executes `pd.read_csv()` for all 6 files on every filter change. With 210K total rows, each widget interaction takes 5-10 seconds.

**Why it happens:** Developers new to Streamlit treat the script as a one-shot program, not an event-driven loop.

**How to avoid:** The `@st.cache_data` decorator must be on `load_data()` before any other development begins. This is the very first thing to write.

**Warning signs:** Dashboard takes >3 seconds to respond to a selectbox change. CPU spikes are visible in the browser's dev tools on every interaction.

---

## Code Examples

Verified patterns from official sources and prior project research:

### Loading a CSV with Types and Dates
```python
# Source: pandas.read_csv documentation
import pandas as pd

users = pd.read_csv(
    "data/users.csv",
    dtype={
        "user_id": "str",
        "subscription_type": "category",
        "country": "category",
        "device_type": "category",
    },
    parse_dates=["join_date"],   # adjust column name after schema inspection
)
```

### Dropping Duplicates
```python
# Source: pandas docs
df = df.drop_duplicates(subset=["user_id"])  # keeps first occurrence
```

### Filling Missing Values (Categorical)
```python
# Fill with most frequent value
df["genre"] = df["genre"].fillna(df["genre"].mode()[0])
```

### Filling Missing Values (Numeric — Median for Outlier Robustness)
```python
# Median is robust to the age/spending outliers noted in the dataset
df["age"] = df["age"].fillna(df["age"].median()).astype("int16")
```

### Capping Outliers
```python
# Source: pandas.Series.clip docs
df["age"] = df["age"].clip(lower=13, upper=100)          # Netflix minimum age
df["watch_duration_min"] = df["watch_duration_min"].clip(lower=0, upper=1440)  # max 24 hrs
```

### Memory Optimization
```python
# Convert object-dtype categoricals to category dtype
for col in ["subscription_type", "country", "device_type", "genre"]:
    if col in df.columns:
        df[col] = df[col].astype("category")
```

### Merge with Validation
```python
# Source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
merged = pd.merge(
    watch_history,
    users[["user_id", "subscription_type", "country"]],  # only needed columns
    on="user_id",
    how="inner",
    validate="m:1",
)
```

### File Size Check (run before git add)
```bash
ls -lh data/
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pd.read_csv()` raw in script body | Wrap in `@st.cache_data` | Streamlit 0.86+ (2021) | No reload on rerun |
| `astype(str)` for all text columns | `astype("category")` for low-cardinality strings | pandas 0.15+ (mature) | 50-70% memory reduction |
| `@st.experimental_memo` | `@st.cache_data` | Streamlit 1.18 (2023) | `experimental_memo` removed |
| Trust dataset join keys | Validate with `isin()` before merge | Best practice — not enforced by pandas | Prevents silent KPI errors |

**Deprecated/outdated:**
- `@st.experimental_memo` and `@st.experimental_singleton`: Removed in Streamlit 1.18+. Use `@st.cache_data` and `@st.cache_resource` respectively.
- pandas `infer_datetime_format=True` in `read_csv`: Deprecated in pandas 2.0; removed in pandas 2.2. Use `parse_dates=["col"]` directly.

---

## Open Questions

1. **Actual column names in the 6 CSV files**
   - What we know: Join keys are `user_id` and `movie_id`; table purposes are documented; data quality issues are documented
   - What's unclear: Exact column names for dates, categorical fields, numeric fields — the Kaggle page does not expose them without downloading
   - Recommendation: The first task in Phase 1 should be to download the dataset and print `.columns` and `.dtypes` for each table. Document the results before writing any cleaning logic.

2. **Churn Rate operational definition**
   - What we know: STATE.md flags this as unresolved; users.csv contains subscription/status data
   - What's unclear: Whether the column is a binary flag (`is_churned`), a date (`subscription_end_date`), or derived from inactivity
   - Recommendation: Inspect `users.describe()` and `users.dtypes` in Phase 1. Pick the definition and document it with a comment in `data_loader.py`. Phase 2 KPI code depends on this.

3. **recommendation_logs join quality**
   - What we know: STATE.md flags this as unresolved; the 80% threshold is the go/no-go gate for the Recommendation CTR KPI
   - What's unclear: Actual match rate between recommendation_logs.user_id and users.user_id
   - Recommendation: Print match rate in the validation step. If below 80%, document the issue in the Word deliverable data prep notes and note that Recommendation CTR KPI (KPI-03) may need to be approximated.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (install required — not yet in project) |
| Config file | none — Wave 0 must create `pytest.ini` or `pyproject.toml` |
| Quick run command | `pytest tests/test_data_loader.py -x -q` |
| Full suite command | `pytest tests/ -q` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-01 | `load_data()` returns a dict with all 6 keys | unit | `pytest tests/test_data_loader.py::test_load_data_returns_all_tables -x` | Wave 0 |
| DATA-01 | Each returned DataFrame has >0 rows | unit | `pytest tests/test_data_loader.py::test_all_tables_nonempty -x` | Wave 0 |
| DATA-02 | No duplicate user_ids in users DataFrame | unit | `pytest tests/test_data_loader.py::test_users_no_duplicate_ids -x` | Wave 0 |
| DATA-02 | No null values in critical columns (subscription_type, user_id) | unit | `pytest tests/test_data_loader.py::test_no_nulls_in_key_columns -x` | Wave 0 |
| DATA-02 | Categorical columns have `category` dtype | unit | `pytest tests/test_data_loader.py::test_category_dtypes -x` | Wave 0 |
| DATA-02 | Age column values are within 13-100 range | unit | `pytest tests/test_data_loader.py::test_age_outliers_capped -x` | Wave 0 |
| DATA-03 | watch_history user_id match rate >= 80% | unit | `pytest tests/test_data_loader.py::test_watch_user_join_quality -x` | Wave 0 |
| DATA-03 | watch_history movie_id match rate >= 80% | unit | `pytest tests/test_data_loader.py::test_watch_movie_join_quality -x` | Wave 0 |
| DATA-03 | Total merged memory < 300MB | unit | `pytest tests/test_data_loader.py::test_memory_under_limit -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_data_loader.py -x -q`
- **Per wave merge:** `pytest tests/ -q`
- **Phase gate:** Full suite green before moving to Phase 2

### Wave 0 Gaps

- [ ] `tests/test_data_loader.py` — covers all DATA-01, DATA-02, DATA-03 requirements above
- [ ] `tests/conftest.py` — shared fixture that calls `load_data()` once for all tests (avoids repeated CSV reads in test suite)
- [ ] `pytest.ini` or `[tool.pytest.ini_options]` in `pyproject.toml` — test discovery config
- [ ] Framework install: `pip install pytest` and add `pytest` to `requirements.txt` dev section (or a separate `requirements-dev.txt`)

---

## Sources

### Primary (HIGH confidence)

- [pandas.DataFrame.merge — pandas 3.0.1 official docs](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) — validate parameter, indicator parameter, how options
- [STACK.md (.planning/research/STACK.md)](internal) — versions, stack decisions, version compatibility verified 2026-03-22
- [ARCHITECTURE.md (.planning/research/ARCHITECTURE.md)](internal) — data layer patterns, @st.cache_data placement, project structure
- [PITFALLS.md (.planning/research/PITFALLS.md)](internal) — memory limits, join validation, GitHub size limits, dtype optimization — HIGH confidence, verified against official Streamlit docs

### Secondary (MEDIUM confidence)

- [Kaggle: Netflix 2025 User Behavior Dataset](https://www.kaggle.com/datasets/sayeeduddin/netflix-2025user-behavior-dataset-210k-records) — table record counts, join keys (user_id, movie_id), intentional data quality issues confirmed via dataset page
- [pandas read_csv — GeeksforGeeks](https://www.geeksforgeeks.org/python/pandas-read_csv-low_memory-and-dtype-options/) — dtype parameter patterns, corroborated by official pandas docs
- [Pandas Merge DataFrames — SparkByExamples](https://sparkbyexamples.com/pandas/pandas-merge-dataframes-explained-examples/) — merge validation patterns, cross-referenced with official docs

### Tertiary (LOW confidence — flag for validation)

- Exact CSV column names: UNKNOWN — must be discovered by downloading and inspecting the dataset. All code examples use placeholder column names that must be verified.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions locked in STACK.md, verified 2026-03-22
- Architecture: HIGH — patterns from ARCHITECTURE.md, verified against official Streamlit caching docs
- Cleaning patterns: HIGH — pandas official docs verified; exact column names LOW until dataset is downloaded
- Pitfalls: HIGH — memory limits, join quality, GitHub limits all sourced from official docs or dataset page
- Test map: MEDIUM — test structure is standard; specific test assertions depend on actual column names discovered in Wave 0

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable libraries; dataset schema won't change)
