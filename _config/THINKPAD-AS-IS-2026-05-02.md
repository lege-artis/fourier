# THINKPAD-AS-IS-2026-05-02.md — ThinkPad State Document
**Date:** 2026-05-02  
**Prepared by:** MacBook / CoWork session  
**Purpose:** Full AS-IS state of ThinkPad scope after 2026-05-02 MacBook session close.  
**Companion delta:** `_config/macbook-delta-2026-05-02.tar.gz` (49K, 11 files)

---

## 1. Context: What Happened on MacBook (2026-05-01 / 2026-05-02)

### 1.1 Sessions completed
| Session | Key outputs |
|---------|-------------|
| 2026-05-01 | SMK9 20/20 PASS; GH-UPL-05/08/09/10 done; all available zips on GitHub Releases; pydantic-settings installed in sandbox; v1.7.4 confirmed live dev baseline |
| 2026-05-02 | CI heartbeat/kh-sim fixes (rebase conflict resolution with ThinkPad); MI-M-T-D08 MacBook schemas (requirements.yaml 17 REQs + test-targets.yaml 15 TTs + TDD-SPEC.md); KB-034/035 branch authority lessons; BUG-024 fixed via TFE; all 3 themes live at new versions |

### 1.2 What is now live (production)
| Site | Version | Key changes |
|------|---------|-------------|
| zemla.org | **v1.7.5** | Seed page template added (page-seed.php + CSS + meta box) |
| mim2000.cz | **v1.9.1** | Dual-layer SVG, azure symbols, Ω↔0 swap; BUG-024 fixed (New Perspective link) |
| bodyterapie.com | **v1.7.1** | Dual-layer SVG (sandstone-tri + brushstone-tri), azure symbols, fp-corner-nav |

### 1.3 CI state (macbook branch)
| Workflow | Status |
|----------|--------|
| ci-heartbeat.yml | All backends green (scala sbt/setup-sbt@v1, pascal fpc, react App.css + @playwright/test fixed — ThinkPad's commits absorbed via rebase) |
| kh-sim-ci.yml | hashFiles() guards on 5 backend jobs + integration-e2e; backends skip gracefully when not present on MacBook |

---

## 2. What ThinkPad Must Apply from macbook-delta-2026-05-02.tar.gz

```bash
# Extract on ThinkPad (from repo root)
tar -xzf _config/macbook-delta-2026-05-02.tar.gz
```

### 2.1 Files in delta (11 items, 49K)

| File | Action | Notes |
|------|--------|-------|
| `.github/workflows/kh-sim-ci.yml` | **MERGE** — ThinkPad must not overwrite | hashFiles() guards added; compare with your version |
| `3-fold-path/backlog/MI-M-T-D08-TDD-SPEC.md` | **NEW** — copy directly | TDD three-tier spec; ThinkPad implementation scope |
| `3-fold-path/evidence/requirements.yaml` | **NEW** — copy directly | 17 requirements, schema v1.0.0 |
| `3-fold-path/evidence/test-targets.yaml` | **NEW** — copy directly | 15 test targets, schema v1.0.0 |
| `3-fold-path/code/SESSION-NOTES.md` | **MERGE** — append new entries | MacBook may have updated; do not overwrite D-01 env notes |
| `CLAUDE.md` | **MERGE** — adopt §CURRENT STATE + §DEVICES** | MacBook updated live_versions + branch authority rules |
| `MANIFEST.yaml` | **OVERWRITE** — MacBook owns this | v1.7.5/v1.9.1/v1.7.1 live versions now correct |
| `_config/DEVICES.md` | **OVERWRITE** — MacBook authored | Branch authority rules added; GitHub protection setup |
| `_config/KB-LESSONS-LEARNED.yaml` | **MERGE** — append KB-034 + KB-035 | Branch authority violation + concurrent CI fix conflict |
| `platform sources/React/src/App.css` | **NEW or OVERWRITE** | Minimal `/* App styles */` — ThinkPad version accepted in rebase |
| `queue-macbook.yaml` | **DO NOT TOUCH** — MacBook owns | Informational only; ThinkPad reads but never writes |

### 2.2 Conflict risk assessment

| File | Risk | Resolution rule |
|------|------|-----------------|
| `kh-sim-ci.yml` | **HIGH** — both devices modified | Diff before applying; keep hashFiles guards from MacBook, keep ThinkPad backend configs |
| `CLAUDE.md` | **MEDIUM** | ThinkPad branch has session notes; merge §CURRENT STATE + §DEVICES from MacBook version |
| `KB-LESSONS-LEARNED.yaml` | **LOW** | Append-only; just add KB-034 + KB-035 entries |
| All others | **LOW** | New files or clearly MacBook-owned |

---

## 3. ThinkPad Scope — Open Tasks

### 3.1 MI-M-T-D08 ThinkPad Implementation (P1-critical)

These tasks are defined in `3-fold-path/backlog/MI-M-T-D08-TDD-SPEC.md` (now in delta).  
MacBook delivered the **schema contracts**. ThinkPad delivers the **code changes**.

| Task | File | Description | Acceptance |
|------|------|-------------|------------|
| Migrate testcases.yaml v1 → v2 | `3-fold-path/evidence/testcases.yaml` | Add `test_target_ref` + `requirement_ref` to all 15 cases per mapping table in TDD-SPEC §8 | `schema_version: "2.0.0"`; triage.py `--orphan-cases` = 0 |
| Write migrate-testcases-v1-to-v2.py | `_config/migrate-testcases-v1-to-v2.py` | Script applies §8 mapping table; bumps schema | Idempotent; validates refs exist in requirements.yaml + test-targets.yaml |
| Update triage.py | `3-fold-path/evidence/tools/triage.py` | Add `--req REQ-NNN`, `--target TT-NNN`, `--matrix-req`, `--orphan-cases`, `--orphan-reqs` flags | See TDD-SPEC §4 |
| Update evidence-report.py | `3-fold-path/evidence/tools/evidence-report.py` | Add `--section requirements`, `--section targets`, `--section traceability` modes | TDD-SPEC §5; traceability output ≥15 rows |
| Run SMK9 smoke after changes | `3-fold-path/evidence/mi_m_t/tests/smoke/smk9.py` | Verify 20/20 PASS still holds after triage.py + evidence-report.py changes | All 20 pass; no regressions |

**TC→TT+REQ mapping table** (from TDD-SPEC §8 — apply exactly):

| TC ID | test_target_ref | requirement_ref |
|-------|----------------|----------------|
| TC-001 | TT-005 | REQ-005 |
| TC-002 | TT-005 | REQ-005 |
| TC-003 | TT-005 | REQ-006 |
| TC-004 | TT-005 | REQ-007 |
| TC-005 | TT-006 | REQ-008 |
| TC-006 | TT-007 | REQ-009 |
| TC-007 | TT-007 | REQ-009 |
| TC-008 | TT-007 | REQ-009 |
| TC-009 | TT-007 | REQ-009 |
| TC-010 | TT-002 | REQ-002 |
| TC-011 | TT-003 | REQ-003 |
| TC-012 | TT-004 | REQ-004 |
| TC-013 | TT-001 | REQ-001 |
| TC-014 | TT-008 | REQ-010 |
| TC-015 | TT-014 | REQ-015 |

*Note: Verify TC IDs against live testcases.yaml before running migration.*

### 3.2 MI-M-T D-09 Portability Pass (P1-critical, pending since D-08)

Delta ready: `_config/thinkpad-delta-D08-2026-04-30.tar.gz` (109K) — transfer required if not already applied.  
D-09 scope: portability pass on the 40-route FastAPI package — ensure Docker/compose-compatible, MySQL migration scripts validated, env vars externalised.

| Task | Notes |
|------|-------|
| Verify D-08 delta applied | `mi_m_t/` package, 40 routes, SQLAlchemy 2.x async |
| Run D-09 portability pass | External env vars, Docker healthcheck, MySQL migration dry-run |
| SMK9 on PostgreSQL | D-08 last run was SQLite; P1 requirement REQ-015 requires PostgreSQL green |
| Push thinkpad branch | `git push origin thinkpad` after D-09 complete |

### 3.3 Branch Authority Compliance (IMMEDIATE — before any push)

See KB-034 (`_config/KB-LESSONS-LEARNED.yaml`). ThinkPad force-pushed `macbook` branch twice on 2026-05-02. This is resolved but must not recur.

**Action required:**
1. Check local git remote config — confirm `origin` is the shared GitHub repo
2. Never `git push origin macbook` from ThinkPad
3. Only push to `origin thinkpad` from ThinkPad
4. GitHub branch protection rules being set up by user (MacBook branch: restrict push; ThinkPad branch: restrict push to MacBook)

### 3.4 kh-sim-ci.yml Reconciliation

The MacBook delta contains an updated `kh-sim-ci.yml` with hashFiles() guards. ThinkPad must:
1. Run `git diff HEAD _config/macbook-delta-2026-05-02.tar.gz:.github/workflows/kh-sim-ci.yml`
2. Keep ThinkPad-specific backend paths; add MacBook's guard conditions
3. Verify CI green on both branches after merge

---

## 4. ThinkPad Branch State (last known)

| Field | Value |
|-------|-------|
| Last known commit | `8ceff7f` |
| Branch | `thinkpad` |
| Primary scope | kh-sim backends, infra/docker, MI-M-T Python package |
| MI-M-T D-08 status | **DONE** — SMK9 20/20 PASS (SQLite, 2026-04-30) |
| D-09 status | **PENDING** — portability pass not yet done |
| testcases.yaml schema | v1 (migration to v2 not yet done) |
| triage.py version | Pre-D08 flags (no --req / --target / --matrix-req) |
| evidence-report.py version | Pre-D08 sections (no requirements / targets / traceability) |

---

## 5. Sync Protocol Reminder

```
Transfer method: USB / LAN-SSH / cloud — see _config/SYNC-BYPASS-MACBOOK-TO-THINKPAD.md
New delta: _config/macbook-delta-2026-05-02.tar.gz (49K)
Previous delta received: macbook-delta-2026-04-27.tar.gz (87K, 7 Opus files)
ThinkPad delta to MacBook: thinkpad-delta-D08-2026-04-30.tar.gz (109K) — not yet received
```

**Session sequence (recommended for ThinkPad next session):**
1. `git pull --rebase origin thinkpad` (get latest, do NOT touch macbook branch)
2. Apply `macbook-delta-2026-05-02.tar.gz` with correct merge strategy (§2 above)
3. Run MI-M-T-D08 ThinkPad scope (§3.1)
4. Run D-09 portability pass (§3.2)
5. Push `thinkpad` branch only: `git push origin thinkpad`
6. Build new thinkpad-delta-D09 and transfer to MacBook

---

*Last updated: 2026-05-02 | Device: MacBook*
