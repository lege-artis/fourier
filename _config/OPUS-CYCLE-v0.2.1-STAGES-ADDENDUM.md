# OPUS-CYCLE v0.2.1 — Stages Addendum
## Stage 0/1/2 maturity model + parallel implementation pattern + Mode-3 Testbase contract sketch + 3-tier role hooks

**Version:** v0.2.1
**Authority:** Companion + correction layer to `_config/OPUS-CYCLE-v0.2-MASTER.md`. Where this addendum and the v0.2 master differ, **this addendum supersedes** for forward planning.
**Trigger for this addendum:** user clarification 2026-05-03 — Linux/Docker is **not** a hard dependency; deployment must traverse three stages with parallel implementation patterns.
**Companion deliverables (also created/updated 2026-05-03):**
- `_config/GITHUB-ORCH-V0.2.md` (edited — actual repo names locked)
- `3-fold-path/backlog/MI-M-T-V0.2.1-POC-STAGE-0-SCOPE.md` (NEW — supersedes parts of MI-M-T-V0.2-POC-ONPREM-SCOPE.md)
- `_config/HANDOVER-V0.2-THINKPAD.md` (edited — points at v0.2.1)

---

## §1. The three stages (binding)

| Stage | Target environment | What MUST work | When | Status |
|:-----:|--------------------|----------------|------|:------:|
| **Stage 0** | ThinkPad-only (Petr's dev box) | Full functionality + tests + a "PRODUCTION instance" alongside the dev instance. Two parallel topologies (see §2). | **NOW** — implementation in v0.2.1 PoC iterations. | In design |
| **Stage 1** | Windows desktop / notebook (target dev station; **no admin permissions guarantee**) | Stand-alone install, easy to deploy by a non-admin user. Mostly the Windows-portable topology from Stage 0. | Specs land Mon/Tue next week; implementation follows. | Pre-design |
| **Stage 2** | On-prem inside corporate network (proxy + firewall) | Roles (Administrator / PowerUser / TA-Tester) enforced; full observability; backup; secrets in proper vault. | Target architecture TBD by user. | Hooks only in v0.2.1 |

**Decoupling principle (binding):** application logic and data model **MUST NOT** depend on Stage-2 specifics. Configuration, adapters, and topology choices are data-driven via env vars + a Stage discriminator (`MIMT_STAGE = 0 | 1 | 2`).

---

## §2. Parallel implementation pattern (Stage 0 binding)

The same application code base runs on **two topologies** that are exercised side-by-side:

### 2.1 Topology A — ThinkPad reference ecosystem

This is the **functionality testbed**. It uses every advanced capability available on Petr's ThinkPad.

| Layer | Tool / version |
|-------|----------------|
| HTTP server | Uvicorn behind Apache (Laragon) — or Uvicorn standalone |
| Application | FastAPI (existing 40 routes; D-08) |
| Database (DEV) | PostgreSQL 14 in Docker on port 5433 (per LL-ENV-006) |
| Database (PROD instance) | PostgreSQL 14 in Docker — separate database name `mimt_prod` on **same instance** (recommended; see §3.2 for the trade-off table) |
| Script runners | Newman + Playwright in a runner sidecar container (Docker) |
| Service supervision | Docker Compose |
| Local PG 17 (already present) | left alone — used by other ThinkPad work; avoids conflict via port 5433 |

Topology A is the **richest** and exercises every code path including Docker orchestration. Test coverage on Topology A counts as the "container path" of the matrix.

### 2.2 Topology B — Windows-portable (Stage 1 simulation)

This is the **portability testbed**. It pre-adapts everything for Stage 1 (Windows, no admin).

| Layer | Tool / version |
|-------|----------------|
| HTTP server | Uvicorn standalone (no Apache, no Docker) |
| Application | Same FastAPI codebase (zero diff) |
| Database (DEV) | SQLite file (no install) — `dev.sqlite` |
| Database (PROD instance) | SQLite file `prod.sqlite` — separate file = full isolation |
| Script runners | Newman as `npm i -g` user-level; Playwright as `pip install playwright && playwright install --with-deps` user-level |
| Service supervision | A pure Python entrypoint script (`run.py`) that boots both DEV + PROD on different ports |
| No Docker, no admin steps | Confirmed |

Topology B is what we ship to Stage 1. SMK9 + integration tests must be green on Topology B as well.

### 2.3 Code-level discipline to support both topologies

- **DB driver selection** is by env var `DB_DRIVER ∈ {sqlite, postgres, mysql}` — already implemented per D-09.
- **Path handling** — `pathlib.Path` everywhere. `os.path.join` and string concatenation are forbidden in any Stage 0 PR.
- **Script runner discovery** — `shutil.which("newman")`, `shutil.which("npx")` — never assume install path.
- **Port and host** — env vars `MIMT_HOST` (default `127.0.0.1`), `MIMT_PORT_DEV` (default 8080), `MIMT_PORT_PROD` (default 8090).
- **Healthcheck** — pure HTTP GET; identical contract on both topologies.
- **Tests** — every `pytest tests/test_smk9.py` invocation runs once per topology in CI matrix:
  - matrix row: `sqlite + windows-native`
  - matrix row: `postgres + thinkpad-docker`
  - (existing rows: `sqlite-only`, `mysql-docker`, `postgres-docker` — keep)
- **Logging** — UTF-8 only (Windows console default is cp1252; force `PYTHONIOENCODING=utf-8`).

### 2.4 What about Stage 2 Linux containers?

Stage 2 will likely use Linux containers — but Stage 0/1 work does **not** need to commit to that. The Topology A Docker compose files already exist (from v0.2 work) and serve as the seed for Stage 2. When Stage 2 specs land, we re-target the compose files to a Linux host without any application code changes.

---

## §3. PROD instance separation on ThinkPad (B/E + F/E + DB)

Per user direction: **B/E and F/E PROD instances must be completely separated processes**. DB instance is shared with separate schema OR fully decoupled — choose by trade-off.

### 3.1 Process & port plan

| Role | Topology A (ThinkPad reference) | Topology B (Windows-portable) |
|------|----------------------------------|--------------------------------|
| B/E DEV | Uvicorn :8080 (auto-reload) | Uvicorn :8080 (auto-reload) |
| F/E DEV | Same process (Jinja2 templates served by FastAPI) | Same process |
| B/E PROD | Uvicorn :8090 (no reload, multi-worker) | Uvicorn :8090 (no reload, single-worker) |
| F/E PROD | Same process (server-rendered) | Same process |
| DB DEV | PG14 Docker, db `mimt_dev` | SQLite `dev.sqlite` |
| DB PROD | PG14 Docker, db `mimt_prod` | SQLite `prod.sqlite` |
| Migration runner | Topology-agnostic CLI: `python runner.py --env=dev|prod` | Same |

**F/E split note:** in v0.2.1 Stage 0, F/E is server-rendered HTML (Jinja2 inside FastAPI); separate process applies only when SPA build ships (post-v0.3). For Stage 0, "B/E and F/E PROD separated" means the **DEV process and the PROD process are separate** — the SPA-vs-server distinction is deferred.

### 3.2 DB shared-instance vs decoupled — decision matrix

| Aspect | Shared instance (separate DB names) | Fully decoupled (separate Postgres or separate file) |
|--------|--------------------------------------|------------------------------------------------------|
| Setup cost | Low — `CREATE DATABASE mimt_prod` | Higher — second container or second file |
| Resource cost | One PG process | Two PG processes (or 1 PG + 1 SQLite file) |
| Crash isolation | None — PG crash takes both DBs | Strong — one DB up = other DB up |
| Backup independence | Per-DB dumps possible | Trivially independent |
| Security boundary | Weak — shared superuser by default | Strong — different connection creds |
| Demo realism | Lower — not a true production split | Higher — closer to Stage 2 |

**Recommendation (Stage 0 default):** **Topology A** uses shared instance with separate DB names (cheapest; demo-quality is fine for ThinkPad). **Topology B** uses fully separate SQLite files (free isolation by design). Promote to fully separate Postgres at Stage 2 boundary.

---

## §4. All 3 deployment modes scaffolded (per user direction)

Each mode gets a defined surface in v0.2.1, even where most behaviour is deferred:

### 4.1 Mode 1 — Replacement (importer skeleton)

- New module `mi_m_t/migrators/` with subclasses:
  - `JiraMigrator` — one-shot bulk import from JIRA Cloud (reuses `JiraAdapter` for HTTP).
  - `RedmineMigrator` — same shape for Redmine.
  - `AdoMigrator` — placeholder; raises `NotImplementedError` with pointer to v0.3.
- New CLI: `mimt migrate-from --source jira|redmine --token … --project … --since 1970-01-01`.
- Storage: imports land in MI-M-T tables with `external_sync_links.last_sync_direction = 'one_shot_import'` so they're re-importable but flagged as migration-origin.
- Acceptance: a small dry-run import (5 issues) from a sandbox Redmine works end-to-end on Topology A.

### 4.2 Mode 2 — Integrator (functional)

- This is the v0.2 PoC primary. No change to scope.
- Includes RedmineAdapter (G-02), JiraAdapter (D03), PostmanAdapter (D04), ZephyrAdapter (D03).
- Acceptance gate: failed test result → bug → push to Redmine round trip works.

### 4.3 Mode 3 — LLM-TDD (bridge skeleton + Testbase contract)

**Concept:** the MI-M-T data model becomes a **deterministic constraint set** that an LLM (Claude or peer) consumes to drive Test-Driven Development. The LLM never sees raw DSO rows — it sees a structured *Testbase Context* (a DDO).

**Module skeleton:**
```
mi_m_t/llm_bridge/
├── __init__.py
├── testbase.py           # composes Testbase Context from MI-M-T DSOs
├── prompts/              # canonical prompt templates
│   ├── tdd_initial.txt
│   ├── tdd_iterate.txt
│   └── result_ingest.txt
└── adapters/
    └── claude_stub.py    # Bring-Your-Own-LLM pattern; this stub
                          # documents the call shape but does not call out
```

**Testbase Context schema (DDO contract sketch — v0.2.1 draft):**

```yaml
testbase_context_version: "0.1.0"
project: { id: …, code: "MIMT-PoC", name: "…" }

scope:
  test_targets:                    # one or more — the LLM's task scope
    - id: TT-…
      title: …
      description: …
      requirement_refs: [REQ-…]
      implementation_ref: "path/to/code"

constraints:
  requirements:                    # what acceptance language the code MUST satisfy
    - id: REQ-…
      acceptance_criteria: [GIVEN…WHEN…THEN…]

test_cases:                        # the executable contract
  - id: TC-…
    test_target_ref: TT-…
    requirement_ref: REQ-…
    phases:
      - phase_type: pre|exec|post
        description: …
        resources: [{ type: test_data|test_script|…, ref: … }]

test_data:                         # the deterministic seed
  - id: TD-…
    payload: { … }                 # JSON; deterministic across runs

environment_seeds:                 # the deterministic environment
  - id: TE-…
    description: …
    seed_values: { … }

prior_results:                     # past runs (LLM may use as hints)
  - test_case_ref: TC-…
    last_verdict: pass|fail|…
    last_actual: …
    last_run_date: …

llm_instructions:                  # generated from prompts/tdd_initial.txt
  task: "Generate code that makes all test cases pass. Do not change test data or environment seeds. Run constraints in this order: …"
  invariants: ["No outbound HTTPS in DB tx", "All paths via pathlib", "Code must be reviewable", …]
  output_format: "unified diff against base_ref or full file"
```

**End-to-end happy path (Mode 3 v0.2.1 acceptance):**
1. Pick one TestTarget (e.g. TT-005 in MI-M-T's own evidence — podcast player init).
2. Render Testbase Context for it via `mi_m_t/llm_bridge/testbase.py:render(test_target_id) → Context`.
3. **Manually** feed the Context to Claude (no auto-call yet — that's Stage 2 work).
4. Claude generates a code suggestion.
5. Petr reviews + applies the suggestion.
6. Run the test cases via the standard MI-M-T runner (Mode 2 path).
7. Record the run; verify the LLM-generated code passed.
8. **Document the cycle** in `3-fold-path/code/SESSION-NOTES.md` as the first Mode-3 demonstration.

This is "scaffolded" — not "automated". Mode 3 automation is v0.3+ scope.

---

## §5. Roles — single admin user; 3-tier hooks (per user direction)

### 5.1 Role model

The 3-tier organizational permission model is **orthogonal** to the existing CAST process roles in `users.role_in_process` (PM/DM/TM/TA/TD/TI/TE/PAn). Both are kept:
- `users.role_in_process` (existing) — drives state-machine transition authority.
- `users.permission_tier` (NEW column in v0.2.1 migration) — drives endpoint access authority.

### 5.2 Permission tiers (3 values + admin singleton)

| Tier | Symbolic name | What can do (Stage 2 enforcement; Stage 0 hook only) |
|------|---------------|------------------------------------------------------|
| `administrator` | Administrator | Full system control: user CRUD, migrations, secrets, all data |
| `power_user` | Power User | All test design + execution + reporting; cannot manage users / system |
| `ta_tester` | TA / Tester | Read all; write only own test runs + results + linked requests |

In Stage 0 only the **administrator** tier exists (one local env-defined admin). The other tiers exist as code but every role check returns `True` for the admin user. Stage 2 activates the actual checks.

### 5.3 Migration to add the column

```sql
-- v0.2.1 migration: 110_add_permission_tier_to_users.sql
ALTER TABLE users ADD COLUMN permission_tier VARCHAR(20)
    NOT NULL DEFAULT 'administrator';

UPDATE users SET permission_tier = 'administrator';   -- Stage 0 default

ALTER TABLE users ADD CONSTRAINT ck_users_permission_tier
    CHECK (permission_tier IN ('administrator', 'power_user', 'ta_tester'));
```

(Portable across SQLite + PG + MySQL per ARCH-SPEC §0.4.)

### 5.4 Decorator + middleware shells

```python
# mi_m_t/auth/permissions.py
from enum import Enum
from functools import wraps

class Tier(str, Enum):
    ADMINISTRATOR = "administrator"
    POWER_USER = "power_user"
    TA_TESTER = "ta_tester"

def require_tier(*allowed: Tier):
    """Stage 0: pass-through for the env-defined admin only.
       Stage 2: actually enforces."""
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            # In Stage 0, the auth middleware injects user as the env admin
            # → permission_tier is ADMINISTRATOR → all checks pass
            return await fn(*args, **kwargs)
        wrapper.__mimt_required_tier__ = tuple(t.value for t in allowed)
        return wrapper
    return decorator
```

The `__mimt_required_tier__` attribute documents intent and is asserted by the smoke suite (`tests/test_permission_tiers_documented.py`) so every endpoint declares its target tier even if the check is pass-through.

### 5.5 Stage 2 activation checklist (NOT in v0.2.1)

- Real auth provider wired (Keycloak via existing AUTH-005/006 work)
- Multi-user creation UI + role assignment
- `require_tier` decorator switches from pass-through to enforced
- Endpoint-tier mapping audit
- Audit-log of access denials

---

## §6. Iteration plan revisions

The v0.2 master §7.1 listed PoC-01..PoC-12. v0.2.1 retargets the early iterations:

| Iter | Owner | Was (v0.2) | Now (v0.2.1) |
|------|-------|------------|--------------|
| **PoC-01** | ThinkPad | testcases.yaml v2 + Dockerfile first cut | testcases.yaml v2 + **Topology B (Windows-portable) entrypoint** + parallel runner script (`run.py` boots DEV + PROD on different ports) |
| **PoC-02** | ThinkPad | Dockerfile finalised + RUNBOOK-DEVOPS | **Topology A Docker compose finalised** (becomes Stage-2 seed) **+ portability matrix** (Topology A × Topology B × {SQLite, PG}) |
| **PoC-03** | ThinkPad | Redmine adapter contract + scaffold | (unchanged — D05 contract doc) |
| **PoC-04** | ThinkPad | Redmine adapter implementation | (unchanged) |
| **PoC-05** | ThinkPad | PlaywrightAdapter | (unchanged — runs on both topologies) |
| **PoC-06** | ThinkPad | SOAP + REST runners | (unchanged) |
| **PoC-07/08** | ThinkPad | TestCase UI | (unchanged) |
| **PoC-09** | ThinkPad | Test cycle UI | (unchanged) |
| **PoC-10** | ThinkPad | Issue tracking + Redmine push | (unchanged) |
| **PoC-11** | ThinkPad | Basic reporting | (unchanged) |
| **PoC-12** | ThinkPad | Hooks (G-10 + G-11) | **Now includes**: 3-tier `permission_tier` migration + decorator shell + Mode 1 importer skeleton + Mode 3 Testbase context renderer + the Mode-3 manual happy-path demonstration |

A new addition for v0.2.1:

| Iter | Owner | Deliverable |
|------|-------|-------------|
| **PoC-13** | ThinkPad | **Stage 1 readiness audit** — confirm Topology B has zero admin-required steps; produce `RUNBOOK-WIN-PORTABLE.md`; dry-run on a fresh Windows user without admin (use a separate Windows account on the ThinkPad) |

---

## §7. Status

| Item | Value |
|------|-------|
| Document | `OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` |
| Output position | `_config/OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` |
| Stages defined | 3 (0/1/2) |
| Topologies in Stage 0 | 2 parallel (A: ThinkPad reference; B: Windows-portable) |
| Modes scaffolded in Stage 0 | 3 (Replacement importer skeleton, Integrator functional, LLM-TDD bridge skeleton) |
| Permission tiers introduced | 3 (Administrator, PowerUser, TA-Tester) — hooks only |
| Iterations adjusted | PoC-01, PoC-02, PoC-12 modified; PoC-13 added |
| Status | Draft v0.2.1 — supersedes v0.2 master where they conflict |

---

*OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md — 2026-05-03 — MacBook CoWork session — Opus*
