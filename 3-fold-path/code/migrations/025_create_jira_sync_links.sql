-- =========================================================================
-- migration: 025_create_jira_sync_links.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.5 (audit/supporting DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Bidirectional key map to JIRA/Zephyr/Postman. D-03/D-04 adapter contract.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS jira_sync_links (
    id                   {{PK_BIGINT_AUTOINC}},
    entity_table         VARCHAR(50)  NOT NULL,
    entity_id            BIGINT       NOT NULL,
    external_system      VARCHAR(20)  NOT NULL,
    external_key         VARCHAR(100) NOT NULL,
    external_url         VARCHAR(500) NULL,
    last_sync_at         {{TS_TYPE}}  NULL,
    last_sync_direction  VARCHAR(10)  NULL,
    sync_state           VARCHAR(20)  NOT NULL DEFAULT 'ok',
    sync_error           TEXT         NULL,
    CONSTRAINT ux_jsl_external UNIQUE (external_system, external_key),
    CONSTRAINT ux_jsl_entity   UNIQUE (entity_table, entity_id, external_system),
    CONSTRAINT ck_jsl_system    CHECK (external_system IN ('jira','zephyr','postman')),
    CONSTRAINT ck_jsl_direction CHECK (last_sync_direction IS NULL OR
        last_sync_direction IN ('push','pull','reconcile')),
    CONSTRAINT ck_jsl_state     CHECK (sync_state IN ('ok','drift','error','disabled'))
){{TABLE_OPTIONS}};
CREATE INDEX ix_jsl_entity ON jira_sync_links(entity_table, entity_id);
CREATE INDEX ix_jsl_state  ON jira_sync_links(sync_state);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_jsl_state;
DROP INDEX IF EXISTS ix_jsl_entity;
DROP TABLE IF EXISTS jira_sync_links;
-- DOWN END
