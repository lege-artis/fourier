-- =========================================================================
-- migration: 020_create_item_status_history.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 002
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.5 (audit/supporting DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Append-only audit log of every item status change.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS item_status_history (
    id             {{PK_BIGINT_AUTOINC}},
    entity_table   VARCHAR(50)  NOT NULL,
    entity_id      BIGINT       NOT NULL,
    from_status    VARCHAR(30)  NULL,
    to_status      VARCHAR(30)  NOT NULL,
    changed_by_id  BIGINT       NOT NULL,
    changed_at     {{TS_TYPE}}   NOT NULL,
    note           TEXT         NULL,
    CONSTRAINT fk_ish_user__users
        FOREIGN KEY (changed_by_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_ish_entity_table CHECK (entity_table IN
        ('test_targets','test_cases','test_scripts','test_data','test_environments',
         'iteration_test_sets','test_runs','requests'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_ish_entity ON item_status_history(entity_table, entity_id, changed_at);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_ish_entity;
DROP TABLE IF EXISTS item_status_history;
-- DOWN END
