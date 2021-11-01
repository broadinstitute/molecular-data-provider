import sys
import sqlite3
import requests
import pandas as pd
import numpy as np
#from memory_profiler import profile

# IMPORTANT to do before running this code:
# Download the TSVs, make sure no other rows exist and that the # was removed from column header
# Use CTD_MESH_to_CID_via_NN.ipynb to generate the mesh to cid conversions
# And generate CTD_from_xml.csv as the output of parse_ctd_xml.py

# Make sure no database already exists with this name
connection = sqlite3.connect("CTD.sqlite", check_same_thread=False)
cur = connection.cursor()
CHUNK_SIZE = 25000
DO_IF_EXISTS = 'append'

create_tables = """
CREATE TABLE chem_gene_ixns_no_cid (
    ChemicalName TEXT COLLATE NOCASE,
    ChemicalID TEXT COLLATE NOCASE,
    CasRN TEXT COLLATE NOCASE,
    GeneSymbol TEXT COLLATE NOCASE,
    GeneID INTEGER,
    GeneForms TEXT COLLATE NOCASE,
    Organism TEXT COLLATE NOCASE,
    OrganismID INTEGER,
    Interaction TEXT,
    InteractionActions TEXT,
    PubMedIDs INTEGER
);

CREATE TABLE chemicals_diseases (
    ChemicalName TEXT COLLATE NOCASE,	
    ChemicalID TEXT COLLATE NOCASE,
    CasRN TEXT COLLATE NOCASE,
    DiseaseName TEXT COLLATE NOCASE,
    DiseaseID TEXT COLLATE NOCASE,
    DirectEvidence TEXT COLLATE NOCASE,
    InferenceGeneSymbol TEXT COLLATE NOCASE,
    InferenceScore REAL,
    OmimIDs	TEXT COLLATE NOCASE,
    PubMedIDs TEXT COLLATE NOCASE
);

CREATE TABLE chem_pathways_enriched (
    ChemicalName TEXT COLLATE NOCASE,
    ChemicalID TEXT COLLATE NOCASE,
    CasRN TEXT COLLATE NOCASE,
    PathwayName TEXT COLLATE NOCASE,
    PathwayID TEXT COLLATE NOCASE,
    PValue REAL,
    CorrectedPValue REAL,
    TargetMatchQty INTEGER,
    TargetTotalQty INTEGER,
    BackgroundMatchQty INTEGER,
    BackgroundTotalQty INTEGER
);

CREATE TABLE chem_go_enriched (
    ChemicalName TEXT COLLATE NOCASE,
    ChemicalID TEXT COLLATE NOCASE,
    CasRN TEXT COLLATE NOCASE,
    Ontology TEXT COLLATE NOCASE,
    GOTermName TEXT COLLATE NOCASE,
    GOTermID TEXT COLLATE NOCASE,
    HighestGOLevel INTEGER,
    PValue REAL,
    CorrectedPValue REAL,
    TargetMatchQty INTEGER,
    TargetTotalQty INTEGER,
    BackgroundMatchQty INTEGER,
    BackgroundTotalQty INTEGER
);

CREATE TABLE pheno_term_ixns (
    chemicalname TEXT COLLATE NOCASE,
    chemicalid TEXT COLLATE NOCASE,
    casrn TEXT COLLATE NOCASE,
    phenotypename TEXT COLLATE NOCASE,
    phenotypeid TEXT COLLATE NOCASE,
    comentionedterms TEXT COLLATE NOCASE,
    organism TEXT COLLATE NOCASE,
    organismid INTEGER,
    interaction TEXT COLLATE NOCASE,
    interactionactions TEXT COLLATE NOCASE,
    anatomyterms TEXT COLLATE NOCASE,
    inferencegenesymbols TEXT COLLATE NOCASE,
    pubmedids INTEGER
);

CREATE TABLE chemicals (
    ChemicalName TEXT COLLATE NOCASE,
    ChemicalID TEXT COLLATE NOCASE,
    CasRN TEXT COLLATE NOCASE,
    Definition TEXT,
    ParentIDs TEXT COLLATE NOCASE,
    TreeNumbers TEXT COLLATE NOCASE,
    ParentTreeNumbers TEXT COLLATE NOCASE,
    Synonyms TEXT COLLATE NOCASE
);

CREATE TABLE chem_gene_ixns_with_axns (
    IxnID INTEGER,
    ChemicalID TEXT COLLATE NOCASE,
    ChemicalName TEXT COLLATE NOCASE,
    ChemicalPosition INTEGER,
    ChemicalForm TEXT COLLATE NOCASE,
    ChemicalFormQualifier TEXT COLLATE NOCASE,
    GeneID TEXT COLLATE NOCASE,
    GeneName TEXT COLLATE NOCASE,
    GenePosition INTEGER,
    GeneForm TEXT COLLATE NOCASE,
    GeneFormQualifier TEXT COLLATE NOCASE,
    GeneSeqID TEXT COLLATE NOCASE,
    TaxonID INTEGER,
    TaxonName TEXT COLLATE NOCASE,
    ReferencePMIDs TEXT COLLATE NOCASE,
    AxnCode TEXT COLLATE NOCASE,
    AxnDegreeCode TEXT COLLATE NOCASE,
    AxnPosition TEXT COLLATE NOCASE,
    AxnParentID TEXT COLLATE NOCASE,
    AxnName TEXT COLLATE NOCASE
);

CREATE TABLE mesh_to_cid (
    ChemicalID TEXT COLLATE NOCASE,
    PubChem_CID TEXT COLLATE NOCASE
);

CREATE TABLE axn_name_inverses (
    OriginalAxnName TEXT COLLATE NOCASE,
    InverseAxnName TEXT COLLATE NOCASE
);
"""


merge_tables = """
CREATE TABLE chemicals_w_PubchemCID AS SELECT 
chemicals.*,
mesh_to_cid.PubChem_CID     
FROM chemicals LEFT JOIN mesh_to_cid ON chemicals.ChemicalID = mesh_to_cid.ChemicalID;

CREATE TABLE chem_gene_ixns AS SELECT 
chem_gene_ixns_no_cid.*,
mesh_to_cid.PubChem_CID     
FROM chem_gene_ixns_no_cid LEFT JOIN mesh_to_cid ON chem_gene_ixns_no_cid.ChemicalID = mesh_to_cid.ChemicalID;

CREATE TABLE chem_gene_ixns_w_axn_info_no_inverses AS SELECT 
chem_gene_ixns_with_axns.*,
chemicals_w_PubchemCID.PubChem_CID 
FROM chem_gene_ixns_with_axns 
LEFT JOIN chemicals_w_PubchemCID ON chemicals_w_PubchemCID.ChemicalID = chem_gene_ixns_with_axns.ChemicalID;

CREATE TABLE chem_gene_ixns_w_axn_info AS SELECT 
chem_gene_ixns_w_axn_info_no_inverses.*,
axn_name_inverses.InverseAxnName  
FROM chem_gene_ixns_w_axn_info_no_inverses 
LEFT JOIN axn_name_inverses ON axn_name_inverses.OriginalAxnName = chem_gene_ixns_w_axn_info_no_inverses.AxnName;

CREATE TABLE pheno_term_ixns_w_pubchem AS SELECT 
pheno_term_ixns.*,
chemicals_w_PubchemCID.PubChem_CID
FROM pheno_term_ixns LEFT JOIN chemicals_w_PubchemCID ON chemicals_w_PubchemCID.ChemicalID = pheno_term_ixns.ChemicalID;

CREATE TABLE chemicals_diseases_w_pubchem AS SELECT 
chemicals_diseases.*,
chemicals_w_PubchemCID.PubChem_CID
FROM chemicals_diseases 
LEFT JOIN chemicals_w_PubchemCID ON chemicals_w_PubchemCID.ChemicalID = chemicals_diseases.ChemicalID;

CREATE TABLE chem_pathways_enriched_w_pubchem AS SELECT 
chem_pathways_enriched.*,
chemicals_w_PubchemCID.PubChem_CID
FROM chem_pathways_enriched 
LEFT JOIN chemicals_w_PubchemCID ON chemicals_w_PubchemCID.ChemicalID = chem_pathways_enriched.ChemicalID;

CREATE TABLE chem_go_enriched_w_pubchem AS SELECT 
chem_go_enriched.*,
chemicals_w_PubchemCID.PubChem_CID
FROM chem_go_enriched
LEFT JOIN chemicals_w_PubchemCID ON chemicals_w_PubchemCID.ChemicalID = chem_go_enriched.ChemicalID;

"""

delete_tables = """
DROP TABLE chemicals;
DROP TABLE chem_gene_ixns_with_axns;
DROP TABLE pheno_term_ixns;
DROP TABLE chemicals_diseases;
DROP TABLE chem_pathways_enriched;
DROP TABLE chem_go_enriched;
DROP TABLE chem_gene_ixns_no_cid;
DROP TABLE chem_gene_ixns_w_axn_info_no_inverses;
ALTER TABLE pheno_term_ixns_w_pubchem RENAME TO pheno_term_ixns;
ALTER TABLE chemicals_diseases_w_pubchem RENAME TO chemicals_diseases;
ALTER TABLE chem_pathways_enriched_w_pubchem RENAME TO chem_pathways_enriched;
ALTER TABLE chem_go_enriched_w_pubchem RENAME TO chem_go_enriched;
"""

create_indexes = """
CREATE INDEX chem_gene_ixns_w_axn_info_ChemicalName_idx ON chem_gene_ixns_w_axn_info (
    ChemicalName COLLATE NOCASE
);

CREATE INDEX chem_gene_ixns_w_axn_info_PubChemCID_idx ON chem_gene_ixns_w_axn_info (
    PubChem_CID COLLATE NOCASE
);

CREATE INDEX chem_gene_ixns_w_axn_info_ChemicalID_idx ON chem_gene_ixns_w_axn_info (
    ChemicalID COLLATE NOCASE
);

CREATE INDEX chem_gene_ixns_ChemicalName_idx ON chem_gene_ixns (
    ChemicalName COLLATE NOCASE
);

CREATE INDEX chem_gene_ixns_PubChemCID_idx ON chem_gene_ixns (
    PubChem_CID COLLATE NOCASE
);

CREATE INDEX chem_gene_ixns_ChemicalID_idx ON chem_gene_ixns (
    ChemicalID COLLATE NOCASE
);

CREATE INDEX chem_gene_ixns_CasRN_idx ON chem_gene_ixns (
    CasRN COLLATE NOCASE
);

CREATE INDEX chemicals_w_PubChemCID_ChemicalName_idx ON chemicals_w_PubchemCID (
    ChemicalName COLLATE NOCASE
);

CREATE INDEX chemicicals_w_PubChemCID_PubChemCID_idx ON chemicals_w_PubchemCID (
    PubChem_CID COLLATE NOCASE
);

CREATE INDEX chemicals_w_PubChemCID_ChemicalID_idx ON chemicals_w_PubchemCID (
    ChemicalID COLLATE NOCASE
);

CREATE INDEX chemicals_w_PubChemCID_CasRN_idx ON chemicals_w_PubchemCID (
    CasRN COLLATE NOCASE
);

CREATE INDEX chem_go_enriched_ChemicalName_idx ON chem_go_enriched (
    ChemicalName COLLATE NOCASE
);

CREATE INDEX chem_go_enriched_PubChemCID_idx ON chem_go_enriched (
    PubChem_CID COLLATE NOCASE
);

CREATE INDEX chem_go_enriched_ChemicalID_idx ON chem_go_enriched (
    ChemicalID COLLATE NOCASE
);

CREATE INDEX chem_go_enriched_CasRN_idx ON chem_go_enriched (
    CasRN COLLATE NOCASE
);

CREATE INDEX chem_pathways_enriched_ChemicalName_idx ON chem_pathways_enriched (
    ChemicalName COLLATE NOCASE
);

CREATE INDEX chem_pathways_enriched_PubChemCID_idx ON chem_pathways_enriched (
    PubChem_CID COLLATE NOCASE
);

CREATE INDEX chem_pathways_enriched_ChemicalID_idx ON chem_pathways_enriched (
    ChemicalID COLLATE NOCASE
);

CREATE INDEX chem_pathways_enriched_CasRN_idx ON chem_pathways_enriched (
    CasRN COLLATE NOCASE
);

CREATE INDEX chemicals_diseases_ChemicalName_idx ON chemicals_diseases (
    ChemicalName COLLATE NOCASE
);

CREATE INDEX chemicals_diseases_PubChemCID_idx ON chemicals_diseases (
    PubChem_CID COLLATE NOCASE
);

CREATE INDEX chemicals_diseases_ChemicalID_idx ON chemicals_diseases (
    ChemicalID COLLATE NOCASE
);

CREATE INDEX chemicals_diseases_CasRN_idx ON chemicals_diseases (
    CasRN COLLATE NOCASE
);

CREATE INDEX pheno_term_ixns_ChemicalName_idx ON pheno_term_ixns (
    ChemicalName COLLATE NOCASE
);

CREATE INDEX pheno_term_ixns_PubChemCID_idx ON pheno_term_ixns (
    PubChem_CID COLLATE NOCASE
);

CREATE INDEX pheno_term_ixns_ChemicalID_idx ON pheno_term_ixns (
    ChemicalID COLLATE NOCASE
);

CREATE INDEX pheno_term_ixns_CasRN_idx ON pheno_term_ixns (
    CasRN COLLATE NOCASE
);

"""

def build_database():
    cur.executescript(create_tables)

    df = pd.read_csv('CTD_chem_gene_ixns.tsv', sep="\t", header=0)
    df.to_sql("chem_gene_ixns_no_cid", connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

    df = pd.read_csv('CTD_chemicals_diseases.tsv', sep="\t", header=0)
    df.to_sql("chemicals_diseases", connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

    df = pd.read_csv('CTD_chem_pathways_enriched.tsv', sep="\t", header=0)
    df.to_sql("chem_pathways_enriched", connection, if_exists=DO_IF_EXISTS, index=False,
              chunksize=CHUNK_SIZE)
    df = pd.read_csv('CTD_chem_go_enriched.tsv', sep="\t", header=0)
    df.to_sql("chem_go_enriched", connection, if_exists=DO_IF_EXISTS, index=False,
              chunksize=CHUNK_SIZE)
    df = pd.read_csv('CTD_pheno_term_ixns.tsv', sep="\t", header=0)
    df.to_sql("pheno_term_ixns", connection, if_exists=DO_IF_EXISTS, index=False,
              chunksize=CHUNK_SIZE)
    df = pd.read_csv('CTD_chemicals.tsv', sep="\t", header=0)
    df['ChemicalID'] = [word[5:] for word in df['ChemicalID']]
    df.to_sql("chemicals", connection, if_exists=DO_IF_EXISTS, index=False,
              chunksize=CHUNK_SIZE)
    df = pd.read_csv('CTD_from_xml.csv', sep=",", header=0)
    df.to_sql("chem_gene_ixns_with_axns", connection, if_exists=DO_IF_EXISTS, index=False,
              chunksize=CHUNK_SIZE)
    df = pd.read_csv('mesh_to_pubchemCID_w_nn.tsv', sep="\t", header=0)
    df.to_sql("mesh_to_cid", connection, if_exists=DO_IF_EXISTS, index=False,
              chunksize=CHUNK_SIZE)

    df = pd.read_csv('CTD_inverses.csv', sep=",", header=0)
    df.to_sql("axn_name_inverses", connection, if_exists=DO_IF_EXISTS, index=False,
              chunksize=CHUNK_SIZE)

    cur.executescript(merge_tables)
    cur.executescript(delete_tables)
    cur.executescript(create_indexes)
    connection.commit()
    cur.close()
    connection.close()


build_database()
