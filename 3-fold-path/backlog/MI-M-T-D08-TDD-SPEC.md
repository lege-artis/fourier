# MI-M-T-D08 — TDD Expansion Spec
**Version:** v0.1.0  
**Date:** 2026-05-02  
**Author:** MacBook (schema contracts) — ThinkPad executes migration  
**Status:** SCHEMA READY — testcases.yaml v2 migration pending ThinkPad sync  
**Severity:** A / P1-critical  

---

## 1. Purpose

Expand the MI-M-T evidence system from a flat bug/testcase register into a
three-tier TDD evidence model:

```
Requirements (requirements.yaml)
    └── TestTargets (test-targets.yaml)       ← scoped test surfaces per requirement
            └── TestCases (testcases.yaml v2)  ← executable cases with dual cross-refs
                    └── TestRuns (testruns/)    ← execution records (unchanged)
```

The TDD loop mandate:
1. **Requirements first** — define acceptance criteria before any code changes
2. **TestTargets scoped** — identify the specific component/endpoint under test
3. **TestCases written** — executable cases linked to both requirement + target
4. **Code authored** — implementation to satisfy green test gate
5. **TestRun closes loop** — pass record references the triggering requirement

---

## 2. New Files

### 2.1 `3-fold-path/evidence/requirements.yaml`
Schema version: `1.0.0`  
Source: ADRs (CLAUDE.md § ADRs) + defect-driven requirements (bugs.yaml) + ARCH-SPEC endpoints (D07)

### 2.2 `3-fold-path/evidence/test-targets.yaml`
Schema version: `1.0.0`  
Source: derived from known testable surfaces across 3 sites + mi_m_t FastAPI routes

---

## 3. Schema Contracts

### 3.1 requirements.yaml schema

```yaml
schema_version: "1.0.0"
generated: "YYYY-MM-DD"

requirements:
  - id: REQ-NNN           # REQ-001, REQ-002, …  (3-digit zero-padded)
    title: ""             # short imperative phrase
    description: |        # full acceptance language
      ""
    source: ""            # ADR-NN | BUG-NNN | ARCH-SPEC-§N | user-story
    priority: P1          # P1-critical | P2-high | P3-medium | P4-low
    site: zemla           # zemla | mim2000 | bodyterapie | cross-site
    component: ""         # gallery | podcast | navigation | content |
                          # translation | mobile | auth | identity | api
    status: active        # active | deprecated | deferred
    test_target_refs:     # back-refs: populated after test-targets.yaml seeded
      - TT-NNN
    acceptance_criteria:
      - "Given <context> when <action> then <outcome>"
```

**Mandatory fields:** `id`, `title`, `source`, `priority`, `site`, `component`, `status`  
**Computed:** `test_target_refs` (populated by triage.py post-seed)

---

### 3.2 test-targets.yaml schema

```yaml
schema_version: "1.0.0"
generated: "YYYY-MM-DD"

test_targets:
  - id: TT-NNN            # TT-001, TT-002, … (3-digit zero-padded)
    title: ""             # short descriptive phrase
    description: |        # what surface / endpoint / component is under test
      ""
    type: component       # component | endpoint | page | integration | regression | smoke
    site: zemla           # zemla | mim2000 | bodyterapie | cross-site
    component: ""         # same taxonomy as requirements.yaml
    requirement_refs:     # back-refs to requirements.yaml
      - REQ-NNN
    implementation_ref: ""  # relative path to PHP/JS/Python file under test (optional)
    status: active        # active | deprecated
```

**Mandatory fields:** `id`, `title`, `type`, `site`, `component`, `status`  
**Computed:** `requirement_refs` (populated by triage.py post-seed)

---

### 3.3 testcases.yaml v2 delta (migration contract)

Add two fields to **every** existing test case entry:

```yaml
    test_target_ref: TT-NNN   # REQUIRED in v2 — links case to scoped test surface
    requirement_ref: REQ-NNN  # REQUIRED in v2 — links case to acceptance criterion
```

**Schema version bump:** `1.0.0` → `2.0.0`  
**Migration script:** `_config/migrate-testcases-v1-to-v2.py` (to be authored ThinkPad-side)  
**Validation:** triage.py must reject any testcase missing either ref field in v2 mode

---

## 4. triage.py Updates (ThinkPad scope)

Add to existing filter/sort capabilities:

| New flag | Behaviour |
|----------|-----------|
| `--req REQ-NNN` | Show all testcases + testruns referencing this requirement |
| `--target TT-NNN` | Show all testcases scoped to this test target |
| `--matrix-req` | Requirements × TestTargets coverage matrix (rows=REQ, cols=TT) |
| `--orphan-cases` | List testcases missing `test_target_ref` or `requirement_ref` |
| `--orphan-reqs` | List requirements with zero linked test targets |

---

## 5. evidence-report.py Updates (ThinkPad scope)

Add section mode:

| Mode | Output |
|------|--------|
| `--section requirements` | Table: id, title, priority, status, #targets, #testcases |
| `--section targets` | Table: id, title, type, site, component, #testcases |
| `--section traceability` | Full chain: REQ → TT → TC → testrun result |

---

## 6. Seed Plan — requirements.yaml

Seed from four sources in priority order:

### 6.1 ADR-derived requirements (authoritative design decisions)

| REQ ID | Source | Title |
|--------|--------|-------|
| REQ-001 | ADR-01 | Shared identity data must live exclusively in `inc/zemla-config.php` |
| REQ-002 | ADR-02 | Gallery layout must use exactly two direct children: `<aside.gallery-sidebar>` + `.album-grid` |
| REQ-003 | ADR-03 | Album cards must use vertical layout with 3:2 aspect ratio image-top |
| REQ-004 | ADR-04 | All `_e()` translation calls must be registered in `inc/translations.php` |

### 6.2 Defect-driven requirements (prevent regression of closed bugs)

| REQ ID | Source | Title |
|--------|--------|-------|
| REQ-005 | BUG-003/004 | Podcast player must initialise exactly once per page load (no double-init) |
| REQ-006 | BUG-018 | Podcast player speed control must hold selected rate across track seek |
| REQ-007 | BUG-018 | Podcast player skip forward/back must not reset playback speed |
| REQ-008 | BUG-018 | Cover art must render at `zemla-wide` size (512×512) on episode pages |
| REQ-009 | BUG-009..012 | CEO blog YouTube embeds must render in all 4 locales (CS/DE/IT/EN) |
| REQ-010 | BUG-023 | mim2000 navigation must resolve: cooperations=179, advisory=180, raw-dev=181 |
| REQ-011 | BUG-024 | mim2000 New Perspective link must resolve to `http://www.newperspective.cz/cs/` |

### 6.3 Architecture requirements (from D07 ARCH-SPEC endpoints — ThinkPad to expand)

| REQ ID | Source | Title |
|--------|--------|-------|
| REQ-012 | ARCH-SPEC | mi_m_t FastAPI `POST /projects` must return 201 with project_id |
| REQ-013 | ARCH-SPEC | mi_m_t FastAPI `GET /projects/{id}/testruns` must return paginated list |
| REQ-014 | ARCH-SPEC | mi_m_t FastAPI health endpoint must return 200 with status=ok |
| REQ-015 | ARCH-SPEC | mi_m_t database writes must be idempotent on re-run with same item_code+run_tag |

*ThinkPad: expand REQ-012..015 from D07 ARCH-SPEC §endpoints — 40 routes documented.*

### 6.4 Content/translation requirements

| REQ ID | Source | Title |
|--------|--------|-------|
| REQ-016 | CC-005 | zemla `inc/translations.php` must contain all strings surfaced by CC-005 scan |
| REQ-017 | CC-006 | zemla must define ZEMLA_SLUG_* constants for all 5 nav slugs |

---

## 7. Seed Plan — test-targets.yaml

Derived from known testable surfaces across 3 sites + mi_m_t API:

| TT ID | Type | Site | Component | Title |
|-------|------|------|-----------|-------|
| TT-001 | component | zemla | identity | `inc/zemla-config.php` — master identity data file |
| TT-002 | component | zemla | gallery | `.gallery-layout` direct children structure |
| TT-003 | component | zemla | gallery | Album card layout — aspect ratio + orientation |
| TT-004 | component | zemla | translation | `inc/translations.php` — completeness gate |
| TT-005 | component | zemla | podcast | `zp-engine.js` — player init, speed, seek |
| TT-006 | page | zemla | podcast | Single episode page — cover art render |
| TT-007 | page | mim2000 | content | CEO blog — all 4 locale YouTube embeds |
| TT-008 | page | mim2000 | navigation | Primary nav — page_id resolution accuracy |
| TT-009 | page | mim2000 | content | New Perspective external link |
| TT-010 | page | mim2000 | identity | MI-M-T prototype page `/projects/mi-m-t/` |
| TT-011 | endpoint | cross-site | api | mi_m_t `POST /projects` |
| TT-012 | endpoint | cross-site | api | mi_m_t `GET /projects/{id}/testruns` |
| TT-013 | endpoint | cross-site | api | mi_m_t `GET /health` |
| TT-014 | smoke | cross-site | api | mi_m_t SMK9 — 20-item smoke suite |
| TT-015 | regression | zemla | translation | CC-005 translation strings present |

---

## 8. testcases.yaml v2 — Mapping Table

*For each of the 15 existing test cases (TC-001..TC-015), assign `test_target_ref` + `requirement_ref`.*  
*ThinkPad: apply this table during `migrate-testcases-v1-to-v2.py` execution.*

| TC ID | test_target_ref | requirement_ref | Notes |
|-------|----------------|----------------|-------|
| TC-001 | TT-005 | REQ-005 | Podcast player init — single init gate |
| TC-002 | TT-005 | REQ-005 | Podcast audio element creation |
| TC-003 | TT-005 | REQ-006 | Speed hold across seek |
| TC-004 | TT-005 | REQ-007 | Skip does not reset speed |
| TC-005 | TT-006 | REQ-008 | Cover art render at zemla-wide |
| TC-006 | TT-007 | REQ-009 | CEO blog CS YouTube embed |
| TC-007 | TT-007 | REQ-009 | CEO blog DE YouTube embed |
| TC-008 | TT-007 | REQ-009 | CEO blog IT YouTube embed |
| TC-009 | TT-007 | REQ-009 | CEO blog EN YouTube embed |
| TC-010 | TT-002 | REQ-002 | Gallery sidebar wrapper structure |
| TC-011 | TT-003 | REQ-003 | Album card vertical layout |
| TC-012 | TT-004 | REQ-004 | Translation strings completeness |
| TC-013 | TT-001 | REQ-001 | zemla-config.php — no hard-coded linkedin |
| TC-014 | TT-008 | REQ-010 | mim2000 nav page_id resolution |
| TC-015 | TT-014 | REQ-015 | mi_m_t SMK9 idempotency on re-run |

*Note: TC-001..015 numbering assumed from CLAUDE.md context. ThinkPad to verify actual IDs in testcases.yaml and correct mapping before migration.*

---

## 9. Implementation Checklist (ThinkPad)

- [ ] Create `3-fold-path/evidence/requirements.yaml` from §6 seed above
- [ ] Create `3-fold-path/evidence/test-targets.yaml` from §7 seed above
- [ ] Write `_config/migrate-testcases-v1-to-v2.py` — adds refs per §8 table, bumps schema to 2.0.0
- [ ] Run migration against live `testcases.yaml` — verify 15/15 cases updated
- [ ] Update `triage.py` — add flags from §4
- [ ] Update `evidence-report.py` — add modes from §5
- [ ] Run SMK9 — verify no regressions
- [ ] Commit as ThinkPad D08 delivery; include in next delta to MacBook

---

## 10. Acceptance Criteria

- `requirements.yaml` parses without error: `python -c "import yaml; yaml.safe_load(open('requirements.yaml'))"`
- `test-targets.yaml` parses without error (same)
- `testcases.yaml` schema_version = "2.0.0" after migration
- Every testcase has non-null `test_target_ref` and `requirement_ref`
- `triage.py --orphan-cases` returns zero results
- `triage.py --matrix-req` renders without error
- `evidence-report.py --section traceability` produces output with ≥15 rows
