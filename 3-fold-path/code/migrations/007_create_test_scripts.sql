-- =========================================================================
-- migration: 007_create_test_scripts.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.1 (BB-1/BB-2 blocks), §1.3 (test_scripts delta),
--           §0.3 (canonical types), §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Executable test procedure. BB-1 + script fields.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_scripts (
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
    -- TestScript-specific
    instructions          TEXT         NULL,
    observation_points    TEXT         NULL,
    control_points        TEXT         NULL,
    log_points            TEXT         NULL,
    expected_results      TEXT         NULL,
    expected_reports      TEXT         NULL,
    script_path           VARCHAR(500) NULL,
    CONSTRAINT ux_test_scripts_project_code    UNIQUE (project_id, item_code),
    CONSTRAINT fk_test_scripts_project__projects  FOREIGN KEY (project_id)       REFERENCES projects(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_scripts_submitter__users   FOREIGN KEY (submitter_id)     REFERENCES users(id)        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_scripts_manager__users     FOREIGN KEY (item_manager_id)  REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_scripts_statadj__users     FOREIGN KEY (stat_adj_by_id)   REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_scripts_parent__test_scripts        FOREIGN KEY (parent_id)        REFERENCES test_scripts(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_scripts_dupl__test_scripts          FOREIGN KEY (duplicate_of_id)  REFERENCES test_scripts(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_scripts_simlr__test_scripts         FOREIGN KEY (similar_to_id)    REFERENCES test_scripts(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_test_scripts_sev_conf  CHECK (severity_confirmed  IS NULL OR severity_confirmed  IN ('A','B','C','X')),
    CONSTRAINT ck_test_scripts_pri_conf  CHECK (priority_confirmed  IS NULL OR priority_confirmed  IN ('H','M','L','X')),
    CONSTRAINT ck_test_scripts_att_conf  CHECK (attention_confirmed IS NULL OR attention_confirmed IN ('P','S','I','X')),
    CONSTRAINT ck_test_scripts_sev_subm  CHECK (severity_by_subm    IS NULL OR severity_by_subm    IN ('A','B','C','X')),
    CONSTRAINT ck_test_scripts_pri_subm  CHECK (priority_by_subm    IS NULL OR priority_by_subm    IN ('H','M','L','X')),
    CONSTRAINT ck_test_scripts_att_subm  CHECK (attention_by_subm   IS NULL OR attention_by_subm   IN ('P','S','I','X')),
    CONSTRAINT ck_test_scripts_status    CHECK (item_status IN (
        'new','in-analysis','confirmed','in-progress','implemented',
        'verifying','passed','failed','closed','cancelled','duplicate','deferred'))
){{TABLE_OPTIONS}};

CREATE INDEX ix_test_scripts_status         ON test_scripts(item_status);
CREATE INDEX ix_test_scripts_project_status ON test_scripts(project_id, item_status);
CREATE INDEX ix_test_scripts_submitter      ON test_scripts(submitter_id);
CREATE INDEX ix_test_scripts_manager        ON test_scripts(item_manager_id);
CREATE INDEX ix_test_scripts_parent         ON test_scripts(parent_id);
CREATE INDEX ix_test_scripts_impulse        ON test_scripts(code_to_impulse);
CREATE INDEX ix_test_scripts_submit_date    ON test_scripts(item_submit_date);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_test_scripts_status;
DROP INDEX IF EXISTS ix_test_scripts_project_status;
DROP INDEX IF EXISTS ix_test_scripts_submitter;
DROP INDEX IF EXISTS ix_test_scripts_manager;
DROP INDEX IF EXISTS ix_test_scripts_parent;
DROP INDEX IF EXISTS ix_test_scripts_impulse;
DROP INDEX IF EXISTS ix_test_scripts_submit_date;
DROP TABLE IF EXISTS test_scripts;
-- DOWN END
