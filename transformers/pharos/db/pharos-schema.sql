--
-- File generated with SQLiteStudio v3.2.1 on Thu Oct 22 17:18:32 2026
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: cmpd_activity
CREATE TABLE cmpd_activity (
    id               INTEGER         PRIMARY KEY AUTOINCREMENT,
    target_id        INT             DEFAULT NULL,
    catype           VARCHAR (255)   NOT NULL,
    cmpd_id_in_src   VARCHAR (255)   NOT NULL,
    cmpd_name_in_src TEXT,
    smiles           TEXT,
    act_value        DECIMAL (10, 8) DEFAULT NULL,
    act_type         VARCHAR (255)   DEFAULT NULL,
    reference        TEXT,
    pubmed_ids       TEXT,
    cmpd_pubchem_cid INT             DEFAULT NULL,
    CONSTRAINT fk_chembl_activity__target FOREIGN KEY (
        target_id
    )
    REFERENCES target (id) ON DELETE CASCADE,
    CONSTRAINT fk_cmpd_activity__cmpd_activity_type FOREIGN KEY (
        catype
    )
    REFERENCES cmpd_activity_type (name) 
);


-- Table: cmpd_activity_type
CREATE TABLE cmpd_activity_type (
    name        VARCHAR (255) PRIMARY KEY
                              NOT NULL,
    description TEXT
);


-- Table: drug_activity
CREATE TABLE drug_activity (
    id               INTEGER         PRIMARY KEY AUTOINCREMENT,
    target_id        INTEGER         NOT NULL,
    drug             VARCHAR (255)   NOT NULL,
    act_value        DECIMAL (10, 8) DEFAULT NULL,
    act_type         VARCHAR (255)   DEFAULT NULL,
    action_type      VARCHAR (255)   DEFAULT NULL,
    has_moa          TINYINT (1)     NOT NULL,
    source           VARCHAR (255)   DEFAULT NULL,
    reference        TEXT,
    smiles           TEXT,
    cmpd_chemblid    VARCHAR (255)   DEFAULT NULL,
    nlm_drug_info    TEXT,
    cmpd_pubchem_cid INT             DEFAULT NULL,
    dcid             INT             NOT NULL,
    CONSTRAINT fk_drug_activity__target FOREIGN KEY (
        target_id
    )
    REFERENCES target (id) ON DELETE CASCADE
);


-- Table: protein
CREATE TABLE protein (
    id          INTEGER       PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR (255) NOT NULL,
    description TEXT          NOT NULL,
    uniprot     VARCHAR (20)  NOT NULL,
    up_version  INT           DEFAULT NULL,
    geneid      INT           DEFAULT NULL,
    sym         VARCHAR (20)  DEFAULT NULL,
    family      VARCHAR (255) DEFAULT NULL,
    chr         VARCHAR (255) DEFAULT NULL,
    seq         TEXT,
    dtoid       VARCHAR (13)  DEFAULT NULL,
    stringid    VARCHAR (15)  DEFAULT NULL,
    dtoclass    VARCHAR (255) DEFAULT NULL
);


-- Table: t2tc
CREATE TABLE t2tc (
    target_id       INTEGER NOT NULL,
    protein_id      INTEGER DEFAULT NULL,
    nucleic_acid_id INTEGER DEFAULT NULL,
    CONSTRAINT fk_t2tc__protein FOREIGN KEY (
        protein_id
    )
    REFERENCES protein (id),
    CONSTRAINT fk_t2tc__target FOREIGN KEY (
        target_id
    )
    REFERENCES target (id) ON DELETE CASCADE
);


-- Table: target
CREATE TABLE target (
    id          INTEGER       PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR (255) NOT NULL,
    ttype       VARCHAR (255) NOT NULL,
    description TEXT,
    comment     TEXT,
    tdl                       DEFAULT NULL,
    idg         TINYINT (1)   NOT NULL
                              DEFAULT '0',
    fam                       DEFAULT NULL,
    famext      VARCHAR (255) DEFAULT NULL
);


-- Index: cmpd_activity_idx1
CREATE INDEX cmpd_activity_idx1 ON cmpd_activity (
    catype
);


-- Index: cmpd_activity_idx2
CREATE INDEX cmpd_activity_idx2 ON cmpd_activity (
    target_id
);


-- Index: cmpd_activity_pubchem_idx
CREATE INDEX cmpd_activity_pubchem_idx ON cmpd_activity (
    cmpd_pubchem_cid
);


-- Index: drug_activity_chembl_idx
CREATE INDEX drug_activity_chembl_idx ON drug_activity (
    cmpd_chemblid
);


-- Index: drug_activity_idx1
CREATE INDEX drug_activity_idx1 ON drug_activity (
    target_id
);


-- Index: protein_idx1
CREATE UNIQUE INDEX protein_idx1 ON protein (
    uniprot
);


-- Index: protein_idx2
CREATE UNIQUE INDEX protein_idx2 ON protein (
    name
);


-- Index: t2tc_idx1
CREATE INDEX t2tc_idx1 ON t2tc (
    target_id
);


-- Index: t2tc_idx2
CREATE INDEX t2tc_idx2 ON t2tc (
    protein_id
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
