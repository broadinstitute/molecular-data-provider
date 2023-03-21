import sqlite3
import pandas as pd
import ast


def list_to_str(pubmed_ids):
    pubmed_ids = ast.literal_eval(pubmed_ids)
    return ";".join(pubmed_ids)


def delete_pdb(compound_names, xrefs):
    if not xrefs or "PDB" not in xrefs.keys():
        return compound_names
    if xrefs["PDB"] in compound_names:
        compound_names.remove(xrefs["PDB"])
    return compound_names


def unzip_dict(input_dict):
    input_dict = ast.literal_eval(input_dict)
    if not input_dict:
        return None, None
    keys, values = zip(*input_dict.items())
    return list(keys), list(values)


# Make sure no database already exists with this name
connection = sqlite3.connect("probeminer.sqlite", check_same_thread=False)
cur = connection.cursor()
CHUNK_SIZE = 25000
DO_IF_EXISTS = 'append'

create_tables = """
CREATE TABLE chemicals (
    COMPOUND_ID INTEGER PRIMARY KEY,
    pains_free INTEGER,
    is_cell_potency INTEGER,
    no_celllines INTEGER,
    no_secondary_targets INTEGER,
    no_targets INTEGER,
    no_celllines_active INTEGER,
    selectivity_comp3 REAL,
    pains_text TEXT,
    cell_potency INTEGER,
    uci INTEGER,
    smiles TEXT,
    inchi TEXT,
    inchi_key TEXT,
    chemical_probes_portal_identifier TEXT,
    chemical_probes_portal_rating INTEGER,
    level1_scaffold TEXT
);

CREATE TABLE proteins (
    UNIPROT_ACCESSION TEXT COLLATE NOCASE PRIMARY KEY,
    auc_max REAL, 
    auc_min REAL, 
    sic_max REAL, 
    sic_min REAL
);

CREATE TABLE interactions (
    COMPOUND_ID INTEGER,
    UNIPROT_ACCESSION TEXT COLLATE NOCASE,
    median_absolute_deviation REAL,
    selectivity_information_content REAL,
    selectivity REAL,
    sar_raw INTEGER,
    no_secondary_targets_unselective INTEGER,
    is_inactive_analogs INTEGER,
    is_target_potency INTEGER,
    active INTEGER,
    target_potency_raw REAL,
    is_sar INTEGER,
    no_secondary_targets INTEGER,
    suitable_probe INTEGER,
    auc REAL,
    selectivity_comp2 REAL,
    selectivity_comp1 REAL,
    target_potency REAL,
    global REAL,
    inactive_analogs_raw INTEGER,
    is_selectivity INTEGER,
    inactive_analogs INTEGER,
    no_secondary_targets_selective INTEGER,
    sar INTEGER,
    median_target_potency INTEGER,
    is_suitable_probe INTEGER,
    chemical_probes_portal_is_probe_for_this_target TEXT,
    rank_global INTEGER,
    pubmed_ids TEXT
);

CREATE TABLE compound_names (
    COMPOUND_ID INTEGER,
    compound_name TEXT COLLATE NOCASE
);

CREATE TABLE xrefs (
    COMPOUND_ID INTEGER,
    database TEXT,
    xref TEXT COLLATE NOCASE
    
);

"""


create_indexes = """
CREATE INDEX chemicals_COMPOUND_ID_idx ON chemicals (
    COMPOUND_ID
);

CREATE INDEX chemicals_inchi_key_idx ON chemicals (
    inchi_key COLLATE NOCASE
);

CREATE INDEX proteins_UNIPROT_ACCESSION_idx ON proteins (
    UNIPROT_ACCESSION COLLATE NOCASE
);

CREATE INDEX interactions_UNIPROT_ACCESSION_idx ON interactions (
    UNIPROT_ACCESSION COLLATE NOCASE
);

CREATE INDEX interactions_COMPOUND_ID_idx ON interactions (
    COMPOUND_ID
);

CREATE INDEX compound_names_COMPOUND_ID_idx ON compound_names (
    COMPOUND_ID
);

CREATE INDEX compound_names_compound_name_idx ON compound_names (
    compound_name
);

CREATE INDEX xrefs_COMPOUND_ID_idx ON xrefs (
    COMPOUND_ID
);
"""


def build_database():
    cur.executescript(create_tables)

    fname = 'probeminer_datadump_2021-02-26.txt'
    df = pd.read_csv(fname, sep="\t", header=0)

    cpd_cols = ['COMPOUND_ID', 'is_pains', 'is_cell_potency', 'no_celllines', 'no_secondary targets', 'no_targets',
                'no_celllines_active', 'selectivity_comp3', 'pains_text', 'cell_potency', 'uci', 'smiles', 'inchi',
                'inchi_key', 'chemical_probes_portal_identifier', 'chemical_probes_portal_rating', 'level1_scaffold']
    prot_cols = ['UNIPROT_ACCESSION', 'auc_max', 'auc_min', 'sic_max', 'sic_min']
    ixn_cols = ['COMPOUND_ID', 'UNIPROT_ACCESSION', 'median_absolute_deviation', 'selectivity_information_content',
                'selectivity', 'sar_raw', 'no_secondary_targets_unselective', 'is_inactive_analogs',
                'is_target_potency', 'active', 'target_potency_raw', 'is_sar', 'no_secondary_targets', 'suitable_probe',
                'auc', 'selectivity_comp2', 'selectivity_comp1', 'target_potency', 'global', 'inactive_analogs_raw',
                'is_selectivity', 'inactive_analogs', 'no_secondary_targets_selective', 'sar', 'median_target_potency',
                'is_suitable_probe', 'chemical_probes_portal_is_probe_for_this_target', 'rank_global', 'pubmed_ids']
    cpd_names_cols = ['COMPOUND_ID', 'compound_names', 'xrefs']
    xrefs_cols = ['COMPOUND_ID', 'xrefs']

    cpd_df = df[[col for col in df.columns if col in cpd_cols]]
    cpd_df.rename(columns={'is_pains': 'pains_free'}, inplace=True)
    cpd_df.drop_duplicates(subset=['COMPOUND_ID'], inplace=True)
    prot_df = df[[col for col in df.columns if col in prot_cols]]
    prot_df.drop_duplicates(subset=['UNIPROT_ACCESSION'], inplace=True)
    ixn_df = df[[col for col in df.columns if (col in ixn_cols)]]
    ixn_df['pubmed_ids'] = ixn_df.apply(lambda x: list_to_str(x.pubmed_ids), axis=1)

    cpd_names_df = df[[col for col in df.columns if col in cpd_names_cols]]
    cpd_names_df.drop_duplicates(subset=['COMPOUND_ID'], inplace=True)
    cpd_names_df.compound_names = cpd_names_df.compound_names.apply(ast.literal_eval)
    cpd_names_df.xrefs = cpd_names_df.xrefs.apply(ast.literal_eval)
    cpd_names_df['compound_name'] = cpd_names_df.apply(lambda x: delete_pdb(x.compound_names, x.xrefs), axis=1)
    cpd_names_df.drop(['compound_names', 'xrefs'], axis=1, inplace=True)
    cpd_names_df = cpd_names_df.explode('compound_name')
    cpd_names_df.dropna(subset=["compound_name"], inplace=True)

    xrefs_df = df[[col for col in df.columns if col in xrefs_cols]]
    xrefs_df.drop_duplicates(subset=['COMPOUND_ID'], inplace=True)
    xrefs_df['database'], xrefs_df['xref'] = zip(*xrefs_df['xrefs'].map(unzip_dict))
    xrefs_df.drop(['xrefs'], axis=1, inplace=True)
    xrefs_df = xrefs_df.explode(['database', 'xref'])
    xrefs_df.dropna(subset=["xref"], inplace=True)

    cpd_df.to_sql("chemicals", connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    prot_df.to_sql("proteins", connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    ixn_df.to_sql("interactions", connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    cpd_names_df.to_sql("compound_names", connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    xrefs_df.to_sql("xrefs", connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

    cur.executescript(create_indexes)
    connection.commit()
    cur.close()
    connection.close()


build_database()
