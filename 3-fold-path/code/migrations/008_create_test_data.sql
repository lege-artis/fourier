-- =========================================================================
-- migration: 008_create_test_data.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.1 (BB-1/BB-2 blocks), §1.3 (test_data delta),
--           §0.3 (canonical types), §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Test input data artefact. BB-1 + data fields.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_data (
    id                    {{PK_BIGINT_AUTOINC}},
    project_id            BIGINT       NOT NULL,
    code_to_impulse       VARCHAR(100) NULL,
    impulse_tree_lvl      SMALLINT     NULL,
    extern_tree_path      TEXT         NULL,
    parent_id             BIGINT       NULL,
    item_code             VARCHAR(100) NOT NULL,
    intern_tree_path      TEXT         NULL,
    item_tree_lvl         SMALLINT     NULL,
    intern_tree_info      TEXT         NULL,
    ext_int_tree_code     TEXT         NULL,
    item_name             VARCHAR(255) NOT NULL,
    item_type             VARCHAR(50)  NULL,
    item_descr            TEXT         NULL,
    ref                   VARCHAR(255) NULL,
    ref01                 VARCHAR(500) NULL,
    ref02                 VARCHAR(100) NULL,
    ref03                 VARCHAR(500) NULL,
    ref04                 VARCHAR(500) NULL,
    ref05                 VARCHAR(500) NULL,
    note                  TEXT         NULL,
    submitter_id          BIGINT       NOT NULL,
    item_submit_date      {{TS_TYPE}}  NOT NULL,
    item_manager_id       BIGINT       NULL,
    note_to_item_manager  TEXT         NULL,
    duplicate_of_id       BIGINT       NULL,
    similar_to_id         BIGINT       NULL,
    item_status           VARCHAR(30)  NOT NULL,
    date_of_adj_status    {{TS_TYPE}}  NULL,
    stat_adj_by_id        BIGINT       NULL,
    severity_confirmed    CHAR(1)      NULL,
    priority_confirmed    CHAR(1)      NULL,
    attention_confirmed   CHAR(1)      NULL,
    severity_by_subm      CHAR(1)      NULL,
    priority_by_subm      CHAR(1)      NULL,
    attention_by_subm     CHAR(1)      NULL,
    ext_attrs             {{JSON_TYPE}} NULL,
    correlation_descr     TEXT         NULL,
    created_at            {{TS_TYPE}}  NOT NULL,
    updated_at            {{TS_TYPE}}  NOT NULL,
    -- TestData-specific
    necessary_conds       TEXT         NULL,
    value_ideas           TEXT         NULL,
    value_ideas_att       VARCHAR(500) NULL,
    format_ideas          TEXT         NULL,
    format_ideas_att      VARCHAR(500) NULL,
    release_path          VARCHAR(500) NULL,
    data_payload          {{JSON_TYPE}} NULL,
    data_payload_ref      VARCHAR(500) NULL,
    CONSTRAINT ux_test_data_project_code    UNIQUE (project_id, item_code),
    CONSTRAINT fk_test_data_project__projects  FOREIGN KEY (project_id)       REFERENCES projects(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_data_submitter__users   FOREIGN KEY (submitter_id)     REFERENCES users(id)        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_data_manager__users     FOREIGN KEY (item_manager_id)  REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_data_statadj__users     FOREIGN KEY (stat_adj_by_id)   REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_data_parent__test_data        FOREIGN KEY (parent_id)        REFERENCES test_data(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_data_dupl__test_data          FOREIGN KEY (duplicate_of_id)  REFERENCES test_data(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_data_simlr__test_data         FOREIGN KEY (similar_to_id)    REFERENCES test_data(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_test_data_sev_conf  CHECK (severity_confirmed  IS NULL OR severity_confirmed  IN ('A','B','C','X')),
    CONSTRAINT ck_test_data_pri_conf  CHECK (priority_confirmed  IS NULL OR priority_confirmed  IN ('H','M','L','X')),
    CONSTRAINT ck_test_data_att_conf  CHECK (attention_confirmed IS NULL OR attention_confirmed IN ('P','S','I','X')),
    CONSTRAINT ck_test_data_sev_subm  CHECK (severity_by_subm    IS NULL OR severity_by_subm    IN ('A','B','C','X')),
    CONSTRAINT ck_test_data_pri_subm  CHECK (priority_by_subm    IS NULL OR priority_by_subm    IN ('H','M','L','X')),
    CONSTRAINT ck_test_data_att_subm  CHECK (attention_by_subm   IS NULL OR attention_by_subm   IN ('P','S','I','X')),
    CONSTRAINT ck_test_data_status    CHECK (item_status IN (
        'new','in-analysis','confirmed','in-progress','implemented',
        'verifying','passed','failed','closed','cancelled','duplicate','deferred'))
){{TABLE_OPTIONS}};

CREATE INDEX ix_test_data_status         ON test_data(item_status);
CREATE INDEX ix_test_data_project_status ON test_data(project_id, item_status);
CREATE INDEX ix_test_data_submitter      ON test_data(submitter_id);
CREATE INDEX ix_test_data_manager        ON test_data(item_manager_id);
CREATE INDEX ix_test_data_parent         ON test_data(parent_id);
CREATE INDEX ix_test_data_impulse        ON test_data(code_to_impulse);
CREATE INDEX ix_test_data_submit_date    ON test_data(item_submit_date);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_test_data_status;
DROP INDEX IF EXISTS ix_test_data_project_status;
DROP INDEX IF EXISTS ix_test_data_submitter;
DROP INDEX IF EXISTS ix_test_data_manager;
DROP INDEX IF EXISTS ix_test_data_parent;
DROP INDEX IF EXISTS ix_test_data_impulse;
DROP INDEX IF EXISTS ix_test_data_submit_date;
DROP TABLE IF EXISTS test_data;
-- DOWN END
