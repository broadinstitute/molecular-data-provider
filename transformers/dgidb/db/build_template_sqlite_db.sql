--
-- File generated with SQLiteStudio v3.2.1 on Mon Aug 31 20:45:23 2020
-- 
-- This is a template SQL script for reconstituting the DGIdb database,
-- which means it will only create the tables, views and indexes but will
-- not INSERT the megabytes of data into the 44 tables. The data should be
-- imported separately. (Some INSERT statements were included for information
-- purpose only)
-- 
-- Text encoding used: macintosh
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: ar_internal_metadata
DROP TABLE IF EXISTS ar_internal_metadata;

CREATE TABLE ar_internal_metadata (
    [key]      CHARACTER                     NOT NULL,
    value      CHARACTER,
    created_at [TIMESTAMP WITHOUT TIME ZONE] NOT NULL,
    updated_at [TIMESTAMP WITHOUT TIME ZONE] NOT NULL,
    CONSTRAINT ar_internal_metadata_pkey PRIMARY KEY (
        [key]
    )
);


-- Table: chembl_molecule_synonyms
DROP TABLE IF EXISTS chembl_molecule_synonyms;

CREATE TABLE chembl_molecule_synonyms (
    id                 INTEGER                   PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    molregno           INTEGER,
    synonym            [CHARACTER VARYING] (200),
    molsyn_id          INTEGER,
    chembl_molecule_id INTEGER,
    syn_type           [CHARACTER VARYING] (50) 
);

--INSERT INTO chembl_molecule_synonyms (id, molregno, synonym, molsyn_id, chembl_molecule_id, syn_type) VALUES (615101, 97, 'CP-12299', 1, 3593651, 'RESEARCH_CODE');


-- Table: chembl_molecules
DROP TABLE IF EXISTS chembl_molecules;

CREATE TABLE chembl_molecules (
    id                   INTEGER                  PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    molregno             INTEGER,
    pref_name            CHARACTER,
    chembl_id            CHARACTER,
    max_phase            INTEGER,
    therapeutic_flag     BOOLEAN,
    dosed_ingredient     BOOLEAN,
    structure_type       CHARACTER,
    chebi_par_id         INTEGER,
    molecule_type        CHARACTER,
    first_approval       INTEGER,
    oral                 BOOLEAN,
    parenteral           BOOLEAN,
    topical              BOOLEAN,
    black_box_warning    BOOLEAN,
    natural_product      BOOLEAN,
    first_in_class       BOOLEAN,
    chirality            INTEGER,
    prodrug              BOOLEAN,
    inorganic_flag       BOOLEAN,
    usan_year            INTEGER,
    availability_type    INTEGER,
    usan_stem            [CHARACTER VARYING] (50),
    polymer_flag         BOOLEAN,
    usan_substem         [CHARACTER VARYING] (50),
    usan_stem_definition TEXT,
    indication_class     TEXT,
    withdrawn_flag       BOOLEAN,
    withdrawn_year       INTEGER,
    withdrawn_country    TEXT,
    withdrawn_reason     TEXT
);
--INSERT INTO chembl_molecules (id, molregno, pref_name, chembl_id, max_phase, therapeutic_flag, dosed_ingredient, structure_type, chebi_par_id, molecule_type, first_approval, oral, parenteral, topical, black_box_warning, natural_product, first_in_class, chirality, prodrug, inorganic_flag, usan_year, availability_type, usan_stem, polymer_flag, usan_substem, usan_stem_definition, indication_class, withdrawn_flag, withdrawn_year, withdrawn_country, withdrawn_reason) VALUES (3593576, 1, '', 'CHEMBL6329', 0, 'f', 'f', 'MOL', '', 'Small molecule', '', 'f', 'f', 'f', 'f', '', '', -1, '', '', '', -1, '', 'f', '', '', '', 'f', '', '', '');

-- Table: delayed_jobs
DROP TABLE IF EXISTS delayed_jobs;

CREATE TABLE delayed_jobs (
    id         BIGINT,
    priority   INTEGER                       NOT NULL
                                             DEFAULT 0,
    attempts   INTEGER                       NOT NULL
                                             DEFAULT 0,
    handler    TEXT                          NOT NULL,
    last_error TEXT,
    run_at     [TIMESTAMP WITHOUT TIME ZONE],
    locked_at  [TIMESTAMP WITHOUT TIME ZONE],
    failed_at  [TIMESTAMP WITHOUT TIME ZONE],
    locked_by  [CHARACTER VARYING],
    queue      [CHARACTER VARYING],
    created_at [TIMESTAMP WITHOUT TIME ZONE],
    updated_at [TIMESTAMP WITHOUT TIME ZONE],
    CONSTRAINT delayed_jobs_pkey PRIMARY KEY (
        id
    )
);


-- Table: drug_alias_blacklists
DROP TABLE IF EXISTS drug_alias_blacklists;

CREATE TABLE drug_alias_blacklists (
    id    BIGINT,
    alias TEXT,
    CONSTRAINT drug_alias_blacklists_pkey PRIMARY KEY (
        id
    )
);

--INSERT INTO drug_alias_blacklists (id, alias) VALUES (1, '');

-- Table: drug_aliases
DROP TABLE IF EXISTS drug_aliases;

CREATE TABLE drug_aliases (
    id      TEXT PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    drug_id TEXT,
    alias   TEXT COLLATE NOCASE
);

--INSERT INTO drug_aliases (id, drug_id, alias) VALUES ('f897aece-74c0-498e-9c73-1a119060f41e', 'aacfbc80-4015-4964-98fa-9c5f413f15ae', 'Pargyline HCl');

-- Table: drug_aliases_sources
DROP TABLE IF EXISTS drug_aliases_sources;

CREATE TABLE drug_aliases_sources (
    drug_alias_id TEXT,
    source_id     TEXT
);

--INSERT INTO drug_aliases_sources (drug_alias_id, source_id) VALUES ('51f35c0a-2261-4375-9a9d-6a5868859af6', '774d9000-b9b3-485f-bb53-07b4d5cccc40');

-- Table: drug_attributes
DROP TABLE IF EXISTS drug_attributes;

CREATE TABLE drug_attributes (
    id      TEXT,
    drug_id TEXT,
    name    TEXT,
    value   TEXT
);

--INSERT INTO drug_attributes (id, drug_id, name, value) VALUES ('9e7f29c5-3e32-4928-b4bf-88aed5989da3', 'c27623e9-072e-4e8b-9c20-f2194d541dd7', 'FDA Approval', 'not approved');

-- Table: drug_attributes_sources
DROP TABLE IF EXISTS drug_attributes_sources;

CREATE TABLE drug_attributes_sources (
    drug_attribute_id TEXT NOT NULL,
    source_id         TEXT NOT NULL,
    CONSTRAINT drug_attributes_sources_pkey PRIMARY KEY (
        drug_attribute_id,
        source_id
    )
);

--INSERT INTO drug_attributes_sources (drug_attribute_id, source_id) VALUES ('9e7f29c5-3e32-4928-b4bf-88aed5989da3', '55a7a373-bba6-4069-a104-ac6e030ac433');

-- Table: drug_claim_aliases
DROP TABLE IF EXISTS drug_claim_aliases;

CREATE TABLE drug_claim_aliases (
    id            TEXT,
    drug_claim_id TEXT,
    alias         TEXT,
    nomenclature  TEXT
);

--INSERT INTO drug_claim_aliases (id, drug_claim_id, alias, nomenclature) VALUES ('552e50ee-8b84-45c2-9b10-472fcef7a695', 'd4abe6cf-38fb-4d5a-90c6-b6bc1e1586f6', 'TRANS-EPHEDRINE', 'Drug Synonym');

-- Table: drug_claim_attributes
DROP TABLE IF EXISTS drug_claim_attributes;

CREATE TABLE drug_claim_attributes (
    id            TEXT PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    drug_claim_id TEXT,
    name          TEXT,
    value         TEXT
);

--INSERT INTO drug_claim_attributes (id, drug_claim_id, name, value) VALUES ('6152067f-30fa-4637-8cd0-704fee4fe68d', '7e7b0af6-6b92-4339-8382-351a3c02a2a1', 'Drug Type', 'biotech');

-- Table: drug_claim_types
DROP TABLE IF EXISTS drug_claim_types;

CREATE TABLE drug_claim_types (
    id   [CHARACTER VARYING] (255),
    type [CHARACTER VARYING] (255) 
);

--INSERT INTO drug_claim_types (id, type) VALUES ('0e212a04-adaa-4fca-af4d-4607934426bc', 'antineoplastic');

-- Table: drug_claim_types_drug_claims
DROP TABLE IF EXISTS drug_claim_types_drug_claims;

CREATE TABLE drug_claim_types_drug_claims (
    drug_claim_id      [CHARACTER VARYING] (255),
    drug_claim_type_id [CHARACTER VARYING] (255) 
);

--INSERT INTO drug_claim_types_drug_claims (drug_claim_id, drug_claim_type_id) VALUES ('fe769c0d-61a5-4379-ab58-2ed8a6544092', '0e212a04-adaa-4fca-af4d-4607934426bc');

-- Table: drug_claims
DROP TABLE IF EXISTS drug_claims;

CREATE TABLE drug_claims (
    id           TEXT,
    name         TEXT,
    nomenclature TEXT,
    source_id    TEXT,
    primary_name [CHARACTER VARYING] (255),
    drug_id      TEXT
);

--INSERT INTO drug_claims (id, name, nomenclature, source_id, primary_name, drug_id) VALUES ('5a5b3baf-5655-447f-ba9e-87b451c6bf8b', 'ANTIHISTAMINE', 'NCI Drug Name', '774d9000-b9b3-485f-bb53-07b4d5cccc40', 'ANTIHISTAMINE', 'b66f9a47-d42c-4076-8d39-35382e08a810');

-- Table: drugs
DROP TABLE IF EXISTS drugs;

CREATE TABLE drugs (
    id                 STRING (100, 100) PRIMARY KEY
                                         NOT NULL,
    name               TEXT              NOT NULL,
    fda_approved       BOOLEAN,
    immunotherapy      BOOLEAN,
    anti_neoplastic    BOOLEAN,
    chembl_id          CHAR,
    chembl_molecule_id INTEGER
);

--INSERT INTO drugs (id, name, fda_approved, immunotherapy, anti_neoplastic, chembl_id, chembl_molecule_id) VALUES ('77b99653-ca45-4674-8b72-d6a05b1dbdfb', 'ALPROSTADIL', 't', 'f', 'f', 'CHEMBL495', 3600593);

-- Table: gene_aliases
DROP TABLE IF EXISTS gene_aliases;

CREATE TABLE gene_aliases (
    id      TEXT,
    gene_id TEXT,
    alias   TEXT
);

--INSERT INTO gene_aliases (id, gene_id, alias) VALUES ('e07be803-1f7b-4b86-a80e-747e07890ce3', '45a80aba-7fe3-4d0f-86ad-67c3778319ce', '1');

-- Table: gene_aliases_sources
DROP TABLE IF EXISTS gene_aliases_sources;

CREATE TABLE gene_aliases_sources (
    gene_alias_id TEXT,
    source_id     TEXT
);

--INSERT INTO gene_aliases_sources (gene_alias_id, source_id) VALUES ('e07be803-1f7b-4b86-a80e-747e07890ce3', '90df7a8d-6931-45ba-94c4-16976251e2fb');

-- Table: gene_attributes
DROP TABLE IF EXISTS gene_attributes;

CREATE TABLE gene_attributes (
    id      TEXT,
    gene_id TEXT,
    name    TEXT,
    value   TEXT
);

--INSERT INTO gene_attributes (id, gene_id, name, value) VALUES ('5ac7acab-4eeb-4b45-b760-41360b56e036', '86984fb4-5ae9-495c-9ba7-21788a488257', 'Gene Biotype', 'LINCRNA');

-- Table: gene_attributes_sources
DROP TABLE IF EXISTS gene_attributes_sources;

CREATE TABLE gene_attributes_sources (
    gene_attribute_id TEXT,
    source_id         TEXT
);

--INSERT INTO gene_attributes_sources (gene_attribute_id, source_id) VALUES ('46477161-3451-4a1e-b7bf-302397a7e7e1', '0a5f4607-2180-44b6-a5c9-ae056ba21b64');

-- Table: gene_categories_genes
DROP TABLE IF EXISTS gene_categories_genes;

CREATE TABLE gene_categories_genes (
    gene_claim_category_id TEXT,
    gene_id                TEXT
);

--INSERT INTO gene_categories_genes (gene_claim_category_id, gene_id) VALUES ('4ce9f470845e469fb46feea79e05727d', '9bba98fc-529a-4ea5-a6ef-e6ffd603dc4f');

-- Table: gene_claim_aliases
DROP TABLE IF EXISTS gene_claim_aliases;

CREATE TABLE gene_claim_aliases (
    id            TEXT NOT NULL,
    gene_claim_id TEXT NOT NULL,
    alias         TEXT NOT NULL,
    nomenclature  TEXT NOT NULL,
    CONSTRAINT gene_claim_aliases_pkey PRIMARY KEY (
        id
    )
);

--INSERT INTO gene_claim_aliases (id, gene_claim_id, alias, nomenclature) VALUES ('967d51a6-e467-4c8e-a5bb-fb87dc946765', 'f4fb9ec3-d71c-4c14-a780-b50aa8cf236c', 'ENSG00000124140', 'Ensembl Gene Id');

-- Table: gene_claim_attributes
DROP TABLE IF EXISTS gene_claim_attributes;

CREATE TABLE gene_claim_attributes (
    id            TEXT NOT NULL,
    gene_claim_id TEXT NOT NULL,
    name          TEXT NOT NULL,
    value         TEXT NOT NULL,
    CONSTRAINT gene_claim_attributes_pkey PRIMARY KEY (
        id
    )
);

--INSERT INTO gene_claim_attributes (id, gene_claim_id, name, value) VALUES ('d6750a72-feff-4c0b-b3eb-be9c634ac6d2', 'b218817a-31ef-444e-a1a2-908d4179bb47', 'Gene Biotype', 'PROCESSED_PSEUDOGENE''"
314fdbbb-319a-43fc-9c25-28e41fea88f9,844b8d94-3796-47d3-ac9e-da40165006ab,Gene Biotype,LINCRNA''"');

-- Table: gene_claim_categories
DROP TABLE IF EXISTS gene_claim_categories;

CREATE TABLE gene_claim_categories (
    id   [CHARACTER VARYING] (255),
    name [CHARACTER VARYING] (255) 
);

--INSERT INTO gene_claim_categories (id, name) VALUES ('51d8dcf789de4dd08ac3c0ce0992d20b', 'TRANSCRIPTION FACTOR COMPLEX');

-- Table: gene_claim_categories_gene_claims
DROP TABLE IF EXISTS gene_claim_categories_gene_claims;

CREATE TABLE gene_claim_categories_gene_claims (
    gene_claim_id          [CHARACTER VARYING] (255),
    gene_claim_category_id [CHARACTER VARYING] (255) 
);

--INSERT INTO gene_claim_categories_gene_claims (gene_claim_id, gene_claim_category_id) VALUES ('e2c99939-a52a-4023-afcf-9aa29259e381', 'd3ec2631e0b2434b9dcc008e793d3fa5');

-- Table: gene_claims
DROP TABLE IF EXISTS gene_claims;

CREATE TABLE gene_claims (
    id           TEXT,
    name         TEXT,
    nomenclature TEXT,
    source_id    TEXT,
    gene_id      TEXT
);

--INSERT INTO gene_claims (id, name, nomenclature, source_id, gene_id) VALUES ('2830b413-180f-4a41-a90e-a87b28259ed9', 'ENSG00000283509', 'Ensembl Gene Id', '0a5f4607-2180-44b6-a5c9-ae056ba21b64', '');

-- Table: gene_gene_interaction_claim_attributes
DROP TABLE IF EXISTS gene_gene_interaction_claim_attributes;

CREATE TABLE gene_gene_interaction_claim_attributes (
    id                             [CHARACTER VARYING] (255) NOT NULL,
    gene_gene_interaction_claim_id [CHARACTER VARYING] (255) NOT NULL,
    name                           [CHARACTER VARYING] (255) NOT NULL,
    value                          [CHARACTER VARYING] (255) NOT NULL,
    CONSTRAINT gene_gene_interaction_claim_attributes_pkey PRIMARY KEY (
        gene_gene_interaction_claim_id
    )
);


-- Table: gene_gene_interaction_claims
DROP TABLE IF EXISTS gene_gene_interaction_claims;

CREATE TABLE gene_gene_interaction_claims (
    id                  [CHARACTER VARYING] (255) NOT NULL,
    gene_id             [CHARACTER VARYING] (255) NOT NULL,
    interacting_gene_id [CHARACTER VARYING] (255) NOT NULL,
    source_id           [CHARACTER VARYING] (255) NOT NULL,
    CONSTRAINT gene_gene_interaction_claims_pkey PRIMARY KEY (
        id
    )
);


-- Table: genes
DROP TABLE IF EXISTS genes;

CREATE TABLE genes (
    id        TEXT,
    name      TEXT,
    long_name CHAR,
    entrez_id INTEGER
);

--INSERT INTO genes (id, name, long_name, entrez_id) VALUES ('45a80aba-7fe3-4d0f-86ad-67c3778319ce', 'A1BG', 'ALPHA-1-B GLYCOPROTEIN', 1);

-- Table: interaction_attributes
DROP TABLE IF EXISTS interaction_attributes;

CREATE TABLE interaction_attributes (
    id             TEXT,
    interaction_id TEXT,
    name           TEXT,
    value          TEXT
);

--INSERT INTO interaction_attributes (id, interaction_id, name, value) VALUES ('d51e863d-d31f-429f-8d08-a246b3c797c5', '3ffb17e1-2bed-4a13-8c47-33361bbd3b39', 'Trial Name', '-');

-- Table: interaction_attributes_sources
DROP TABLE IF EXISTS interaction_attributes_sources;

CREATE TABLE interaction_attributes_sources (
    interaction_attribute_id TEXT NOT NULL,
    source_id                TEXT NOT NULL,
    CONSTRAINT interaction_attributes_sources_pkey PRIMARY KEY (
        interaction_attribute_id,
        source_id
    )
);

INSERT INTO interaction_attributes_sources (interaction_attribute_id, source_id) VALUES ('d51e863d-d31f-429f-8d08-a246b3c797c5', '55a7a373-bba6-4069-a104-ac6e030ac433');

-- Table: interaction_claim_attributes
DROP TABLE IF EXISTS interaction_claim_attributes;

CREATE TABLE interaction_claim_attributes (
    id                   TEXT NOT NULL,
    interaction_claim_id TEXT NOT NULL,
    name                 TEXT NOT NULL,
    value                TEXT NOT NULL,
    CONSTRAINT interaction_claim_attributes_pkey PRIMARY KEY (
        id
    )
);

INSERT INTO interaction_claim_attributes (id, interaction_claim_id, name, value) VALUES ('577e2ce0-e4e7-40dc-9f66-4582ab4618e0', '1ffb8c98-0e92-412d-bc0e-ef9657ef4d6c', 'Reported Cancer Type', 'Melanoma');

-- Table: interaction_claim_types
DROP TABLE IF EXISTS interaction_claim_types;

CREATE TABLE interaction_claim_types (
    id             [CHARACTER VARYING] (255) NOT NULL,
    type           [CHARACTER VARYING] (255),
    directionality INTEGER,
    definition     TEXT,
    CONSTRAINT interaction_claim_types_pkey PRIMARY KEY (
        id
    )
);

INSERT INTO interaction_claim_types (id, type, directionality, definition) VALUES ('c0ef4205-a449-4cca-b240-07c2ee7d233b', 'partial agonist', '', '');

-- Table: interaction_claim_types_interaction_claims
DROP TABLE IF EXISTS interaction_claim_types_interaction_claims;

CREATE TABLE interaction_claim_types_interaction_claims (
    interaction_claim_type_id [CHARACTER VARYING] (255) NOT NULL,
    interaction_claim_id      [CHARACTER VARYING] (255) NOT NULL,
    CONSTRAINT interaction_claim_types_interaction_claims_pkey PRIMARY KEY (
        interaction_claim_type_id,
        interaction_claim_id
    )
);

INSERT INTO interaction_claim_types_interaction_claims (interaction_claim_type_id, interaction_claim_id) VALUES ('f19ad8e7-bf84-4b85-8487-dbf3edc97dbb', 'f18dd2d3-7069-4917-ac7f-4e101c590302');

-- Table: interaction_claims
DROP TABLE IF EXISTS interaction_claims;

CREATE TABLE interaction_claims (
    id             TEXT NOT NULL,
    drug_claim_id  TEXT NOT NULL,
    gene_claim_id  TEXT NOT NULL,
    source_id      TEXT,
    interaction_id TEXT,
    CONSTRAINT interaction_claims_pkey PRIMARY KEY (
        id
    )
);

INSERT INTO interaction_claims (id, drug_claim_id, gene_claim_id, source_id, interaction_id) VALUES ('99525974-a305-41e5-b585-4922cf96baf3', 'de9f8299-91f4-4578-90b7-415166e8b065', '3120a77e-e944-4454-b426-0c151a818fa4', '55a7a373-bba6-4069-a104-ac6e030ac433', '60b2ee68-239b-4498-8459-6e5493da6549');

-- Table: interaction_claims_publications
DROP TABLE IF EXISTS interaction_claims_publications;

CREATE TABLE interaction_claims_publications (
    interaction_claim_id TEXT NOT NULL,
    publication_id       TEXT NOT NULL,
    CONSTRAINT interaction_claims_publications_pkey PRIMARY KEY (
        interaction_claim_id,
        publication_id
    )
);

INSERT INTO interaction_claims_publications (interaction_claim_id, publication_id) VALUES ('96896b0f-33bc-4062-9e8a-0614c8a21c08', '855cf52e-7e75-4293-b844-bb3c3ae98aad');

-- Table: interaction_types_interactions
DROP TABLE IF EXISTS interaction_types_interactions;

CREATE TABLE interaction_types_interactions (
    interaction_claim_type_id TEXT NOT NULL,
    interaction_id            TEXT NOT NULL,
    CONSTRAINT interaction_types_interactions_pkey PRIMARY KEY (
        interaction_claim_type_id,
        interaction_id
    )
);

INSERT INTO interaction_types_interactions (interaction_claim_type_id, interaction_id) VALUES ('f19ad8e7-bf84-4b85-8487-dbf3edc97dbb', '4c4995e4-b06b-46b4-ae71-46e9a6dbd51e');

-- Table: interactions
DROP TABLE IF EXISTS interactions;

CREATE TABLE interactions (
    id      TEXT,
    drug_id TEXT,
    gene_id TEXT
);

INSERT INTO interactions (id, drug_id, gene_id) VALUES ('028d5474-94e5-431b-9e2c-a6ab07de5a14', '9a4ebc16-4f04-45f9-acf6-186da0396512', '65ef57ca-a48b-48ec-b0c0-e2de2dd0f795');

-- Table: interactions_publications
DROP TABLE IF EXISTS interactions_publications;

CREATE TABLE interactions_publications (
    interaction_id TEXT,
    publication_id TEXT
);

INSERT INTO interactions_publications (interaction_id, publication_id) VALUES ('ec04fd82-763b-43a1-8562-f1a7d1b2c77d', 'a2de77b1-adcc-4920-b34f-90a2f90e0aeb');

-- Table: interactions_sources
DROP TABLE IF EXISTS interactions_sources;

CREATE TABLE interactions_sources (
    interaction_id TEXT,
    source_id      TEXT
);

INSERT INTO interactions_sources (interaction_id, source_id) VALUES ('028d5474-94e5-431b-9e2c-a6ab07de5a14', '0dbd3093-d272-4db5-ae07-20ba65f4ea7a');

-- Table: publications
DROP TABLE IF EXISTS publications;

CREATE TABLE publications (
    id         TEXT,
    pmid       INTEGER,
    citation   TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

INSERT INTO publications (id, pmid, citation, created_at, updated_at) VALUES ('40ed2c3d-88b8-43cf-928c-22b1a27cd8e6', 10505536, 'Turpie, 1999, Anticoagulants in acute coronary syndromes., Am. J. Cardiol.', '2017-04-28 20:52:00.638361', '2017-05-02 16:32:28.4502');

-- Table: schema_migrations
DROP TABLE IF EXISTS schema_migrations;

CREATE TABLE schema_migrations (
    version [CHARACTER VARYING] (255) NOT NULL
);

INSERT INTO schema_migrations (version) VALUES ('0');

-- Table: source_trust_levels
DROP TABLE IF EXISTS source_trust_levels;

CREATE TABLE source_trust_levels (
    id    [CHARACTER VARYING] (255) NOT NULL,
    level [CHARACTER VARYING] (255) NOT NULL,
    CONSTRAINT source_trust_levels_pkey PRIMARY KEY (
        id
    )
);

INSERT INTO source_trust_levels (id, level) VALUES ('600d121e-6260-4db8-9689-e72a13cbf2c3', 'Expert curated');

-- Table: source_types
DROP TABLE IF EXISTS source_types;

CREATE TABLE source_types (
    id           [CHARACTER VARYING] (255),
    type         [CHARACTER VARYING] (255),
    display_name [CHARACTER VARYING] (255),
    CONSTRAINT source_types_pkey PRIMARY KEY (
        id
    )
);

INSERT INTO source_types (id, type, display_name) VALUES ('bd6d3b57-f8ca-431a-9ba6-d412c96cd364', 'gene', 'Gene');

-- Table: sources
DROP TABLE IF EXISTS sources;

CREATE TABLE sources (
    id                                 TEXT,
    source_db_name                     TEXT,
    source_db_version                  TEXT,
    citation                           TEXT,
    base_url                           TEXT,
    site_url                           TEXT,
    full_name                          TEXT,
    source_type_id                     [CHARACTER VARYING] (255),
    gene_claims_count                  INTEGER                   DEFAULT 0,
    drug_claims_count                  INTEGER                   DEFAULT 0,
    interaction_claims_count           INTEGER                   DEFAULT 0,
    interaction_claims_in_groups_count INTEGER                   DEFAULT 0,
    gene_claims_in_groups_count        INTEGER                   DEFAULT 0,
    drug_claims_in_groups_count        INTEGER                   DEFAULT 0,
    source_trust_level_id              [CHARACTER VARYING] (255),
    gene_gene_interaction_claims_count INTEGER                   DEFAULT 0
);

INSERT INTO sources (id, source_db_name, source_db_version, citation, base_url, site_url, full_name, source_type_id, gene_claims_count, drug_claims_count, interaction_claims_count, interaction_claims_in_groups_count, gene_claims_in_groups_count, drug_claims_in_groups_count, source_trust_level_id, gene_gene_interaction_claims_count) VALUES ('b51d654b-5b39-4dce-ab99-28b78958f9f1', 'MyCancerGenomeClinicalTrial', '30-February-2014', 'http://www.mycancergenome.org/', 'http://www.mycancergenome.org/', 'http://www.mycancergenome.org/', 'MyCancerGenome Clinical Trial', 'ce28974a-b813-4717-a3d2-2df0cc54ab5a', 83, 112, 377, 305, 80, 105, '600d121e-6260-4db8-9689-e72a13cbf2c3', 0);

-- Index: 
DROP INDEX IF EXISTS "";

CREATE INDEX "" ON drug_attributes_sources (
    source_id
);


-- Index: drug_aliases_index_on_clean_alias
DROP INDEX IF EXISTS drug_aliases_index_on_clean_alias;

CREATE INDEX drug_aliases_index_on_clean_alias ON drug_aliases (
    alias
);


-- Index: idx_drugs_chembl
DROP INDEX IF EXISTS idx_drugs_chembl;

CREATE INDEX idx_drugs_chembl ON drugs (
    chembl_id
);


-- Index: idx_drugs_id
DROP INDEX IF EXISTS idx_drugs_id;

CREATE INDEX idx_drugs_id ON drugs (
    id
);


-- Index: idx_gene_attr_gene_id
DROP INDEX IF EXISTS idx_gene_attr_gene_id;

CREATE INDEX idx_gene_attr_gene_id ON gene_attributes (
    gene_id
);


-- Index: index_chembl_molecules_on_chembl_id
DROP INDEX IF EXISTS index_chembl_molecules_on_chembl_id;

CREATE UNIQUE INDEX index_chembl_molecules_on_chembl_id ON chembl_molecules (
    chembl_id ASC
);


-- Index: index_drug_alias_id
DROP INDEX IF EXISTS index_drug_alias_id;

CREATE INDEX index_drug_alias_id ON drug_aliases_sources (
    drug_alias_id
);


-- Index: index_drug_aliases_on_drug_id
DROP INDEX IF EXISTS index_drug_aliases_on_drug_id;

CREATE INDEX index_drug_aliases_on_drug_id ON drug_aliases (
    drug_id
);


-- Index: index_drug_attributes_on_drug_id_and_name_and_value
DROP INDEX IF EXISTS index_drug_attributes_on_drug_id_and_name_and_value;

CREATE UNIQUE INDEX index_drug_attributes_on_drug_id_and_name_and_value ON drug_attributes (
    drug_id,
    name,
    value
);


-- Index: index_drug_attributes_sources_id
DROP INDEX IF EXISTS index_drug_attributes_sources_id;

CREATE INDEX index_drug_attributes_sources_id ON drug_attributes_sources (
    drug_attribute_id
);


-- Index: index_drugs_on_name
DROP INDEX IF EXISTS index_drugs_on_name;

CREATE UNIQUE INDEX index_drugs_on_name ON drugs (
    name
);


-- Index: index_gene_attribute_sources_id
DROP INDEX IF EXISTS index_gene_attribute_sources_id;

CREATE INDEX index_gene_attribute_sources_id ON gene_attributes_sources (
    gene_attribute_id
);


-- Index: index_gene_attributes_on_gene_id_and_name_and_value
DROP INDEX IF EXISTS index_gene_attributes_on_gene_id_and_name_and_value;

CREATE UNIQUE INDEX index_gene_attributes_on_gene_id_and_name_and_value ON gene_attributes (
    gene_id,
    name,
    value
);


-- Index: index_genes
DROP INDEX IF EXISTS index_genes;

CREATE INDEX index_genes ON genes (
    id,
    entrez_id
);


-- Index: index_interaction_attr_src_id
DROP INDEX IF EXISTS index_interaction_attr_src_id;

CREATE INDEX index_interaction_attr_src_id ON interaction_attributes_sources (
    interaction_attribute_id
);


-- Index: index_interaction_attributes
DROP INDEX IF EXISTS index_interaction_attributes;

CREATE INDEX index_interaction_attributes ON interaction_attributes (
    interaction_id ASC
);


-- Index: index_interaction_attributes_id
DROP INDEX IF EXISTS index_interaction_attributes_id;

CREATE INDEX index_interaction_attributes_id ON interaction_attributes (
    id
);


-- Index: index_interactions_id
DROP INDEX IF EXISTS index_interactions_id;

CREATE INDEX index_interactions_id ON interactions (
    id
);


-- Index: index_interactions_on_drug_id_and_gene_id
DROP INDEX IF EXISTS index_interactions_on_drug_id_and_gene_id;

CREATE UNIQUE INDEX index_interactions_on_drug_id_and_gene_id ON interactions (
    drug_id,
    gene_id
);


-- Index: index_interactions_pub_int_id
DROP INDEX IF EXISTS index_interactions_pub_int_id;

CREATE INDEX index_interactions_pub_int_id ON interactions_publications (
    interaction_id
);


-- Index: index_interactions_pub_pub_id
DROP INDEX IF EXISTS index_interactions_pub_pub_id;

CREATE INDEX index_interactions_pub_pub_id ON interactions_publications (
    publication_id
);


-- Index: index_publications_id
DROP INDEX IF EXISTS index_publications_id;

CREATE INDEX index_publications_id ON publications (
    id
);


-- Index: index_sources_id
DROP INDEX IF EXISTS index_sources_id;

CREATE INDEX index_sources_id ON sources (
    id
);


-- View: Drugs_Claims
DROP VIEW IF EXISTS Drugs_Claims;
CREATE VIEW Drugs_Claims AS
    SELECT *
      FROM drugs
           JOIN
           interactions ON drugs.id = interactions.drug_id
           JOIN
           genes ON interactions.gene_id = genes.id
           JOIN
           gene_attributes ON genes.id = gene_attributes.gene_id
           JOIN
           gene_aliases ON genes.id = gene_aliases.gene_id
           JOIN
           gene_aliases_sources ON gene_aliases.id = gene_aliases_sources.gene_alias_id
           JOIN
           gene_claims ON genes.id = gene_claims.gene_id
           JOIN
           gene_claim_categories_gene_claims ON gene_claims.id = gene_claim_categories_gene_claims.gene_claim_id
           JOIN
           gene_claim_categories ON gene_claim_categories_gene_claims.gene_claim_category_id = gene_claim_categories.id
     WHERE drugs.name = 'TAMOXIFEN';


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
