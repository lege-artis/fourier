-- =========================================================================
-- migration: 011_create_test_runs.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002, 009, 010
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.1 (BB-1/BB-2 blocks), §1.3 (test_runs delta),
--           §0.3 (canonical types), §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Single test execution. BB-1 + run metadata + executor FK.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS test_runs (
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
    -- TestRun-specific
    iteration_test_set_id BIGINT       NULL,
    environment_id        BIGINT       NULL,
    run_date              {{TS_TYPE}}  NOT NULL,
    run_finished_at       {{TS_TYPE}}  NULL,
    executor_id           BIGINT       NOT NULL,
    overall_verdict       VARCHAR(20)  NULL,
    build_under_test      VARCHAR(100) NULL,
    notes                 TEXT         NULL,
    CONSTRAINT ux_test_runs_project_code    UNIQUE (project_id, item_code),
    CONSTRAINT fk_test_runs_project__projects  FOREIGN KEY (project_id)       REFERENCES projects(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_submitter__users   FOREIGN KEY (submitter_id)     REFERENCES users(id)        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_manager__users     FOREIGN KEY (item_manager_id)  REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_statadj__users     FOREIGN KEY (stat_adj_by_id)   REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_parent__test_runs        FOREIGN KEY (parent_id)        REFERENCES test_runs(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_dupl__test_runs          FOREIGN KEY (duplicate_of_id)  REFERENCES test_runs(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_simlr__test_runs         FOREIGN KEY (similar_to_id)    REFERENCES test_runs(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_test_runs_sev_conf  CHECK (severity_confirmed  IS NULL OR severity_confirmed  IN ('A','B','C','X')),
    CONSTRAINT ck_test_runs_pri_conf  CHECK (priority_confirmed  IS NULL OR priority_confirmed  IN ('H','M','L','X')),
    CONSTRAINT ck_test_runs_att_conf  CHECK (attention_confirmed IS NULL OR attention_confirmed IN ('P','S','I','X')),
    CONSTRAINT ck_test_runs_sev_subm  CHECK (severity_by_subm    IS NULL OR severity_by_subm    IN ('A','B','C','X')),
    CONSTRAINT ck_test_runs_pri_subm  CHECK (priority_by_subm    IS NULL OR priority_by_subm    IN ('H','M','L','X')),
    CONSTRAINT ck_test_runs_att_subm  CHECK (attention_by_subm   IS NULL OR attention_by_subm   IN ('P','S','I','X')),
    CONSTRAINT ck_test_runs_status    CHECK (item_status IN (
        'new','in-analysis','confirmed','in-progress','implemented',
        'verifying','passed','failed','closed','cancelled','duplicate','deferred')),
    CONSTRAINT fk_test_runs_its__iteration_test_sets
        FOREIGN KEY (iteration_test_set_id) REFERENCES iteration_test_sets(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_env__test_environments
        FOREIGN KEY (environment_id)        REFERENCES test_environments(id)   ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_test_runs_executor__users
        FOREIGN KEY (executor_id)           REFERENCES users(id)               ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT ck_test_runs_overall CHECK (
        overall_verdict IS NULL OR overall_verdict IN
        ('pass','fail','partial','aborted','in-progress'))
){{TABLE_OPTIONS}};

CREATE INDEX ix_test_runs_status         ON test_runs(item_status);
CREATE INDEX ix_test_runs_project_status ON test_runs(project_id, item_status);
CREATE INDEX ix_test_runs_submitter      ON test_runs(submitter_id);
CREATE INDEX ix_test_runs_manager        ON test_runs(item_manager_id);
CREATE INDEX ix_test_runs_parent         ON test_runs(parent_id);
CREATE INDEX ix_test_runs_impulse        ON test_runs(code_to_impulse);
CREATE INDEX ix_test_runs_submit_date    ON test_runs(item_submit_date);
CREATE INDEX ix_test_runs_run_date    ON test_runs(run_date);
CREATE INDEX ix_test_runs_executor    ON test_runs(executor_id);
CREATE INDEX ix_test_runs_iteration   ON test_runs(iteration_test_set_id);
CREATE INDEX ix_test_runs_environment ON test_runs(environment_id);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_test_runs_status;
DROP INDEX IF EXISTS ix_test_runs_project_status;
DROP INDEX IF EXISTS ix_test_runs_submitter;
DROP INDEX IF EXISTS ix_test_runs_manager;
DROP INDEX IF EXISTS ix_test_runs_parent;
DROP INDEX IF EXISTS ix_test_runs_impulse;
DROP INDEX IF EXISTS ix_test_runs_submit_date;
DROP INDEX IF EXISTS ix_test_runs_run_date;
DROP INDEX IF EXISTS ix_test_runs_executor;
DROP INDEX IF EXISTS ix_test_runs_iteration;
DROP INDEX IF EXISTS ix_test_runs_environment;
DROP TABLE IF EXISTS test_runs;
-- DOWN END
