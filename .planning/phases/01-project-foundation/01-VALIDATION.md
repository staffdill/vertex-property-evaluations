---
phase: 1
slug: project-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-10
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~3 seconds |

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
| 01-01-01 | 01 | 1 | FRNT-03 (health) | integration | `python -m pytest tests/test_health.py -x` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | FRNT-03 (db) | unit | `python -m pytest tests/test_database.py -x` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | FRNT-03 (static) | integration | `python -m pytest tests/test_health.py::test_root_serves_html -x` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01 | 1 | FRNT-03 (css) | integration | `python -m pytest tests/test_health.py::test_css_accessible -x` | ❌ W0 | ⬜ pending |
| 01-01-05 | 01 | 1 | FRNT-03 (wal) | unit | `python -m pytest tests/test_database.py::test_wal_mode -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — package marker
- [ ] `tests/conftest.py` — shared fixtures (async client, temp DB)
- [ ] `tests/test_health.py` — health check + static file tests
- [ ] `tests/test_database.py` — schema creation + WAL mode tests
- [ ] `pyproject.toml` `[tool.pytest.ini_options]` — asyncio_mode = "auto"

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dark theme renders correctly | FRNT-03 | Visual appearance check | Open http://localhost:8000 in browser, verify dark background and light text |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---

*Phase: 01-project-foundation*
*Validation strategy created: 2026-03-10*
