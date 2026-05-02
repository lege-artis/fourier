-- =========================================================================
-- migration: 018_create_request_test_cases.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 006, 012
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.4 (junction/sub-entity DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Bug/CR <-> test case linkage (triggered_by/covers/regresses).
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS request_test_cases (
    request_id    BIGINT      NOT NULL,
    test_case_id  BIGINT      NOT NULL,
    link_kind     VARCHAR(20) NOT NULL DEFAULT 'triggered_by',
    created_at    {{TS_TYPE}} NOT NULL,
    CONSTRAINT pk_rtc PRIMARY KEY (request_id, test_case_id),
    CONSTRAINT fk_rtc_req__requests
        FOREIGN KEY (request_id)   REFERENCES requests(id)   ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rtc_case__test_cases
        FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_rtc_link_kind CHECK (link_kind IN
        ('triggered_by','covers','regresses','related'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_rtc_case ON request_test_cases(test_case_id);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_rtc_case;
DROP TABLE IF EXISTS request_test_cases;
-- DOWN END
