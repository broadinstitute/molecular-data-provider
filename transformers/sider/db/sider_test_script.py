import sys
import sqlite3

import pandas as pd
#import numpy as np

connection_source = sqlite3.connect("data/sider_source.sqlite", check_same_thread=False)
connection_db = sqlite3.connect("data/sider.sqlite", check_same_thread=False)
connection_source.row_factory = sqlite3.Row
connection_db.row_factory = sqlite3.Row 

# Create functions to check the count for each table (so data from sider db matches data from sider_source db)-----------------------
#ATC counts----------------------------------------------------------------------------------------------------------------------
def get_db_atc_count():
    statement="""
    select count (atc) as count from atc;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_atc_count():
    statement="""
    select count (atc) as count from drug_atc;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_atc():
    if get_db_atc_count() != get_source_atc_count():
        print("ATC: oh no!")
    else:
        print("ATC: yay!")

#CID_STEREO counts---------------------------------------------------------------------------------------------------------------
def get_db_cid_stereo_count():
    statement="""
    select count (cid_stereo) as count from drug;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_cid_stereo_count():
    statement="""
    select count (distinct cid_stereo) as count from meddra_all_se;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_drug_cid_stereo():
    if get_db_cid_stereo_count() != get_source_cid_stereo_count():
        print("DRUG (cid_stereo): oh no!")
    else:
        print("DRUG (cid_stereo): yay!")

#DRUG NAME counts---------------------------------------------------------------------------------------------------------------------
def get_db_drug_name_count(): # WILL COME BACK TO THIS LATER
    statement="""
    select count (distinct drug_name collate binary) as count from drug;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_db_drug_name(): # WILL COME BACK TO THIS LATER
    statement="""
    select distinct drug_name from drug;
    """
    names = set()
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        names.add(row['drug_name'])
    return names

def get_source_drug_name_count():
    statement="""
    select count (distinct drug_name collate binary) as count from drug_names;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_drug_name():
    statement="""
    select distinct drug_name from drug_names;
    """
    names = []
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        names.append(row['drug_name'])
    return names

def test_drug_name():
    if get_db_drug_name_count() != get_source_drug_name_count():
        print("DRUG (name): oh no!")
        print("db: ", get_db_drug_name_count(), "source: ", get_source_drug_name_count() )
        db_names = get_db_drug_name() 
        for name in get_source_drug_name():
            if name not in db_names:
                print("missing: " + name)
    else:
        print("DRUG (name): yay!")

# INDICATIONS TABLE counts------------------------------------------------------------------------------------------------------
def get_db_indications_count():
    statement="""
    select count (*) as count from (select distinct cid_stereo, umls_id, method_of_detection from indications);
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_indications_count():
    statement="""
    select count (*) as count from (select distinct cid_stereo, umls_meddra as umls_id, method_of_detection from meddra_all_label_indications where umls_meddra is not null
    union
    select distinct cid_stereo, umls_on_label as umls_id, method_of_detection from meddra_all_label_indications where umls_meddra is null);
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_indications():
    if get_db_indications_count() != get_source_indications_count():
        print("INDICATIONS: oh no!")
    else:
        print("INDICATIONS: yay!")

# INDICATION LABEL TABLE counts------------------------------------------------------------------------------------------------
def get_db_ind_label_count():
    statement="""
    select count (distinct source_label) as count from indication_labels;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_ind_label_count():
    statement="""
    select count (distinct source_label) as count from meddra_all_label_indications;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_indications_label():
    if get_db_ind_label_count() != get_source_ind_label_count():
        print("INDICATION LABELS: oh no!")
    else:
        print("INDICATION LABEL: yay!")

# SIDE EFFECT TABLE counts-----------------------------------------------------------------------------------------------------
def get_db_se_count():
    statement="""
    select count (*) as count from (select cid_stereo, umls_id from side_effects);
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_se_count():
    statement="""
    select count (*) as count from (select distinct cid_stereo, umls_se from meddra_all_se where umls_se is not null
    union
    select distinct cid_stereo, umls_on_label as umls_se from meddra_all_se where umls_se is null);
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_side_effect():
    if get_db_se_count() != get_source_se_count():
        print("SIDE EFFECTS: oh no!")
    else:
        print("SIDE EFFECTS: yay!")

# SIDE EFFECT LABEL TABLE counts------------------------------------------------------------------------------------------------
def get_db_se_label_count():
    statement="""
    select count (distinct se_source_label) as count from side_effects_labels;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_se_label_count():
    statement="""
    select count (distinct source_label) as count from meddra_all_label_se;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_se_label():
    if get_db_se_label_count() != get_source_se_label_count():
        print("SIDE EFFECT LABEL: oh no!")
    else:
        print("SIDE EFFECT LABEL: yay!")

# SYNONYMS TABLE (meddra_id) counts---------------------------------------------------------------------------------------------------------
def get_db_synonyms_id_count():
    statement="""
    select count (distinct meddra_id) as count from synonyms;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_synonyms_id_count():
    statement="""
    select count(distinct meddra_id) as count from meddra;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_synonyms_id():
    if get_db_synonyms_id_count() != get_source_synonyms_id_count():
        print("SYNONYMS (meddra_id): oh no!")
    else:
        print("SYNONYMS (meddra_id): yay!")

# SYNONYMS TABLE (meddra_term) counts---------------------------------------------------------------------------------------
def get_db_synonyms_term_count():
    statement="""
    select count (distinct meddra_term) as count from synonyms;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_synonyms_term_count():
    statement="""
    select count(distinct side_effect) as count from meddra;
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_synonyms_term():
    if get_db_synonyms_term_count() != get_source_synonyms_term_count():
        print("SYNONYMS (meddra_term): oh no!")
    else:
        print("SYNONYMS (meddra_term): yay!")

# UMLS TABLE count--------------------------------------------------------------------------------------------------------------
def get_db_umls_count():
    statement="""
    select count (*) as count from (select distinct umls_id, concept_name from umls);
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_umls_count():
    statement="""
    select count (*) as count from (select distinct umls_se, side_effect_name from meddra_all_se
    union 
    select distinct umls_meddra, meddra_concept_name from meddra_all_indications
    union
    select distinct umls_meddra, side_effect from meddra_freq
    union
    select distinct umls_se, side_effect_name from meddra_all_label_se
    union
    select distinct umls_meddra, meddra_concept_name from meddra_all_label_indications);
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_umls():
    if get_db_umls_count() != get_source_umls_count():
        print("UMLS: oh no!")
    else:
        print("UMLS: yay!")

# UMLS ID TABLE count-----------------------------------------------------------------------------------------------------------
def get_db_umls_id_count():
    statement="""
    select count (distinct umls_id) as count from umls;
    """
    cur = connection_db.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def get_source_umls_id_count():
    statement="""
    select count (*) as count from (select distinct umls_se from meddra_all_se
    union 
    select distinct umls_meddra from meddra_all_indications
    union
    select distinct umls_meddra from meddra_freq
    union
    select distinct umls_se from meddra_all_label_se
    union
    select distinct umls_meddra from meddra_all_label_indications);
    """
    cur = connection_source.cursor()
    cur.execute(statement)
    for row in cur.fetchall():
        return row['count']

def test_umls_id():
    if get_db_umls_id_count() != get_source_umls_id_count():
        print("UMLS_ID: oh no!")
    else:
        print("UMLS_ID: yay!")


if __name__ == "__main__":
    # run tests
    test_atc()
    test_drug_cid_stereo()
    test_drug_name() 
    test_indications()
    test_indications_label() 
    test_side_effect() 
    test_se_label()
    test_synonyms_id()
    test_synonyms_term()
    test_umls()
    # test_umls_id()
    