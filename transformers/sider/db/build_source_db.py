import sys
import sqlite3

import pandas as pd
#import numpy as np

connection_source = sqlite3.connect("data/sider_source.sqlite", check_same_thread=False)
connection_source.row_factory = sqlite3.Row

CHUNK_SIZE = 25000
DO_IF_EXISTS = 'append'
nocase='NOCASE'

def create_index(table, column, colate=None):
    colate_nocase = 'COLLATE ' + nocase if colate == nocase else ''
    stmt = """
        CREATE INDEX {}_{}_idx 
        ON {} ({} {});    
    """.format(table, column,table, column, colate_nocase)
    cur = connection_source.cursor()
    cur.executescript(stmt)
    cur.close()


def build_database():
    df = pd.read_csv('data/drug_atc.tsv', sep="\t", header=None, names=['cid_flat','atc'])
    print(len(df))
    df.to_sql("drug_atc", connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('drug_atc','cid_flat')
    print("drug_atc")

    names = ['source_label','cid_flat','cid_stereo','umls_on_label','concept_type','umls_se','side_effect_name']
    df = pd.read_csv('data/meddra_all_label_se.tsv', sep="\t", header=None, names = names)
    print(len(df))
    df.to_sql('meddra_all_label_se', connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('meddra_all_label_se','cid_flat')
    print('meddra_all_label_se')

    names = ['cid_flat','cid_stereo','umls_on_label','concept_type','umls_se','side_effect_name']
    df = pd.read_csv('data/meddra_all_se.tsv', sep="\t", header=None, names=names)
    print(len(df))
    df.to_sql('meddra_all_se', connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('meddra_all_se','cid_flat')
    print('meddra_all_se')

    names = ['cid_flat', 'drug_name']
    df = pd.read_csv('data/drug_names.tsv', sep="\t", header=None, names=names)
    print(len(df))
    df.to_sql('drug_names', connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('drug_names', 'cid_flat')
    print('drug_names')

    names = ['umls_on_label', 'concept_type', 'meddra_id', 'side_effect']
    df = pd.read_csv('data/meddra.tsv', sep="\t", header=None, names=names)
    print(len(df))
    df.to_sql('meddra', connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('meddra', 'umls_on_label')
    print('meddra')

    names = ['cid_flat', 'umls_on_label', 'method_of_detection', 'concept_name', 'concept_type', 'umls_meddra', 'meddra_concept_name']
    df = pd.read_csv('data/meddra_all_indications.tsv', sep="\t", header=None, names=names)
    print(len(df))
    df.to_sql('meddra_all_indications', connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('meddra_all_indications', 'cid_flat')
    print('meddra_all_indications')

    names = ['source_label', 'cid_flat', 'cid_stereo', 'umls_on_label', 'method_of_detection', 'concept_name', 'concept_type', 'umls_meddra', 'meddra_concept_name']
    df = pd.read_csv('data/meddra_all_label_indications.tsv', sep="\t", header=None, names=names)
    print(len(df))
    df.to_sql('meddra_all_label_indications', connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('meddra_all_label_indications', 'cid_flat')
    print('meddra_all_label_indications')

    names = ['cid_flat', 'cid_stereo', 'umls_on_label', 'placebo', 'frequency', 'lower_bound_freq', 'upper_bound_freq', 'concept_type', 'umls_meddra', 'side_effect']
    df = pd.read_csv('data/meddra_freq.tsv', sep="\t", header=None, names=names)
    print(len(df))
    df.to_sql('meddra_freq', connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    create_index('meddra_freq', 'cid_flat')
    print('meddra_freq')

def create_indexes():
    statement="""
    CREATE INDEX meddra_all_label_se_cid_stereo_idx ON meddra_all_label_se (
    cid_stereo);
    CREATE INDEX meddra_all_label_se_cid_stereo_umls_se_idx ON meddra_all_label_se (
    cid_stereo,
    umls_se);
    CREATE INDEX meddra_freq_cid_stereo_umls_meddra_idx ON meddra_freq (
    cid_stereo,
    umls_meddra
    );
    """
    cur = connection_source.cursor()
    cur.executescript(statement)
    connection_source.commit()
    

    
if __name__ == "__main__":
    # Call functions to create and build the new tables
    build_database()
    create_indexes()