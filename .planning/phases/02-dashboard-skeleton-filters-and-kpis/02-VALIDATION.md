---
phase: 2
slug: dashboard-skeleton-filters-and-kpis
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 (already installed) |
| **Config file** | tests/conftest.py (session fixture exists) |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 3 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 1 | DASH-01, DASH-02 | manual | Visual inspection of app | N/A | ⬜ pending |
| 2-02-01 | 02 | 1 | FLT-01..04 | unit | `python -m pytest tests/test_filters.py -x` | ❌ W0 | ⬜ pending |
| 2-02-02 | 02 | 1 | KPI-01..04 | unit | `python -m pytest tests/test_kpis.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_kpis.py` — stubs for KPI-01..04 computation functions
- [ ] `tests/test_filters.py` — stubs for filter application logic

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Netflix logo visible at top | DASH-01 | Visual element rendering | Run `streamlit run app.py`, verify logo/title at top |
| Single-screen layout at 1080p | DASH-02 | Layout constraint | Run app, verify no vertical scrolling at 1080p 100% zoom |
| KPI alarm coloring | KPI-01..04 | Visual styling | Apply filters that trigger alarm thresholds, verify colors |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 3s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
