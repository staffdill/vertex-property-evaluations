---
phase: 2
slug: property-crud
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-11
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + pytest-asyncio 1.3.0 |
| **Config file** | `pyproject.toml` (`asyncio_mode = "auto"`) |
| **Quick run command** | `./venv/bin/python -m pytest tests/ -x -q` |
| **Full suite command** | `./venv/bin/python -m pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `./venv/bin/python -m pytest tests/ -x -q`
- **After every plan wave:** Run `./venv/bin/python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | PROP-01 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_create_property -x` | Wave 0 | ⬜ pending |
| 02-01-02 | 01 | 0 | PROP-01 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_create_missing_fields -x` | Wave 0 | ⬜ pending |
| 02-01-03 | 01 | 1 | PROP-02 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_list_properties -x` | Wave 0 | ⬜ pending |
| 02-01-04 | 01 | 1 | PROP-03 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_get_property -x` | Wave 0 | ⬜ pending |
| 02-01-05 | 01 | 1 | PROP-03 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_get_property_not_found -x` | Wave 0 | ⬜ pending |
| 02-01-06 | 01 | 1 | PROP-04 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_delete_property -x` | Wave 0 | ⬜ pending |
| 02-01-07 | 01 | 1 | PROP-04 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_delete_cascades_assets -x` | Wave 0 | ⬜ pending |
| 02-01-08 | 01 | 1 | PROP-04 | integration | `./venv/bin/python -m pytest tests/test_properties.py::test_delete_not_found -x` | Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/routers/__init__.py` — package marker
- [ ] `app/routers/properties.py` — property CRUD router (POST, GET list, GET detail, DELETE)
- [ ] `app/routers/assets.py` — asset record router (stub for Phase 3)
- [ ] `app/models.py` — Pydantic request/response models
- [ ] `tests/test_properties.py` — covers PROP-01 through PROP-04 (all 8 test cases)
- [ ] Updated `app/main.py` — include_router calls before StaticFiles mount

*Existing infrastructure in `conftest.py`, `pyproject.toml`, and `tests/` is fully usable — no framework gaps.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| risk_badge is null in list response | PROP-02 | Field is nullable until Phase 5 analysis runs | Check GET /api/properties response — `risk_badge` must be `null`, not absent |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
