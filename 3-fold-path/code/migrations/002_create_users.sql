-- =========================================================================
-- migration: 002_create_users.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.2 (users DDL), §3.6 (role_in_process vocabulary),
--           §0.3 (canonical types), §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Identity table for PM/DM/TM/TA/TD/TI/TE/PAn roles.
--           role_in_process CHECK: VARCHAR(10) + constrained set (no ENUM).
--           is_active: {{BOOL_TYPE}} — TINYINT(1)/BOOLEAN/INTEGER per engine.
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id              {{PK_BIGINT_AUTOINC}},
    username        VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    display_name    VARCHAR(255) NOT NULL,
    role_in_process VARCHAR(10)  NULL,             -- NULL = role not yet assigned
    is_active       {{BOOL_TYPE}} NOT NULL DEFAULT {{BOOL_TRUE}},
    created_at      {{TS_TYPE}}  NOT NULL,
    updated_at      {{TS_TYPE}}  NOT NULL,
    CONSTRAINT ux_users_username UNIQUE (username),
    CONSTRAINT ux_users_email    UNIQUE (email),
    CONSTRAINT ck_users_role     CHECK (
        role_in_process IS NULL OR
        role_in_process IN ('PM','DM','TM','TA','TD','TI','TE','PAn')
    )
){{TABLE_OPTIONS}};

-- ─── DOWN ────────────────────────────────────────────────────────────────
-- DOWN BEGIN
DROP TABLE IF EXISTS users;
-- DOWN END
