-- =========================================================================
-- migration: 023_create_item_correlation_groups.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.5 (audit/supporting DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  CAST correlation group container per project.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS item_correlation_groups (
    id           {{PK_BIGINT_AUTOINC}},
    project_id   BIGINT        NOT NULL,
    group_code   VARCHAR(100)  NOT NULL,
    description  TEXT          NULL,
    created_at   {{TS_TYPE}}   NOT NULL,
    CONSTRAINT ux_icg_project_code UNIQUE (project_id, group_code),
    CONSTRAINT fk_icg_project__projects
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE
){{TABLE_OPTIONS}};

-- DOWN BEGIN
DROP TABLE IF EXISTS item_correlation_groups;
-- DOWN END
