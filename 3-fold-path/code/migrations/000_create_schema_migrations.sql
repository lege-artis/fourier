-- =========================================================================
-- migration: 000_create_schema_migrations.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   (none — always first)
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §8.4 (tracking table design) + §8.3 (token table)
--           + §0.3 (canonical type vocabulary) + §0.4 (cross-engine constraints)
-- Purpose:  Bootstrap the migration tracking table.
--           This file is applied before all other migrations and is
--           idempotent: CREATE TABLE IF NOT EXISTS guards re-entrant apply.
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS schema_migrations (
    version       VARCHAR(20)  NOT NULL,           -- e.g. "000", "005"  (ARCH-SPEC §8.4)
    description   VARCHAR(255) NOT NULL,
    applied_at    {{TS_TYPE}}  NOT NULL,            -- UTC  (ARCH-SPEC §8.4)
    applied_by    VARCHAR(100) NULL,               -- runner identity string
    sha256_hex    CHAR(64)     NOT NULL,           -- SHA-256 of the UP section (ARCH-SPEC §8.4)
    duration_ms   INT          NULL,
    CONSTRAINT pk_schema_migrations PRIMARY KEY (version)
){{TABLE_OPTIONS}};

-- ─── DOWN ────────────────────────────────────────────────────────────────
-- DOWN BEGIN
DROP TABLE IF EXISTS schema_migrations;
-- DOWN END
