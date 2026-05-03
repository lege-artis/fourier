# OPUS-READING-LIST.md — Strategic Session Input Sequence
**For:** Opus cold-start strategic session — MI-M-T first production + demo deployment  
**Prepared:** 2026-05-02 | MacBook CoWork session  
**Commit:** `4979e6d` (macbook branch)

> Read files in the order below. Phase 1 is mandatory before forming any plan.  
> Files marked `[thinkpad]` require `git show origin/thinkpad:<path>` — they are not on the macbook branch.  
> Estimated total context load: ~5,000–6,000 lines across all phases.

---

## Phase 1 — Orientation (read first, in this order)

These three files establish the full project context and the session mandate. Read all of Phase 1 before touching anything else.

### 1.1 `_config/OPUS-SESSION-PREP-MI-M-T-PROD.md` — 465 lines
**The primary brief.** Self-contained strategic input written specifically for this session. Contains:
- §1: Project context — owner, three-fold-path ecosystem, deployment model, device workflow
- §2: Ecosystem AS-IS state — three sites live (zemla v1.7.5 / mim2000 v1.9.1 / bodyterapie v1.7.1), open bug summary, CI state
- §3: MI-M-T architecture + current build state (D-01..D-09 + T5/T6/T7 all DONE)
- §4: Open questions — §4.2 D-09 RESOLVED (OQ-029..034), §4.3 PHP layer IS implemented (D-07, gaps documented), §4.4 Active24 pre-flight blockers
- §5: Full task registry — open items with priority and device
- §6: Strategic goal + 4 deployment options + constraints + success definition
- §7: Reference file index
- §8: Expected Opus outputs

**Read this first. Everything else is evidence supporting the decisions §6 asks Opus to make.**

### 1.2 `CLAUDE.md` — 338 lines
**Project operating manual.** Contains:
- §PROJECT TOPOLOGY: three-fold-path sites, multilingual scope, shared master data (zemla-config.php)
- §LOAD ORDER: canonical file read sequence for any session restart
- §DEPLOYMENT RULE: Tier 1 (theme zip, user uploads) vs Tier 2 (Claude via FTP/TFE)
- §CURRENT STATE (as of 2026-05-02): live versions, MI-M-T dev layer table (D-01..D-09 + T5/T6/T7 all DONE), pending tasks list
- §KEY ARCHITECTURAL DECISIONS: ADR-01..04
- §HANDOFF BLOCK — 2026-05-02: ThinkPad D-09 close summary
- §DEVICES & SYNC: branch authority rules (KB-034), device table
- §DO NOT: hard constraints that must not be violated

### 1.3 `MANIFEST.yaml` — 213 lines
**Live version registry.** Contains current production versions, pending release queue, GitHub Releases inventory, MI-M-T section with DB engine test results. Cross-reference against OPUS-SESSION-PREP §2 to confirm no version drift.

---

## Phase 2 — Architecture Ground Truth

Read these to understand the system being planned for production deployment. The ARCH-SPEC is the canonical design contract; everything built (D-01..D-09) implements it.

### 2.1 `3-fold-path/backlog/MI-M-T-D08-TDD-SPEC.md` — 256 lines
**TDD three-tier schema contracts** (MacBook-authored, 2026-05-02). Defines:
- Three-tier traceability model: requirements.yaml → test-targets.yaml → testcases.yaml
- Schema v1.0.0 (requirements + test-targets) and v2.0.0 migration spec (testcases)
- §8: TC→TT+REQ mapping table (15 test cases × 2 foreign keys each) — the ThinkPad pending migration
- Acceptance criteria for triage.py / evidence-report.py tooling updates

**Why read it:** establishes the quality gate that production must satisfy (orphan-cases=0, traceability ≥15 rows).

### 2.2 `3-fold-path/evidence/requirements.yaml` — 292 lines
**17 acceptance requirements**, schema v1.0.0. Organised in four groups:
- REQ-001..004: ADR-derived (zemla-config.php, gallery DOM, album card, translations)
- REQ-005..011: Defect-regression requirements (podcast, CEO embeds, nav page_ids, New Perspective)
- REQ-012..015: MI-M-T API requirements (POST /projects, GET /testruns, GET /health, idempotency)
- REQ-016..017: Content/translation (CC-005 strings, ZEMLA_SLUG_* constants)

**Why read it:** REQ-012..015 are the production acceptance gate for MI-M-T MVP. Opus must plan against these explicitly.

### 2.3 `3-fold-path/evidence/test-targets.yaml` — 230 lines
**15 test targets**, schema v1.0.0. Each TT maps to one or more requirements and defines the observable behaviour under test. TT-001..008 cover MI-M-T API behaviour directly. Critical for defining "demo-ready" acceptance: a working demo must satisfy TT-001..008 at minimum.

### 2.4 `3-fold-path/code/SESSION-NOTES.md` — 875 lines (macbook branch, includes D-09)
**ThinkPad development log — D-01 through D-09.** Chronological record of every dev session. Key sections for Opus planning:
- §D-07: PHP API layer implementation details (17 files, public_html/ layout, route table)
- §D-08: Python FastAPI package structure (40 routes, SQLAlchemy 2.x async, Alembic, SMK9 first pass)
- §D-09: Portability pass — OQ-029..034 resolution details, all three DB engines green, PowerShell env injection, file changelog

**Read §D-07 carefully** — it documents the PHP layer structure that is the primary deployment vehicle for Option A.

---

## Phase 3 — Gap Analysis and Implementation State

These files define the delta between current build state and production-ready state. The Opus delivery plan must close these gaps.

### 3.1 `[thinkpad]` `3-fold-path/code/MI-M-T-PHP-ROUTE-AUDIT.md` — 226 lines
**T6 PHP Route Audit — the primary gap document** (ThinkPad, 2026-05-02).

Access via: `git show origin/thinkpad:3-fold-path/code/MI-M-T-PHP-ROUTE-AUDIT.md`

Contains:
- Full route inventory: PHP implementation completeness vs Python FastAPI (symbol key: ✅ IMPL / ⚠️ IMPL* / 🚫 501 / ❌ MISSING)
- §5.1.2 Projects: all 5 CRUD routes MISSING — `POST /api/v1/projects`, `GET /api/v1/projects`, `GET /api/v1/projects/{id}`, `PUT /api/v1/projects/{id}`, `DELETE /api/v1/projects/{id}`
- §5.1.1 Health: shape divergence — PHP returns `{status, service, ts}`, Python returns `{status, version, db_driver, db_status}` + HTTP 503 on failure
- §3 Portability analysis: `is_active = 1` integer literal issue for PG14 (low priority for MySQL MVP)
- §5.1.3..5.1.9: test targets, test cases, test runs, state machine, projects (MISSING) — per-section completeness tables

**This is the single most important technical input for the delivery plan.** Read in full before proposing any milestone plan.

### 3.2 `_config/KB-LESSONS-LEARNED.yaml` — 763 lines
**Cross-project lessons learned registry.** Relevant sections for Opus:
- KB-034/035: Branch authority violation lessons (ThinkPad force-pushed macbook — now has GitHub protection queue)
- LL-ENV-001..004: LDE environment lessons (KC health probe port, PHP version, Laragon config)
- LL-ENV-005..009: D-09 portability lessons (PowerShell env vars, PG port 5433, asyncpg lastrowid, boolean=1 vs TRUE, PG IDENTITY sequences)

**Skim only** — read LL-ENV-005..009 section for D-09 context, KB-034/035 for workflow constraints.

---

## Phase 4 — Evidence Data (reference, read if needed)

These files define the test coverage and bug state. Read if planning the evidence/traceability milestone. Can be skipped for pure architecture/deployment planning.

### 4.1 `[thinkpad]` `3-fold-path/evidence/testcases.yaml`
**15 manual test cases** (schema v1 — v2 migration pending). TC-001..015 cover podcast player, CEO blog embeds, gallery, translations, zemla-config, mim2000 nav, SMK9 idempotency.

Access via: `git show origin/thinkpad:3-fold-path/evidence/testcases.yaml`

Note: v1 schema — missing `test_target_ref` and `requirement_ref` fields. Mapping table in TDD-SPEC §8.

### 4.2 `[thinkpad]` `3-fold-path/evidence/bugs.yaml`
**24 bugs** (schema v0.1.0): 12 reported, 3 fixed, 6 closed, 1 verified, 2 fix-in-progress.

Access via: `git show origin/thinkpad:3-fold-path/evidence/bugs.yaml`

Note: both bugs.yaml and testcases.yaml live on the thinkpad branch only — they are ThinkPad-authored evidence and are excluded from the macbook branch by the sync-cleanup step (Phase 2 of macbook-git-sync script).

---

## Phase 5 — Interface Contracts (reference only)

Read only if the delivery plan includes JIRA or Postman integration work. Not required for MVP planning.

### 5.1 `3-fold-path/backlog/MI-M-T-D03-JIRA-CONTRACT.md`
JIRA Cloud REST API v3 bidirectional interface contract (v0.1.0). Defines JiraAdapter I/O surface.

### 5.2 `3-fold-path/backlog/MI-M-T-D04-POSTMAN-CONTRACT.md`
Postman/Newman interface contract (v0.1.0). Defines PostmanAdapter I/O surface.

---

## Files to Skip

| File | Reason |
|------|--------|
| `TASKS-shared.yaml` (2317 lines) | Too large for cold-start. MI-M-T section already summarised in OPUS-SESSION-PREP §5. Read only if a specific task ID needs resolution. |
| `3-fold-path/backlog/PROJECT-PLAN-3fold-path-active-backlog.md` | Sprint state for 3-fold-path sites. Not relevant to MI-M-T production planning. |
| `3-fold-path/backlog/EPIC-ARCH-01-architecture-revision.md` | Parked epic. Not relevant to MI-M-T session. |
| `_config/SESSION-LIFECYCLE-SOP.md` | Session ops manual. Not relevant to strategic planning. |
| `queue-macbook.yaml` | Current MacBook task queue. Not needed for Opus — use OPUS-SESSION-PREP §5 instead. |
| `_config/GITHUB-TOKEN-POLICY.md` | Token budget rules. Already summarised in OPUS-SESSION-PREP §6.2 constraints. |
| `_config/SYNC-BYPASS-MACBOOK-TO-THINKPAD.md` | Inter-device sync protocol. Operational, not strategic. |

---

## Quick-Reference: Key Numbers

| Metric | Value |
|--------|-------|
| DB migrations | 29 (000-102), all engines green |
| Python FastAPI routes | 40 (D-08) |
| PHP API routes | 31 API + 14 HTML (D-07) |
| PHP routes MISSING | 5 (`/api/v1/projects` CRUD) |
| SMK9 test cases | 20 (pytest, T7) |
| SMK9 result | 20/20 PASS on SQLite + MySQL8 + PG14 |
| Requirements | 17 (REQ-001..017) |
| Test targets | 15 (TT-001..015) |
| Test cases | 15 (TC-001..015, schema v1) |
| Bugs open | 12 reported (BUG-001..022 total, most closed) |
| Active24 unknowns | 4 (OQ-001/002/006/026) — must resolve before production apply |

---

*Prepared: 2026-05-02 | MacBook CoWork session | commit 4979e6d*
