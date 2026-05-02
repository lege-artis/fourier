-- =========================================================================
-- migration: 013_create_test_case_phases.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002, 006
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.4 (junction/sub-entity DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Phase sub-entity for a test case (pre/exec/post). R-TC-3.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_case_phases (
    id              {{PK_BIGINT_AUTOINC}},
    test_case_id    BIGINT       NOT NULL,
    phase_type      VARCHAR(10)  NOT NULL,
    phase_descr     TEXT         NULL,
    sort_order      SMALLINT     NOT NULL DEFAULT 0,
    created_at      {{TS_TYPE}}  NOT NULL,
    updated_at      {{TS_TYPE}}  NOT NULL,
    CONSTRAINT ux_tcp_case_phase    UNIQUE (test_case_id, phase_type),
    CONSTRAINT fk_tcp_case__test_cases
        FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_tcp_phase_type    CHECK (phase_type IN ('pre','exec','post'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_tcp_case ON test_case_phases(test_case_id);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_tcp_case;
DROP TABLE IF EXISTS test_case_phases;
-- DOWN END
