# OPUS-SESSION-PREP — MI-M-T First Production + Demo Deployment
**Version:** v1.1.0  
**Prepared:** 2026-05-02 | MacBook CoWork session — updated post ThinkPad D-09 close  
**For:** Opus strategic planning session (cold-start — fully self-contained)  
**Goal:** Devise solution architecture and delivery plan for MI-M-T first production deployment + live demo on mim2000.cz

> **How to use this document:**  
> Read §1 (context) → §2 (ecosystem state) → §3 (MI-M-T architecture) → §4 (open questions) → §5 (task registry) → §6 (strategic goal) → §7 (constraints).  
> Then produce: delivery plan, phased milestones, risk register, device allocation, and next-session instructions.

---

## §1. Project Context

### 1.1 Owner
Petr Zemla (petr.yamyang@gmail.com). Sole developer + analyst. Dual-device workspace: MacBook (analytics/coordination) + ThinkPad (development/testing). All production sites run on Active24 shared hosting (Czech Republic).

### 1.2 Three-Fold-Path Ecosystem
Three interdependent WordPress sites on Active24 shared hosting (ftp.r4.websupport.sk):

| Site | Domain | Live version | Purpose |
|------|--------|-------------|---------|
| zemla | zemla.org | **v1.7.5** | Personal: psychology · buddhadharma · philosophy · blog · gallery · podcast |
| mim2000 | mim2000.cz | **v1.9.1** | Professional: teaching · consulting · MI-M-T prototype host |
| bodyterapie | bodyterapie.com | **v1.7.1** | Service: body therapy, somatic work, multilingual booking |

All themes share `inc/zemla-config.php` master identity file. Common PHP/CSS base. Multilingual: CS/EN/JA/DE/IT on zemla, subset on mim2000/bodyterapie.

**Deployment model (Tier 1/2):**
- Tier 1 (theme changes): user uploads complete theme .zip via WP Admin → Themes → Upload
- Tier 2 (content/config): Claude applies via WP Admin TFE or FTP

### 1.3 Dual-Device Workflow
| Device | Role | Branch | Last commit |
|--------|------|--------|-------------|
| MacBook | Analytics · coordination · deliverable authoring | `macbook` | `6f9c68a` (remote; local pending rebase) |
| ThinkPad | Development · testing · MI-M-T coding | `thinkpad` | `de0e98a` (D-09 + T5/T6/T7 closed) |

- Each device owns its branch exclusively; cross-device push is prohibited (KB-034)
- Sync via physical delta packages (`_config/macbook-delta-*.tar.gz`)
- Token budget: ~800 GitHub tokens/month; batch pushes at session boundaries

---

## §2. Ecosystem AS-IS State

### 2.1 Three-Fold-Path Site Health

**zemla.org (v1.7.5) — Current status:**
- Podcast player: fully operational (HOTFIX-ZP-004 closed all regressions — dual-init, speed drift, track restart)
- Gallery: ADR-02/03 compliant (sidebar+album-grid two-child pattern, vertical card 3:2)
- Translations: 5-locale (CS/EN/JA/DE/IT), 33 Physics DoF strings fixed, CC-005 patch applied
- Seed page template: added in v1.7.5
- Open bugs: BUG-001 (podcast archive CS heading), BUG-002 (podcast CTA), BUG-005..007 (blog categories/editing), BUG-008 (translation)

**mim2000.cz (v1.9.1) — Current status:**
- Design: dual-layer SVG (sandstone-sq + brushstone-sq), azure symbols, Ω↔0 corner swap
- Navigation: BUG-023 closed — cooperations=179, advisory-services=180, raw-dev-case-studies=181
- MI-M-T prototype page: page_id=176 at `mim2000.cz/projects/mi-m-t/` (live since 2026-04-28)
- BUG-024 fixed (2026-05-02): New Perspective link corrected in page-contacts.php
- Open bugs: BUG-013 (CEO blog layout), BUG-014 (JA translations), BUG-022 (CS bleed-through)

**bodyterapie.com (v1.7.1) — Current status:**
- Design: dual-layer SVG (sandstone-tri + brushstone-tri), azure symbols, fp-corner-nav
- Open bugs: BUG-015 (no blog section), BUG-016 (Gutenberg block duplication)

### 2.2 Open Bugs Summary

| ID | Sev | Pri | Site | Status | Title |
|----|-----|-----|------|--------|-------|
| BUG-001 | B | B | zemla | reported | Podcast archive CS heading: 'Archivy: Podcast Episodes' |
| BUG-002 | B | B | zemla | reported | Podcast archive CTA 'Read →' should be 'K poslechu →' |
| BUG-005 | A | B | zemla | reported | Blog posts all 'Uncategorized' despite WP taxonomy |
| BUG-006 | A | B | zemla | reported | 'New Post' → generic Gutenberg, no structure guidance |
| BUG-007 | A | B | zemla | reported | Blog content structure destroyed in Gutenberg edit rounds |
| BUG-008 | C | B | zemla | reported | 'Hračkové modely' wrong translation |
| BUG-013 | B | C | mim2000 | reported | CEO blog header layout messy all locales |
| BUG-014 | B | C | mim2000 | reported | CEO blog JA mechanical translations |
| BUG-015 | A | C | bodyterapie | reported | No blog section in theme |
| BUG-016 | B | C | bodyterapie | reported | Gutenberg block duplication on edit |
| BUG-017 | A | B | all | reported | Cross-site blog organisation inconsistency |
| BUG-022 | B | B | mim2000 | reported | CS content bleed-through in non-CS locale mutations |

*BUG-003/004/009/010/011/018/019/020/021/023/024 are closed/verified.*

### 2.3 CI/CD Pipeline State

| Workflow | Status | Location |
|----------|--------|----------|
| ci-heartbeat.yml | Green (all language backends) | `.github/workflows/ci-heartbeat.yml` |
| kh-sim-ci.yml | Green (hashFiles guards; backends skip if absent) | `.github/workflows/kh-sim-ci.yml` |
| kh-sim backends | Rust/Scala/C++/Fortran/Pascal + FastAPI simulation | ThinkPad branch |
| Auth suite | AUTH-001..006 done (KC OIDC, OAuth2, GitHub Actions OIDC) | ThinkPad branch |

---

## §3. MI-M-T Architecture and Current State

### 3.1 What MI-M-T Is

**MI-M-T = Meta Informed/Inferred/Integrated Measurement (which do) Testing.**
*(Reframed 2026-05-03 — supersedes earlier "Methodology for Integrated Manual Testing". MI-M-T is not a manual-test tool; it is a meta-informed measurement layer whose primary use is testing at every level — manual, scripted, recorded, and LLM-driven. See `_config/OPUS-CYCLE-v0.2-MASTER.md` §1 for full positioning and the three deployment modes.)*

A custom measurement-and-evidence platform designed to be:
- Hosted on Active24 shared hosting alongside the 3-fold-path sites
- Backed by MySQL (Active24) with SQLite for local dev
- Exposed as REST API (PHP thin layer on Active24 MVP; Python FastAPI for ThinkPad LDE)
- Integrable with JIRA (D03) and Postman (D04)
- The prototype page is already live at `mim2000.cz/projects/mi-m-t/`

**Conceptual model (4-step framework):**
1. **Impulse** — requirement / issue from JIRA, Postman collection, or manual entry
2. **Test Set** — iteration-scoped set of test cases derived from impulse
3. **Execution** — manual test run against a test set, recording pass/fail per case
4. **Evidence** — structured proof-of-test artifact linked to deployment

### 3.2 ARCH-SPEC v0.1.0 — What Was Designed (Opus D07 Session)

Nine deliverables produced in Opus inception session (2026-04-27):

| Deliverable | File | Content |
|-------------|------|---------|
| D1 — Full DDL | MI-M-T-ARCH-SPEC §1 | 25 tables, canonical type vocabulary, portability tokens |
| D2 — ERD | MI-M-T-ARCH-SPEC §2 | PlantUML ER diagram, entity relationships |
| D3 — Field spec | MI-M-T-ARCH-SPEC §3 | Column-level spec per table |
| D4 — State machine DDL | MI-M-T-ARCH-SPEC §4 | 12-state lifecycle, seed data |
| D5 — REST API surface | MI-M-T-ARCH-SPEC §5 | ~40 routes, request/response schemas |
| D6 — PHP thin layer | MI-M-T-ARCH-SPEC §6 | Active24 PHP 8.x implementation spec, directory layout |
| D7 — Python FastAPI | MI-M-T-ARCH-SPEC §7 | FastAPI layout, SQLAlchemy 2.x async, Alembic |
| D8 — Migration strategy | MI-M-T-ARCH-SPEC §8 | runner.py + runner.php, token substitution, portability matrix |
| D9 — Open questions | MI-M-T-ARCH-SPEC §9 | 27 open questions (Active24 env, hosting, language choices) |

**Supporting docs in `3-fold-path/backlog/`:**
- `MI-M-T-ARCH-ANALYSIS-v0.1.md` — CAST 2.4.03 decomposition (717 lines)
- `MI-M-T-ARCH-MODELS-v0.1.md` — UML class models
- `MI-M-T-ARCH-TAGS-v0.1.md` — service/data/trigger tags on every endpoint
- `MI-M-T-MOCK-FIXTURES-v0.1.md` — test fixture data
- `MI-M-T-D03-JIRA-CONTRACT.md` — JIRA Cloud REST API v3 interface contract
- `MI-M-T-D04-POSTMAN-CONTRACT.md` — Postman/Newman interface contract
- `MI-M-T-D08-TDD-SPEC.md` — TDD three-tier spec (NEW 2026-05-02)

### 3.3 What Is Built (ThinkPad D-01 through D-08)

ThinkPad Dev Sonnet sessions delivered:

| Iteration | Scope | Status |
|-----------|-------|--------|
| D-01 | DB schema migrations (25 tables), runner.py + runner.php, portability matrix | **DONE** |
| D-02 | Adapter interface + base_adapter.py, 43/43 smoke PASS | **DONE** |
| D-03 | JiraAdapter implementation + JIRA Cloud REST API v3 contract | **DONE** |
| D-04 | PostmanAdapter implementation + Newman interface contract | **DONE** |
| D-05 | mim2000.cz prototype page (page_id=176) live | **DONE** |
| D-06 | MI-M-T-ARCH-ANALYSIS-v0.1.md (717 lines, CAST decomposition) | **DONE** |
| D-07 | Opus inception session — 6 artifacts, 8324 lines | **DONE** (MacBook) |
| D-08 | Python FastAPI package: 40 routes, SQLAlchemy 2.x async. SMK9 20/20 PASS (SQLite) | **DONE** (ThinkPad) |
| D-08 schemas | requirements.yaml (17 REQs) + test-targets.yaml (15 TTs) — TDD three-tier model | **DONE** (MacBook) |
| D-09 | Portability pass: env vars externalised, Docker healthcheck; MySQL8 29/29 migrations + SMK9 20/20 PASS; PG14 29/29 migrations + SMK9 20/20 PASS. OQ-029..034 resolved (UTC datetime, {{BOOL_TRUE}} token, PG identity reset, DateTime/String(30), asyncpg lastrowid, is_active PG literal). | **DONE** (ThinkPad, 2026-05-02) |
| T5 | Health endpoint DB probe: `/health` now reports live DB engine (SQLite/MySQL/PG) in response body | **DONE** (ThinkPad, 2026-05-02) |
| T6 | PHP Route Audit: completeness check Python FastAPI vs PHP thin layer — 5 gap categories found | **DONE** (ThinkPad, 2026-05-02) |
| T7 | pytest SMK9 suite: `tests/conftest.py` + `tests/test_smk9.py` (20 test functions) replacing smoke_test.py script | **DONE** (ThinkPad, 2026-05-02) |

### 3.4 TDD Evidence Layer — AS-IS State

The MI-M-T project uses its own tooling to track its own development (dogfooding):

**Three-tier model (introduced D-08):**
```
requirements.yaml     — 17 requirements (REQ-001..017), schema v1.0.0
    └── test-targets.yaml  — 15 test targets (TT-001..015), schema v1.0.0
            └── testcases.yaml  — 15 test cases, currently schema v1 (v2 migration PENDING)
                    └── testruns/  — execution records
```

**requirements.yaml (17 REQs):**
- REQ-001..004: ADR-derived (identity config, gallery DOM, album card, translations)
- REQ-005..011: Defect-regression (podcast double-init/speed/skip/cover art, CEO embeds, nav page_ids, New Perspective)
- REQ-012..015: mi_m_t API (POST /projects, GET /testruns, GET /health, idempotency)
- REQ-016..017: Content/translation (CC-005 strings, ZEMLA_SLUG_* constants)

**testcases.yaml (15 TCs, schema v1 — migration to v2 pending ThinkPad):**
- TC-001..005: Podcast player (init, audio, speed hold, skip, cover art)
- TC-006..009: mim2000 CEO blog (CS/DE/IT/EN YouTube embed)
- TC-010..011: Gallery (sidebar structure, album card)
- TC-012..015: Translation, zemla-config, mim2000 nav, SMK9 idempotency

**bugs.yaml (24 bugs, schema v0.1.0):**
- 12 reported, 3 fixed, 6 closed, 1 verified, 2 fix-in-progress
- Sites: zemla×12, mim2000×7, bodyterapie×2, all×1

### 3.5 Target Deployment Architecture for Production

**MVP target (Active24 shared hosting):**
```
Active24 mim2000.cz hosting
├── wp-content/themes/mim2000-theme-v*/
│   └── mi-m-t/           ← PHP thin layer (ARCH-SPEC §6)
│       ├── api/           ← REST endpoints (PHP handlers)
│       ├── migrations/    ← SQL + runner.php
│       └── public/        ← SPA shell or minimal UI
└── MySQL 8.0 database     ← 25-table schema
```

**LDE (Local Dev Environment, ThinkPad):**
```
ThinkPad Laragon (Windows)
├── Python FastAPI (port 8000)   ← mi_m_t/ package (D-08)
├── SQLite (dev) / MySQL (test)
├── Alembic migrations
└── SMK9 smoke suite
```

**Open questions for production (from ARCH-SPEC §9):**
- Q01: Active24 MySQL exact version (affects JSON/CHECK/charset)
- Q02: Active24 PHP version + extensions (pdo_mysql, mbstring, json, openssl)
- Q06: Active24 SSH access (controls migration apply method — CLI vs HTTP runner)
- Q07: ThinkPad Laragon stack parity (PHP CLI version, MySQL version)
- Q09: Production language decision (Scala/Rust/C# — out of MVP scope)
- Q10: Production hosting decision (on-prem/private cloud/AWS — out of MVP scope)

### 3.6 Demo Deployment Vision

The "first production + demo" target means:
1. A working MI-M-T instance accessible at `mim2000.cz/projects/mi-m-t/` (already live as prototype page)
2. MySQL schema deployed on Active24 (25 tables from D-08 migrations)
3. PHP thin layer serving REST API endpoints
4. Basic UI showing: project list, test targets, test cases, test runs
5. At least one "seed demo project" pre-loaded (ARCH-SPEC §8: `200_seed_demo_project.sql`)
6. JIRA and/or Postman integration demonstrable in a controlled scenario

---

## §4. Open Questions Requiring Strategic Resolution

### 4.1 Architecture decisions (must resolve for production)

| OQ# | Question | Impact | Current status |
|-----|----------|--------|---------------|
| OQ-001 | Active24 MySQL exact version | JSON columns, CHECK enforcement | Open — check via PHPMyAdmin |
| OQ-002 | Active24 PHP version + extensions | PHP syntax ceiling, PDO availability | Open — check via phpinfo() |
| OQ-006 | Active24 SSH access | Migration apply method (CLI vs HTTP runner) | Open — check Active24 plan |
| OQ-009 | Production language (PHP vs Python vs other) | ORM, build pipeline, hosting | Strategic decision deferred |
| OQ-010 | Production hosting topology | Scale, secret management | Strategic decision deferred |
| OQ-020 | Migration runner on Active24 (PHP CLI vs HTTP-admin) | Deployment ergonomics | PHP HTTP runner with shared-secret guard for MVP |

### 4.2 D-09 portability — RESOLVED (2026-05-02)

All three DB engines are now green end-to-end:

| Engine | Migrations | SMK9 | Notes |
|--------|-----------|------|-------|
| SQLite | 29/29 | 20/20 PASS | D-08 baseline |
| MySQL 8.0 | 29/29 | 20/20 PASS | D-09 fixed OQ-030, OQ-032, OQ-034 |
| PostgreSQL 14 | 29/29 | 20/20 PASS | D-09 fixed OQ-029, OQ-031, OQ-033 |

**OQ-029..034 resolutions (documented in SESSION-NOTES.md D-09 section):**
- OQ-029: Naive UTC datetime — added `timezone.utc` to all `datetime.now()` calls
- OQ-030: `{{BOOL_TRUE}}` token — migration runner substitution for MySQL `TRUE` literal
- OQ-031: `reset_pg_identity_sequences()` — PG identity column reset after seed data
- OQ-032: `DateTime` vs `String(30)` — SQLAlchemy type mapping normalised
- OQ-033: asyncpg `lastrowid` — replaced with `RETURNING id` pattern for PG
- OQ-034: `is_active = true` — PG boolean literal fix in value-list queries

**Environment:** Docker Compose (ThinkPad LDE), env vars externalised to `.env` files, DB_ENGINE switch controls which adapter loads.

### 4.3 PHP thin layer — IMPLEMENTED with gaps (D-07, 2026-04-29)

ARCH-SPEC §6 PHP thin layer is **implemented**: 17 files in `public_html/mi-m-t/`, 31 API + 14 HTML routes per ARCH-SPEC §6. This was delivered in D-07 (2026-04-29) prior to the FastAPI D-08 work.

**T6 PHP Route Audit findings (2026-05-02) — gaps vs Python FastAPI:**

| Gap | Category | Routes affected | Severity |
|-----|----------|----------------|---------|
| `/api/v1/projects` | All 5 CRUD routes MISSING from PHP | POST /projects, GET /projects, GET /projects/{id}, PUT /projects/{id}, DELETE /projects/{id} | **HIGH — blocks demo** |
| `/health` shape divergence | PHP returns `{"status":"ok"}`, Python now returns DB engine info (T5) | 1 route | MEDIUM |
| `is_active = 1` | PHP uses MySQL `1`; PG portability requires `TRUE` literal or adapter switch | Multiple routes | LOW (MySQL-only deploy OK for MVP) |
| Test targets | 7 routes all implemented ✓ | — | OK |
| Test cases + runs | Implemented ✓ | — | OK |

**Strategic implication:** The 5 missing `/api/v1/projects` routes are the primary PHP gap blocking demo-ready state. This is the **key implementation task** for Active24 MVP deployment (not a "new layer" — it's a targeted extension to existing PHP code).

**For Opus to resolve:** Active24 deployment via PHP thin layer is the most viable path (Option A). The gap is bounded (5 routes + /health sync), not a greenfield implementation.

### 4.4 Active24 environment unknowns (pre-flight blockers)

| OQ# | Question | Probe method | Status |
|-----|----------|-------------|--------|
| OQ-001 | Active24 MySQL exact version | PHPMyAdmin `SELECT VERSION()` | Open |
| OQ-002 | Active24 PHP version + extensions | Upload phpinfo() probe script | Open |
| OQ-006 | Active24 SSH access | Check Active24 control panel plan | Open |
| OQ-026 | PHP syntax ceiling on Active24 | Can now validate on ThinkPad PHP CLI first | Open (probing available) |

These three OQs must be resolved before running migrations on Active24. ThinkPad can probe OQ-026 locally first as a dry run.

---

## §5. Full Task Registry — Open Items

### 5.1 MI-M-T Development Track (primary focus)

| ID | Priority | Device | Status | Description |
|----|----------|--------|--------|-------------|
| MI-M-T-D09 | P1 | ThinkPad | **DONE** 2026-05-02 | Portability pass: env vars externalised, Docker, MySQL8+PG14 SMK9 20/20 |
| MI-M-T-T5 | P1 | ThinkPad | **DONE** 2026-05-02 | /health DB probe endpoint — reports live engine in response |
| MI-M-T-T6 | P1 | ThinkPad | **DONE** 2026-05-02 | PHP Route Audit — gap analysis vs Python FastAPI (5 gaps found) |
| MI-M-T-T7 | P1 | ThinkPad | **DONE** 2026-05-02 | pytest SMK9 suite (tests/conftest.py + tests/test_smk9.py, 20 functions) |
| MI-M-T-SMK9-POSTGRES | P1 | ThinkPad | **DONE** 2026-05-02 | SMK9 on PostgreSQL 14 — 20/20 PASS (D-09 scope, REQ-015 satisfied) |
| MI-M-T-D08-TP | P1 | ThinkPad | PENDING | testcases.yaml v1→v2 migration, triage.py + evidence-report.py updates per TDD-SPEC §8 |
| MI-M-T-PROD-PLAN | P1 | MacBook/Opus | NEW | **This session's output** — delivery plan for first production deploy |
| MI-M-T-PHP-PROJECTS | P1 | ThinkPad | PENDING | Add 5 missing /api/v1/projects CRUD routes to PHP thin layer (T6 gap) |
| MI-M-T-PHP-HEALTH-SYNC | P2 | ThinkPad | PENDING | Sync /health response shape: PHP → match Python T5 DB probe format |
| MI-M-T-ACTIVE24-PROBE | P1 | ThinkPad | PENDING | Resolve OQ-001/002/006/026: MySQL version, PHP extensions, SSH, syntax ceiling |
| MI-M-T-MYSQL-DEPLOY | P1 | ThinkPad | PENDING | Deploy 25-table schema to Active24 MySQL (migration runner after OQ probe) |
| MI-M-T-DEMO-SEED | P2 | ThinkPad | PENDING | Seed demo project data (200_seed_demo_project.sql) |
| MI-M-T-UI-MVP | P2 | ThinkPad | PENDING | Minimal read-only UI: project list → test targets → test cases |
| MI-M-T-P06 | P2 | ThinkPad | PENDING | First testrun: mim2000 CEO blog (unblocked after delta transfer) |

### 5.2 R3 Release Gate — MI-M-T Initial Release

The R3 milestone requires:
- [x] MI-M-T-D01 — DB schema migrations
- [x] MI-M-T-D02 — Adapter interface
- [x] MI-M-T-D03 — JIRA interface contract + adapter
- [x] MI-M-T-D04 — Postman interface contract + adapter
- [x] MI-M-T-D05 — Prototype page live on mim2000.cz
- [x] MI-M-T-D07 — PHP thin layer implemented (17 files, 31 API + 14 HTML routes)
- [x] MI-M-T-D08 — Python FastAPI (40 routes, SQLite 20/20 PASS)
- [x] MI-M-T-D09 — Portability pass (MySQL8 20/20 + PG14 20/20 PASS)
- [ ] MI-M-T-PHP-PROJECTS — 5 missing /projects CRUD routes in PHP
- [ ] MI-M-T-ACTIVE24-PROBE — OQ-001/002/006/026 environment resolution
- [ ] MI-M-T-MYSQL-DEPLOY — Schema on Active24 MySQL (25 tables)
- [ ] MI-M-T-UI-MVP — Minimal usable UI

### 5.3 Three-Fold-Path Site Track (ongoing)

| ID | Priority | Status | Description |
|----|----------|--------|-------------|
| CC-006 | P3 | Open | Add 5 ZEMLA_SLUG_* constants (REQ-017) |
| BUG-005/006/007 | P2 | Reported | Blog categories + editing flow (zemla) |
| BUG-022 | P2 | Reported | CS content bleed-through in mim2000 locale mutations |
| BUG-017 | P2 | Reported | Cross-site blog organisation inconsistency |
| BUG-015 | P3 | Reported | bodyterapie.com: no blog section |
| ARCH-E01 | P2 | Parked | Architecture revision epic (full scope) |
| MOB-E01 | P3 | Blocked | Mobile optimisation (blocked on ARCH-E01) |
| PIL-07 | P2 | Pending | Podcast pilot harness on ep00 real stems |
| AUTH-004 | P3 | Pending | WordPress OAuth2.0 SSO plugin |

### 5.4 Infrastructure / CI Track (ThinkPad primary)

| ID | Priority | Status | Description |
|----|----------|--------|-------------|
| AUTH-005 | P2 | Pending | GitHub Actions OIDC token integration |
| AUTH-006 | P2 | Pending | Auth integration smoke tests (49 tests) |
| PINN-002..009 | P3 | Pending | PINN solver service (physics-informed neural nets) |
| TF-001..007 | P3 | Pending | TensorFlow integration connectors |
| KH-008..013 | P3 | Blocked | kh-sim React F/E pages per language |

### 5.5 Deferred / Parked

| ID | Priority | Notes |
|----|----------|-------|
| SYMB-002..005 | Deferred | Julia/Clojure symbolic reasoning layer |
| GR-001..002 | Deferred | GR test-case framework + Minkowski space test case |
| KH-VAL | Deferred | Validation hardening on kh-sim |
| ARCH-E01 | Parked | Full architecture revision — requires dedicated sprint |

---

## §6. Strategic Goal for Opus Session

### 6.1 Primary mandate
**Design the delivery plan for MI-M-T first production deployment + live demo on mim2000.cz.**

This means Opus must resolve:

1. **Architecture decision**: How does MI-M-T run on Active24 shared hosting?
   - **Option A: PHP thin layer on Active24** (as per ARCH-SPEC §6) — layer already exists; only 5 /projects routes missing + OQ-001/002/006 Active24 env must be resolved. **Most viable for MVP.**
   - Option B: Python FastAPI on a cheap VPS (Hetzner/DigitalOcean), reverse-proxied or CORS-opened, called from mim2000.cz frontend — requires VPS provisioning, HTTPS config, ongoing cost
   - Option C: Hybrid — PHP handles auth + DB on Active24, FastAPI handles complex queries on VPS
   - Option D: Static SPA on mim2000.cz calling FastAPI on ThinkPad (dev/demo only, not production)
   
   **Bias going in:** Option A is significantly more attainable than when originally analysed. PHP thin layer is implemented (D-07); 5 missing routes is bounded, estimable work. Remaining blocker is Active24 environment probe (OQ-001/002/006).

2. **Phase plan**: What are the milestones from current state (D-09 MySQL8+PG14 done, PHP layer implemented with 5-route gap) to first production deploy?

3. **Device allocation**: Which device handles which iteration?

4. **Demo definition**: What exactly is "demo-ready"? Minimum viable feature set?

5. **Active24 unknowns (OQ-001/002/006)**: Plan to resolve before production apply.

6. **Risk register**: What are the top-5 risks and mitigations?

### 6.2 Constraints Opus must respect

| Constraint | Detail |
|-----------|--------|
| Active24 shared hosting | No Docker, no SSH (likely), no server-side cron (likely), PHP 8.x + MySQL 8.0 |
| No Composer on Active24 | vendor/ must be built locally (ThinkPad) and uploaded |
| Token budget | ~800 GitHub tokens/month; batch pushes only |
| Dual-device sync | Physical delta packages only; no real-time collab |
| Branch authority | ThinkPad: `thinkpad` only. MacBook: `macbook` only. No cross-push. |
| No new credentials | mim2000.cz WP Admin: `mim.admin` / `Proper_314_admin_likes_Tea` (do not share outside session) |
| Pilot/demo-first | No full JIRA/Postman integration needed for demo; seed data + basic CRUD sufficient |
| MI-M-T full stack | Python FastAPI (40 routes) + PHP thin layer (17 files, 31 API + 14 HTML routes) both implemented. All 3 DB engines green: SQLite + MySQL8 + PG14 (SMK9 20/20 PASS each). PHP has 5 /projects routes missing. |

### 6.3 What success looks like

**Minimum demo-ready state:**
- `mim2000.cz/projects/mi-m-t/` shows a real MI-M-T interface (not just a prototype page)
- At least one project visible with test targets and test cases populated
- At least one test run logged with pass/fail evidence
- BUG-024 (New Perspective link): ✓ **already fixed** (2026-05-02)
- PHP API responding at `mim2000.cz/projects/mi-m-t/api/health` with `{"status":"ok"}` (at minimum; T5-aligned response with DB engine is a nice-to-have)
- `/api/v1/projects` CRUD routes implemented in PHP (5 missing routes — the critical gap)

**Production-ready additional requirements:**
- MySQL schema applied on Active24 (all 25 tables)
- Migration runner (PHP HTTP or CLI depending on OQ-006 resolution)
- Auth: at minimum shared-secret on admin endpoints, or WP session integration
- Backup posture documented (Active24 scheduled backups + restore runbook)

---

## §7. Key Reference Files (read before planning)

The following files are the canonical inputs. All exist in the repository at the paths shown.

| File | Location | Purpose |
|------|----------|---------|
| ARCH-SPEC v0.1.0 | `3-fold-path/backlog/MI-M-T-ARCH-SPEC-v0.1.md` | Full DDL, API, PHP/Python specs, migration strategy |
| ARCH-ANALYSIS | `3-fold-path/backlog/MI-M-T-ARCH-ANALYSIS-v0.1.md` | CAST decomposition, component graph |
| ARCH-MODELS | `3-fold-path/backlog/MI-M-T-ARCH-MODELS-v0.1.md` | UML class models |
| ARCH-TAGS | `3-fold-path/backlog/MI-M-T-ARCH-TAGS-v0.1.md` | Service/data/trigger tags per endpoint |
| D03-JIRA-CONTRACT | `3-fold-path/backlog/MI-M-T-D03-JIRA-CONTRACT.md` | JIRA Cloud REST API v3 interface contract |
| D04-POSTMAN-CONTRACT | `3-fold-path/backlog/MI-M-T-D04-POSTMAN-CONTRACT.md` | Postman/Newman interface contract |
| D08-TDD-SPEC | `3-fold-path/backlog/MI-M-T-D08-TDD-SPEC.md` | TDD three-tier model schema contracts |
| OPEN-QUESTIONS-LOG | `3-fold-path/backlog/OPEN-QUESTIONS-LOG.md` | 27 open questions, Active24 env blockers |
| DEV-SONNET-INSTRUCTIONS | `3-fold-path/backlog/DEV-SONNET-INSTRUCTIONS-v0.1.md` | ThinkPad Dev Sonnet operating manual |
| requirements.yaml | `3-fold-path/evidence/requirements.yaml` | 17 acceptance requirements |
| test-targets.yaml | `3-fold-path/evidence/test-targets.yaml` | 15 test targets |
| bugs.yaml | `3-fold-path/evidence/bugs.yaml` | 24 bugs, schema v0.1.0 |
| testcases.yaml | `3-fold-path/evidence/testcases.yaml` | 15 test cases, schema v1 |
| SESSION-NOTES.md | `3-fold-path/code/SESSION-NOTES.md` | ThinkPad D-01 through D-09 session notes (includes OQ-029..034 resolution details) |
| PHP-ROUTE-AUDIT | `3-fold-path/code/MI-M-T-PHP-ROUTE-AUDIT.md` | T6 audit: PHP vs Python route completeness; gap table per section |
| TASKS-shared.yaml | `TASKS-shared.yaml` | 80+ canonical task registry |
| CLAUDE.md | `CLAUDE.md` | Full session context; read first |
| MANIFEST.yaml | `MANIFEST.yaml` | Live versions, pending releases |

---

## §8. Expected Opus Session Outputs

1. **Production deployment architecture decision** — chosen option (A/B/C/D) with rationale
2. **Phased delivery plan** — milestones M1..Mn with:
   - What gets built in each milestone
   - Device allocation (MacBook vs ThinkPad per task)
   - Acceptance criteria per milestone
   - Estimated session count
3. **Active24 pre-flight checklist** — OQ resolution sequence (what ThinkPad checks first, in what order)
4. **Demo definition document** — exact feature set, seed data, URL structure, auth model
5. **Risk register** — top-5 risks with likelihood, impact, mitigation
6. **Next session instructions** — ThinkPad: PHP /projects routes (5) + Active24 probe + MySQL deploy. MacBook: testcases.yaml v2 migration brief + coordination
7. **Updated TASKS-shared.yaml entries** — new tasks for production track (MI-M-T-D10..D-NN)

---

*Prepared: 2026-05-02 | MacBook CoWork session | v1.0.0 → v1.1.0 updated post ThinkPad D-09 close*
