-- =========================================================================
-- migration: 003_create_value_lists.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.2 (value_lists DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Domain registry for extensible enum picklists.
--           Each row = one domain (e.g. 'item_status', 'severity').
--           Populated by seed 100_seed_reference_data.sql.
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS value_lists (
    id          {{PK_BIGINT_AUTOINC}},
    domain      VARCHAR(50)  NOT NULL,             -- 'item_status' | 'severity' | ...
    description TEXT         NULL,
    created_at  {{TS_TYPE}}  NOT NULL,
    CONSTRAINT ux_value_lists_domain UNIQUE (domain)
){{TABLE_OPTIONS}};

-- ─── DOWN ────────────────────────────────────────────────────────────────
-- DOWN BEGIN
DROP TABLE IF EXISTS value_lists;
-- DOWN END
