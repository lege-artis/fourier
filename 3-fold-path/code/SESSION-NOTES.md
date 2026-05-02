# SESSION-NOTES.md — MI-M-T Dev Sonnet
## Device: ThinkPad (CoWork / Claude Sonnet 4.6)

---

## D-01 environment

**Captured:** 2026-04-27

```
Python 3.10.12
sqlite3 module:      3.37.2
sqlalchemy:          2.0.49
alembic:             1.18.4
pymysql:             1.4.6
psycopg2:            2.9.12 (dt dec pq3 ext lo64)
PHP:                 NOT AVAILABLE (no sudo / no php binary in sandbox)
MySQL (socket):      Connection refused 127.0.0.1:3306
MySQL (alt port):    Connection refused 127.0.0.1:3307
PostgreSQL (socket): Connection refused 127.0.0.1:5432
sqlite3 CLI:         NOT AVAILABLE (Python module used instead)
mysql CLI:           NOT AVAILABLE
psql CLI:            NOT AVAILABLE
```

**Status:** Python toolchain complete. PHP + MySQL server + PostgreSQL server not available
in this sandbox. OQ-026 (PHP binary) and OQ-027 (MySQL/PostgreSQL servers) raised below.
SQLite validation proceeds via Python `sqlite3` module — sufficient for D-01.

---

## D-01 input read confirmation

Canonical types in use per ARCH-SPEC §0.3: all DDL uses token vocabulary `{{PK_BIGINT_AUTOINC}}`,
`{{TABLE_OPTIONS}}`, `{{JSON_TYPE}}`, `{{BOOL_TYPE}}`, `{{TS_TYPE}}`; no bare `BIGINT AUTO_INCREMENT`
or dialect-specific syntax in migration files. The state-machine algorithm (12-state lifecycle,
ARCH-SPEC §6 / DEV-SONNET-INSTRUCTIONS §6) is not yet implemented in D-01 (first iteration is
the runner itself); it will be mirrored in PHP (PDO + token substitution) and Python (Alembic
`op.execute()` wrapping raw SQL) starting D-02 onwards. The portability matrix — MySQL 8.0 /
PostgreSQL 14 / SQLite 3.38 — is kept green by the token replacement map defined in ARCH-SPEC §8.3
and enforced at apply time by both `runner.py` and `runner.php`; no engine-specific syntax escapes
into migration SQL files.

---

## D-01 plan

Create `code/migrations/000_create_schema_migrations.sql` (tracking table, token-parametrised),
`code/migrations/runner.py` (Python CLI; wraps raw SQL via SQLAlchemy `text()`, Alembic env also
wired), and `code/migrations/runner.php` (PHP 8.x PDO CLI + HTTP-triggered variant). Validate
SQLite path in sandbox via Python `sqlite3` module. Surface PHP/MySQL/PG gaps as OQ-026 and
OQ-027. Record results here.

---

## D-01 matrix results

### SQLite — Python sqlite3 module

```
PASS — all three checks (apply, idempotency, drift-abort)

--- Run 1: first apply ---
MI-M-T migration runner v0.1.0
Engine : sqlite
DB URL : sqlite:////…/.test/d01.sqlite

  [000] APPLIED — create schema migrations (13ms, sha256=82dc923fc19c…)

Done. applied=1 skipped=0 aborted=0

schema_migrations contents:
  version  applied_at             sha256_hex[:16]    description
  -------- ---------------------- ------------------ ----------------------------------------
  000      2026-04-27T20:07:01Z   82dc923fc19c49ff…  create schema migrations

--- Run 2: idempotency (re-apply same file) ---
  [000] SKIP  — already applied, hash matches.
Done. applied=0 skipped=1 aborted=0

--- Run 3: drift detection (UP section tampered) ---
  ABORT: DRIFT DETECTED for version 000:
    recorded sha256=82dc923fc19c…
    file sha256=65622e29afeb…
    — refusing apply (ARCH-SPEC §8.4).
Exit code: 1
```

### MySQL 8.0 — Laragon (ThinkPad)

```
BLOCKED — OQ-026 / OQ-027: MySQL server not running in sandbox.
Action: run runner.py --engine mysql on ThinkPad Laragon instance.
```

### PostgreSQL 14 — Docker (ThinkPad)

```
BLOCKED — OQ-027: PostgreSQL container not running in sandbox.
Action: docker compose up -d postgres, then runner.py --engine postgres.
```

---

## D-01 commit message

```
feat(migrations): D-01 — migration runner + schema_migrations table (SQLite PASS)

Deliverables
────────────
• code/migrations/000_create_schema_migrations.sql
    Token-parametrised DDL for schema_migrations tracking table.
    Constraint name: pk_schema_migrations.
    Columns: version VARCHAR(20) PK, description VARCHAR(255),
             applied_at DATETIME (UTC), applied_by VARCHAR(100),
             sha256_hex CHAR(64), duration_ms INT.
    Citation: ARCH-SPEC §8.4 (DDL) + §8.3 (token table) + §0.3 (canonical types).
    Tags: [μS-CAND][TRIG-REQ][CRIT-AUDIT] — per ARCH-TAGS §1.

• code/migrations/runner.py
    Python 3.10 CLI using argparse + SQLAlchemy 2.x (engine-per-dialect).
    Token substitution via str.replace for the 5 canonical tokens.
    SHA-256 drift detection: refuses re-apply if hash changes.
    --engine {sqlite,mysql,postgres} + --db-url override.
    Alembic env.py wired to call runner.apply_pending().
    Citation: ARCH-SPEC §8.5 runner contracts + §8.3 token table.
    Tags: [μS-CAND][TRIG-REQ][CRIT-AUDIT].

• code/migrations/runner.php
    PHP 8.x PDO-based runner (CLI + HTTP-triggered variants).
    Same token substitution logic; writes schema_migrations row.
    Drift detection identical to Python runner.
    Citation: ARCH-SPEC §8.5 + DEV-SONNET-INSTRUCTIONS §3 (Active24 target).
    Tags: [μS-CAND][TRIG-REQ][CRIT-AUDIT].

Tests passing
─────────────
• SQLite: schema_migrations created + self-record inserted (Python sqlite3 PASS).
• MySQL: BLOCKED — OQ-027 (server not running in sandbox).
• PostgreSQL: BLOCKED — OQ-027 (server not running in sandbox).

Design citations
────────────────
• No ENUM / triggers / stored procs / window functions / ON UPDATE — ARCH-SPEC §0.4.
• schema_migrations.applied_at stored as UTC TEXT in SQLite (ISO-8601), DATETIME in MySQL,
  TIMESTAMP in PostgreSQL — via {{TS_TYPE}} token substitution.
• Runner idempotency: skip if version present with matching sha256_hex; abort if hash differs.
• File naming: 000_create_schema_migrations.sql — ARCH-SPEC §8.1.
• Header comment tags on runner files: [μS-CAND][TRIG-REQ][CRIT-AUDIT] — ARCH-TAGS §1.
```

---

## Open bounce-backs

| OQ | Title | Severity | Raised |
|----|-------|----------|--------|
| OQ-026 | PHP binary not available in dev sandbox | Medium | D-01, 2026-04-27 |
| OQ-027 | MySQL + PostgreSQL servers not running in sandbox | High | D-01, 2026-04-27 |

OQ-026 and OQ-027 do not block D-01 SQLite validation. D-02 (tables 001–004) can proceed on
SQLite. MySQL + PostgreSQL matrix validation deferred to ThinkPad Laragon + Docker.

---

---

## D-02 results

**Date:** 2026-04-27

### Runner fix applied (D-02)

`split_statements()` helper added to `runner.py`. Root cause: naive `split(";")` hit semicolons
inside `--` comment text (e.g. `no ENUM; FK ON DELETE CASCADE portable`). Fix: strip all
`--[^\n]*` comment spans via regex before splitting. Idempotency and drift detection unaffected
(hash is computed on the raw pre-substitution UP section, which includes comments).

### SQLite matrix results — D-02

```
MI-M-T migration runner v0.1.0
Engine : sqlite
DB URL : …/.test/d02.sqlite

  [000] APPLIED — create schema migrations        (14ms, sha256=82dc923fc19c…)
  [001] APPLIED — create projects                  (3ms, sha256=ec731bcaf08f…)
  [002] APPLIED — create users                     (0ms, sha256=eed68aced83e…)
  [003] APPLIED — create value lists               (0ms, sha256=24ef7b6b6ac9…)
  [004] APPLIED — create value list items          (0ms, sha256=ecd439daea22…)
  [100] APPLIED — seed reference data              (1ms, sha256=1de007c3283c…)

Done. applied=6 skipped=0 aborted=0
```

Data integrity checks (Python sqlite3):
  projects             2 rows  PASS
  users                8 rows  PASS
  value_lists         11 rows  PASS (all 11 domains seeded)
  value_list_items    56 rows  PASS
  item_status codes:  12/12   PASS (new→in-analysis→…→deferred)
  FK orphans:         0       PASS
  Invalid roles:      0       PASS

Idempotency re-run: applied=0 skipped=6 aborted=0  PASS

### MySQL / PostgreSQL — D-02

BLOCKED — OQ-027 still open (servers not running in sandbox).
Action: on ThinkPad, start Laragon MySQL + Docker PostgreSQL, then:
  python runner.py --engine mysql    --db-url mysql+pymysql://root:@127.0.0.1:3306/mimt_dev
  python runner.py --engine postgres --db-url postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/mimt_dev

---

## D-02 commit message

```
feat(migrations): D-02 — tables 001-004 + reference data seed (SQLite PASS)

Deliverables
────────────
* code/migrations/001_create_projects.sql
    Tenant boundary table. status CHECK: active/archived/deleted.
    Citation: ARCH-SPEC §1.2.

* code/migrations/002_create_users.sql
    Identity table. role_in_process CHECK: PM/DM/TM/TA/TD/TI/TE/PAn.
    is_active: {{BOOL_TYPE}}. Citation: ARCH-SPEC §1.2 + §3.6.

* code/migrations/003_create_value_lists.sql
    Domain registry for extensible enum picklists.
    Citation: ARCH-SPEC §1.2.

* code/migrations/004_create_value_list_items.sql
    Picklist rows. FK value_list_items → value_lists ON DELETE CASCADE.
    ix_vli_active index. Citation: ARCH-SPEC §1.2.

* code/migrations/100_seed_reference_data.sql
    2 projects, 8 users, 11 value_list domains, 56 value_list_items.
    Idempotent via DELETE + INSERT (FK-safe order). No dialect-specific
    INSERT idioms. Citation: MOCK-FIXTURES §1.1–§1.3.

Runner fix (this iteration)
────────────────────────────
* split_statements() helper: strips -- comments before ; split.
  Prevents false statement splits on semicolons inside comment text.

Tests passing
─────────────
* SQLite: 6/6 APPLIED, data integrity PASS, idempotency PASS.
* MySQL:  BLOCKED — OQ-027.
* PostgreSQL: BLOCKED — OQ-027.

Design citations
────────────────
* Token vocabulary: ARCH-SPEC §8.3 (all 5 tokens used across 001-004).
* No ENUM/triggers/procs/window functions: ARCH-SPEC §0.4.
* Seed idempotency via DELETE+INSERT: MOCK-FIXTURES §1.3 + ARCH-SPEC §8.7.
* File naming 001-004/100: ARCH-SPEC §8.1 + §8.6.
```

---

---

## D-03 results

**Date:** 2026-04-27

### Runner fix applied (D-03)

Python f-string in generator produced `){{{TABLE_OPTIONS}}}` (triple brace) instead of
`){{TABLE_OPTIONS}}`. Runner's `str.replace("{{TABLE_OPTIONS}}", "")` left `){}` residue.
Fix: post-generation `str.replace("{{{TABLE_OPTIONS}}}", "{{TABLE_OPTIONS}}")` on all 8 files.
Root cause noted for LESSONS-LEARNED: use `Path.write_text()` with literal token strings in
generator, not f-strings, to avoid brace-escaping errors.

### SQLite matrix results — D-03

```
MI-M-T migration runner v0.1.0 / SQLite
Applied: 14/14  (000–012 + 100)  skipped=0  aborted=0

  [005] APPLIED — create test targets        (1ms, sha256=6e25c27c1c38…)
  [006] APPLIED — create test cases          (1ms, sha256=345f113cbc3f…)
  [007] APPLIED — create test scripts        (1ms, sha256=64cda81df651…)
  [008] APPLIED — create test data           (1ms, sha256=872b05a6205d…)
  [009] APPLIED — create test environments   (1ms, sha256=d0897c16b9f7…)
  [010] APPLIED — create iteration test sets (1ms, sha256=ddb9c89ce77a…)
  [011] APPLIED — create test runs           (2ms, sha256=d54bc94a0a20…)
  [012] APPLIED — create requests            (2ms, sha256=8bb3c175aaaa…)
```

Smoke rows (1 per table from MOCK-FIXTURES §2–§4):
  test_targets         TGT-001  PASS
  test_scripts         SCR-001  PASS
  test_data            DAT-001  PASS
  test_environments    ENV-001  PASS
  iteration_test_sets  ITS-001  PASS
  test_runs            RUN-001  PASS
  test_cases           TC-001   PASS (FK test_target_id → TGT-001 resolved)
  requests             BUG-001  PASS
  test_cases FK orphans: 0      PASS
  item_status CHECK: all valid  PASS

### MySQL / PostgreSQL — D-03

BLOCKED — OQ-027 still open.

---

## D-03 commit message

```
feat(migrations): D-03 — item tables 005-012 (SQLite PASS, smoke rows inserted)

Deliverables
────────────
* 005_create_test_targets.sql      BB-1 + tst_strat_ideas. CAST §2.4.
* 006_create_test_cases.sql        BB-1 + test_target_id FK + last_run denorm. CAST §2.6.
* 007_create_test_scripts.sql      BB-1 + instruction/observation/script fields.
* 008_create_test_data.sql         BB-1 + data_payload {{JSON_TYPE}} + path fields.
* 009_create_test_environments.sql BB-1 + hw/sw/url fields.
* 010_create_iteration_test_sets.sql BB-1 + dates + env FK + ck_its_dates.
* 011_create_test_runs.sql         BB-1 + run_date/executor + its/env FKs + verdict CHECK.
* 012_create_requests.sql          BB-1 + item_type discriminator + repro fields. CAST §2.7.

All tables: BB-2 constraint suite (8 FKs + 6 CHECK flags + status CHECK) + 7 standard indexes.
Extra entity indexes: test_cases(2), iteration_test_sets(1), test_runs(4), requests(3).

Generator fix
─────────────
Triple-brace TABLE_OPTIONS token corrected post-generation via str.replace.

Tests passing
─────────────
* SQLite: 14/14 APPLIED, 1 smoke row per table, FK + CHECK PASS.
* MySQL/PostgreSQL: BLOCKED — OQ-027.

Citations
─────────
ARCH-SPEC §1.1 (BB-1/BB-2), §1.3 (deltas), §0.3 (types), §0.4 (constraints), §8.3 (tokens).
MOCK-FIXTURES §2–§4 (smoke row data).
```

---

---

## D-04 results

**Date:** 2026-04-27

### SQLite matrix — D-04

```
Applied: 21/21 (000-019 + 100)  skipped=0  aborted=0
013 test_case_phases           sha256=fed221c60e65…
014 test_case_targets          sha256=a175c763e467…
015 test_case_phase_resources  sha256=ec3b6e5da6c6…
016 iteration_test_set_cases   sha256=5da59ffa290a…
017 test_run_results           sha256=995be6cd0b6b…
018 request_test_cases         sha256=df407f493f64…
019 request_test_run_results   sha256=be055ffb3a70…
```

Smoke: full 6-join chain  BUG-001 -> pass -> TC-001 -> TGT-001 -> RUN-001  PASS
FK + CHECK: all constraints resolved  PASS

---

## D-05 results

**Date:** 2026-04-27

### SQLite matrix — D-05

```
Applied: 27/27 (000-025 + 100)  skipped=0  aborted=0
020 item_status_history        sha256=c53783835513…
021 item_status_transitions    sha256=0bd254b0b501…
022 item_attachments           sha256=9be85da9a33b…
023 item_correlation_groups    sha256=264780da044f…
024 item_correlations          sha256=4914195d1d9a…
025 jira_sync_links            sha256=8430483a765c…
```

Smoke:
  item_status_history: 2 rows, chain NULL->new->confirmed  PASS
  item_status_transitions: 2 rows (new->in-analysis, in-analysis->confirmed)  PASS
  item_attachments: 1 row  PASS
  item_correlation_groups + item_correlations: 1+1 rows  PASS
  jira_sync_links: MIMT-001 -> jira  PASS
  ck_ish_entity_table CHECK on bad_table: IntegrityError (fired correctly)  PASS

---

## D-04 + D-05 commit message

```
feat(migrations): D-04 + D-05 — junction + audit tables 013-025 (SQLite PASS)

D-04 deliverables (junction/sub-entity/execution):
  013 test_case_phases          Phase sub-entity (pre/exec/post). R-TC-3.
  014 test_case_targets         N:M secondary coverage map.
  015 test_case_phase_resources Polymorphic resource attachment. R-TC-4.
  016 iteration_test_set_cases  M:N test set <-> test case.
  017 test_run_results          One result row per executed case per run.
  018 request_test_cases        Bug/CR <-> test case linkage.
  019 request_test_run_results  Pinpoint result row for a request.

D-05 deliverables (audit/supporting/integration):
  020 item_status_history       Append-only status audit log. ARCH-SPEC §1.5.
  021 item_status_transitions   State machine registry. Seed in 101.
  022 item_attachments          Normalised attachment store (replaces ref01-05).
  023 item_correlation_groups   CAST correlation group per project.
  024 item_correlations         Polymorphic group membership.
  025 jira_sync_links           JIRA/Zephyr/Postman key map. D-03/D-04 contract.

Generator technique: plain string concatenation for all SQL token sections.
No f-strings used. No triple-brace artifacts.

Tests: 27/27 APPLIED. Smoke + CHECK guards PASS. MySQL/PG: BLOCKED OQ-027.
```

---

## Documentation deliverables — 2026-04-28

- `docs/LESSONS-LEARNED.md` written: 156 lines, LL-001..LL-010 (D-05 closure)
- `docs/IMPLEMENTATION-STATUS.md` written: 261 lines (full portability matrix,
  schema completeness 25/25, runner status, D-06..D-12 roadmap, commit template)

---

## Next session opens here

**D-06 — Seed extensions.**
  101_seed_item_status_transitions.sql: valid transition rows for all 12 states.
  102_seed_postman_stubs.sql (optional): jira_sync_links demo rows per D04-CONTRACT §3.

Pre-flight for D-06:
- No blockers. CoWork sandbox SQLite is sufficient.
- Read ARCH-SPEC §5.2 (item_status_transitions seed spec) before authoring rows.
- Read MOCK-FIXTURES §2.1 (canonical transition table) for allowed pairs.
- After D-06: resolve OQ-027 on ThinkPad (MySQL + PostgreSQL full-stack apply).

---

## D-06 — Seed extensions (2026-04-28)

**Scope:** 101_seed_item_status_transitions.sql, 102_seed_integration_demo.sql,
runner.py split_statements hardening.

**Input:** ARCH-SPEC §4.2 (canonical transition seed, verbatim 66-row set).

**Files created:**
- `migrations/101_seed_item_status_transitions.sql` — 66 rows, 8 entity tables,
  'any' sentinel in test_cases per ARCH-SPEC §4.3.
- `migrations/102_seed_integration_demo.sql` — 10 jira_sync_links rows covering
  jira (4), zephyr (3), postman (3); includes drift + error state examples.

**Runner fix — split_statements() hardened (LL-011):**
  Upgraded from regex comment-strip + naive split to character-level state machine.
  Correctly handles:
    - semicolons inside -- comments (Error 3 / D-02 regression)
    - semicolons inside single-quoted string literals (NEW — D-06 trigger)
    - SQL '' escaped quotes inside strings
  7-case regression suite: all PASS.

**Validation matrix:**
```
Engine    Result
SQLite    29/29 APPLIED (d06.sqlite)  PASS
MySQL     BLOCKED (OQ-027)
PG        BLOCKED (OQ-027)
```

**Smoke results:**
  item_status_transitions: 66 rows total
    test_targets=18, test_cases=12 (incl. 'any' sentinel id=30),
    test_scripts=6, test_data=3, test_environments=3,
    iteration_test_sets=4, test_runs=6, requests=14
  ux_ist_triple UNIQUE guard on dupe: IntegrityError PASS
  jira_sync_links: 10 rows (jira=4, zephyr=3, postman=3)
    sync_states present: drift, error, ok
  ck_jsl_system CHECK (bad 'github'): IntegrityError PASS
  ck_jsl_state CHECK (bad 'unknown'): IntegrityError PASS
  split_statements 7-case regression: all PASS

---

## D-06 commit message

```
feat(migrations): D-06 — seed extensions 101+102 + runner split_statements fix

101_seed_item_status_transitions.sql:
  66 rows across 8 entity tables. Source: ARCH-SPEC §4.2 verbatim.
  'any' wildcard sentinel (id=30, test_cases) per §4.3 app-layer rule.

102_seed_integration_demo.sql:
  10 jira_sync_links demo rows (jira, zephyr, postman).
  Exercises ok/drift/error sync_state values. LDE/dev-only.

runner.py split_statements() — state-machine upgrade:
  Old: re.sub(--comments) + str.split(';')
  New: char-level FSM — handles ; in comments AND ; in string literals.
  7 regression cases PASS. Closes LL-003 partial risk (string literal ';').

Tests: 29/29 APPLIED (d06.sqlite). MySQL/PG: BLOCKED OQ-027.
Next: D-07 — PHP API route stubs (ARCH-SPEC §9 / §5.1).

Refs: ARCH-SPEC §4.2, §4.3, §7.1, §8.6
```

---

## Next session opens here

**D-07 — PHP API route stubs (ARCH-SPEC §9 / §5.1).**
  Scaffold PHP router + controller stubs for all entity endpoints.
  Implement status transition handler per §6.5.1 pattern.

Pre-flight for D-07:
- OQ-026 partial blocker: PHP binary needed. Check ThinkPad availability.
- Read ARCH-SPEC §5.1 (route catalogue) + §6 (PHP implementation) before coding.
- Read ARCH-SPEC §6.5.1 (transitionEntity() pattern) — canonical PHP impl.
- On MacBook/CoWork: can scaffold stubs + write unit-testable logic,
  defer live PHP execution to ThinkPad.

---

## D-07 — PHP API layer (2026-04-29)

**Scope:** Full PHP MVP layer per ARCH-SPEC §6 — front controller, router,
validators, repos, controllers, layout, assets.

**Files created (17):**
```
public_html/
  .htaccess                        5 lines   rewrite all → index.php (§6.6)
  index.php                      102 lines   front controller, all routes (§6.5.3)
  config/env.php                  36 lines   env/constants bootstrap
  src/Db.php                      79 lines   PDO factory (sqlite/mysql/pgsql) + transaction()
  src/Router.php                  96 lines   method+path dispatcher, named params
  src/Validators/Transition.php  136 lines   transitionEntity() canonical impl (§6.5.1)
  src/Validators/Phase.php        88 lines   R-TC-3 + R-TC-5 validators (§6.5.2)
  src/Repos/BaseRepo.php          67 lines   fetchOne/fetchAll/paginate helpers
  src/Repos/TestTargetRepo.php   133 lines   test_targets CRUD + children + history
  src/Repos/TestCaseRepo.php     154 lines   test_cases + phases + resources
  src/Repos/TestRunRepo.php      125 lines   test_runs + result append + verdict compute
  src/Repos/RequestRepo.php      104 lines   requests CRUD + linkTestCases + history
  src/Controllers/ApiController.php  472 lines  31 JSON API routes (MVP subset §6.4)
  src/Controllers/PageController.php  90 lines  14 HTML page routes (§6.3)
  src/Views/layout.php            33 lines   minimal HTML layout stub
  assets/style.css                 8 lines   minimal nav/layout CSS
  assets/app.js                   30 lines   fetch wrapper (mimt.get/post/patch)
```

**Coverage:**
  Routes registered: 31 API + 14 HTML = 45 total
  Controller methods: ApiController=31, PageController=14 — 100% coverage
  Brace balance: all 13 .php files balanced
  PHP syntax: OQ-026 (binary absent) — deferred to ThinkPad

**Key design decisions:**
  - Db::transaction() wraps all multi-step operations (status transition = 5 queries)
  - TransitionValidator.apply() fans 'any' sentinel (ARCH-SPEC §4.3) via OR clause
  - SQLite branch skips FOR UPDATE (not supported); uses connection-level serialization
  - Non-MVP sync/trace endpoints return 501 with pointer to Python service (§6.4)
  - Error type prefix codes (ENTITY_NOT_FOUND / TRANSITION_NOT_ALLOWED / ROLE_INSUFFICIENT)
    map to HTTP 404 / 409 / 403 in mapTransitionError()
  - RequestRepo.linkTestCases uses INSERT OR IGNORE (idempotent; SQLite dialect — needs
    INSERT IGNORE for MySQL, ON CONFLICT DO NOTHING for PG — OQ-028 logged below)

**Verification: 35/35 logical checks PASS**
  (route coverage, contract points, engine support, R-TC-3/5 matrix)

**New open question:**
  OQ-028 (Low): INSERT OR IGNORE syntax is SQLite-only. MySQL needs INSERT IGNORE,
  PostgreSQL needs INSERT ... ON CONFLICT DO NOTHING. Fix in D-09 portability pass
  or abstract into Db::insertIgnore() helper.

---

## D-07 commit message

```
feat(php): D-07 — PHP API layer (17 files, 31 routes, transitionEntity)

public_html/ scaffold per ARCH-SPEC §6.2:
  - index.php: front controller, 45 routes (31 API + 14 HTML)
  - src/Db.php: PDO factory sqlite/mysql/pgsql + transaction()
  - src/Router.php: method+path dispatcher, named {param} segments
  - src/Validators/Transition.php: canonical transitionEntity() §6.5.1
    SELECT FOR UPDATE (MySQL/PG) / BEGIN-level serialization (SQLite)
    fans 'any' sentinel, role check, history INSERT, entity UPDATE
    error prefix codes → HTTP 404/409/403
  - src/Validators/Phase.php: R-TC-3 phase presence + R-TC-5 admissibility
  - src/Repos/: TestTarget, TestCase, TestRun, Request (CRUD + relations)
  - src/Controllers/ApiController.php: 31 MVP routes; 501 for non-MVP
  - src/Controllers/PageController.php: 14 HTML page stubs
  - assets/style.css, assets/app.js: minimal UI stubs

Structural verification: 35/35 checks PASS.
PHP syntax: deferred (OQ-026 — no PHP binary in CoWork sandbox).
OQ-028 logged: INSERT OR IGNORE is SQLite-only (fix in D-09).

Next: D-08 — Python FastAPI layer (ARCH-SPEC §7).

Refs: ARCH-SPEC §5.1, §6, §6.5.1, §6.5.2, §6.5.3
```

---

## Next session opens here

**D-08 — Python FastAPI layer (ARCH-SPEC §7).**
  mi_m_t/ package: main.py app factory, models (SQLAlchemy ORM),
  routers (one per entity group), domain/statuses.py transition checker,
  domain/decomposition.py R-RT/R-TC validators.

Pre-flight for D-08:
- Read ARCH-SPEC §7 (Python FastAPI spec) before coding.
- Read §7.2 (project layout) — full directory tree is defined there.
- Read §7.3 (Pydantic schemas) if present — request/response models.
- FastAPI + SQLAlchemy 2 async available in CoWork sandbox (pip install).
- Alembic integration with runner.py apply_pending() hook already in place.

---

## D-08 — Python FastAPI layer — COMPLETE (2026-04-30)

**Deliverable:** `mi_m_t/` Python package — FastAPI app, SQLAlchemy 2.x async, 40 routes.

**Smoke test result: SMK9 20/20 PASS**

### Files written / patched

| File | Action | Key change |
|------|--------|-----------|
| `mi_m_t/models/__init__.py` | created | Import all 9 ORM models to force mapper registration before first flush |
| `mi_m_t/models/iteration_test_set.py` | created | Minimal BB-1 model; FK target for `test_runs.iteration_test_set_id` |
| `mi_m_t/models/test_run.py` | patched | `started_at→run_date`, `finished_at→run_finished_at`; `executor_id`/`run_date` NOT NULL |
| `mi_m_t/models/request.py` | patched | Removed `repro_steps`, `expected_result`, `actual_result` (not in DDL) |
| `mi_m_t/schemas/test_run.py` | patched | Added `submitter_id`/`item_submit_date` (BB-1 NOT NULL); `ResultAppend` fields renamed to `started_at`/`finished_at` to match `test_run_results` DDL |
| `mi_m_t/schemas/request_schema.py` | patched | Removed non-DDL fields |
| `mi_m_t/services/test_runs.py` | rewritten (×2) | Verdict values aligned to DDL; `append_result`+`finalize` removed nested `begin()` (autobegin conflict fix) |
| `mi_m_t/services/requests.py` | patched | Table `request_test_cases` (not `request_test_case_links`); removed non-DDL constructor args |
| `mi_m_t/services/transitions.py` | patched | Conditional `FOR UPDATE` omitted on SQLite |
| `mi_m_t/routers/projects.py` | rewritten | Schema fields `name`/`description` (ORM column names) |
| `mi_m_t/routers/test_runs.py` | patched | `status_code=200` on `/results` upsert; removed pre-check `svc.get()` from `append_result` handler |
| `mi_m_t/routers/{test_targets,requests,test_cases,test_runs}.py` | patched | `Page(items=…)→Page(data=list(rows),total_pages=…)` to match `common.Page` schema |
| `mi_m_t/main.py` | created | `import mi_m_t.models` early; 40-route app factory; lifespan `engine.dispose()`; exception handlers 409/403 |

### Root causes resolved in sequence

1. **`NoReferencedTableError: users`** — `User` model not imported before first flush. Fix: `models/__init__.py`.
2. **`NoReferencedTableError: iteration_test_sets`** — no model for FK target. Fix: `models/iteration_test_set.py`.
3. **`no such column: phase_id`** — `test_case_phase_resources` uses `test_case_phase_id`. Fix: service INSERT/SELECT.
4. **`request_test_case_links` not found** — actual table: `request_test_cases`. Fix: service raw SQL.
5. **`near "FOR": syntax error`** — SQLite rejects `FOR UPDATE`. Fix: conditional lock suffix via `settings.db_driver`.
6. **`no column named repro_steps`** — Request ORM/schema had non-DDL columns. Fix: removed.
7. **`no column named started_at` (test_runs)** — DDL uses `run_date`/`run_finished_at`. Fix: model+schema+service rename.
8. **`NOT NULL: test_runs.submitter_id`** — BB-1 NOT NULL fields missing from schema+service. Fix: added.
9. **`project_name` validation error** (projects router) — ORM column is `name` not `project_name`. Fix: router rewrite via bash heredoc (Edit tool Windows→Linux sync lag workaround).
10. **`Page(items=…)` ValidationError** — `Page` schema uses `data=`, requires `total_pages`. Fix: all 4 list routers.
11. **`UNIQUE: projects.project_code`** — stale SMK row from prior run. Fix: timestamp-suffixed codes in smoke test.
12. **`item_type` required on RequestCreate** — smoke test S09 missing field. Fix: added `"item_type": "bug"`.
13. **`InvalidRequestError` on `db.begin()` after autobegun SELECT** — `append_result` router called `svc.get()` before `svc.append_result()` which tried `async with db.begin()`. SQLAlchemy 2.x: cannot call `begin()` when autobegin already active. Fix: removed `async with db.begin()` wrappers from `append_result` and `finalize`; execute DML directly in existing autobegin transaction; `get_db` commits. Also removed redundant pre-check `svc.get()` from router handler.
14. **S14 returns 201 not 200** — `/results` is an upsert, not a pure create. Fix: `status_code=200`.

### SQLAlchemy 2.x autobegin rule (new lesson)
> `async with session.begin()` must only be called as the **first database operation** on a session. Any prior `execute()` or ORM query on the same session triggers autobegin, making a subsequent `begin()` raise `InvalidRequestError`. Pattern: for methods that SELECT then mutate, execute DML directly without `begin()` wrapper; the autobegin transaction is committed by `get_db`.

### D-08 commit message

```
feat(python): D-08 — FastAPI layer complete, SMK9 20/20 PASS

mi_m_t/ Python package:
  - main.py: create_app() factory, 40 routes, lifespan, 409/403 handlers
  - models/: 9 ORM models (ItemBase mixin); __init__.py forces mapper registration
  - schemas/: Pydantic v2 request/response models; Page[T] pagination envelope
  - services/: TestTarget, TestCase, TestRun, Request, Transition (async SQLAlchemy 2.x)
  - routers/: projects, test_targets, test_cases, requests, test_runs,
              state_machine, value_lists, sync (501 stubs), trace
  - domain/statuses.py: TransitionError, RoleError; state machine loader
  - config.py: pydantic-settings, db_driver switch (sqlite/mysql/postgres)
  - db.py: async engine + AsyncSessionFactory; SQLite FK pragma on connect

Key fixes vs DDL:
  - run_date/run_finished_at (not started_at/finished_at) in test_runs
  - submitter_id/item_submit_date BB-1 NOT NULL in all item tables
  - request_test_cases (not request_test_case_links); no id column
  - test_case_phase_resources.test_case_phase_id (not phase_id)
  - SQLite: FOR UPDATE conditionally omitted
  - SQLAlchemy autobegin rule: begin() only as first op on session

Smoke test: SMK9 20/20 PASS (httpx ASGITransport, d06.sqlite)

Next: D-09 — portability pass (MySQL/PG full-stack, OQ-027/OQ-028).

Refs: ARCH-SPEC §7, OQ-027, OQ-028
```

---

## Next session opens here

**D-09 — Portability pass.**
- OQ-027: MySQL 8 + PostgreSQL 14 full-stack on ThinkPad (separate session)
- OQ-028: `request_test_cases` INSERT portability — SQLite uses `INSERT OR IGNORE`,
  MySQL needs `INSERT IGNORE`, PG needs `ON CONFLICT DO NOTHING`.
  Current code uses portable DELETE+INSERT idiom (already addressed for SQLite).
  Verify behaviour on MySQL/PG in D-09.
- Consider abstracting `insertOrIgnore()` in a dialect helper if D-09 reveals issues.

Pre-flight for D-09:
  - ThinkPad has MySQL 8 + PG 14 in Docker (from AUTH-005 LDE).
  - Transfer `mi_m_t/` package to ThinkPad via SYNC bypass protocol.
  - Run `pytest` smoke suite against each DB engine (adapt smoke_test.py to accept
    `--db-driver` arg and `--db-url`).

---

## Phase 3 sync + GH-UPL batch — 2026-05-01

**Device:** MacBook (CoWork / Claude Sonnet 4.6)
**Session type:** Maintenance — session restart gate + GH-UPL batch + delta rebuild

### Deliverables

| File / Action | Key change |
|---------------|-----------|
| SMK9 daily smoke | 20/20 PASS (SQLite). pydantic-settings installed in CoWork sandbox. |
| MI-M-T-SLUG-FIX | Verified already done — page_id=176 slug=mi-m-t, link confirmed live. |
| GH-UPL-09 | zemla-theme-v1.7.4.zip → GitHub Releases. v1.7.4 = live dev baseline. |
| GH-UPL-05 | bodyterapie-theme-v1.3.0.zip → GitHub Releases. |
| GH-UPL-08 | zemla-theme-v1.7.2.zip → GitHub Releases. |
| GH-UPL-10 | zemla-theme-v1.7.3.zip → GitHub Releases (found in archive, not in original batch). |
| GH-UPL-04/06/07 | DEFERRED — zips not in local archive; superseded by v1.7.4. |
| macbook-delta-2026-04-27.tar.gz | Rebuilt (87K, 7 Opus backlog files). ThinkPad-ready. |
| thinkpad-delta-D08-2026-04-30.tar.gz | Verified intact (109K, full mi_m_t package). |
| CLAUDE.md | HANDOFF BLOCK updated. Current state updated. |
| queue-macbook.yaml | GH-UPL done items moved. Stale pending items cleaned. |
| macbook branch | Force-pushed 1364eb8 → final commit for session. |

### Root causes / lessons captured

1. PowerShell `curl` aliases to `Invoke-WebRequest` — must use `curl.exe` for REST calls.
2. `gh` CLI on Windows PATH not visible inside Git Bash — use PowerShell `gh` directly.
3. Stale `.git/index.lock` from crashed process — remove manually before git ops.
4. `macbook` branch not present locally (only on remote) — create with `git checkout -b macbook`.
5. `pydantic-settings` not in sandbox by default — install separately before SMK9 runs.

### Commit
```
chore: session 2026-05-01 close — GH-UPL-05/08/10 done, all available zips on Releases
```

---

## Next session opens here

**ThinkPad — D-09 portability pass.**
Pre-flight: transfer `_config/thinkpad-delta-D08-2026-04-30.tar.gz` + `_config/macbook-delta-2026-04-27.tar.gz` to ThinkPad.
Then: `bash _config/THINKPAD-APPLY-D08.md` → run SMK9 against MySQL + PostgreSQL engines.
MacBook: no pending feature work. GH token budget conserved for D-09 push.

---

## D-09 — Portability pass: MySQL 8 + PostgreSQL 14

**Captured:** 2026-05-02  
**Device:** ThinkPad (CoWork / Claude Sonnet 4.6)  
**Engines verified:** SQLite (D-08 baseline) · MySQL 8 · PostgreSQL 14

### Result

| Engine | Migrations | SMK9 |
|--------|-----------|------|
| SQLite | 20/20 (D-08) | 20/20 PASS (D-08) |
| MySQL 8 | 29/29 APPLIED | 20/20 PASS |
| PostgreSQL 14 | 29/29 APPLIED | 20/20 PASS |

**D-09 complete. All three engines green.**

### Infrastructure

- Docker Compose: `docker-compose.mimt-d09.yml` — `mimt-mysql8` (3306) + `mimt-postgres14` (5433, remapped from 5432 to avoid native Windows PG 17 conflict)
- Migration runner: `migrations/runner.py` (custom token substitution, SHA-256 drift detection, idempotent)
- Smoke suite: `mi_m_t/smoke_test.py` (httpx ASGITransport, 20 tests, `--db-driver` + env vars)

### Open Questions resolved (OQ series)

| OQ | Title | Fix |
|----|-------|-----|
| OQ-029 | `applied_at` must be naive datetime (not ISO string with Z) | `record_migration()` uses `datetime.now(timezone.utc).replace(tzinfo=None)` |
| OQ-030 | `{{BOOL_TRUE}}` portability | Token table: `1` for sqlite/mysql, `TRUE` for postgres |
| OQ-031 | PostgreSQL IDENTITY sequences don't advance on explicit-ID seed inserts | `reset_pg_identity_sequences()` in `runner.py` — queries `information_schema`, calls `setval(pg_get_serial_sequence(table, 'id'), COALESCE(MAX(id), 1))` after seed migrations complete. COALESCE floor = 1 (PG sequences minimum). |
| OQ-032 | ORM type mismatch: `last_run_date` was `String(30)`, DDL is `TIMESTAMP` | `models/test_case.py`: `Mapped[Optional[datetime]] = mapped_column(DateTime)` |
| OQ-033 | `asyncpg` cursor has no `lastrowid` attribute | `services/test_cases.py`: follow-up `SELECT id FROM test_case_phases WHERE test_case_id=:tc_id AND phase_type=:pt ORDER BY id DESC LIMIT 1` within same transaction |
| OQ-034 | PostgreSQL rejects `is_active = 1` for BOOLEAN column | `services/transitions.py:72`, `routers/state_machine.py:31,55`: `= 1` → `= true` |

### File changelog

| File | Change | OQ |
|------|--------|----|
| `migrations/runner.py` | Added `reset_pg_identity_sequences()`; `COALESCE(...,0)→1`; call after pg migration block | OQ-031 |
| `migrations/runner.py` | `record_migration()` naive UTC datetime | OQ-029 |
| `migrations/runner.py` | `{{BOOL_TRUE}}` token: `1`/`1`/`TRUE` | OQ-030 |
| `migrations/100_seed_reference_data.sql` | Reconstructed truncated tail (external_system codes 110–112) | — |
| `mi_m_t/models/test_case.py` | `last_run_date`: `String(30)` → `Mapped[Optional[datetime]] / DateTime` | OQ-032 |
| `mi_m_t/services/test_cases.py` | `_insert_phase()`: removed `result.lastrowid`; follow-up SELECT id | OQ-033 |
| `mi_m_t/services/transitions.py` | `is_active = 1` → `is_active = true` | OQ-034 |
| `mi_m_t/routers/state_machine.py` | `is_active = 1` → `is_active = true` (×2) | OQ-034 |

### PowerShell invocation note (OQ-ENV-001)

`KEY=value cmd` syntax is bash-only. PowerShell requires `$env:KEY="value"` assignments chained with `;` before the command. The `--db-url` monkeypatch in `smoke_test.py` fires after module import, so DB params must be injected via env vars which pydantic-settings reads at `Settings()` instantiation:

```powershell
$env:DB_DRIVER="postgres"; $env:DB_HOST="127.0.0.1"; $env:DB_PORT="5433"; $env:DB_NAME="mimt_dev"; $env:DB_USER="postgres"; $env:DB_PASS="postgres"; python smoke_test.py --db-driver postgres
```

### Root causes resolved in sequence (PostgreSQL)

1. **`applied_at` MySQL DATETIME rejects ISO-8601 Z suffix** — naive UTC datetime fix in `record_migration()`.
2. **`value_list_items.is_active = 1` fails on PG BOOLEAN** — `{{BOOL_TRUE}}` token = `TRUE` for postgres.
3. **Seed file truncated** — `100_seed_reference_data.sql` truncated at `(106, 10, 'TE', 'Test` by prior regex pass; tail reconstructed from `102_seed_integration_demo.sql`.
4. **`setval(0)` out of bounds** — PG identity sequences have minimum 1; `COALESCE(MAX(id), 0)` → `COALESCE(MAX(id), 1)`.
5. **`column "last_run_date" is of type timestamp but expression is of type character varying`** — ORM `String(30)` vs DDL `TIMESTAMP`. Fix: `DateTime` mapped column.
6. **`asyncpg cursor has no attribute lastrowid`** — asyncpg does not implement DBAPI `lastrowid`. Fix: follow-up SELECT within same transaction.
7. **`operator does not exist: boolean = integer`** — `is_active = 1` in raw SQL rejected by PG strict type system. Fix: `= true` literal. Affected: `transitions.py` + `state_machine.py` (×2).

### D-09 commit message

```
feat(python): D-09 — portability pass complete, MySQL8 + PG14 SMK9 20/20 PASS

All three engines verified:
  SQLite:      SMK9 20/20 PASS (D-08 baseline)
  MySQL 8:     migrations 29/29 APPLIED, SMK9 20/20 PASS
  PostgreSQL 14: migrations 29/29 APPLIED, SMK9 20/20 PASS

Portability fixes:
  OQ-029: applied_at naive UTC datetime (MySQL rejects 'Z' suffix)
  OQ-030: {{BOOL_TRUE}} token — 1 for sqlite/mysql, TRUE for postgres
  OQ-031: reset_pg_identity_sequences() after seed — COALESCE floor = 1
  OQ-032: TestCase.last_run_date String(30) → DateTime (PG type mismatch)
  OQ-033: asyncpg has no lastrowid — SELECT id follow-up in same txn
  OQ-034: is_active = 1 → is_active = true (PG rejects int for BOOLEAN)

Files changed:
  migrations/runner.py
  migrations/100_seed_reference_data.sql (truncation repair)
  mi_m_t/models/test_case.py
  mi_m_t/services/test_cases.py
  mi_m_t/services/transitions.py
  mi_m_t/routers/state_machine.py

Refs: OQ-029..034, ARCH-SPEC §7 (portability matrix)
```

---

---

## T5-T7 — Infrastructure hygiene + PHP audit + pytest suite

**Captured:** 2026-05-02 (continuation of D-09 session)  
**Device:** ThinkPad (CoWork / Claude Sonnet 4.6)

### T5 — /health DB connectivity probe

Enhanced `mi_m_t/main.py` health endpoint — was static `{status: ok}`, now performs
async `SELECT 1` against the engine pool and returns DB diagnostics:

```json
{"status": "ok"|"degraded", "version": "0.1.0", "db_driver": "sqlite", "db_status": "ok"|"error"}
```

HTTP 503 returned when `db_status = "error"`. `settings` imported at module level to avoid
redundant per-request import. Monitoring can now distinguish application-up vs application-up-but-db-down.

**File:** `mi_m_t/mi_m_t/main.py`  
**Note:** T5 edit was reverted by `git checkout HEAD` run to fix D-09 truncation issue; re-applied cleanly in this session.

### T6 — PHP layer route audit

Full route audit produced at `3-fold-path/code/MI-M-T-PHP-ROUTE-AUDIT.md`.

**Summary:**
- 23 routes fully implemented (MVP subset — test-targets, test-cases, test-runs, requests, state-machine, value-lists, health)
- 8 routes correctly stubbed 501 (sync, trace — non-MVP per §6.4)
- 5 routes absent from PHP but present in Python: projects CRUD (PHP-GAP-01)
- 3 routes partially absent: `PATCH /test-cases/{id}`, `GET /test-runs/{id}`, `GET /requests[/{id}]` (PHP-GAP-02..04)
- 3 PG portability issues: `is_active = 1` in `valueLists()`, `stateMachine()`, `stateMachineFrom()` (same root cause as OQ-034; PHP MVP = MySQL/SQLite only, acceptable)
- `/health` response shape diverges between PHP (`{status,service,ts}`) and Python (`{status,version,db_driver,db_status}`)
- `authedUserId()` reads X-User-Id header — spoofable, must be replaced before non-local deployment

**Delivery signals for Opus MacBook session:**
- Quick-win closures: `GET /test-runs/{id}`, `GET /requests[/{id}]`, `PATCH /test-cases/{id}` (each ~5 LoC)
- Projects API requires architectural decision on which layer owns project creation
- Auth gate is hard blocker for any external integration test

### T7 — pytest conftest + SMK9 split into 20 test functions

Created:
- `tests/__init__.py` (package marker)
- `tests/conftest.py` — session-scoped `client` (httpx ASGI), `hdrs`, `run_tag` fixtures; env defaults before `mi_m_t` import
- `tests/test_smk9.py` — 20 async test functions `test_s01_health` .. `test_s20_trace`

Design: module-level `_state` dict carries entity IDs across sequential smoke tests.
`asyncio_mode = "auto"` (already in pyproject.toml) — no `@pytest.mark.asyncio` needed.

**Run:** `pytest tests/ -v` (SQLite default) or inject DB env vars for MySQL/PG.

Also repaired `smoke_test.py` trailing corruption (lines 213-223 were duplicated/corrupt
remnants of prior truncation repair — trimmed to clean `if __name__ == "__main__":` block).

### File changelog

| File | Change |
|------|--------|
| `mi_m_t/mi_m_t/main.py` | T5: async DB probe in `/health`; `settings` import at module level |
| `3-fold-path/code/MI-M-T-PHP-ROUTE-AUDIT.md` | T6: PHP route audit (NEW) |
| `mi_m_t/smoke_test.py` | T7 prep: trimmed corrupt trailing lines 213-223 |
| `mi_m_t/tests/__init__.py` | T7: new package marker |
| `mi_m_t/tests/conftest.py` | T7: session fixtures (client, hdrs, run_tag) |
| `mi_m_t/tests/test_smk9.py` | T7: 20 pytest async test functions (S01-S20) |

### Commit message

```
feat(python): T5-T7 — health DB probe, PHP audit, pytest SMK9 suite

T5: /health endpoint now probes DB with SELECT 1; returns db_driver +
    db_status; HTTP 503 on DB failure (was static 200 with no probe).

T6: PHP layer route audit — MI-M-T-PHP-ROUTE-AUDIT.md
    23 impl / 8 stubs (501) / 5 gaps vs Python (projects + partial reads)
    Portability issues: is_active=1 in 3 PHP SQL statements (MySQL/SQLite
    MVP scope; PG fix deferred per ARCH-SPEC §6.4).

T7: pytest suite (tests/conftest.py + tests/test_smk9.py)
    20 async test functions matching SMK9 S01-S20.
    Session-scoped ASGI client fixture; run_tag prevents code collisions.
    smoke_test.py trailing corruption repaired.

Run: pytest tests/ -v
Refs: ARCH-SPEC §7.1 (/health), §5.1 (route catalogue), §6.4 (PHP split)
```

---

## Next session opens here

**Verify T5 + T7:** Run from ThinkPad PowerShell:
```powershell
cd C:\Users\vitez\Documents\VibeCodeProjects\3-fold-path\code\mi_m_t
# Verify smoke_test still passes (S01 now tests enhanced health)
$env:DB_DRIVER="sqlite"; $env:SQLITE_PATH=".test/d06.sqlite"; python smoke_test.py
# Run pytest suite
pytest tests/ -v
```

**Then:** Commit T5-T7 changes + push `thinkpad` branch. Assess D-10+ vs project close per Opus MacBook session output.
