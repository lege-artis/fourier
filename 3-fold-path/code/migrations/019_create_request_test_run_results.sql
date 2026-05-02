-- =========================================================================
-- migration: 019_create_request_test_run_results.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 012, 017
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.4 (junction/sub-entity DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Pinpoint the exact result row that surfaced a request.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS request_test_run_results (
    request_id           BIGINT NOT NULL,
    test_run_result_id   BIGINT NOT NULL,
    created_at           {{TS_TYPE}} NOT NULL,
    CONSTRAINT pk_rtrr PRIMARY KEY (request_id, test_run_result_id),
    CONSTRAINT fk_rtrr_req__requests
        FOREIGN KEY (request_id)         REFERENCES requests(id)         ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rtrr_result__test_run_results
        FOREIGN KEY (test_run_result_id) REFERENCES test_run_results(id) ON DELETE CASCADE ON UPDATE CASCADE
){{TABLE_OPTIONS}};

-- DOWN BEGIN
DROP TABLE IF EXISTS request_test_run_results;
-- DOWN END
