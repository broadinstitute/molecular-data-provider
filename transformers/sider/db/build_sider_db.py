import sys
import sqlite3

import pandas as pd
#import numpy as np

connection_source = sqlite3.connect("data/sider_source.sqlite", check_same_thread=False)
connection_db = sqlite3.connect("data/sider.sqlite", check_same_thread=False)
connection_source.row_factory = sqlite3.Row
connection_db.row_factory = sqlite3.Row 

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

# Functions to create new tables---------------------------------------------------------------------------------------------------------
def create_drug_table(): 
    DRUG_TABLE="""
    CREATE TABLE drug (
    cid_stereo TEXT PRIMARY KEY,
    cid_flat   TEXT,
    drug_name  TEXT COLLATE NOCASE
    );
    """
    cur = connection_db.cursor()
    cur.execute(DRUG_TABLE)
    cur.close()
    connection_db.commit()

def create_atc_table():
    ATC_TABLE = """
    CREATE TABLE atc (
    cid_flat TEXT,
    atc      TEXT
    );
    """
    cur = connection_db.cursor()
    cur.execute(ATC_TABLE)
    cur.close()
    connection_db.commit()

def create_umls_table():
    UMLS_TABLE="""
    CREATE TABLE umls (
    umls_id      TEXT PRIMARY KEY,
    concept_name TEXT COLLATE NOCASE
    );
    """
    cur = connection_db.cursor()
    cur.execute(UMLS_TABLE)
    cur.close()
    connection_db.commit()

def create_indications_table():
    INDICATIONS_TABLE="""
    CREATE TABLE indications (
    indication_id       INTEGER PRIMARY KEY, 
    cid_stereo          TEXT    NOT NULL
                                REFERENCES drug (cid_stereo),
    umls_id             TEXT    NOT NULL
                                REFERENCES umls (umls_id),
    method_of_detection TEXT
    );
    """
    cur = connection_db.cursor()
    cur.execute(INDICATIONS_TABLE)
    cur.close()
    connection_db.commit()

def create_indication_labels_table():
    INDICATION_LABELS_TABLE="""
    CREATE TABLE indication_labels (
    indication_id INTEGER,
    source_label  TEXT    COLLATE NOCASE
    );
    """
    cur = connection_db.cursor()
    cur.execute(INDICATION_LABELS_TABLE)
    cur.close()
    connection_db.commit()

def create_se_table():
    SIDE_EFFECTS_TABLE="""
    CREATE TABLE side_effects (
    se_id      INTEGER PRIMARY KEY,
    cid_stereo TEXT    REFERENCES drug (cid_flat) 
                       NOT NULL,
    umls_id    TEXT    NOT NULL
                       REFERENCES drug (cid_flat) 
    );
    """
    cur = connection_db.cursor()
    cur.execute(SIDE_EFFECTS_TABLE)
    cur.close()
    connection_db.commit()


def create_se_labels_table():
    SIDE_EFFECTS_LABELS_TABLE="""
    CREATE TABLE side_effects_labels (
    se_id           INTEGER,
    se_source_label TEXT    COLLATE NOCASE
    );
    """
    cur = connection_db.cursor()
    cur.execute(SIDE_EFFECTS_LABELS_TABLE)
    cur.close()
    connection_db.commit()

def create_se_freq_table():
    SIDE_EFFECT_FREQUENCY_TABLE="""
    CREATE TABLE side_effect_frequency (
    se_id            INTEGER REFERENCES side_effects (se_id),
    placebo          TEXT,
    frequency        TEXT,
    lower_bound_freq DECIMAL,
    upper_bound_freq DECIMAL
    );
    """
    cur = connection_db.cursor()
    cur.execute(SIDE_EFFECT_FREQUENCY_TABLE)
    cur.close()
    connection_db.commit()

def create_synonyms_table():
    SYNONYMS_TABLE="""
    CREATE TABLE synonyms (
    meddra_id   TEXT,
    umls_id     TEXT,
    meddra_term TEXT
    );
    """
    cur = connection_db.cursor()
    cur.execute(SYNONYMS_TABLE)
    cur.close()
    connection_db.commit()


# Functions to build new tables-------------------------------------------------------------------------------------------------------
def build_drug_table():
    cid_flats = get_cids()
    cur = connection_db.cursor()
    for flat in cid_flats:
        name = get_drug_name(flat) # get the drug name based on cid_flat
        for stereo in get_cid_stereos(flat): # for each stereo, insert the cid_flat and drug name
            insert_drug(cur, stereo, flat, name)
    cur.close()
    connection_db.commit()

def build_atc_table():
    cid_flats = get_cids()
    cur = connection_db.cursor()
    for flat in cid_flats:
        for atc in get_atc(flat):
        #atc = get_atc(flat)
            insert_atc(cur, flat, atc)
    cur.close()
    connection_db.commit()

def build_umls_table():
    # set up variables for returned values in get_info function
    umls_ids, concept_names = get_info()
    cur = connection_db.cursor()
    for umls, concept_name in zip(umls_ids, concept_names):
        insert_umls(cur, umls, concept_name) #insert the umls ids and the concept name with it
    cur.close()
    connection_db.commit()

def build_indications_table():
    # have indication id start at 1 and increment
    # cid, umls id, and method of detection taken from meddra_all_indications table
    cids, umls_ids, methods_detection = get_indication_info()
    cur = connection_db.cursor()
    for cid, umls, method in zip(cids, umls_ids, methods_detection):
        insert_indication(cur, cid, umls, method) # insert the information into the table
    cur.close()
    connection_db.commit()

def build_indications_indexes():
    create_indications_indexes = """
    CREATE INDEX indications_cid_stereo_idx ON indications (
    cid_stereo
    );
    CREATE INDEX indications_umls_id_idx ON indications (
    umls_id
    );
    CREATE INDEX indications_method_of_detection_idx ON indications (
    method_of_detection
    );
    CREATE INDEX indications_cid_stereo_umls_id_method_of_detection_idx ON indications (
    cid_stereo,
    umls_id,
    method_of_detection
    );
    """
    cur = connection_db.cursor()
    cur.executescript(create_indications_indexes)
    connection_db.commit()

def build_indication_labels_table():
    # get indication id, cid, umls id, and method of detection from indication table
    cids, umls_ids, methods_detection = get_indication_info()
    cur = connection_db.cursor()
    for cid, umls, method in zip(cids, umls_ids, methods_detection):
        # loop through this list and obtain the id and source label(s) associated with it
        indication_id = get_id(cid, umls, method)
        for source_label in get_source_labels(cid, umls, method):
            insert_indication_label(cur, indication_id, source_label) #insert the id and label into the table
    cur.close()
    connection_db.commit()

def build_se_table():
    # get cid_stereo and umls_id information and insert into table (along with an id number)
    cids_stereo, umls_ids = get_se_info()
    cur = connection_db.cursor()
    for cid, umls, in zip(cids_stereo, umls_ids):
        insert_se(cur, cid, umls) # insert information into the table
    cur.close()
    connection_db.commit()

def build_se_indexes():
    create_se_indexes = """
    CREATE INDEX side_effects_cid_stereo_idx ON side_effects (
    cid_stereo
    );
    CREATE INDEX side_effects_cid_stereo_umls_id_idx ON side_effects (
    cid_stereo,
    umls_id
    );
    CREATE INDEX side_effects_umls_id_idx ON side_effects (
    umls_id
    );
    """
    cur = connection_db.cursor()
    cur.executescript(create_se_indexes)
    connection_db.commit()

def build_se_labels_table():
    # get se_id, cid, and umls id from side effect table
    cids_stereo, umls_ids = get_se_info()
    cur = connection_db.cursor()
    for cid, umls in zip(cids_stereo, umls_ids):
        # loop through this list and obtain the se_id and source label(s) associated with it
        se_id = get_se_id(cid, umls)
        for se_source_label in get_se_source_label(cid, umls):
            insert_se_table(cur, se_id, se_source_label) # insert the se_id and label into the table
    cur.close()
    connection_db.commit()

def build_se_freq_table():
    # get cid_stereo and umls_id information
    cids_stereo, umls_ids = get_se_freq_info()
    cur = connection_db.cursor()
    cur_source = connection_source.cursor()
    for stereo, umls in zip(cids_stereo, umls_ids):
        # obtain the id as well as the other information(get the lists separately and then loop through at same time)
        se_id_freq = get_se_id_freq(stereo, umls)
        frequencies = get_frequency(stereo, umls)
        for placebo, freq, lower, upper in (frequencies):
            # insert the id, placebo, and frequency information into the table
            insert_se_freq_table(cur, se_id_freq, placebo, freq, lower, upper)
    cur.close()
    cur_source.close()
    connection_db.commit()
    connection_source.commit()

def build_synonyms_table():
    #get meddra id, umls id, and meddra term
    meddra_ids, umls_ids, meddra_terms = get_meddra_info()
    cur = connection_db.cursor()
    for meddra, umls, term in zip(meddra_ids, umls_ids, meddra_terms):
        insert_meddra(cur, meddra, umls, term)
    cur.close()
    connection_db.commit()



#------------------------------------ Create function to obtain data for drug table-------------------------------------------------------------
#Create functions for Drug Table and ATC Table--------------------------------------------------------------------------------------------------
def get_cids():
    cids=[]
    statement="""
    select cid_flat from drug_names
    union
    select cid_flat from drug_atc;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        cids.append(row['cid_flat'])
    return cids

def get_cid_stereos(cid):
    stereos = []
    statement="""
    select distinct cid_stereo from meddra_all_se where cid_flat = ?;
    """
    cur = connection_source.cursor()
    cur.execute(statement, (cid,))
    for row in cur.fetchall():
        stereos.append(row['cid_stereo'])
    return stereos

def get_atc(cid):
    atcs = []
    statement="""
    select atc from drug_atc where cid_flat = ?;
    """
    cur = connection_source.cursor()
    cur.execute(statement, (cid,))
    for row in cur.fetchall():
        atcs.append(row['atc'])
    return atcs

def get_drug_name(cid):
    statement="""
    select drug_name from drug_names where cid_flat = ?;
    """
    cur = connection_source.cursor()
    cur.execute(statement, (cid,))
    for row in cur.fetchall():
        return row['drug_name']

def insert_drug(cur, cid_stereo, cid_flat, name):
    statement="""
    insert into drug (cid_stereo, cid_flat, drug_name)
    values (?, ?, ?)
    """
    cur.execute(statement, (cid_stereo, cid_flat, name))

def insert_atc(cur, cid_flat, atc):
    statement="""
    insert into atc (cid_flat, atc)
    values (?, ?)
    """
    cur.execute(statement, (cid_flat, atc))


# Create functions to get the data needed for the umls table------------------------------------------------------------------------------
def get_info():
    umls_ids=[]
    concept_names=[]
    statement="""
    select distinct umls_se as umls_id, side_effect_name as concept_name from meddra_all_se where umls_se is not null
    union
    select distinct umls_on_label as umls_id, side_effect_name as concept_name from meddra_all_se where umls_se is null
    union
    select distinct umls_meddra as umls_id, meddra_concept_name as concept_name from meddra_all_indications where umls_meddra is not null
    union
    select distinct umls_on_label as umls_id, meddra_concept_name as concept_name from meddra_all_indications where umls_meddra is null
    union
    select distinct umls_meddra as umls_id, side_effect as concept_name from meddra_freq where umls_meddra is not null
    union
    select distinct umls_on_label as umls_id, side_effect as concept_name from meddra_freq where umls_meddra is null
    union
    select distinct umls_se as umls_id, side_effect_name as concept_name from meddra_all_label_se where umls_se is not null
    union
    select distinct umls_on_label as umls_id, side_effect_name as concept_name from meddra_all_label_se where umls_se is null
    union
    select distinct umls_meddra as umls_id, meddra_concept_name as concept_name from meddra_all_label_indications where umls_meddra is not null
    union
    select distinct umls_on_label as umls_id, meddra_concept_name as concept_name from meddra_all_label_indications where umls_meddra is null;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        # append the umls ids to the umls id list
        umls_ids.append(row['umls_id'])
        # append the concept names to the concept name list
        concept_names.append(row['concept_name'])
    return umls_ids, concept_names

def insert_umls(cur, umls, concept_name):
    statement = """
    insert into umls (umls_id, concept_name)
    values (?, ?)
    """
    cur.execute(statement, (umls, concept_name))


# Create functions to obtain data needed for the indications table------------------------------------------------------------------------------
def get_indication_info():
    cids = []
    umls_ids = []
    methods_detection = []
    statement="""
    select distinct cid_stereo, umls_meddra as umls_id, method_of_detection from meddra_all_label_indications where umls_meddra is not null
    union
    select distinct cid_stereo, umls_on_label as umls_id, method_of_detection from meddra_all_label_indications where umls_meddra is null;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        # append the list of cids, umls_ids, and the methods of detection
        cids.append(row['cid_stereo'])
        umls_ids.append(row['umls_id'])
        methods_detection.append(row['method_of_detection'])
    return cids, umls_ids, methods_detection

def insert_indication(cur, cid, umls, method):
    statement="""
    insert into indications (cid_stereo, umls_id, method_of_detection)
    values (?, ?, ?)
    """
    cur.execute(statement, (cid, umls, method))


#Create functions needed for indication_labels table----------------------------------------------------------------------------------------
def get_id(cid, umls, method):
    statement="""
    select indication_id from indications 
    where cid_stereo = ? and umls_id = ? and method_of_detection = ?;
    """
    cur = connection_db.cursor()
    cur.execute(statement,(cid, umls, method))
    for row in cur.fetchall():
        return row['indication_id']

def get_source_labels(cid, umls, method):
    label = []
    statement="""
    select distinct source_label from meddra_all_label_indications
    where cid_stereo = ? and umls_meddra = ? and method_of_detection = ?;
    """
    cur = connection_source.cursor()
    cur.execute(statement, (cid, umls, method))
    for row in cur.fetchall():
        label.append(row['source_label'])
    return label

def insert_indication_label(cur, indication_id, source_label):
    statement="""
    insert into indication_labels (indication_id, source_label)
    values ( ?, ?)
    """
    cur.execute(statement, (indication_id, source_label))


# Create functions needed for side_effects table--------------------------------------------------------------------------------------------
def get_se_info():
    cids_stereo = []
    umls_ids = []
    statement="""
    select distinct cid_stereo, umls_se as umls_id from meddra_all_se where umls_se is not null
    union
    select distinct cid_stereo, umls_on_label as umls_id from meddra_all_se where umls_se is null;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        # append the list of cid_stereo and umls_ids
        cids_stereo.append(row['cid_stereo'])
        umls_ids.append(row['umls_id'])
    return cids_stereo, umls_ids

def insert_se(cur, cid, umls):
    statement="""
    insert into side_effects (cid_stereo, umls_id)
    values (?, ?)
    """
    cur.execute(statement, (cid, umls))


# Create functions needed for side_effects labels table-------------------------------------------------------------------------------------
def get_se_id(cid, umls):
    statement="""
    select se_id from side_effects
    where cid_stereo = ? and umls_id = ?;
    """
    cur = connection_db.cursor()
    cur.execute(statement, (cid, umls))
    for row in cur.fetchall():
        return row['se_id']

def get_se_source_label(cid, umls):
    se_label = []
    statement="""
    select distinct source_label from meddra_all_label_se
    where cid_stereo = ? and umls_se = ?;
    """
    cur = connection_source.cursor()
    cur.execute(statement, (cid, umls))
    for row in cur.fetchall():
        se_label.append(row['source_label'])
    return se_label

def insert_se_table(cur, se_id, se_source_label):
    statement="""
    insert into side_effects_labels (se_id, se_source_label)
    values (?, ?)
    """
    cur.execute(statement, (se_id, se_source_label))


# Create functions needed for side_effect_frequency table------------------------------------------------------------------------------------
def get_se_freq_info():
    cids_stereo = []
    umls_ids = []
    statement="""
    select distinct cid_stereo, umls_meddra as umls_id from meddra_freq where umls_meddra is not null
    union
    select distinct cid_stereo, umls_on_label as umls_id from meddra_freq where umls_meddra is null;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        # append the list of cid_stereo and umls_ids
        cids_stereo.append(row['cid_stereo'])
        umls_ids.append(row['umls_id'])
    return cids_stereo, umls_ids

def get_se_id_freq(stereo, umls):
    statement="""
    select se_id from side_effects where cid_stereo = ? and umls_id = ?;
    """
    cur = connection_db.cursor()
    cur.execute(statement, (stereo, umls))
    for row in cur.fetchall():
        return row['se_id']

def get_frequency(stereo, umls):
    freq = []
    statement="""
    select placebo, frequency, lower_bound_freq, upper_bound_freq from meddra_freq where
    cid_stereo = ? and umls_meddra = ?;
    """
    cur = connection_source.cursor()
    cur.execute(statement, (stereo, umls))
    for row in cur.fetchall():
        freq.append((row['placebo'], row['frequency'], row['lower_bound_freq'], row['upper_bound_freq']))
    return freq

def insert_se_freq_table(cur, se_id_freq, placebo, freq, lower, upper):
    statement="""
    insert into side_effect_frequency (se_id, placebo, frequency, lower_bound_freq, upper_bound_freq)
    values (?, ?, ?, ?, ?)
    """
    cur.execute(statement, (se_id_freq, placebo, freq, lower, upper))


# Create functions needed for Synonyms table-----------------------------------------------------------------------------------------------
def get_meddra_info():
    meddra_ids = []
    umls_ids = []
    meddra_terms = []
    statement="""
    select distinct meddra_id, umls_on_label, side_effect from meddra;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        # append the three lists
        meddra_ids.append(row['meddra_id'])
        umls_ids.append(row['umls_on_label'])
        meddra_terms.append(row['side_effect'])
    return meddra_ids, umls_ids, meddra_terms

def insert_meddra(cur, meddra, umls, term):
    statement="""
    insert into synonyms (meddra_id, umls_id, meddra_term)
    values (?, ?, ?)
    """
    cur.execute(statement, (meddra, umls, term))


if __name__ == "__main__":
    # Call functions to create and build the new tables
    create_drug_table()
    build_drug_table()
    print("build_drug_table")
    create_atc_table()
    build_atc_table()
    print("build_atc_table")
    create_umls_table()
    build_umls_table()
    print("build_umls_table")
    create_indications_table()
    build_indications_table()
    build_indications_indexes()
    print("build_indications_table")
    create_indication_labels_table()
    build_indication_labels_table()
    print("build_indication_labels_table")
    create_se_table()
    build_se_table()
    build_se_indexes()
    print("build_se_table")
    create_se_labels_table()
    build_se_labels_table()
    print("build_se_labels_table")
    create_se_freq_table()
    build_se_freq_table()
    print("build_se_freq_table")
    create_synonyms_table()
    build_synonyms_table()
    print("build_synonyms_table")