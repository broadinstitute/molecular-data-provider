import sys
import sqlite3
import requests
import pandas as pd
import numpy as np
from memory_profiler import profile

#Make sure no database already exists with this name
connection = sqlite3.connect("data/STITCH.sqlite", check_same_thread=False)
cur = connection.cursor()
CHUNK_SIZE = 25000
DO_IF_EXISTS='append'
create_tables = """
CREATE TABLE actions (
    item_id_a   TEXT,
    item_id_b   TEXT,
    mode        TEXT,
    [action]    TEXT,
    a_is_acting TEXT,
    score       INTEGER
);

CREATE TABLE chemical_chemical_links_detailed (
    chemical1      TEXT,
    chemical2      TEXT,
    similarity     INTEGER,
    experimental   INTEGER,
    [database]     INTEGER,
    textmining     INTEGER,
    combined_score INTEGER
);

CREATE TABLE chemical_data (
    chemical         TEXT COLLATE NOCASE,
    name             TEXT COLLATE NOCASE,
    molecular_weight REAL,
    SMILES_string    TEXT
);

CREATE TABLE chemicals_inchikeys (
    flat_chemical_id   TEXT    COLLATE NOCASE,
    stereo_chemical_id TEXT    COLLATE NOCASE,
    source_cid         INTEGER,
    inchikey           TEXT    COLLATE NOCASE
);

CREATE TABLE protein_chemical_links_transfer (
    chemical                 TEXT,
    protein                  TEXT,
    experimental_direct      INTEGER,
    experimental_transferred INTEGER,
    prediction_direct        INTEGER,
    prediction_transferred   INTEGER,
    database_direct          INTEGER,
    database_transferred     INTEGER,
    textmining_direct        INTEGER,
    textmining_transferred   INTEGER,
    combined_score           INTEGER
);
"""

create_indexes = """
CREATE INDEX chemical_data_name_idx ON chemical_data (
    name COLLATE NOCASE
);

CREATE INDEX chemical_data_chemical_idx ON chemical_data (
    chemical
);

CREATE INDEX chemicals_inchikeys_flat_chemical_id_idx ON chemicals_inchikeys (
    flat_chemical_id COLLATE NOCASE
);

CREATE INDEX chemicals_inchikeys_stereo_chemical_id_idx ON chemicals_inchikeys (
    stereo_chemical_id COLLATE NOCASE
);

CREATE INDEX chemicals_inchikeys_inchikey_idx ON chemicals_inchikeys (
    inchikey COLLATE NOCASE
);

CREATE INDEX protein_chemical_links_transfer_chemical_idx ON protein_chemical_links_transfer (
    chemical
);

CREATE INDEX actions_item_ids_ab_idx ON actions (
    item_id_a,
    item_id_b
);
"""


def parse_chemicals(filename, connection):
    chemical_df = pd.read_csv(filename, sep="\t", header=0)
    chemical_df.to_sql("chemical_data", connection, if_exists=DO_IF_EXISTS, index = False, chunksize=CHUNK_SIZE)

@profile
def build_database():
    cur.executescript(create_tables)

    parse_chemicals('chemicals.v5.0.tsv', connection)

    protein_chemical_links_transfer_df = pd.read_csv('9606.protein_chemical.links.transfer.v5.0.tsv', sep="\t", header=0)
    protein_chemical_links_transfer_df.to_sql("protein_chemical_links_transfer", connection, if_exists=DO_IF_EXISTS, index = False, chunksize=CHUNK_SIZE)

    chemicals_inchikeys_df = pd.read_csv('chemicals.inchikeys.v5.0.tsv', sep="\t", header=0)
    chemicals_inchikeys_df.to_sql("chemicals_inchikeys", connection, if_exists=DO_IF_EXISTS, index = False, chunksize=CHUNK_SIZE)

    actions_df = pd.read_csv('9606.actions.v5.0.tsv', sep="\t", header=0)
    actions_df.to_sql("actions", connection, if_exists=DO_IF_EXISTS, index = False, chunksize=CHUNK_SIZE)

    cur.executescript(create_indexes)
    connection.commit()
    cur.close()
    connection.close()

build_database()
