import sqlite3
import re
import pandas as pd
from collections import defaultdict
import os
import math


######################  
# PATHS
db_folder = 'data'


######################  
# DATABASE CONNECTION
db_connection = sqlite3.connect("data/reactome.sqlite", check_same_thread=False)
db_connection.row_factory = sqlite3.Row
DO_IF_EXISTS = 'append'


####################### 
# Extract, Transform and Load into PATHWAY_MAP table
# (A table parent_pathway and child_pathway)
def etl_pathway_relation():
    create_pathway_relation_table()
    df = pd.read_csv('data/download/ReactomePathwaysRelation.txt', sep="\t", header=None, names=['parent_pathway', 'child_pathway'])
    df['parent_pathway'] = df['parent_pathway'].apply(lambda x: 'pathway:' + str(x))
    df['child_pathway']  = df['child_pathway'].apply(lambda x: 'pathway:' + str(x))
    df.to_sql("PATHWAY_MAP", db_connection, if_exists=DO_IF_EXISTS, index=False)  # copy the data into the table


####################### 
# Extract, Transform and Load into PATHWAY table
# R-BTA-73843\5-Phosphoribose 1-diphosphate biosynthesis\Bos taurus
#'pathway_stable_identifier', 'pathway','species'
def etl_pathway():
    create_pathway_table()
    df = pd.read_csv('data/download/ReactomePathways.txt', sep="\t", header=None, names=['pathway_stable_identifier', 'pathway','species'])
    df['pathway_stable_identifier'] = df['pathway_stable_identifier'].apply(lambda x: 'pathway:' + str(x))
    df.to_sql("PATHWAY", db_connection, if_exists=DO_IF_EXISTS, index=False)  # copy the data into the table


####################### 
# Extract, Transform and Load into ProteinRoleReaction table
# A0A023GPK8 \ input \ R-DME-373714
# uniprot_id, role, pathway_stable_identifier
#
def etl_protein_role_reactions():
    create_protein_role_reaction_table()
    protein_role_df = pd.read_csv('data/download/ProteinRoleReaction.txt', sep="\t", header=None, names=['uniprot_id', 'role', 'pathway_stable_identifier'])
    protein_role_df['pathway_stable_identifier'] = protein_role_df['pathway_stable_identifier'].apply(lambda x: 'pathway:' + str(x))
    protein_role_df.to_sql("PROTEIN_ROLE_REACTIONS", db_connection, if_exists=DO_IF_EXISTS, index=False)  # copy the data into the table


####################### 
# Extract, Transform and Load into PUBMED table
# R-HSA-9626046 \ 26118642
# 'pathway_stable_identifier', 'PubMed_citation_identifier'
def etl_pubmed():
    create_pubmed_table()
    prefix = 'PMID:'
    pubmed_df = pd.read_csv('data/download/ReactionPMIDS.txt', sep="\t", header=None, names=['pathway_stable_identifier', 'PubMed_citation_identifier'])
    pubmed_df['pathway_stable_identifier'] = pubmed_df['pathway_stable_identifier'].apply(lambda x: 'pathway:' + str(x))
    pubmed_df['PubMed_citation_identifier'] = pubmed_df['PubMed_citation_identifier'].apply(lambda x: prefix + str(x))
    pubmed_df.to_sql("PUBMED", db_connection, if_exists=DO_IF_EXISTS, index=False)  # copy the data into the table


####################### 
# Extract, Transform and Load into REACTOME_ID_MAP table
# R-HSA-9626046 \ 26118642
# 'pathway_stable_identifier', 'old_identifier'
#
def etl_reactome_ids():
    reactome_id_df = pd.read_csv('data/download/reactome_stable_ids.txt', sep="\t", names=['stable_identifier', 'old_identifier'])
    reactome_id_df = reactome_id_df[2:] #take the data less the 2 header rows
########################## TEMPORARY COMMENT ####################################
################# LET pathway_stable_identifier HAVE NO PREFIX ##################
#    reactome_id_df['pathway_stable_identifier'] = reactome_id_df['pathway_stable_identifier'].apply(lambda x: 'pathway:' + str(x))
#   parse out the comma-delimited strings into separate rows in the 'old_identifier' column
    reactome_id_df = reactome_id_df.drop('old_identifier', axis=1).join(reactome_id_df['old_identifier']
                                   .str
                                   .split(',', expand=True)
                                   .stack()
                                   .reset_index(level=1, drop=True)
                                   .rename('old_identifier')).reset_index(drop=True)
    create_reactome_id_map_table()
    reactome_id_df.to_sql("REACTOME_ID_MAP", db_connection, if_exists=DO_IF_EXISTS, index=False)  # copy the data into the table


 ####################### 
 # CREATE PATHWAY_RELATION TABLE
def create_pathway_relation_table():
       cursor = db_connection.cursor()
       cursor.execute('''CREATE TABLE PATHWAY_MAP(parent_pathway TEXT, child_pathway TEXT)''')
       db_connection.commit()

 ####################### 
 # CREATE PROTEIN_ROLE_REACTIONS TABLE
def create_protein_role_reaction_table():
       cursor = db_connection.cursor()
       cursor.execute('''CREATE TABLE PROTEIN_ROLE_REACTIONS(uniprot_id TEXT,
                                                                           role TEXT, 
                                                                           pathway_stable_identifier TEXT,
                             FOREIGN KEY (pathway_stable_identifier) REFERENCES PATHWAY(pathway_stable_identifier) )''')
       db_connection.commit()


 ####################### 
 # CREATE PUBMED TABLE
def create_pubmed_table():
       cursor = db_connection.cursor()
       cursor.execute('''CREATE TABLE PUBMED(pathway_stable_identifier TEXT, PubMed_citation_identifier TEXT, FOREIGN KEY (pathway_stable_identifier) REFERENCES PATHWAY(pathway_stable_identifier) )''')
       db_connection.commit()


 ####################### 
 # CREATE reactome_id_map TABLE
def create_reactome_id_map_table():
       cursor = db_connection.cursor()
    #    cursor.execute('''DROP TABLE IF EXISTS REACTOME_ID_MAP''')
       db_connection.commit()
       cursor.execute('''CREATE TABLE REACTOME_ID_MAP(stable_identifier TEXT, pathway_stable_identifier TEXT,  reactome_stable_identifier TEXT, old_identifier TEXT, FOREIGN KEY (pathway_stable_identifier) REFERENCES PATHWAY(pathway_stable_identifier) )''')
       db_connection.commit()


 ####################### 
 # CREATE PATHWAY TABLE
def create_pathway_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS PATHWAY''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE PATHWAY(pathway_stable_identifier TEXT PRIMARY KEY, pathway TEXT, species TEXT)''')
    db_connection.commit()


def create_indexes():
    cursor = db_connection.cursor()
    cursor.execute('''CREATE INDEX index_pathway_map_1 ON PATHWAY_MAP (parent_pathway)''')
    cursor.execute('''CREATE INDEX index_pathway_map_2 ON PATHWAY_MAP (child_pathway)''')
    cursor.execute('''CREATE INDEX index_protein_role_rxn_1 ON PROTEIN_ROLE_REACTIONS(uniprot_id)''')
    cursor.execute('''CREATE INDEX index_protein_role_rxn_2 ON PROTEIN_ROLE_REACTIONS(pathway_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_pubmed_1 ON PUBMED(PubMed_citation_identifier)''')
    cursor.execute('''CREATE INDEX index_pubmed_2 ON PUBMED(pathway_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_reactome_id_map_1 ON REACTOME_ID_MAP(reactome_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_reactome_id_map_2 ON REACTOME_ID_MAP(pathway_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_reactome_id_map_3 ON REACTOME_ID_MAP(stable_identifier)''')
    cursor.execute('''CREATE INDEX index_pathway_1 ON PATHWAY (pathway)''')
    cursor.execute('''CREATE INDEX index_pathway_2 ON PATHWAY (pathway_stable_identifier)''')
    db_connection.commit()  


def main():
    etl_pathway()
    etl_protein_role_reactions()
    etl_pubmed()   
    etl_reactome_ids()
    etl_pathway_relation()
    create_indexes()


if __name__ == '__main__':
    main()

