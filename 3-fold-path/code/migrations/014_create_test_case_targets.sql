-- =========================================================================
-- migration: 014_create_test_case_targets.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002, 005, 006
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.4 (junction/sub-entity DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  N:M secondary coverage map test_cases <-> test_targets.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_case_targets (
    test_case_id    BIGINT       NOT NULL,
    test_target_id  BIGINT       NOT NULL,
    coverage_kind   VARCHAR(20)  NOT NULL DEFAULT 'secondary',
    created_at      {{TS_TYPE}}  NOT NULL,
    CONSTRAINT pk_test_case_targets   PRIMARY KEY (test_case_id, test_target_id),
    CONSTRAINT fk_tct_case__test_cases
        FOREIGN KEY (test_case_id)   REFERENCES test_cases(id)   ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_tct_target__test_targets
        FOREIGN KEY (test_target_id) REFERENCES test_targets(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_tct_coverage CHECK (coverage_kind IN ('primary','secondary','regression'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_tct_target ON test_case_targets(test_target_id);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_tct_target;
DROP TABLE IF EXISTS test_case_targets;
-- DOWN END
