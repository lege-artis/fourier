-- =========================================================================
-- migration: 010_create_iteration_test_sets.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002, 009
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.1 (BB-1/BB-2 blocks), §1.3 (iteration_test_sets delta),
--           §0.3 (canonical types), §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Sprint/iteration container. BB-1 + dates + environment FK.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS iteration_test_sets (
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
    -- IterationTestSet-specific
    iteration_label       VARCHAR(100) NULL,
    iteration_start_date  {{TS_TYPE}}  NULL,
    iteration_end_date    {{TS_TYPE}}  NULL,
    target_environment_id BIGINT       NULL,
    CONSTRAINT ux_iteration_test_sets_project_code    UNIQUE (project_id, item_code),
    CONSTRAINT fk_iteration_test_sets_project__projects  FOREIGN KEY (project_id)       REFERENCES projects(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_iteration_test_sets_submitter__users   FOREIGN KEY (submitter_id)     REFERENCES users(id)        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_iteration_test_sets_manager__users     FOREIGN KEY (item_manager_id)  REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_iteration_test_sets_statadj__users     FOREIGN KEY (stat_adj_by_id)   REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_iteration_test_sets_parent__iteration_test_sets        FOREIGN KEY (parent_id)        REFERENCES iteration_test_sets(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_iteration_test_sets_dupl__iteration_test_sets          FOREIGN KEY (duplicate_of_id)  REFERENCES iteration_test_sets(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_iteration_test_sets_simlr__iteration_test_sets         FOREIGN KEY (similar_to_id)    REFERENCES iteration_test_sets(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_iteration_test_sets_sev_conf  CHECK (severity_confirmed  IS NULL OR severity_confirmed  IN ('A','B','C','X')),
    CONSTRAINT ck_iteration_test_sets_pri_conf  CHECK (priority_confirmed  IS NULL OR priority_confirmed  IN ('H','M','L','X')),
    CONSTRAINT ck_iteration_test_sets_att_conf  CHECK (attention_confirmed IS NULL OR attention_confirmed IN ('P','S','I','X')),
    CONSTRAINT ck_iteration_test_sets_sev_subm  CHECK (severity_by_subm    IS NULL OR severity_by_subm    IN ('A','B','C','X')),
    CONSTRAINT ck_iteration_test_sets_pri_subm  CHECK (priority_by_subm    IS NULL OR priority_by_subm    IN ('H','M','L','X')),
    CONSTRAINT ck_iteration_test_sets_att_subm  CHECK (attention_by_subm   IS NULL OR attention_by_subm   IN ('P','S','I','X')),
    CONSTRAINT ck_iteration_test_sets_status    CHECK (item_status IN (
        'new','in-analysis','confirmed','in-progress','implemented',
        'verifying','passed','failed','closed','cancelled','duplicate','deferred')),
    CONSTRAINT fk_its_env__test_environments
        FOREIGN KEY (target_environment_id) REFERENCES test_environments(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_its_dates CHECK (
        iteration_end_date IS NULL OR iteration_start_date IS NULL
        OR iteration_end_date >= iteration_start_date)
){{TABLE_OPTIONS}};

CREATE INDEX ix_iteration_test_sets_status         ON iteration_test_sets(item_status);
CREATE INDEX ix_iteration_test_sets_project_status ON iteration_test_sets(project_id, item_status);
CREATE INDEX ix_iteration_test_sets_submitter      ON iteration_test_sets(submitter_id);
CREATE INDEX ix_iteration_test_sets_manager        ON iteration_test_sets(item_manager_id);
CREATE INDEX ix_iteration_test_sets_parent         ON iteration_test_sets(parent_id);
CREATE INDEX ix_iteration_test_sets_impulse        ON iteration_test_sets(code_to_impulse);
CREATE INDEX ix_iteration_test_sets_submit_date    ON iteration_test_sets(item_submit_date);
CREATE INDEX ix_its_dates ON iteration_test_sets(iteration_start_date, iteration_end_date);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_iteration_test_sets_status;
DROP INDEX IF EXISTS ix_iteration_test_sets_project_status;
DROP INDEX IF EXISTS ix_iteration_test_sets_submitter;
DROP INDEX IF EXISTS ix_iteration_test_sets_manager;
DROP INDEX IF EXISTS ix_iteration_test_sets_parent;
DROP INDEX IF EXISTS ix_iteration_test_sets_impulse;
DROP INDEX IF EXISTS ix_iteration_test_sets_submit_date;
DROP INDEX IF EXISTS ix_its_dates;
DROP TABLE IF EXISTS iteration_test_sets;
-- DOWN END
