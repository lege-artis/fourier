-- =========================================================================
-- migration: 005_create_test_targets.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.1 (BB-1/BB-2 blocks), §1.3 (test_targets delta),
--           §0.3 (canonical types), §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Subject under test. BB-1 + tst_strat_ideas (CAST §2.4).
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_targets (
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
    -- TestTarget-specific (CAST §2.4)
    tst_strat_ideas       TEXT         NULL,
    CONSTRAINT ux_test_targets_project_code    UNIQUE (project_id, item_code),
    CONSTRAINT fk_test_targets_project__projects  FOREIGN KEY (project_id)       REFERENCES projects(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_targets_submitter__users   FOREIGN KEY (submitter_id)     REFERENCES users(id)        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_targets_manager__users     FOREIGN KEY (item_manager_id)  REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_targets_statadj__users     FOREIGN KEY (stat_adj_by_id)   REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_targets_parent__test_targets        FOREIGN KEY (parent_id)        REFERENCES test_targets(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_targets_dupl__test_targets          FOREIGN KEY (duplicate_of_id)  REFERENCES test_targets(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_targets_simlr__test_targets         FOREIGN KEY (similar_to_id)    REFERENCES test_targets(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_test_targets_sev_conf  CHECK (severity_confirmed  IS NULL OR severity_confirmed  IN ('A','B','C','X')),
    CONSTRAINT ck_test_targets_pri_conf  CHECK (priority_confirmed  IS NULL OR priority_confirmed  IN ('H','M','L','X')),
    CONSTRAINT ck_test_targets_att_conf  CHECK (attention_confirmed IS NULL OR attention_confirmed IN ('P','S','I','X')),
    CONSTRAINT ck_test_targets_sev_subm  CHECK (severity_by_subm    IS NULL OR severity_by_subm    IN ('A','B','C','X')),
    CONSTRAINT ck_test_targets_pri_subm  CHECK (priority_by_subm    IS NULL OR priority_by_subm    IN ('H','M','L','X')),
    CONSTRAINT ck_test_targets_att_subm  CHECK (attention_by_subm   IS NULL OR attention_by_subm   IN ('P','S','I','X')),
    CONSTRAINT ck_test_targets_status    CHECK (item_status IN (
        'new','in-analysis','confirmed','in-progress','implemented',
        'verifying','passed','failed','closed','cancelled','duplicate','deferred'))
){{TABLE_OPTIONS}};

CREATE INDEX ix_test_targets_status         ON test_targets(item_status);
CREATE INDEX ix_test_targets_project_status ON test_targets(project_id, item_status);
CREATE INDEX ix_test_targets_submitter      ON test_targets(submitter_id);
CREATE INDEX ix_test_targets_manager        ON test_targets(item_manager_id);
CREATE INDEX ix_test_targets_parent         ON test_targets(parent_id);
CREATE INDEX ix_test_targets_impulse        ON test_targets(code_to_impulse);
CREATE INDEX ix_test_targets_submit_date    ON test_targets(item_submit_date);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_test_targets_status;
DROP INDEX IF EXISTS ix_test_targets_project_status;
DROP INDEX IF EXISTS ix_test_targets_submitter;
DROP INDEX IF EXISTS ix_test_targets_manager;
DROP INDEX IF EXISTS ix_test_targets_parent;
DROP INDEX IF EXISTS ix_test_targets_impulse;
DROP INDEX IF EXISTS ix_test_targets_submit_date;
DROP TABLE IF EXISTS test_targets;
-- DOWN END
