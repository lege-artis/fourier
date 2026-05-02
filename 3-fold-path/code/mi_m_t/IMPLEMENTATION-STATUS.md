# MI-M-T Python Layer — Implementation Status
**Updated:** 2026-04-30  
**Milestone:** D-08 COMPLETE — SMK9 20/20 PASS

---

## Phase status

| Phase | ID | Description | Status |
|-------|----|-------------|--------|
| Migration runner | D-01 | schema_migrations + runner.py | ✅ DONE |
| Core tables | D-02 | tables 001–004 + value_list seed | ✅ DONE |
| Item tables | D-03 | tables 005–012 (BB-1 items) | ✅ DONE |
| Audit tables | D-04/D-05 | tables 020–025 + docs | ✅ DONE |
| Seeds | D-06 | seeds 101+102 + split_statements | ✅ DONE |
| PHP API layer | D-07 | 17 files, 31 routes, transitionEntity | ✅ DONE |
| Python FastAPI | D-08 | 40 routes, SMK9 20/20 PASS | ✅ **DONE** |
| Portability pass | D-09 | MySQL/PG full-stack, OQ-027/OQ-028 | ⬜ PENDING (ThinkPad) |
| Postman adapter | D-10 | Newman adapter smoke | ⬜ PENDING |
| Dogfood run | D-11 | Real MI-M-T evidence against live app | ⬜ PENDING |
| Full portability | D-12 | Close portability matrix | ⬜ PENDING |

---

## D-08 deliverables

### Package structure
```
mi_m_t/
├── main.py                    # create_app() factory, 40 routes, lifespan
├── config.py                  # pydantic-settings (sqlite/mysql/postgres)
├── db.py                      # async engine + AsyncSessionFactory
├── deps.py                    # get_db, current_user (dev-mode header auth)
├── models/
│   ├── __init__.py            # forces mapper registration (all 9 models)
│   ├── base.py                # ItemBase BB-1 mixin + DeclarativeBase
│   ├── project.py
│   ├── user.py
│   ├── test_target.py
│   ├── test_case.py
│   ├── request.py
│   ├── test_run.py
│   ├── item_status_history.py
│   ├── item_status_transition.py
│   └── iteration_test_set.py
├── schemas/
│   ├── common.py              # Page[T], Problem
│   ├── test_target.py
│   ├── test_case.py
│   ├── request_schema.py
│   └── test_run.py
├── services/
│   ├── test_targets.py
│   ├── test_cases.py
│   ├── test_runs.py
│   ├── requests.py
│   └── transitions.py
├── routers/
│   ├── projects.py
│   ├── test_targets.py
│   ├── test_cases.py
│   ├── requests.py
│   ├── test_runs.py
│   ├── state_machine.py
│   ├── value_lists.py
│   ├── sync.py                # 501 stubs (D-10)
│   └── trace.py
└── domain/
    ├── statuses.py            # TransitionError, RoleError, state machine loader
    └── decomposition.py       # R-TC-3/R-TC-5 validators
```

### Smoke test (SMK9)
- **Result:** 20/20 PASS
- **DB:** d06.sqlite (29 migrations applied)
- **Runner:** `SQLITE_PATH=d06.sqlite python3 smoke_test.py`
- **Coverage:** projects CRUD, test-targets CRUD, test-cases create+get,
  requests create+link-cases+list, test-runs full lifecycle (create→result→finalize),
  transition, state-machine query, value-lists, trace

### Key architectural notes
- `Page[T]` envelope: `data`, `total`, `total_pages`, `page`, `page_size`
- Verdict values: `test_run_results.verdict` CHECK `pass|fail|skip|blocked|partial`
  → `overall_verdict` CHECK `pass|fail|partial|aborted|in-progress`
  → `item_status` long-form `passed|failed`
- **SQLAlchemy autobegin rule:** `db.begin()` safe only as first op on session.
  Methods that SELECT-then-mutate execute DML directly in autobegin transaction;
  `get_db` commits on response.
- SQLite: `FOR UPDATE` omitted (`settings.db_driver == "sqlite"` check in transitions.py)
- `request_test_cases` upsert: portable DELETE+INSERT (OQ-028 SQLite workaround)

---

## Open questions

| ID | Pri | Description | Owner |
|----|-----|-------------|-------|
| OQ-027 | Med | MySQL 8 + PG 14 full-stack smoke (D-09) | ThinkPad |
| OQ-028 | Low | `request_test_cases` INSERT dialect variants — covered by DELETE+INSERT for now | D-09 |
| OQ-026 | Low | PHP syntax validation (no PHP binary in CoWork sandbox) | ThinkPad |
