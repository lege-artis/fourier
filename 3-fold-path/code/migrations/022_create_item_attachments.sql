-- =========================================================================
-- migration: 022_create_item_attachments.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 002
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.5 (audit/supporting DDL), §0.3 (canonical types),
--           §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Normalised attachment store (replaces ref01-ref05). Append-only rows.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS item_attachments (
    id              {{PK_BIGINT_AUTOINC}},
    entity_table    VARCHAR(50)   NOT NULL,
    entity_id       BIGINT        NOT NULL,
    file_name       VARCHAR(255)  NOT NULL,
    storage_uri     VARCHAR(1000) NOT NULL,
    mime_type       VARCHAR(100)  NULL,
    size_bytes      BIGINT        NULL,
    sha256_hex      CHAR(64)      NULL,
    uploaded_by_id  BIGINT        NOT NULL,
    uploaded_at     {{TS_TYPE}}   NOT NULL,
    description     TEXT          NULL,
    CONSTRAINT fk_ia_user__users
        FOREIGN KEY (uploaded_by_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE
){{TABLE_OPTIONS}};
CREATE INDEX ix_ia_entity ON item_attachments(entity_table, entity_id);
CREATE INDEX ix_ia_sha    ON item_attachments(sha256_hex);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_ia_sha;
DROP INDEX IF EXISTS ix_ia_entity;
DROP TABLE IF EXISTS item_attachments;
-- DOWN END
