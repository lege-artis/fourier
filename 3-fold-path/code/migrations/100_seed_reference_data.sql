-- =========================================================================
-- migration: 100_seed_reference_data.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   001, 002, 003, 004
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §8.6 (seed apply order), §8.7 (idempotency posture),
--           MOCK-FIXTURES §1.1–§1.3 (canonical seed data)
-- Purpose:  Load reference / lookup rows for the MI-M-T demo project.
--           Idempotency: DELETE in FK-safe order (children first), then
--           INSERT. Re-running this file always converges to the defined
--           canonical state. Do NOT run in production without confirmation.
-- Portability: uses only DELETE + INSERT (no ON DUPLICATE KEY / ON CONFLICT
--           / INSERT OR IGNORE) — canonical SQL, valid on all three engines.
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

-- Delete in FK-safe order: children before parents (ARCH-SPEC §8.7)
DELETE FROM value_list_items;
DELETE FROM value_lists;
DELETE FROM users;
DELETE FROM projects;

-- ── projects (MOCK-FIXTURES §1.2) ────────────────────────────────────────
INSERT INTO projects (id, project_code, name, description, status, created_at, updated_at) VALUES
    (1, 'MIMT', 'MI-M-T Demo',
     'Inception-phase demo project — dogfoods MI-M-T testing itself.',
     'active', '2026-04-27 00:00:00', '2026-04-27 00:00:00'),
    (2, 'ECOM', 'ECommerce Site',
     'Second project to exercise multi-tenancy isolation in queries.',
     'active', '2026-04-27 00:00:00', '2026-04-27 00:00:00');

-- ── users (MOCK-FIXTURES §1.2) ────────────────────────────────────────────
INSERT INTO users (id, username, email, display_name, role_in_process, is_active, created_at, updated_at) VALUES
    (1, 'pm.alice',  'pm.alice@example.com',  'Alice (PM)',  'PM',  {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00'),
    (2, 'dm.bob',    'dm.bob@example.com',    'Bob (DM)',    'DM',  {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00'),
    (3, 'tm.carol',  'tm.carol@example.com',  'Carol (TM)',  'TM',  {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00'),
    (4, 'ta.dave',   'ta.dave@example.com',   'Dave (TA)',   'TA',  {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00'),
    (5, 'td.eve',    'td.eve@example.com',    'Eve (TD)',    'TD',  {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00'),
    (6, 'ti.frank',  'ti.frank@example.com',  'Frank (TI)',  'TI',  {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00'),
    (7, 'te.grace',  'te.grace@example.com',  'Grace (TE)',  'TE',  {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00'),
    (8, 'pan.heidi', 'pan.heidi@example.com', 'Heidi (PAn)', 'PAn', {{BOOL_TRUE}}, '2026-04-01 00:00:00', '2026-04-01 00:00:00');

-- ── value_lists (MOCK-FIXTURES §1.3) ─────────────────────────────────────
INSERT INTO value_lists (id, domain, description, created_at) VALUES
    (1,  'item_status',        'Canonical 12-state lifecycle',        '2026-04-27 00:00:00'),
    (2,  'severity',           'Severity flag (A/B/C/X)',              '2026-04-27 00:00:00'),
    (3,  'priority',           'Priority flag (H/M/L/X)',              '2026-04-27 00:00:00'),
    (4,  'attention',          'Attention flag (P/S/I/X)',             '2026-04-27 00:00:00'),
    (5,  'verdict',            'Per-result verdict',                   '2026-04-27 00:00:00'),
    (6,  'overall_run_verdict','Per-run aggregate verdict',            '2026-04-27 00:00:00'),
    (7,  'phase_type',         'TestCase phase discriminator',         '2026-04-27 00:00:00'),
    (8,  'resource_type',      'Phase resource discriminator',         '2026-04-27 00:00:00'),
    (9,  'request_item_type',  'Request discriminator',                '2026-04-27 00:00:00'),
    (10, 'role_in_process',    'User role',                            '2026-04-27 00:00:00'),
    (11, 'external_system',    'Sync target system',                   '2026-04-27 00:00:00');

-- ── value_list_items (MOCK-FIXTURES §1.3) ────────────────────────────────
INSERT INTO value_list_items (id, value_list_id, code, display_label, sort_order, is_active) VALUES
    -- item_status (12 states — full lifecycle per ARCH-SPEC §6)
    (1,  1, 'new',          'New',          10, {{BOOL_TRUE}}),
    (2,  1, 'in-analysis',  'In Analysis',  20, {{BOOL_TRUE}}),
    (3,  1, 'confirmed',    'Confirmed',    30, {{BOOL_TRUE}}),
    (4,  1, 'in-progress',  'In Progress',  40, {{BOOL_TRUE}}),
    (5,  1, 'implemented',  'Implemented',  50, {{BOOL_TRUE}}),
    (6,  1, 'verifying',    'Verifying',    60, {{BOOL_TRUE}}),
    (7,  1, 'passed',       'Passed',       70, {{BOOL_TRUE}}),
    (8,  1, 'failed',       'Failed',       80, {{BOOL_TRUE}}),
    (9,  1, 'closed',       'Closed',       90, {{BOOL_TRUE}}),
    (10, 1, 'cancelled',    'Cancelled',   100, {{BOOL_TRUE}}),
    (11, 1, 'duplicate',    'Duplicate',   110, {{BOOL_TRUE}}),
    (12, 1, 'deferred',     'Deferred',    120, {{BOOL_TRUE}}),
    -- severity (MOCK-FIXTURES §1.3)
    (20, 2, 'A', 'A — Critical',  10, {{BOOL_TRUE}}),
    (21, 2, 'B', 'B — High',      20, {{BOOL_TRUE}}),
    (22, 2, 'C', 'C — Low',       30, {{BOOL_TRUE}}),
    (23, 2, 'X', 'X — Undefined', 40, {{BOOL_TRUE}}),
    -- priority (MOCK-FIXTURES §1.3)
    (30, 3, 'H', 'H — High',      10, {{BOOL_TRUE}}),
    (31, 3, 'M', 'M — Middle',    20, {{BOOL_TRUE}}),
    (32, 3, 'L', 'L — Low',       30, {{BOOL_TRUE}}),
    (33, 3, 'X', 'X — Undefined', 40, {{BOOL_TRUE}}),
    -- attention (ARCH-SPEC §3.1.3 — BB-2 constraint values)
    (40, 4, 'P', 'P — Primary',   10, {{BOOL_TRUE}}),
    (41, 4, 'S', 'S — Secondary', 20, {{BOOL_TRUE}}),
    (42, 4, 'I', 'I — Informational', 30, {{BOOL_TRUE}}),
    (43, 4, 'X', 'X — Undefined', 40, {{BOOL_TRUE}}),
    -- verdict per test_run_result (MOCK-FIXTURES §1.3)
    (50, 5, 'pass',    'Pass',    10, {{BOOL_TRUE}}),
    (51, 5, 'fail',    'Fail',    20, {{BOOL_TRUE}}),
    (52, 5, 'skip',    'Skip',    30, {{BOOL_TRUE}}),
    (53, 5, 'blocked', 'Blocked', 40, {{BOOL_TRUE}}),
    (54, 5, 'partial', 'Partial', 50, {{BOOL_TRUE}}),
    -- overall_run_verdict (ARCH-SPEC §ck_test_runs_overall)
    (60, 6, 'pass',       'Pass',        10, {{BOOL_TRUE}}),
    (61, 6, 'fail',       'Fail',        20, {{BOOL_TRUE}}),
    (62, 6, 'partial',    'Partial',     30, {{BOOL_TRUE}}),
    (63, 6, 'aborted',    'Aborted',     40, {{BOOL_TRUE}}),
    (64, 6, 'in-progress','In Progress', 50, {{BOOL_TRUE}}),
    -- phase_type (ARCH-SPEC §R-TC-3)
    (70, 7, 'pre',  'Pre-condition',  10, {{BOOL_TRUE}}),
    (71, 7, 'exec', 'Execution',      20, {{BOOL_TRUE}}),
    (72, 7, 'post', 'Post-condition', 30, {{BOOL_TRUE}}),
    -- resource_type (ARCH-SPEC §R-TC-4 / ck_tcpr_resource_type)
    (80, 8, 'test_script',      'Test Script',      10, {{BOOL_TRUE}}),
    (81, 8, 'test_data',        'Test Data',        20, {{BOOL_TRUE}}),
    (82, 8, 'test_environment', 'Test Environment', 30, {{BOOL_TRUE}}),
    (83, 8, 'test_procedure',   'Test Procedure',   40, {{BOOL_TRUE}}),
    (84, 8, 'test_component',   'Test Component',   50, {{BOOL_TRUE}}),
    (85, 8, 'test_user',        'Test User',        60, {{BOOL_TRUE}}),
    -- request_item_type (MOCK-FIXTURES §1.3)
    (90, 9, 'bug',            'Bug',            10, {{BOOL_TRUE}}),
    (91, 9, 'change_request', 'Change Request', 20, {{BOOL_TRUE}}),
    -- role_in_process (ARCH-SPEC §3.6 / ck_users_role)
    (100, 10, 'PM',  'Project Manager',      10, {{BOOL_TRUE}}),
    (101, 10, 'DM',  'Delivery Manager',     20, {{BOOL_TRUE}}),
    (102, 10, 'TM',  'Test Manager',         30, {{BOOL_TRUE}}),
    (103, 10, 'TA',  'Test Analyst',         40, {{BOOL_TRUE}}),
    (104, 10, 'TD',  'Test Designer',        50, {{BOOL_TRUE}}),
    (105, 10, 'TI',  'Test Implementer',     60, {{BOOL_TRUE}}),
    (106, 10, 'TE',  'Test Executor',        70, {{BOOL_TRUE}}),
    (107, 10, 'PAn', 'Process Analyst',      80, {{BOOL_TRUE}}),
    -- external_system (MI-M-T-D03-JIRA-CONTRACT, MI-M-T-D04-POSTMAN-CONTRACT)
    (110, 11, 'jira',    'JIRA Cloud',       10, {{BOOL_TRUE}}),
    (111, 11, 'zephyr',  'Zephyr Scale',     20, {{BOOL_TRUE}}),
    (112, 11, 'postman', 'Postman / Newman', 30, {{BOOL_TRUE}});