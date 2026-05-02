-- =========================================================================
-- migration: 004_create_value_list_items.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 003
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [μS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.2 (value_list_items DDL), §0.3 (canonical types),
--           §0.4 (constraints — no ENUM; FK ON DELETE CASCADE portable),
--           §8.3 (tokens)
-- Purpose:  Rows of each domain registry.
--           code = canonical value used in item-table CHECK constraints.
--           is_active: soft-delete without hard-delete (append-only pattern).
--           sort_order: SMALLINT — portable across all three engines.
-- =========================================================================

-- ─── UP ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS value_list_items (
    id              {{PK_BIGINT_AUTOINC}},
    value_list_id   BIGINT       NOT NULL,
    code            VARCHAR(50)  NOT NULL,         -- canonical value
    display_label   VARCHAR(255) NOT NULL,
    sort_order      SMALLINT     NOT NULL DEFAULT 0,
    is_active       {{BOOL_TYPE}} NOT NULL DEFAULT {{BOOL_TRUE}},
    description     TEXT         NULL,
    CONSTRAINT ux_value_list_items      UNIQUE (value_list_id, code),
    CONSTRAINT fk_vli_list__value_lists FOREIGN KEY (value_list_id)
        REFERENCES value_lists(id) ON DELETE CASCADE ON UPDATE CASCADE
){{TABLE_OPTIONS}};

CREATE INDEX ix_vli_active ON value_list_items(value_list_id, is_active);

-- ─── DOWN ────────────────────────────────────────────────────────────────
-- DOWN BEGIN
DROP INDEX IF EXISTS ix_vli_active;
DROP TABLE IF EXISTS value_list_items;
-- DOWN END
