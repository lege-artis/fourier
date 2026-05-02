-- =========================================================================
-- migration: 024_create_item_correlations.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 023
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.5 (audit/supporting DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Polymorphic entity membership in a correlation group.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS item_correlations (
    id                    {{PK_BIGINT_AUTOINC}},
    correlation_group_id  BIGINT       NOT NULL,
    entity_table          VARCHAR(50)  NOT NULL,
    entity_id             BIGINT       NOT NULL,
    correlation_type      VARCHAR(20)  NOT NULL,
    created_at            {{TS_TYPE}}  NOT NULL,
    CONSTRAINT ux_ic_group_entity UNIQUE (correlation_group_id, entity_table, entity_id),
    CONSTRAINT fk_ic_group__item_correlation_groups
        FOREIGN KEY (correlation_group_id) REFERENCES item_correlation_groups(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT ck_ic_corr_type CHECK (correlation_type IN
        ('obligate','optional','competitive','denied'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_ic_entity ON item_correlations(entity_table, entity_id);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_ic_entity;
DROP TABLE IF EXISTS item_correlations;
-- DOWN END
