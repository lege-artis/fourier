-- =========================================================================
-- migration: 001_create_projects.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.2 (projects DDL), §0.3 (canonical types),
--           §0.4 (cross-engine constraints), §8.1 (file naming), §8.3 (tokens)
-- Purpose:  Tenant boundary table. One row per isolated test project.
--           status CHECK: 'active' | 'archived' | 'deleted' (no ENUM — §0.4).
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS projects (
    id              {{PK_BIGINT_AUTOINC}},
    project_code    VARCHAR(20)  NOT NULL,          -- short key, e.g. "MIMT"
    name            VARCHAR(255) NOT NULL,
    description     TEXT         NULL,
    status          VARCHAR(20)  NOT NULL DEFAULT 'active',
    created_at      {{TS_TYPE}}  NOT NULL,
    updated_at      {{TS_TYPE}}  NOT NULL,
    CONSTRAINT ux_projects_code   UNIQUE (project_code),
    CONSTRAINT ck_projects_status CHECK (status IN ('active','archived','deleted'))
){{TABLE_OPTIONS}};

-- ─── DOWN ────────────────────────────────────────────────────────────────
-- DOWN BEGIN
DROP TABLE IF EXISTS projects;
-- DOWN END
