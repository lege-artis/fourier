-- =========================================================================
-- migration: 017_create_test_run_results.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 002, 006, 011
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.4 (junction/sub-entity DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  One result row per executed test case per run.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_run_results (
    id                {{PK_BIGINT_AUTOINC}},
    test_run_id       BIGINT       NOT NULL,
    test_case_id      BIGINT       NOT NULL,
    verdict           VARCHAR(20)  NOT NULL,
    actual_result     TEXT         NULL,
    started_at        {{TS_TYPE}}  NULL,
    finished_at       {{TS_TYPE}}  NULL,
    duration_seconds  INT          NULL,
    executor_id       BIGINT       NULL,
    evidence_ref      VARCHAR(500) NULL,
    created_at        {{TS_TYPE}}  NOT NULL,
    CONSTRAINT ux_trr_run_case       UNIQUE (test_run_id, test_case_id),
    CONSTRAINT fk_trr_run__test_runs
        FOREIGN KEY (test_run_id)  REFERENCES test_runs(id)  ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_trr_case__test_cases
        FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_trr_executor__users
        FOREIGN KEY (executor_id)  REFERENCES users(id)      ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_trr_verdict CHECK (verdict IN ('pass','fail','skip','blocked','partial'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_trr_case_verdict ON test_run_results(test_case_id, verdict);
CREATE INDEX ix_trr_run_verdict  ON test_run_results(test_run_id,  verdict);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_trr_case_verdict;
DROP INDEX IF EXISTS ix_trr_run_verdict;
DROP TABLE IF EXISTS test_run_results;
-- DOWN END
