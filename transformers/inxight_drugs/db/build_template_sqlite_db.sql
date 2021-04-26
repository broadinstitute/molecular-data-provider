--
-- File generated with SQLiteStudio v3.2.1 on Wed Nov 25 17:32:22 2020
--
-- This is a template SQL script for reconstituting the Inxight:Drugs database,
-- which means it will only create the tables, views and indexes but will
-- not INSERT the megabytes of data into the 20 tables. The data should be
-- imported separately.
-- 
--
-- Text encoding used: macintosh
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: _references
CREATE TABLE _references (
    uuid         STRING (100, 100) PRIMARY KEY
                                   NOT NULL,
    citation     TEXT,
    id           TEXT,
    docType      TEXT,
    publicDomain TEXT,
    url          TEXT,
    uploadedFile TEXT
);


-- Table: codes
CREATE TABLE codes (
    uuid       STRING (100, 100) PRIMARY KEY
                                 NOT NULL,
    type       TEXT,
    codeSystem TEXT,
    comments   TEXT,
    code       TEXT,
    url        TEXT,
    codeText   TEXT
);


-- Table: components
CREATE TABLE components (
    uuid       TEXT PRIMARY KEY
                    NOT NULL,
    mixture_id TEXT,
    refuuid    TEXT,
    type       TEXT
);


-- Table: entity_references
CREATE TABLE entity_references (
    entity_id    TEXT NOT NULL,
    reference_id TEXT NOT NULL,
    entity_type  TEXT
);


-- Table: mixtures
CREATE TABLE mixtures (
    uuid                    TEXT NOT NULL,
    parentSubstance_refuuid TEXT
);


-- Table: names
CREATE TABLE names (
    uuid        STRING (100, 100) PRIMARY KEY
                                  NOT NULL,
    name        TEXT,
    type        TEXT,
    preferred   TEXT,
    displayName TEXT
);


-- Table: nucleic_acid_sequences
CREATE TABLE nucleic_acid_sequences (
    uuid            TEXT    PRIMARY KEY
                            NOT NULL,
    nucleic_acid_id TEXT    NOT NULL,
    subunitIndex    INTEGER,
    sequence        TEXT,
    length          INTEGER
);


-- Table: nucleic_acid_sugars
CREATE TABLE nucleic_acid_sugars (
    uuid            TEXT PRIMARY KEY
                         NOT NULL,
    nucleic_acid_id TEXT NOT NULL,
    sugar           TEXT,
    sitesShorthand  TEXT
);


-- Table: nucleic_acids
CREATE TABLE nucleic_acids (
    uuid            TEXT PRIMARY KEY
                         NOT NULL,
    substance_id    TEXT NOT NULL,
    sequenceType    TEXT,
    nucleicAcidType TEXT,
    sequenceOrigin  TEXT
);


-- Table: polymers
CREATE TABLE polymers (
    uuid                  TEXT PRIMARY KEY
                               NOT NULL,
    substance_id          TEXT NOT NULL,
    polymerClass          TEXT,
    polymerSubclass       TEXT,
    polymerGeometry       TEXT,
    sourceType            TEXT,
    displayStructure_id   TEXT,
    idealizedStructure_id TEXT
);


-- Table: protein_sequences
CREATE TABLE protein_sequences (
    uuid         TEXT PRIMARY KEY
                      NOT NULL,
    protein_id   TEXT NOT NULL,
    subunitIndex TEXT,
    sequence     TEXT,
    length       TEXT
);


-- Table: proteins
CREATE TABLE proteins (
    uuid              TEXT PRIMARY KEY
                           NOT NULL,
    substance_id      TEXT NOT NULL,
    proteinType       TEXT,
    proteinSubType    TEXT,
    sequenceType      TEXT,
    sequenceOrigin    TEXT,
    disulfideLinks    TEXT,
    glycosylationType TEXT
);


-- Table: relationships
CREATE TABLE relationships (
    uuid                 STRING (100, 100) PRIMARY KEY
                                           NOT NULL,
    relatedSubstance_id  TEXT,
    originatorUuid       TEXT,
    type                 TEXT,
    mediatorSubstance_id TEXT,
    interactionType      TEXT,
    qualification        TEXT,
    amount_average       TEXT,
    amount_high          TEXT,
    amount_low           TEXT,
    amount_units         TEXT,
    comments             TEXT,
    substance_id         TEXT
);


-- Table: structurallyDiverse
CREATE TABLE structurallyDiverse (
    uuid                          TEXT PRIMARY KEY
                                       NOT NULL,
    substance_id                  TEXT NOT NULL,
    sourceMaterialClass           TEXT,
    sourceMaterialType            TEXT,
    developmentalStage            TEXT,
    infraSpecificName             TEXT,
    organismFamily                TEXT,
    organismGenus                 TEXT,
    organismSpecies               TEXT,
    fractionName                  TEXT,
    part                          TEXT,
    partLocation                  TEXT,
    parentSubstance_refuuid       TEXT,
    infraSpecificType             TEXT,
    fractionMaterialType          TEXT,
    sourceMaterialState           TEXT,
    hybridSpeciesMaternalOrganism TEXT,
    hybridSpeciesPaternalOrganism TEXT
);


-- Table: structures
CREATE TABLE structures (
    id              STRING (100, 100) PRIMARY KEY
                                      NOT NULL,
    digest          TEXT,
    smiles          TEXT,
    formula         TEXT,
    opticalActivity TEXT,
    atropisomerism  TEXT,
    stereoCenters   TEXT,
    definedStereo   TEXT,
    ezCenters       TEXT,
    charge          TEXT,
    mwt             TEXT,
    stereochemistry TEXT,
    InChIKey        TEXT,
    pubChem         TEXT,
    stereoComments  TEXT
);


-- Table: substance_attributes
CREATE TABLE substance_attributes (
    substance_id TEXT,
    name         TEXT,
    value        TEXT
);


-- Table: substance_codes
CREATE TABLE substance_codes (
    substance_id TEXT NOT NULL,
    code_id      TEXT
);


-- Table: substance_names
CREATE TABLE substance_names (
    substance_id TEXT NOT NULL,
    name_id      TEXT
);


-- Table: substances
CREATE TABLE substances (
    uuid                STRING (100, 100) PRIMARY KEY
                                          NOT NULL,
    definitionType      TEXT,
    definitionLevel     TEXT,
    substanceClass      TEXT,
    status              TEXT,
    approvalID          TEXT,
    UNII                TEXT,
    structurallyDiverse TEXT,
    protein             TEXT,
    nucleicAcid         TEXT,
    _name               TEXT              COLLATE NOCASE,
    mixture             TEXT,
    _moieties           TEXT,
    structure_id        TEXT,
    polymer             TEXT
);


-- Table: unii_lookup
CREATE TABLE unii_lookup (
    UNII            TEXT (12) PRIMARY KEY,
    PT              TEXT,
    RN              TEXT,
    EC              TEXT,
    NCIT            TEXT,
    RXCUI           TEXT,
    PUBCHEM         TEXT,
    ITIS            TEXT,
    NCBI            TEXT,
    PLANTS          TEXT,
    GRIN            TEXT,
    MPNS            TEXT,
    INN_ID          TEXT,
    MF              TEXT,
    INCHIKEY        TEXT,
    SMILES          TEXT,
    INGREDIENT_TYPE TEXT
);


-- Index: codes_index
CREATE INDEX codes_index ON codes (
    uuid
);


-- Index: index_substance_on_uuid
CREATE UNIQUE INDEX index_substance_on_uuid ON substances (
    uuid
);


-- Index: index_entity_references_entity_id
CREATE INDEX index_entity_references_entity_id ON entity_references (
    entity_id
);


-- Index: references_uuid
CREATE INDEX references_uuid ON entity_references (
    entity_id,
    reference_id
);


-- Index: referencesIndex
CREATE INDEX referencesIndex ON _references (
    uuid
);


-- Index: relationship_index
CREATE INDEX relationship_index ON relationships (
    relatedSubstance_id ASC,
    substance_id
);


-- Index: structures_index
CREATE INDEX structures_index ON structures (
    id
);


-- Index: unii_lookup_index
CREATE INDEX unii_lookup_index ON unii_lookup (
    UNII
);


-- Index: index_unii_lookup_rxcui
CREATE INDEX index_unii_lookup_rxcui ON unii_lookup (
    RXCUI
);


-- Index: substance_names_substance_id_index
CREATE INDEX substance_names_substance_id_index ON substance_names (
    substance_id
);


-- Index: substance_codes_substance_id_index
CREATE INDEX substance_codes_substance_id_index ON substance_codes (
    substance_id
);


-- Index: proteins_substance_id_index
CREATE INDEX proteins_substance_id_index ON proteins (
    substance_id
);


-- Index: protein_sequences_protein_id_index
CREATE INDEX protein_sequences_protein_id_index ON protein_sequences (
    protein_id
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
