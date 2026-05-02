-- =========================================================================
-- migration: 101_seed_item_status_transitions.sql
-- date:      2026-04-28
-- author:    pete
-- depends:   021
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §4.2 (canonical state machine seed),
--           §4.3 (app-layer 'any' expansion rule — see note below),
--           §8.6 (seed apply order), §8.7 (idempotency posture)
-- Purpose:  Populate item_status_transitions with the MI-M-T MVP state
--           machine for all 8 entity tables.
-- Idempotency: DELETE + INSERT. Re-running converges to canonical state.
-- Note on 'any': row ('test_cases','any','deferred','TM',...) is intentional.
--   'any' is not a status value — it is a wildcard sentinel. The query layer
--   (§6.5.1 PHP / §7 Python) matches it as:
--     WHERE (from_status = :from OR from_status = 'any')
--   No CHECK constraint guards from_status, so the row is DB-valid.
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

DELETE FROM item_status_transitions;

INSERT INTO item_status_transitions
    (id, entity_table, from_status, to_status, requires_role, description, is_active)
VALUES

-- ── test_targets (18 transitions) ────────────────────────────────────────
    ( 1, 'test_targets', 'new',          'in-analysis', NULL, 'Submit for analysis',       {{BOOL_TRUE}}),
    ( 2, 'test_targets', 'new',          'cancelled',   'TM', 'Reject before analysis',    {{BOOL_TRUE}}),
    ( 3, 'test_targets', 'new',          'duplicate',   NULL, 'Mark duplicate',             {{BOOL_TRUE}}),
    ( 4, 'test_targets', 'in-analysis',  'confirmed',   'TM', 'Confirm scope',              {{BOOL_TRUE}}),
    ( 5, 'test_targets', 'in-analysis',  'deferred',    'TM', 'Defer to later release',    {{BOOL_TRUE}}),
    ( 6, 'test_targets', 'in-analysis',  'cancelled',   'TM', 'Reject after analysis',     {{BOOL_TRUE}}),
    ( 7, 'test_targets', 'in-analysis',  'duplicate',   NULL, 'Mark duplicate',             {{BOOL_TRUE}}),
    ( 8, 'test_targets', 'confirmed',    'in-progress', NULL, 'Begin test design',          {{BOOL_TRUE}}),
    ( 9, 'test_targets', 'confirmed',    'deferred',    'TM', 'Defer',                      {{BOOL_TRUE}}),
    (10, 'test_targets', 'in-progress',  'implemented', NULL, 'Test cases drafted',         {{BOOL_TRUE}}),
    (11, 'test_targets', 'in-progress',  'deferred',    'TM', 'Defer',                      {{BOOL_TRUE}}),
    (12, 'test_targets', 'implemented',  'verifying',   NULL, 'Hand off for verification',  {{BOOL_TRUE}}),
    (13, 'test_targets', 'verifying',    'passed',      NULL, 'Verification passed',        {{BOOL_TRUE}}),
    (14, 'test_targets', 'verifying',    'failed',      NULL, 'Verification failed',        {{BOOL_TRUE}}),
    (15, 'test_targets', 'failed',       'in-progress', NULL, 'Re-open for rework',         {{BOOL_TRUE}}),
    (16, 'test_targets', 'passed',       'closed',      'TM', 'Close target',               {{BOOL_TRUE}}),
    (17, 'test_targets', 'deferred',     'in-analysis', NULL, 'Resume analysis',            {{BOOL_TRUE}}),
    (18, 'test_targets', 'deferred',     'cancelled',   'TM', 'Cancel deferred target',     {{BOOL_TRUE}}),

-- ── test_cases (12 transitions — including 'any' sentinel) ───────────────
    (19, 'test_cases', 'new',          'in-analysis', NULL, 'Begin design',                       {{BOOL_TRUE}}),
    (20, 'test_cases', 'new',          'cancelled',   'TM', 'Reject',                             {{BOOL_TRUE}}),
    (21, 'test_cases', 'new',          'duplicate',   NULL, 'Mark duplicate',                      {{BOOL_TRUE}}),
    (22, 'test_cases', 'in-analysis',  'in-progress', 'TD', 'Start drafting',                     {{BOOL_TRUE}}),
    (23, 'test_cases', 'in-progress',  'implemented', 'TD', 'Draft complete',                     {{BOOL_TRUE}}),
    (24, 'test_cases', 'implemented',  'verifying',   'TM', 'Submit for review',                  {{BOOL_TRUE}}),
    (25, 'test_cases', 'verifying',    'passed',      'TM', 'Review approved',                    {{BOOL_TRUE}}),
    (26, 'test_cases', 'verifying',    'failed',      'TM', 'Review rejected',                    {{BOOL_TRUE}}),
    (27, 'test_cases', 'failed',       'in-progress', 'TD', 'Rework',                             {{BOOL_TRUE}}),
    (28, 'test_cases', 'passed',       'closed',      'TM', 'Close (active in MasterTestSet)',     {{BOOL_TRUE}}),
    (29, 'test_cases', 'closed',       'in-progress', 'TM', 'Re-open for change',                 {{BOOL_TRUE}}),
    (30, 'test_cases', 'any',          'deferred',    'TM', 'Defer — any sentinel (see §4.3)',    {{BOOL_TRUE}}),

-- ── test_scripts (6 transitions) ─────────────────────────────────────────
    (31, 'test_scripts', 'new',          'in-progress', NULL, 'Author script',  {{BOOL_TRUE}}),
    (32, 'test_scripts', 'in-progress',  'implemented', NULL, 'Script ready',   {{BOOL_TRUE}}),
    (33, 'test_scripts', 'implemented',  'passed',      NULL, 'Verified',       {{BOOL_TRUE}}),
    (34, 'test_scripts', 'implemented',  'failed',      NULL, 'Found broken',   {{BOOL_TRUE}}),
    (35, 'test_scripts', 'failed',       'in-progress', NULL, 'Repair',         {{BOOL_TRUE}}),
    (36, 'test_scripts', 'passed',       'closed',      'TM', 'Archive',        {{BOOL_TRUE}}),

-- ── test_data (3 transitions) ─────────────────────────────────────────────
    (37, 'test_data', 'new',          'implemented', NULL, 'Provided',    {{BOOL_TRUE}}),
    (38, 'test_data', 'implemented',  'closed',      'TM', 'Archive',     {{BOOL_TRUE}}),
    (39, 'test_data', 'implemented',  'deferred',    'TM', 'Defer',       {{BOOL_TRUE}}),

-- ── test_environments (3 transitions) ────────────────────────────────────
    (40, 'test_environments', 'new',          'implemented', NULL, 'Provisioned',  {{BOOL_TRUE}}),
    (41, 'test_environments', 'implemented',  'closed',      'TM', 'Archive',      {{BOOL_TRUE}}),
    (42, 'test_environments', 'implemented',  'deferred',    'TM', 'Defer',        {{BOOL_TRUE}}),

-- ── iteration_test_sets (4 transitions) ──────────────────────────────────
    (43, 'iteration_test_sets', 'new',          'confirmed',   'TM', 'Plan locked',          {{BOOL_TRUE}}),
    (44, 'iteration_test_sets', 'confirmed',    'in-progress', NULL, 'Iteration starts',     {{BOOL_TRUE}}),
    (45, 'iteration_test_sets', 'in-progress',  'closed',      'TM', 'Iteration closed',     {{BOOL_TRUE}}),
    (46, 'iteration_test_sets', 'in-progress',  'cancelled',   'TM', 'Iteration cancelled',  {{BOOL_TRUE}}),

-- ── test_runs (6 transitions) ─────────────────────────────────────────────
    (47, 'test_runs', 'new',          'in-progress', NULL, 'Run started',                               {{BOOL_TRUE}}),
    (48, 'test_runs', 'in-progress',  'passed',      NULL, 'Run completed: all pass',                   {{BOOL_TRUE}}),
    (49, 'test_runs', 'in-progress',  'failed',      NULL, 'Run completed: at least one fail',          {{BOOL_TRUE}}),
    (50, 'test_runs', 'in-progress',  'cancelled',   NULL, 'Run aborted',                               {{BOOL_TRUE}}),
    (51, 'test_runs', 'passed',       'closed',      'TM', 'Sign off',                                  {{BOOL_TRUE}}),
    (52, 'test_runs', 'failed',       'closed',      'TM', 'Sign off (failures captured as requests)',  {{BOOL_TRUE}}),

-- ── requests (14 transitions) ─────────────────────────────────────────────
    (53, 'requests', 'new',          'in-analysis', NULL, 'Triage',                     {{BOOL_TRUE}}),
    (54, 'requests', 'in-analysis',  'confirmed',   'TM', 'Confirm bug/change',         {{BOOL_TRUE}}),
    (55, 'requests', 'in-analysis',  'duplicate',   NULL, 'Mark duplicate',              {{BOOL_TRUE}}),
    (56, 'requests', 'in-analysis',  'cancelled',   'TM', 'Reject',                     {{BOOL_TRUE}}),
    (57, 'requests', 'in-analysis',  'deferred',    'TM', 'Defer to next release',      {{BOOL_TRUE}}),
    (58, 'requests', 'confirmed',    'in-progress', 'DM', 'Assign to development',      {{BOOL_TRUE}}),
    (59, 'requests', 'in-progress',  'implemented', NULL, 'Fix submitted',               {{BOOL_TRUE}}),
    (60, 'requests', 'implemented',  'verifying',   'TM', 'Hand to QA',                 {{BOOL_TRUE}}),
    (61, 'requests', 'verifying',    'passed',      'TE', 'Verified',                   {{BOOL_TRUE}}),
    (62, 'requests', 'verifying',    'failed',      'TE', 'Verification failed',        {{BOOL_TRUE}}),
    (63, 'requests', 'failed',       'in-progress', 'DM', 'Re-open',                   {{BOOL_TRUE}}),
    (64, 'requests', 'passed',       'closed',      'TM', 'Close successfully',         {{BOOL_TRUE}}),
    (65, 'requests', 'deferred',     'in-analysis', NULL, 'Resume triage',              {{BOOL_TRUE}}),
    (66, 'requests', 'deferred',     'cancelled',   'TM', 'Cancel deferred',            {{BOOL_TRUE}});

-- ─── DOWN ─────────────────────────────────────────────────────────────────
-- DOWN BEGIN
DELETE FROM item_status_transitions;
-- DOWN END
