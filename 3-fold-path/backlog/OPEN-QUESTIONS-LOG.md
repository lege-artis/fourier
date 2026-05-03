# MI-M-T Open Questions Log
## Schema version: 1.0 — template per DEV-SONNET-INSTRUCTIONS §9

**Authority:** MacBook/Opus resolves Blocking/High entries. Dev Sonnet opens entries and stops.  
**Created:** 2026-04-27 — MacBook CoWork session, seeded from ARCH-SPEC §9  
**Format:** append-only — never delete entries; update status and add resolution notes.

---

## Template (copy for each new OQ)

```
### OQ-NNN — {one-line title}
- **Raised by:** {Dev Sonnet D-NN | MacBook/Opus | user}
- **Date:** YYYY-MM-DD
- **Severity:** Blocking | High | Medium | Low
- **Blocking impact:** {what stops if unresolved}
- **Suggested resolution:** {how to find the answer}
- **Status:** open | in-progress | answered | deferred
- **Resolution:** (fill when answered)
- **Input doc change:** none | {doc name vX.Y}
```

---

## Seeded from ARCH-SPEC §9 (2026-04-27 — pre-development, not yet Blocking)

### OQ-001 — Active24 MySQL exact version
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** JSON column behaviour, CHECK enforcement, utf8mb4_0900_ai_ci availability
- **Suggested resolution:** `SHOW VARIABLES LIKE 'version%';` on Active24 PHPMyAdmin during first connection
- **Status:** open
- **Resolution:** —

### OQ-002 — Active24 PHP version + extensions
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** High
- **Blocking impact:** Controls available syntax (8.0/8.1/8.2) and pdo_mysql/mbstring/json/openssl availability
- **Suggested resolution:** `phpinfo()` page on Active24 (delete after read)
- **Status:** open
- **Resolution:** —

### OQ-003 — Active24 disk quota and per-file upload limit
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** item_attachments storage strategy (local FS vs external object storage)
- **Suggested resolution:** Active24 control panel or support ticket
- **Status:** open
- **Resolution:** —

### OQ-004 — Active24 outbound HTTPS allowance
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low
- **Blocking impact:** Whether light D03/D04 sync from PHP is feasible
- **Suggested resolution:** `curl https://api.atlassian.com/...` from a PHP test script
- **Status:** open
- **Resolution:** —

### OQ-005 — Active24 cron / scheduled-task support
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** How D03/D04 reconcile runs are scheduled
- **Suggested resolution:** Active24 docs or support
- **Status:** open
- **Resolution:** —

### OQ-006 — Active24 SSH access
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** High
- **Blocking impact:** Controls how migrations are applied (CLI vs HTTP runner)
- **Suggested resolution:** Active24 plan check
- **Status:** open
- **Resolution:** —

### OQ-007 — ThinkPad Laragon stack versions
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** Local dev parity vs Active24; D-01 STEP 1 env verification
- **Suggested resolution:** `php -v && mysql --version && python --version` on ThinkPad (D-01 STEP 1 captures this)
- **Status:** open — resolved by D-01 STEP 1 verification
- **Resolution:** —

### OQ-008 — ThinkPad Docker availability
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** Multi-engine portability matrix (SQLite + MySQL + PostgreSQL)
- **Suggested resolution:** `docker info` on ThinkPad
- **Status:** open — resolved by D-01 STEP 1 verification
- **Resolution:** —

### OQ-009 — Production language decision (Scala/Rust/C#)
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low (deferred — out of MVP scope)
- **Blocking impact:** ORM choice, build pipeline, hosting — none for MVP
- **Suggested resolution:** Tracked as ARC-DEC-LANG; decide post-MVP
- **Status:** deferred
- **Resolution:** Deferred post-MVP per project constraints.

### OQ-010 — Production hosting decision
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low (deferred — out of MVP scope)
- **Blocking impact:** Deployment topology, secret management
- **Suggested resolution:** Tracked as ARC-DEC-HOST; decide post-MVP
- **Status:** deferred
- **Resolution:** Deferred post-MVP per project constraints.

### OQ-011 — Auth provider for MVP (local users vs SSO)
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** password_hash column strategy in users table
- **Suggested resolution:** Assume local users with bcrypt for MVP; add password_hash CHAR(60) NULL in later migration
- **Status:** answered
- **Resolution:** Local users + bcrypt assumed for MVP per ARCH-SPEC §9 Q11 default.

### OQ-012 — Frozen JIRA + Zephyr API versions in production tenant
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** High
- **Blocking impact:** D03 contract depends on v3/v2 surface availability
- **Suggested resolution:** Confirm with target JIRA Cloud tenant; pin Atlassian-API-Version header
- **Status:** open
- **Resolution:** —

### OQ-013 — Postman/Newman version on target test runner
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** D04 contract assumes Postman v10 / Newman 6
- **Suggested resolution:** `newman --version` on ThinkPad; document in adapter README
- **Status:** open — resolved by D-01 STEP 1 verification
- **Resolution:** —

### OQ-014 — Time zone policy (UTC vs per-user display TZ)
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low
- **Blocking impact:** UI only
- **Suggested resolution:** Assume browser-local display; UTC storage
- **Status:** answered
- **Resolution:** UTC storage, browser-local display for MVP.

### OQ-015 — Soft-delete vs hard-delete for requests and test_runs
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** Whether deleted_at column needed
- **Suggested resolution:** Current spec uses status=cancelled; confirm with stakeholders
- **Status:** open
- **Resolution:** —

### OQ-016 — Multi-tenant isolation strategy
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low (MVP)
- **Blocking impact:** Strategic only; row-level adequate for MVP
- **Suggested resolution:** Row-level (project_id filter) confirmed for MVP
- **Status:** answered
- **Resolution:** Row-level via project_id for MVP. Schema-per-tenant deferred.

### OQ-017 — Concurrency model for test_run_results ingestion
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** Partial result resubmission semantics
- **Suggested resolution:** Define in test execution UX session; UNIQUE(test_run_id, test_case_id) already prevents double-write
- **Status:** open
- **Resolution:** —

### OQ-018 — last_run_date/verdict denormalisation refresh strategy
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low
- **Blocking impact:** MVP volumes manageable synchronously
- **Suggested resolution:** Synchronous for MVP; async job post-MVP
- **Status:** answered
- **Resolution:** Synchronous refresh in PHP/Python for MVP.

### OQ-019 — item_correlations UI surface for MVP
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low
- **Blocking impact:** None — storage model defined, UI deferrable
- **Suggested resolution:** Read-only display for MVP; full editor post-MVP
- **Status:** answered
- **Resolution:** Read-only for MVP.

### OQ-020 — Migration runner on Active24 (CLI vs HTTP)
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** Deployment ergonomics for D-10
- **Suggested resolution:** PHP HTTP runner with shared-secret guard for MVP (see ARCH-SPEC §6.5)
- **Status:** answered
- **Resolution:** HTTP-triggered runner with shared-secret guard per ARCH-SPEC §6.5.

### OQ-021 — Materialised path maintenance without triggers
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low
- **Blocking impact:** None — app-maintained pattern decided
- **Suggested resolution:** App-maintained on every parent change; TestTargetRepo.update_parent
- **Status:** answered
- **Resolution:** Application-layer maintained per ARCH-SPEC §9 Q21.

### OQ-022 — test/ fixture size and CI matrix cost
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low
- **Blocking impact:** CI runtime
- **Suggested resolution:** SQLite as default fast-CI; nightly cron for MySQL + PG matrix (D-11)
- **Status:** answered
- **Resolution:** SQLite fast-CI default; nightly MySQL+PG per D-11 plan.

### OQ-023 — FL-CAST 26-state lifecycle round-trip requirement
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low (strategic)
- **Blocking impact:** Whether CAST Excel export is needed
- **Suggested resolution:** Confirm CAST is read-only/archive; ARCH-ANALYSIS §3.1 mapping is one-way
- **Status:** answered
- **Resolution:** CAST Excel is archive/reference only. MI-M-T 12-state is canonical. No round-trip required.

### OQ-024 — Polymorphic tables enforcement (app-only vs partial indexes)
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Low
- **Blocking impact:** Query plan quality at scale
- **Suggested resolution:** App-only enforcement for MVP; revisit if query plans degrade
- **Status:** answered
- **Resolution:** App-layer only for MVP.

### OQ-025 — Active24 backup posture
- **Raised by:** MacBook/Opus ARCH-SPEC §9
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** Data safety for demo environment
- **Suggested resolution:** Active24 control-panel scheduled backups; document restore runbook in RUNBOOK.md (D-10)
- **Status:** open
- **Resolution:** —

---

## Raised in D-01 (2026-04-27 — Dev Sonnet ThinkPad session)

### OQ-026 — PHP binary not available in CoWork sandbox
- **Raised by:** Dev Sonnet D-01 environment verification
- **Date:** 2026-04-27
- **Severity:** Medium
- **Blocking impact:** runner.php cannot be syntax-checked or smoke-tested in the sandbox.
  PHP validation deferred to ThinkPad Laragon (PHP 8.x present) or Active24 environment.
  Does NOT block D-01 SQLite validation (Python runner covers that) or D-02 DDL work.
- **Suggested resolution:** Run `php runner.php --engine=mysql` on ThinkPad Laragon after
  starting MySQL. Verify on Active24 as part of D-09 (adapter smoke).
- **Status:** open
- **Resolution:** —

### OQ-027 — MySQL + PostgreSQL servers not running in CoWork sandbox
- **Raised by:** Dev Sonnet D-01 environment verification
- **Date:** 2026-04-27
- **Severity:** High
- **Blocking impact:** D-01 portability matrix is incomplete for MySQL and PostgreSQL engines.
  SQLite path fully validated (PASS: apply + idempotency + drift detection).
  MySQL and PostgreSQL validation must be completed on ThinkPad before D-02 closes.
- **Suggested resolution:** On ThinkPad: (1) start Laragon MySQL → run
  `python runner.py --engine mysql`; (2) `docker compose up -d postgres` →
  run `python runner.py --engine postgres`. Record output in SESSION-NOTES.md
  under "D-01 matrix results — MySQL / PostgreSQL". Mark OQ-027 answered once
  both engines show APPLIED for version 000.
- **Status:** open
- **Resolution:** —

---

*OPEN-QUESTIONS-LOG.md — append-only — MacBook/Opus owns resolution of Blocking/High entries*

---

## Raised in PoC-03 (2026-05-03 — ThinkPad CoWork session)

### OQ-100 — Org Redmine workflow status names
- **Raised by:** ThinkPad Sonnet PoC-03
- **Date:** 2026-05-03
- **Severity:** High
- **Blocking impact:** RedmineAdapter.map_status() cannot produce correct MI-M-T status values
  without knowing the org's actual Redmine status list. Default mapping in D05 §3.4 assumes
  Redmine factory defaults: New / In Progress / Resolved / Feedback / Closed / Rejected.
  If the org has renamed or added statuses (e.g. "Open", "Under Review", "Fixed", "Verified",
  "Won't Fix"), PoC-04 fixture replays will produce incorrect status mappings.
  **PoC-04 STOP gate** — do not start RedmineAdapter implementation until answered.
- **Suggested resolution:** Run `GET /issue_statuses.json` on the org's Redmine instance
  and copy the full list of `{id, name, is_closed}` objects here. Then fill the
  `redmine.status_map` block in `_config/mi-m-t-sync.yaml`.
- **Status:** deferred — recall Tuesday 2026-05-05 (Redmine config artifacts expected)
- **Resolution:** —
- **Input doc change:** MI-M-T-D05-REDMINE-CONTRACT.md §3.4 status_map table

### OQ-101 — Org Redmine instance URL + version
- **Raised by:** ThinkPad Sonnet PoC-03
- **Date:** 2026-05-03
- **Severity:** High
- **Blocking impact:** Determines: (a) base_url in credentials.yaml; (b) webhook strategy
  (§5.1 built-in for Redmine 5.1+; §5.2 plugin for ≤5.0; §5.3 polling-only if no public
  endpoint). Version < 2.2 would mean no REST API at all (extremely unlikely).
- **Suggested resolution:** (1) Provide the Redmine URL. (2) Run `GET /api/v1/about.json`
  or check Redmine Administration → Information → Redmine version.
- **Status:** deferred — recall Tuesday 2026-05-05 (Redmine config artifacts expected)
- **Resolution:** —
- **Input doc change:** MI-M-T-D05-REDMINE-CONTRACT.md §1.2 + §5

### OQ-102 — Tracker name for Test Cases in org Redmine
- **Raised by:** ThinkPad Sonnet PoC-03
- **Date:** 2026-05-03
- **Severity:** Medium
- **Blocking impact:** `testcase_tracker_id` config cannot be set; import --tracker testcase
  will fail to resolve the correct tracker. Default assumption: tracker name "Test Case".
  If not present, test case import is blocked.
- **Suggested resolution:** Run `GET /trackers.json` on the org's Redmine and list tracker
  names. Confirm which tracker (if any) is designated for test cases.
  If absent: confirm whether MI-M-T should create test cases under a different tracker
  (e.g. "Task") or request a new "Test Case" tracker from Redmine admin.
- **Status:** open
- **Resolution:** —
- **Input doc change:** MI-M-T-D05-REDMINE-CONTRACT.md §3.3

### OQ-103 — Custom field IDs in org Redmine (TC-ID, Test Target, Requirement)
- **Raised by:** ThinkPad Sonnet PoC-03
- **Date:** 2026-05-03
- **Severity:** Medium
- **Blocking impact:** D05 §3.3 custom field mapping (TC-ID, Test Target ref, Requirement ref)
  requires the org's Redmine custom field IDs. Without them, the adapter cannot read/write
  MI-M-T-specific metadata via Redmine custom fields. Workaround: embed metadata in
  issue description using §3.6 step block convention (no custom fields needed for MVP).
- **Suggested resolution:** Run `GET /custom_fields.json` with an admin API key. List fields
  associated with the Bug and Test Case trackers. Or defer to description-only mode for MVP.
- **Status:** open
- **Resolution:** —
- **Input doc change:** MI-M-T-D05-REDMINE-CONTRACT.md §3.5


---

### OQ-300 — kh-sim license preference

- **Raised:** 2026-05-03 (KH-01 audit)
- **Severity:** Low
- **Block:** None — MIT defaulted; change only if user requests different license
- **Question:** Is MIT the correct license for kh-sim public release, or should a
  different license (GPL-2.0, Apache-2.0, etc.) be applied?
- **Status:** open — confirm or leave MIT as-is
- **Context:** `kh-sim/LICENSE` committed as MIT. If changed, update LICENSE file and
  README.md badge. CONTRIBUTING.md references MIT implicitly via LICENSE link.
