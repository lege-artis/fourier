-- =========================================================================
-- migration: 021_create_item_status_transitions.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.5 (audit/supporting DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  State-machine transition registry (from/to/role). Seed in 101.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS item_status_transitions (
    id             {{PK_BIGINT_AUTOINC}},
    entity_table   VARCHAR(50)  NOT NULL,
    from_status    VARCHAR(30)  NOT NULL,
    to_status      VARCHAR(30)  NOT NULL,
    requires_role  VARCHAR(10)  NULL,
    description    TEXT         NULL,
    is_active      {{BOOL_TYPE}}  NOT NULL DEFAULT {{BOOL_TRUE}},
    CONSTRAINT ux_ist_triple UNIQUE (entity_table, from_status, to_status)
){{TABLE_OPTIONS}};
CREATE INDEX ix_ist_lookup ON item_status_transitions(entity_table, from_status, is_active);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_ist_lookup;
DROP TABLE IF EXISTS item_status_transitions;
-- DOWN END
