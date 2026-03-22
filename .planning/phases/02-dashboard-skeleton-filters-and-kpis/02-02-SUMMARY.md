---
phase: 02-dashboard-skeleton-filters-and-kpis
plan: 02
subsystem: ui
tags: [streamlit, filters, kpis, pandas, tdd]

# Dependency graph
requires:
  - phase: 02-dashboard-skeleton-filters-and-kpis/01
    provides: app.py skeleton with Netflix branding, data_loader
provides:
  - 4 sidebar filters (genre, subscription, device, date range) wired to live data
  - 4 KPI tiles with alarm coloring and delta indicators
  - Pure filter and KPI computation modules with full test coverage
affects: [03-charts, 04-deployment]

# Tech tracking
tech-stack:
  added: []
  patterns: [pure-function-modules, tdd-red-green, alarm-threshold-coloring]

key-files:
  created: [src/filter.py, src/kpis.py, tests/test_filter.py, tests/test_kpis.py]
  modified: [app.py]

key-decisions:
  - "Alarm colors via CSS nth-of-type selectors on stMetric data-testid"
  - "Delta indicators hidden when no filters active (delta=None)"
  - "Churn rate uses inverse delta_color (lower = green)"

patterns-established:
  - "Pure function modules: filter.py and kpis.py are pure functions taking/returning dicts of DataFrames"
  - "TDD workflow: tests written first, then implementation to pass them"
  - "Filter passthrough: empty list = no filter applied"

requirements-completed: [KPI-01, KPI-02, KPI-03, KPI-04, FLT-01, FLT-02, FLT-03, FLT-04]

# Metrics
duration: 3min
completed: 2026-03-22
---

# Phase 2 Plan 2: Filters and KPIs Summary

**4 sidebar filters (genre, subscription, device, date) and 4 alarm-colored KPI tiles with delta indicators, all wired to live Netflix dataset via pure function modules with 12 unit tests**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-22T17:42:27Z
- **Completed:** 2026-03-22T17:44:57Z
- **Tasks:** 3 (2 auto + 1 checkpoint auto-approved)
- **Files modified:** 5

## Accomplishments
- Pure filter module (apply_filters) supporting genre, subscription, device, and date range with passthrough defaults
- Pure KPI module (compute_kpis + get_alarm_level) for 4 KPIs with empty DataFrame guards
- Full test coverage: 12 tests (6 filter + 6 KPI) all passing via TDD
- app.py wired with real sidebar widgets, computed KPI tiles, alarm coloring, and delta indicators

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Write failing tests** - `e0711fd` (test)
2. **Task 1 GREEN: Implement filter.py and kpis.py** - `48e5c28` (feat)
3. **Task 2: Wire filters and KPI tiles into app.py** - `0feeb7d` (feat)
4. **Task 3: Checkpoint auto-approved** - no commit (verification only)

## Files Created/Modified
- `src/filter.py` - Pure apply_filters function: genre, subscription, device, date range filtering
- `src/kpis.py` - Pure compute_kpis and get_alarm_level functions for 4 KPIs with alarm thresholds
- `tests/test_filter.py` - 6 unit tests for all filter types including combined and no-filter
- `tests/test_kpis.py` - 6 unit tests for all KPIs, empty guard, and alarm color thresholds
- `app.py` - Updated from skeleton to full interactive dashboard with filters and KPI tiles

## Decisions Made
- Alarm colors applied via CSS nth-of-type selectors targeting Streamlit's data-testid="stMetric" elements
- Delta indicators only shown when filters are active; hidden (delta=None) for baseline view
- Churn rate tile uses delta_color="inverse" since lower churn is better
- Date filtering uses watch_date column (not timestamp) as confirmed from actual CSV schema
- Rec CTR uses was_clicked column (not clicked) as confirmed from actual CSV schema

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 4 filters and 4 KPIs are functional and tested
- Chart placeholder grid remains intact for Phase 3
- filter.py and kpis.py provide clean interfaces for any future chart interactions
- 21 total tests passing (data_loader + filter + kpis)

## Self-Check: PASSED

All 6 files found. All 3 commit hashes verified.

---
*Phase: 02-dashboard-skeleton-filters-and-kpis*
*Completed: 2026-03-22*
