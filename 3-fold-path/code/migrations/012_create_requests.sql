-- =========================================================================
-- migration: 012_create_requests.sql
-- date:      2026-04-27
-- author:    pete
-- depends:   000, 001, 002
-- engines:   mysql8, postgres14, sqlite3
-- tags:      [uS-CAND][TRIG-REQ][CRIT-AUDIT]
-- =========================================================================
-- Citation: ARCH-SPEC §1.1 (BB-1/BB-2 blocks), §1.3 (requests delta),
--           §0.3 (canonical types), §0.4 (constraints), §8.3 (tokens)
-- Purpose:  Bug or change request. BB-1 + item_type discriminator + repro fields.
-- =========================================================================

-- UP

CREATE TABLE IF NOT EXISTS requests (
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
    -- Request-specific (CAST §2.7)
    repeatability         VARCHAR(20)  NULL,
    visibility            TEXT         NULL,
    used_environment      VARCHAR(100) NULL,
    used_hw_system        VARCHAR(100) NULL,
    used_hw_accessories   VARCHAR(200) NULL,
    used_os_pc            VARCHAR(100) NULL,
    regional_lang_set     VARCHAR(100) NULL,
    used_other_sw         TEXT         NULL,
    used_prod_name        VARCHAR(100) NULL,
    used_prod_build       VARCHAR(50)  NULL,
    prod_localization     VARCHAR(20)  NULL,
    used_test_data        TEXT         NULL,
    bug_source            VARCHAR(255) NULL,
    solving_ideas         TEXT         NULL,
    way_of_solving        TEXT         NULL,
    fixed_in_build        VARCHAR(100) NULL,
    CONSTRAINT ux_requests_project_code    UNIQUE (project_id, item_code),
    CONSTRAINT fk_requests_project__projects  FOREIGN KEY (project_id)       REFERENCES projects(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_requests_submitter__users   FOREIGN KEY (submitter_id)     REFERENCES users(id)        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_requests_manager__users     FOREIGN KEY (item_manager_id)  REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_requests_statadj__users     FOREIGN KEY (stat_adj_by_id)   REFERENCES users(id)        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_requests_parent__requests        FOREIGN KEY (parent_id)        REFERENCES requests(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_requests_dupl__requests          FOREIGN KEY (duplicate_of_id)  REFERENCES requests(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_requests_simlr__requests         FOREIGN KEY (similar_to_id)    REFERENCES requests(id)          ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT ck_requests_sev_conf  CHECK (severity_confirmed  IS NULL OR severity_confirmed  IN ('A','B','C','X')),
    CONSTRAINT ck_requests_pri_conf  CHECK (priority_confirmed  IS NULL OR priority_confirmed  IN ('H','M','L','X')),
    CONSTRAINT ck_requests_att_conf  CHECK (attention_confirmed IS NULL OR attention_confirmed IN ('P','S','I','X')),
    CONSTRAINT ck_requests_sev_subm  CHECK (severity_by_subm    IS NULL OR severity_by_subm    IN ('A','B','C','X')),
    CONSTRAINT ck_requests_pri_subm  CHECK (priority_by_subm    IS NULL OR priority_by_subm    IN ('H','M','L','X')),
    CONSTRAINT ck_requests_att_subm  CHECK (attention_by_subm   IS NULL OR attention_by_subm   IN ('P','S','I','X')),
    CONSTRAINT ck_requests_status    CHECK (item_status IN (
        'new','in-analysis','confirmed','in-progress','implemented',
        'verifying','passed','failed','closed','cancelled','duplicate','deferred')),
    CONSTRAINT ck_requests_item_type CHECK (item_type IN ('bug','change_request')),
    CONSTRAINT ck_requests_repeatability CHECK (
        repeatability IS NULL OR repeatability IN ('Always','Sometimes','Rarely','Once'))
){{TABLE_OPTIONS}};

CREATE INDEX ix_requests_status         ON requests(item_status);
CREATE INDEX ix_requests_project_status ON requests(project_id, item_status);
CREATE INDEX ix_requests_submitter      ON requests(submitter_id);
CREATE INDEX ix_requests_manager        ON requests(item_manager_id);
CREATE INDEX ix_requests_parent         ON requests(parent_id);
CREATE INDEX ix_requests_impulse        ON requests(code_to_impulse);
CREATE INDEX ix_requests_submit_date    ON requests(item_submit_date);
CREATE INDEX ix_requests_type           ON requests(item_type);
CREATE INDEX ix_requests_used_prod_bld  ON requests(used_prod_name, used_prod_build);
CREATE INDEX ix_requests_fixed_in_build ON requests(fixed_in_build);

-- DOWN BEGIN
DROP INDEX IF EXISTS ix_requests_status;
DROP INDEX IF EXISTS ix_requests_project_status;
DROP INDEX IF EXISTS ix_requests_submitter;
DROP INDEX IF EXISTS ix_requests_manager;
DROP INDEX IF EXISTS ix_requests_parent;
DROP INDEX IF EXISTS ix_requests_impulse;
DROP INDEX IF EXISTS ix_requests_submit_date;
DROP INDEX IF EXISTS ix_requests_type;
DROP INDEX IF EXISTS ix_requests_used_prod_bld;
DROP INDEX IF EXISTS ix_requests_fixed_in_build;
DROP TABLE IF EXISTS requests;
-- DOWN END
