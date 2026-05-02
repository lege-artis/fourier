-- =========================================================================
-- migration: 015_create_test_case_phase_resources.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 013
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.4 (junction/sub-entity DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Polymorphic resource attachment per phase. R-TC-4.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_case_phase_resources (
    id                 {{PK_BIGINT_AUTOINC}},
    test_case_phase_id BIGINT       NOT NULL,
    resource_type      VARCHAR(20)  NOT NULL,
    resource_id        BIGINT       NOT NULL,
    sort_order         SMALLINT     NOT NULL DEFAULT 0,
    usage_notes        TEXT         NULL,
    created_at         {{TS_TYPE}}  NOT NULL,
    CONSTRAINT ux_tcpr_phase_resource UNIQUE (test_case_phase_id, resource_type, resource_id),
    CONSTRAINT fk_tcpr_phase__test_case_phases
        FOREIGN KEY (test_case_phase_id) REFERENCES test_case_phases(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_tcpr_resource_type CHECK (resource_type IN
        ('test_script','test_data','test_environment',
         'test_procedure','test_component','test_user'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_tcpr_resource ON test_case_phase_resources(resource_type, resource_id);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_tcpr_resource;
DROP TABLE IF EXISTS test_case_phase_resources;
-- DOWN END
