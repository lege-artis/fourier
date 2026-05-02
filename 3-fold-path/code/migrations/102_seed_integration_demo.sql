-- =========================================================================
-- migration: 102_seed_integration_demo.sql
-- date:      2026-04-28
-- author:    pete
-- depends:   025, 100
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ]
-- =========================================================================
-- Citation: ARCH-SPEC §7.1 (jira_sync_links DDL), §8.6 (seed apply order),
--           MI-M-T-D03-JIRA-CONTRACT §3 (JIRA adapter key conventions),
--           MI-M-T-D04-POSTMAN-CONTRACT §3 (Postman adapter key conventions)
-- Purpose:  Demo/LDE rows for jira_sync_links — exercises all three external
--           systems (jira, zephyr, postman) across representative entity types.
--           NOT for production. Soft-FK rows: entity_table/entity_id are
--           representative placeholder IDs; no DB-level FK enforced.
-- Idempotency: DELETE + INSERT.
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

DELETE FROM jira_sync_links;

-- jira_sync_links: (entity_table, entity_id, external_system, external_key)
-- Soft-FK mapping pattern per ARCH-SPEC §7.1. entity_id=1 refers to the
-- first MIMT project item in each entity table (created during dogfood runs).

INSERT INTO jira_sync_links
    (id, entity_table, entity_id, external_system, external_key,
     external_url, last_sync_at, last_sync_direction, sync_state, sync_error)
VALUES

-- ── JIRA Cloud links (entity type: requests / test_targets) ──────────────
    (1, 'requests',     1, 'jira', 'MIMT-001',
     'https://your-domain.atlassian.net/browse/MIMT-001',
     '2026-04-27T00:00:00', 'push', 'ok', NULL),

    (2, 'requests',     2, 'jira', 'MIMT-002',
     'https://your-domain.atlassian.net/browse/MIMT-002',
     '2026-04-27T00:00:00', 'push', 'ok', NULL),

    (3, 'test_targets', 1, 'jira', 'MIMT-010',
     'https://your-domain.atlassian.net/browse/MIMT-010',
     NULL, NULL, 'ok', NULL),

-- ── Zephyr Scale links (entity type: test_cases / test_runs) ─────────────
    (4, 'test_cases',   1, 'zephyr', 'ZS-TC-001',
     'https://your-domain.atlassian.net/jira/software/projects/MIMT/boards?selectedIssue=ZS-TC-001',
     '2026-04-27T00:00:00', 'pull', 'ok', NULL),

    (5, 'test_cases',   2, 'zephyr', 'ZS-TC-002',
     NULL,
     NULL, NULL, 'ok', NULL),

    (6, 'test_runs',    1, 'zephyr', 'ZS-EXEC-001',
     NULL,
     NULL, NULL, 'ok', NULL),

-- ── Postman / Newman links (entity type: test_runs / test_scripts) ────────
    (7, 'test_runs',    2, 'postman', 'pm-collection/mimt-smoke/run-001',
     'https://www.postman.com/your-workspace/collection/mimt-smoke',
     '2026-04-27T00:00:00', 'pull', 'ok', NULL),

    (8, 'test_scripts', 1, 'postman', 'pm-collection/mimt-api/script-001',
     'https://www.postman.com/your-workspace/collection/mimt-api',
     NULL, NULL, 'ok', NULL),

-- ── Drift + error rows — exercises CHECK states ───────────────────────────
    (9, 'requests',     3, 'jira', 'MIMT-003',
     'https://your-domain.atlassian.net/browse/MIMT-003',
     '2026-04-27T00:00:00', 'reconcile', 'drift',
     'remote status=resolved / local status=in-progress — hash mismatch'),

    (10, 'test_runs',   3, 'postman', 'pm-collection/mimt-smoke/run-002',
     NULL,
     '2026-04-27T00:00:00', 'pull', 'error',
     'HTTP 401 from Postman API — token expired');

-- ─── DOWN ─────────────────────────────────────────────────────────────────
-- DOWN BEGIN
DELETE FROM jira_sync_links;
-- DOWN END
