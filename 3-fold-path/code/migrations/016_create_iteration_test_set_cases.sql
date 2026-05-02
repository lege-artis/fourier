-- =========================================================================
-- migration: 016_create_iteration_test_set_cases.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 006, 010
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.4 (junction/sub-entity DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  M:N test set <-> test case execution plan.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS iteration_test_set_cases (
    iteration_test_set_id BIGINT       NOT NULL,
    test_case_id          BIGINT       NOT NULL,
    execution_order       SMALLINT     NOT NULL DEFAULT 0,
    inclusion_status      VARCHAR(20)  NOT NULL DEFAULT 'planned',
    inclusion_notes       TEXT         NULL,
    created_at            {{TS_TYPE}}  NOT NULL,
    CONSTRAINT pk_itsc PRIMARY KEY (iteration_test_set_id, test_case_id),
    CONSTRAINT fk_itsc_set__iteration_test_sets
        FOREIGN KEY (iteration_test_set_id) REFERENCES iteration_test_sets(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_itsc_case__test_cases
        FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_itsc_status CHECK (inclusion_status IN
        ('planned','executed','skipped','blocked','removed'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_itsc_case ON iteration_test_set_cases(test_case_id);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_itsc_case;
DROP TABLE IF EXISTS iteration_test_set_cases;
-- DOWN END
