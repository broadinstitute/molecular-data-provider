import sys
import json
import sqlite3
import pandas as pd

db_connection = sqlite3.connect("data/reactome.sqlite", check_same_thread=False)
db_connection.row_factory = sqlite3.Row


################################################################################
# Gather all the Reactomes and Pathways
# 
def analysis_pathways():
    pathway_set = set()
    reactome_set = set()

    collect_complex(reactome_set)
    collect_complex_participant(reactome_set)
    collect_complex_pathway_map(pathway_set, reactome_set)
    collect_interaction(pathway_set, reactome_set)
    #collect_interaction_map(pathway_set)
#   note: INTERACTION_MAP has no reactome/pathway identifiers
    collect_interactor(reactome_set)
    collect_interactor_id(reactome_set)
    collect_interactor_name(reactome_set)
    collect_pathway(pathway_set)
    collect_pathway_map(pathway_set)
    collect_physical_entity(reactome_set)
    collect_protein_roles_rxn(pathway_set)
    collect_pubmed(pathway_set)
    collect_reaction(pathway_set)
    collect_reaction_map(pathway_set,reactome_set)

    # identify the reactomes and pathways in the REACTOME_ID_MAP table
    update_reactome_id_map(pathway_set, reactome_set)


############################################################
#   
def collect_complex(reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT complex_stable_identifier
                      FROM COMPLEX''')
    for row in cursor.fetchall():
        reactome_set.add(str(row['complex_stable_identifier']).split(':')[1])


############################################################
#   
def collect_complex_participant(reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT complex_stable_identifier, complex_participant_identifier
                      FROM COMPLEX_PARTICIPANT''')
    for row in cursor.fetchall():
        reactome_set.add(str(row['complex_stable_identifier']).split(':')[1])
        if 'reactome:' in str(row['complex_participant_identifier']):
            reactome_set.add(str(row['complex_participant_identifier']).split(':')[1])


############################################################
#   
def collect_complex_pathway_map(pathway_set,reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT complex_stable_identifier, pathway_stable_identifier, top_level_pathway
                      FROM COMPLEX_PATHWAY_MAP''')
    for row in cursor.fetchall():
        reactome_set.add(str(row['complex_stable_identifier']).split(':')[1])
        pathway_set.add(str(row['pathway_stable_identifier']).split(':')[1])
        pathway_set.add(str(row['top_level_pathway']).split(':')[1])


############################################################
#     
def collect_interaction(pathway_set, reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT entity_stable_identifier_interactor_A,
                             entity_stable_identifier_interactor_B
                      FROM INTERACTION''')
# parsing the retrieved data
    for row in cursor.fetchall():
        if len(row['entity_stable_identifier_interactor_A']) > 0:
            reactome_set.add(str(row['entity_stable_identifier_interactor_A']).split(':')[1])
        if len(row['entity_stable_identifier_interactor_B']) > 0:
            reactome_set.add(str(row['entity_stable_identifier_interactor_B']).split(':')[1])



############################################################
#     
def collect_interaction_map(pathway_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT interaction_annotation
                      FROM INTERACTION_MAP''')
    for row in cursor.fetchall():
        if row['interaction_annotation'] != None and len(row['interaction_annotation']) > 1:
            pathway_set.add(str(row['interaction_annotation']).split(':')[1])


############################################################
#   
def collect_interactor(reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT entity_stable_identifier
                      FROM INTERACTOR''')
    for row in cursor.fetchall():
        reactome_set.add(str(row['entity_stable_identifier']).split(':')[1])


############################################################
#   
def collect_interactor_id(reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT entity_stable_identifier
                      FROM INTERACTOR_ID''')
    for row in cursor.fetchall():
        reactome_set.add(str(row['entity_stable_identifier']).split(':')[1])


############################################################
#   
def collect_interactor_name(reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT entity_stable_identifier
                      FROM INTERACTOR_NAME''')
    for row in cursor.fetchall():
        reactome_set.add(str(row['entity_stable_identifier']).split(':')[1])


############################################################
#   
def collect_pathway(pathway_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT pathway_stable_identifier
                      FROM PATHWAY''')
    for row in cursor.fetchall():
        pathway_set.add(str(row['pathway_stable_identifier']).split(':')[1])


############################################################   
#   
def collect_pathway_map(pathway_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT parent_pathway, child_pathway
                      FROM PATHWAY_MAP''')
    for row in cursor.fetchall():
        pathway_set.add(str(row['parent_pathway']).split(':')[1])
        pathway_set.add(str(row['child_pathway']).split(':')[1])


############################################################
#   
def collect_physical_entity(reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT entity_stable_identifier
                      FROM PHYSICAL_ENTITY''')
    for row in cursor.fetchall():
        reactome_set.add(str(row['entity_stable_identifier']).split(':')[1]) 


############################################################
#   
def collect_protein_roles_rxn(pathway_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT pathway_stable_identifier
                      FROM PROTEIN_ROLE_REACTIONS''')
    for row in cursor.fetchall():
        pathway_set.add(str(row['pathway_stable_identifier']).split(':')[1])


############################################################
#   
def collect_pubmed(pathway_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT pathway_stable_identifier
                      FROM PUBMED''')
    for row in cursor.fetchall():
        pathway_set.add(str(row['pathway_stable_identifier']).split(':')[1])     


############################################################
#   
def collect_reaction(pathway_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT pathway_stable_identifier
                      FROM REACTION''')
    for row in cursor.fetchall():
        pathway_set.add(str(row['pathway_stable_identifier']).split(':')[1]) 


############################################################
#   
def collect_reaction_map(pathway_set, reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT pathway_stable_identifier, entity_stable_identifier
                      FROM REACTION_MAP''')
    for row in cursor.fetchall():
        pathway_set.add(str(row['pathway_stable_identifier']).split(':')[1]) 
        reactome_set.add(str(row['entity_stable_identifier']).split(':')[1]) 


###############################################################
# 
def update_reactome_id_map(pathway_set, reactome_set):
    cursor = db_connection.cursor()
    cursor.execute('''SELECT DISTINCT stable_identifier
                      FROM REACTOME_ID_MAP''')
    for row in cursor.fetchall():
        if row['stable_identifier'] in pathway_set:
            # add to pathway_stable_identifier column
            sql = "UPDATE REACTOME_ID_MAP SET pathway_stable_identifier = '{}' WHERE stable_identifier = '{}' ".format('pathway:' + str(row['stable_identifier']), str(row['stable_identifier']))
            cursor.execute( sql)

        if row['stable_identifier'] in reactome_set:
            sql = "UPDATE REACTOME_ID_MAP SET reactome_stable_identifier = '{}' WHERE stable_identifier = '{}' ".format('reactome:' + str(row['stable_identifier']), str(row['stable_identifier']))
            cursor.execute( sql)
    db_connection.commit()   


###############################################################
# Use the values of REACTOME_ID_MAP's pathway_stable_identifier & reactome_stable_identifier
# to determine whether INTERACTION's interaction_identifier values are pathway or reactome.
#
def update_interaction():
    cursor = db_connection.cursor()
    cursor.execute('''SELECT DISTINCT interaction_id, interaction_identifier
                      FROM INTERACTION''')
    for row in cursor.fetchall():
            id = row['interaction_id']
            sql = "SELECT DISTINCT pathway_stable_identifier FROM REACTOME_ID_MAP WHERE stable_identifier = '{}' ".format(str(row['interaction_identifier']).split(':')[1]) 
            cursor.execute(sql)
            for row_1 in cursor.fetchall():
                if row_1['pathway_stable_identifier'] != None:
                    sql = "UPDATE INTERACTION SET interaction_identifier = '{}' WHERE interaction_id = '{}' ".format(row_1['pathway_stable_identifier'], id)
                    cursor.execute( sql)
    db_connection.commit()


def main():
    analysis_pathways()
    update_interaction()

if __name__ == '__main__':
    main()