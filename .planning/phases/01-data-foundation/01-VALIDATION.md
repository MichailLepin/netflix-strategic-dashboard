---
phase: 1
slug: data-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | DATA-01 | unit | `python -m pytest tests/test_data_loader.py::test_all_tables_load -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | DATA-02 | unit | `python -m pytest tests/test_data_loader.py::test_no_duplicates -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | DATA-02 | unit | `python -m pytest tests/test_data_loader.py::test_missing_values_handled -x` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 1 | DATA-03 | unit | `python -m pytest tests/test_data_loader.py::test_join_cardinality -x` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01 | 1 | DATA-01 | unit | `python -m pytest tests/test_data_loader.py::test_memory_under_400mb -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_data_loader.py` — stubs for DATA-01, DATA-02, DATA-03
- [ ] `tests/conftest.py` — shared fixtures (data paths, small sample data)
- [ ] `pip install pytest` — install test framework

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| CSV files under 90MB for GitHub | DATA-01 | File size is a repo constraint, not logic | Run `ls -lh data/` and verify no file > 90MB |
| `@st.cache_data` decorator applied | DATA-01 | Decorator presence is structural, not behavioral | Inspect `src/data_loader.py` for `@st.cache_data` on load function |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
