# MI-M-T PHP Layer Route Audit
**Date:** 2026-05-02  
**Scope:** `public_html/src/Controllers/ApiController.php` + `public_html/index.php`  
**Purpose:** Feed material for Opus MacBook strategic session — maps PHP implementation completeness vs Python service, surfaces gaps, portability issues, and architectural divergences.  
**Citation:** ARCH-SPEC §5.1 (route catalogue), §6.4 (PHP/Python split policy)

---

## 1. Route Inventory — JSON API

### Legend
| Symbol | Meaning |
|--------|---------|
| ✅ IMPL | Fully implemented with validation, repo call, and correct HTTP semantics |
| ⚠️ IMPL* | Implemented with a noted caveat or deviation |
| 🚫 501 | Non-MVP stub — returns HTTP 501 with pointer to Python service (policy-correct per §6.4) |
| ❌ MISSING | Route absent from both index.php and ApiController (gap vs Python service) |

---

### §5.1.1 Health + Value-lists

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/health` | `health()` | ⚠️ IMPL* | Returns `{status, service, ts}`. No DB probe. Python returns `{status, version, db_driver, db_status}` + HTTP 503 on failure. Response shapes diverge — clients cannot use same parser. |
| GET | `/api/v1/value-lists` | `valueLists()` | ⚠️ IMPL* | `is_active = 1` (integer literal). MySQL/SQLite accept this. **PG14 rejects** (`operator does not exist: boolean = integer`). See §3 for portability analysis. |

---

### §5.1.2 Projects

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/projects` | — | ❌ MISSING | Python: `projects_router`. No PHP API. Only `PageController@projectsList` (HTML). |
| POST | `/api/v1/projects` | — | ❌ MISSING | — |
| GET | `/api/v1/projects/{id}` | — | ❌ MISSING | — |
| PATCH | `/api/v1/projects/{id}` | — | ❌ MISSING | — |
| POST | `/api/v1/projects/{id}/transition` | — | ❌ MISSING | — |

> **Impact:** Projects entity is fully absent from PHP JSON API. Any client calling `/api/v1/projects` against the PHP service gets 404. PHP MVP assumes project selection happens via HTML UI; API-only clients (Postman, JIRA sync) cannot create or manage projects through PHP layer.

---

### §5.1.3 Test Targets

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/test-targets` | `targetsList()` | ✅ IMPL | Pagination via `page`/`page_size`; filters delegated to `TestTargetRepo::list()`. |
| POST | `/api/v1/test-targets` | `targetsCreate()` | ✅ IMPL | Validates `project_id`, `item_code`, `item_name`, `submitter_id`. Returns 201 + Location header. |
| GET | `/api/v1/test-targets/{id}` | `targetsRead()` | ✅ IMPL | 404 on missing. |
| PATCH | `/api/v1/test-targets/{id}` | `targetsUpdate()` | ✅ IMPL | Partial update via repo. No field whitelist in controller (delegated to repo). |
| POST | `/api/v1/test-targets/{id}/transition` | `targetsTransition()` | ✅ IMPL | `TransitionValidator::apply()` — mirrors Python `TransitionService`. Correct error mapping (404/409/403). |
| GET | `/api/v1/test-targets/{id}/children` | `targetsChildren()` | ✅ IMPL | Returns `{data: [...]}` envelope. |
| GET | `/api/v1/test-targets/{id}/history` | `targetsHistory()` | ✅ IMPL | Returns `{data: [...]}` envelope. |

---

### §5.1.4 Test Cases

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/test-cases` | `caseList()` | ✅ IMPL | Pagination; filters via `TestCaseRepo::list()`. |
| POST | `/api/v1/test-cases` | `caseCreate()` | ✅ IMPL | PhaseValidator + nested phase/resource txn inside `Db::transaction()`. R-TC-3/R-TC-5 enforced. |
| GET | `/api/v1/test-cases/{id}` | `caseRead()` | ✅ IMPL | Uses `findByIdFull()` (eager phase+resource load). |
| PATCH | `/api/v1/test-cases/{id}` | — | ❌ MISSING | Python has `PATCH /api/v1/test-cases/{id}`. PHP has no update route for test cases. |
| POST | `/api/v1/test-cases/{id}/transition` | `caseTransition()` | ✅ IMPL | — |
| POST | `/api/v1/test-cases/{id}/phases` | `phaseAdd()` | ✅ IMPL | Returns 201 + phase payload. |
| POST | `/api/v1/test-cases/{id}/phases/{phase_id}/resources` | `resourceAttach()` | ✅ IMPL | `PhaseValidator::assertResourceAdmissible()` gate. Returns 201. |

---

### §5.1.5 Iteration Test Sets (ITS)

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/iteration-test-sets` | — | ❌ MISSING | Python: `test_runs_router` covers ITS. PHP HTML UI has `PageController@itsList` / `@itsShow` but no API routes. |
| POST | `/api/v1/iteration-test-sets` | — | ❌ MISSING | — |
| GET | `/api/v1/iteration-test-sets/{id}` | — | ❌ MISSING | — |

> **Note:** PHP conflates ITS and test-runs in its model (no explicit ITS API). Python exposes them separately.

---

### §5.1.7 Test Runs

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| POST | `/api/v1/test-runs` | `runCreate()` | ✅ IMPL | Validates `project_id`, `item_code`, `item_name`. Returns 201. |
| GET | `/api/v1/test-runs/{id}` | — | ❌ MISSING | No GET route for a single run. Can create and finalize, but cannot retrieve by ID via JSON API. |
| GET | `/api/v1/test-runs` | — | ❌ MISSING | No list route. |
| POST | `/api/v1/test-runs/{id}/results` | `runResultAppend()` | ✅ IMPL | Validates `test_case_id`, `verdict`. Returns 201. |
| POST | `/api/v1/test-runs/{id}/finalize` | `runFinalize()` | ✅ IMPL | Computes `overall_verdict` (pass/fail/partial), applies transition. |

---

### §5.1.8 Requests

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| POST | `/api/v1/requests` | `requestCreate()` | ✅ IMPL | Validates `item_type` ∈ {`bug`, `change_request`}. Returns 201. |
| GET | `/api/v1/requests` | — | ❌ MISSING | No list endpoint. HTML: `PageController@requestsList`. |
| GET | `/api/v1/requests/{id}` | — | ❌ MISSING | No GET-by-ID. HTML: `PageController@requestShow`. |
| POST | `/api/v1/requests/{id}/transition` | `requestTransition()` | ✅ IMPL | — |
| POST | `/api/v1/requests/{id}/test-cases` | `requestLinkCases()` | ✅ IMPL | `link_kind` defaults to `'covers'`. Returns `{linked: n}`. |

---

### §5.1.10 State-machine Introspection

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/state-machine/{entity_table}` | `stateMachine()` | ⚠️ IMPL* | `is_active = 1` — PG portability issue. Returns `{entity_table, transitions:[...]}`. |
| GET | `/api/v1/state-machine/{entity_table}/{from_status}` | `stateMachineFrom()` | ⚠️ IMPL* | `is_active = 1` — same. Fans `any` sentinel correctly. |

---

### §5.1.12 Sync (non-MVP stubs)

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/sync/links` | `syncLinks()` | 🚫 501 | Policy-correct per §6.4. |
| POST | `/api/v1/sync/jira/pull/{entity_table}/{entity_id}` | `syncJiraPull()` | 🚫 501 | — |
| POST | `/api/v1/sync/jira/push/{entity_table}/{entity_id}` | `syncJiraPush()` | 🚫 501 | — |
| POST | `/api/v1/sync/zephyr/push/run/{id}` | `syncZephyr()` | 🚫 501 | — |
| POST | `/api/v1/sync/postman/import/collection` | `syncPostman()` | 🚫 501 | — |
| GET | `/api/v1/sync/health` | `syncHealth()` | 🚫 501 | — |

---

### §5.1.9 Trace (non-MVP stubs)

| Method | Path | PHP Handler | Status | Notes |
|--------|------|-------------|--------|-------|
| GET | `/api/v1/trace/impulse/{code}` | `traceImpulse()` | 🚫 501 | — |
| GET | `/api/v1/trace/test-target/{id}/full` | `traceFull()` | 🚫 501 | Note: same handler `traceFull` used for all 3 entity types — no entity_type branching needed since it's a stub. |
| GET | `/api/v1/trace/test-case/{id}/full` | `traceFull()` | 🚫 501 | — |
| GET | `/api/v1/trace/request/{id}/full` | `traceFull()` | 🚫 501 | — |

---

## 2. Gap Summary

### 2a. Routes present in Python, absent from PHP JSON API

| Gap ID | Route(s) | Entity | Risk |
|--------|----------|--------|------|
| PHP-GAP-01 | `GET/POST /api/v1/projects`, `GET/PATCH /projects/{id}`, `POST /projects/{id}/transition` | projects | HIGH — no API-level project management from PHP. |
| PHP-GAP-02 | `PATCH /api/v1/test-cases/{id}` | test_cases | MEDIUM — test case edit must go through Python or HTML UI. |
| PHP-GAP-03 | `GET /api/v1/test-runs`, `GET /api/v1/test-runs/{id}` | test_runs | MEDIUM — run created but unreadable via JSON API. |
| PHP-GAP-04 | `GET /api/v1/requests`, `GET /api/v1/requests/{id}` | requests | MEDIUM — request created/linked/transitioned but not retrievable via JSON API. |
| PHP-GAP-05 | `/api/v1/iteration-test-sets/*` | ITS | LOW for MVP — ITS is Python-only feature, PHP UI covers display. |

### 2b. Response shape divergences (same route, different contract)

| Route | PHP shape | Python shape | Impact |
|-------|-----------|--------------|--------|
| `GET /api/v1/health` | `{status, service, ts}` | `{status, version, db_driver, db_status}` + HTTP 503 on DB failure | Client health-check logic cannot be shared. Integration tests must branch on service type. |

### 2c. Routes in PHP not in Python

None identified. All PHP routes are a subset of the Python catalogue.

---

## 3. Portability Issues (PG14 — `is_active = 1`)

The PHP MVP targets MySQL 8 / SQLite. Three raw SQL statements use `is_active = 1` (integer literal against a BOOLEAN column), which PG14 rejects:

| File | Line | Statement fragment |
|------|------|--------------------|
| `ApiController.php` | 96 | `WHERE vli.is_active = 1` (valueLists) |
| `ApiController.php` | 414 | `WHERE ... is_active = 1` (stateMachine) |
| `ApiController.php` | 430 | `AND is_active = 1` (stateMachineFrom) |

**Fix pattern:** Replace with `is_active = TRUE` (SQL standard; accepted by MySQL 8, PG14, and SQLite 3.38+).  
Equivalent Python fix was applied in D-09 (OQ-034) as `is_active = true`.  
**Blocked by:** PHP MVP scope does not target PG (ARCH-SPEC §6.4). Fix is a prerequisite if PHP layer is ever evaluated against PG.

---

## 4. Auth / Security Observations

`authedUserId()` at line 63–69 reads the `X-User-Id` HTTP header and defaults to user_id=1 if absent. Marked "dev only — not for production" in source. This means:

- Any unauthenticated caller can impersonate any user_id by setting the header.
- All transitions, history entries, and run results are stamped with a spoofable user_id.
- **Status:** Known debt, annotated. Must be replaced before any non-local deployment (JWT/session gate).

---

## 5. Structural Quality Observations

| Obs | Finding | Severity |
|-----|---------|---------|
| OBS-01 | `authedUserId()` uses `$_SERVER['HTTP_X_USER_ID']` header — no auth enforcement | CRITICAL for any non-dev deployment |
| OBS-02 | `is_active = 1` in 3 SQL statements — PG incompatible | LOW (MVP scope = MySQL/SQLite only) |
| OBS-03 | `/health` has no DB connectivity probe — cannot detect DB down at infrastructure level | MEDIUM — monitoring blind spot |
| OBS-04 | `PATCH /test-cases/{id}` absent — test case edit only via Python or HTML | MEDIUM |
| OBS-05 | `GET /test-runs/{id}` absent — run created but not retrievable via PHP JSON API | MEDIUM |
| OBS-06 | `GET /requests`, `GET /requests/{id}` absent — requests read-only via HTML | MEDIUM |
| OBS-07 | `traceFull()` single handler for 3 routes (test-target, test-case, request) — entity type not inspected | LOW — acceptable while stub, must branch when implemented |
| OBS-08 | No DELETE routes on any entity — correct: lifecycle managed by state transitions | OK by design |
| OBS-09 | `health()` response shape differs from Python service — `service` vs `db_driver`/`db_status` | LOW — divergence should be documented as intentional or harmonized |

---

## 6. Delivery Signals for Opus Strategic Session

**PHP layer is a valid MVP subset** — all core write operations (create, transition, link) and primary read operations (list, read by ID) are implemented for test-targets and test-cases. The gaps are skewed toward read-back and project management.

**Priority closure candidates** (minimal effort, high API completeness gain):
1. `GET /api/v1/test-runs/{id}` — single `findById()` call; `runCreate()` already does it at line 307.
2. `GET /api/v1/requests`, `GET /api/v1/requests/{id}` — mirrors the targets pattern; `RequestRepo` already has `findById()`.
3. `PATCH /api/v1/test-cases/{id}` — mirrors `targetsUpdate()`; one-line repo delegation.

**Deferred / Python-first**:
- Projects API (complex, multi-entity, may need Opus architectural decision on which layer owns project creation).
- ITS (Python-only concept, no PHP data model gap).
- `is_active` PG fix (descoped for PHP MVP per §6.4).

**Auth gate** is the hard blocker for any production deployment. Must be sequenced before any external integration test (JIRA, Postman, Zephyr).

---

*Generated by: ThinkPad CoWork session 2026-05-02 — T6 route audit*  
*Next: T7 — pytest conftest + split SMK9 into 20 individual test functions*
