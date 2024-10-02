import sys
import re
import sqlite3
import math
import pandas as pd
import requests
import json
request_headers = {}

db_connection = sqlite3.connect("data/reactome.sqlite", check_same_thread=False)
db_connection.row_factory = sqlite3.Row

################################################################################
# Populate INTERACTION Table
def etl_interaction():
    interaction_file_df = pd.read_csv('data/download/reactome.homo_sapiens.interactions.psi-mitab.txt', dtype = str, sep="\t")
    # Modify the dataframe
    interaction_file_df['interaction_id'] = interaction_file_df.index + 1  # Add a column of auto-incremented primary key index

    interaction_file_df.to_csv('data/tmp/indexed_interaction_map_df.csv', sep='\t', encoding='utf-8')


    # Add entity_stable_identifier column with value from the first ID in 'Alt. ID(s) interactor A" (to be used in INTERACTOR Table)
    interaction_file_df['entity_stable_identifier_interactor_A'] = interaction_file_df['Alt. ID(s) interactor A'].apply(get_entity_stable_id)
    interaction_file_df['entity_stable_identifier_interactor_B'] = interaction_file_df['Alt. ID(s) interactor B'].apply(get_entity_stable_id)
    interaction_table_df = interaction_file_df[ ['interaction_id', 'entity_stable_identifier_interactor_A', 'entity_stable_identifier_interactor_B','Interaction detection method(s)', 'Publication 1st author(s)', 
                    'Publication Identifier(s)', 'Interaction type(s)', 'Source database(s)', 'Interaction identifier(s)',
                    'Confidence value(s)', 'Expansion method(s)', 'Biological role(s) interactor A', 'Biological role(s) interactor B',
                    'Experimental role(s) interactor A','Experimental role(s) interactor B','Host organism(s)'
                    ,'Interaction parameter(s)', 'Negative', 'Feature(s) interactor A', 'Feature(s) interactor B', 'Stoichiometry(s) interactor A', 'Stoichiometry(s) interactor B',
                    'Identification method participant A' ] ]
    column_values = list(interaction_table_df.itertuples(index=False, name=None))

#### POPULATE INTERACTION Table
    cursor = db_connection.cursor()
    create_interaction_table()  
    for i in range(0, interaction_table_df.shape[0]):
        cursor.execute('''INSERT INTO INTERACTION (interaction_id, entity_stable_identifier_interactor_A, entity_stable_identifier_interactor_B, interaction_detection_method, publication_first_author, publication_identifier,
        interaction_type, source_database, interaction_identifier, confidence_value, expansion_method, biological_role_interactor_A, 
        biological_role_interactor_B, experimental_role_interactor_A, experimental_role_interactor_B, host_organism,
        interaction_parameter, negative, feature_interactor_A, feature_interactor_B, stoichiometry_interactor_A, stoichiometry_interactor_B, 
        identification_method
        ) VALUES(?,?, ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', column_values[i])
    db_connection.commit()
#### POPULATE INTERACTION Table  
    return interaction_file_df


#################################################################
# Find the reactome identifier in a string
#
def get_entity_stable_id(x):
    found = False
    entity_stable_id = ''
    alt_id_list = x.split('|')
    for alt_id in alt_id_list:
        if 'reactome' in alt_id and not found:
            entity_stable_id = alt_id
            found = True
    return entity_stable_id


################################################################################
# Populate INTERACTOR Table
def etl_interactor(interaction_file_df):
    create_interactor_table()
    interactor_id_set = set()
    # For interactor A
    interactor_df = interaction_file_df[ ['#ID(s) interactor A', 'entity_stable_identifier_interactor_A', 'Taxid interactor A', 'Type(s) interactor A',
                                     'Xref(s) interactor A', 'Annotation(s) interactor A']]   
    interactor_df_copy =  interactor_df.copy()    # Use copy() to avoid "SettingWithCopyWarning"                                                              
    interactor_df_copy['entity_stable_identifier_interactor_A'] = interactor_df.apply(lambda x: x['#ID(s) interactor A'] if x['entity_stable_identifier_interactor_A']=='' else x['entity_stable_identifier_interactor_A'], axis=1)  
    interactor_df = interactor_df_copy
    column_values = list(interactor_df.itertuples(index=False, name=None))

    # For interactor B
    interactor_df_B = interaction_file_df[ ['ID(s) interactor B', 'entity_stable_identifier_interactor_B', 'Taxid interactor B', 'Type(s) interactor B',
                                     'Xref(s) interactor B', 'Annotation(s) interactor B']]
    interactor_df_B_copy =  interactor_df_B.copy()    # Use copy() to avoid "SettingWithCopyWarning"                                 
    interactor_df_B_copy['entity_stable_identifier_interactor_B'] = interactor_df_B.apply(lambda x: x['ID(s) interactor B'] if x['entity_stable_identifier_interactor_B']=='' else x['entity_stable_identifier_interactor_B'], axis=1)
    interactor_df_B = interactor_df_B_copy
    column_values_B = list(interactor_df_B.itertuples(index=False, name=None))

#### TO POPULATE INTERACTOR Table
    cursor = db_connection.cursor()
    for i in range(0, interactor_df.shape[0]):
        
        if not column_values[i][1] in interactor_id_set:  # if 'entity_stable_identifier_interactor_A' was not already saved to INTERACTOR table
            cursor.execute('''INSERT INTO INTERACTOR (interactor_id, entity_stable_identifier, interactor_taxid, 
                        interactor_type, interactor_xref, interactor_annotations) 
                        VALUES(?,?,?,?,?,?)''', column_values[i])
            interactor_id_set.add(column_values[i][1])

        if not column_values_B[i][1] in interactor_id_set: # if 'entity_stable_identifier_interactor_A' was not already saved to INTERACTOR table
            cursor.execute('''INSERT INTO INTERACTOR (interactor_id, entity_stable_identifier, interactor_taxid, 
                        interactor_type, interactor_xref, interactor_annotations) 
                        VALUES(?,?,?,?,?,?)''', column_values_B[i])
            interactor_id_set.add(column_values_B[i][1])
    db_connection.commit()
#### POPULATE INTERACTOR Table


################################################################################
# Populate INTERACTOR_ID Table
#  (entity_stable_identifier & alt_id_interactor)
def etl_interactor_id(interaction_file_df):
    create_interactor_id_table()
    alt_id_interactor_set = set()
    interactor_id_df = interaction_file_df[ [ 'entity_stable_identifier_interactor_A', 'entity_stable_identifier_interactor_B', 'Alt. ID(s) interactor A', 'Alt. ID(s) interactor B']]

    interactor_id_df_A = interactor_id_df.drop('entity_stable_identifier_interactor_B', axis=1)
    interactor_id_df_A = interactor_id_df_A.drop('Alt. ID(s) interactor A', axis=1).drop('Alt. ID(s) interactor B', axis=1).join(interaction_file_df['Alt. ID(s) interactor A']
                        .str
                        .split('|', expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .rename('Alt. ID(s) interactor A')).reset_index(drop=True)
    interactor_id_df_B = interactor_id_df.drop('entity_stable_identifier_interactor_A', axis=1) 
    interactor_id_df_B = interactor_id_df_B.drop('Alt. ID(s) interactor A', axis=1).drop('Alt. ID(s) interactor B', axis=1).join(interaction_file_df['Alt. ID(s) interactor B']
                        .str
                        .split('|', expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .rename('Alt. ID(s) interactor B')).reset_index(drop=True)  

    interactor_id_df_A = interactor_id_df_A[ ['entity_stable_identifier_interactor_A', 'Alt. ID(s) interactor A'] ]
    interactor_id_df_B = interactor_id_df_B[ ['entity_stable_identifier_interactor_B', 'Alt. ID(s) interactor B'] ]

    column_values_A = list(interactor_id_df_A.itertuples(index=False, name=None))
    column_values_B = list(interactor_id_df_B.itertuples(index=False, name=None))  

    cursor = db_connection.cursor()
#   Blend the 'Alt. ID(s) interactor A' and 'Alt. ID(s) interactor B' columns into the 'alt_id_interactor' column
    for i in range(0, interactor_id_df_A.shape[0]):
        if (len(column_values_A[i][0]) > 1 and len(column_values_A[i][1]) > 1) and not column_values_A[i] in alt_id_interactor_set:
            cursor.execute('''INSERT INTO INTERACTOR_ID (entity_stable_identifier, alt_id_interactor) VALUES(?,?)''', column_values_A[i])
            alt_id_interactor_set.add(column_values_A[i])
    for i in range(0, interactor_id_df_B.shape[0]):
        if (len(column_values_B[i][0]) > 1 and len(column_values_B[i][1]) > 1) and not column_values_B[i] in alt_id_interactor_set:    
            cursor.execute('''INSERT INTO INTERACTOR_ID (entity_stable_identifier, alt_id_interactor) VALUES(?,?)''', column_values_B[i])
            alt_id_interactor_set.add(column_values_B[i])
    db_connection.commit()
    

################################################################################
# Populate INTERACTOR_NAME Table
def etl_interactor_name(interaction_file_df):
    create_interactor_name_table()
    interactor_name_set = set()
    interactor_name_df = interaction_file_df[ ['entity_stable_identifier_interactor_A', 'entity_stable_identifier_interactor_B', 'Alias(es) interactor A', 'Alias(es) interactor B']]
#   parse the '|'-separated string in column 'Alias(es) interactor A' into separate rows
    interactor_name_dfA = interactor_name_df.drop('Alias(es) interactor A', axis=1).drop('entity_stable_identifier_interactor_B', axis=1).drop('Alias(es) interactor B', axis=1).join(interactor_name_df['Alias(es) interactor A']
                        .str
                        .split('|', expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .rename('Alias(es) interactor A')).reset_index(drop=True)
    interactor_name_dfA['source'] = interactor_name_dfA['Alias(es) interactor A'].apply(get_name_source)
    interactor_name_dfA['name']   = interactor_name_dfA['Alias(es) interactor A'].apply(get_name)
    interactor_name_dfA['type']   = interactor_name_dfA['Alias(es) interactor A'].apply(get_type)
    interactor_name_dfA = interactor_name_dfA[['entity_stable_identifier_interactor_A','source','name','type']]
    interactor_name_dfA.to_csv('data/tmp/interactor_name_dfA.csv', index=False)
#   parse the '|'-separated string in column 'Alias(es) interactor B' into separate rows
    interactor_name_dfB = interactor_name_df.drop('Alias(es) interactor A', axis=1).drop('entity_stable_identifier_interactor_A', axis=1).drop('Alias(es) interactor B', axis=1).join(interactor_name_df['Alias(es) interactor B']
                        .str
                        .split('|', expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .rename('Alias(es) interactor B')).reset_index(drop=True)  
    interactor_name_dfB['source'] = interactor_name_dfB['Alias(es) interactor B'].apply(get_name_source)
    interactor_name_dfB['name']   = interactor_name_dfB['Alias(es) interactor B'].apply(get_name)
    interactor_name_dfB['type']   = interactor_name_dfB['Alias(es) interactor B'].apply(get_type)
    interactor_name_dfB = interactor_name_dfB[['entity_stable_identifier_interactor_B','source','name','type']]
    interactor_name_dfB.to_csv('data/tmp/interactor_name_dfB.csv', index=False)

    column_values_A = list(interactor_name_dfA.itertuples(index=False, name=None))
    column_values_B = list(interactor_name_dfB.itertuples(index=False, name=None))  

    cursor = db_connection.cursor()
    for i in range(0, interactor_name_dfA.shape[0]):
        if column_values_A[i][0] != None and column_values_A[i][1] != None and len(column_values_A[i][0])>0 and len(column_values_A[i][2])>0 and not column_values_A[i] in interactor_name_set:
            cursor.execute('''INSERT INTO INTERACTOR_NAME (entity_stable_identifier, source, name, type) VALUES(?,?,?,?)''', column_values_A[i])
            interactor_name_set.add(column_values_A[i])
    for i in range(0, interactor_name_dfB.shape[0]):
        if column_values_B[i][0] != None and column_values_B[i][1] != None and len(column_values_B[i][0])>0 and len(column_values_B[i][2])>0 and not column_values_B[i] in interactor_name_set:    
            cursor.execute('''INSERT INTO INTERACTOR_NAME (entity_stable_identifier, source, name, type) VALUES(?,?,?,?)''', column_values_B[i])
            interactor_name_set.add(column_values_B[i])
    db_connection.commit()


#################################################################
# Find the SOURCE
# entity_stable_identifier_interactor_A,  'Alias(es) interactor A'
def get_name_source(x):
            if ':"' in x:  # colon and a quote
                source_name_list = x.split(':"')
                return source_name_list[0]
            elif ':' in x: # colon only
                source_name_list = x.split(':')
                return source_name_list[0]


#################################################################
# Find the NAME
def get_name(x):
            if ':"' in x:
                source_name_list = x.split(':"')
                part_list = source_name_list[1].split('"(')
                return part_list[0]
            elif ':' in x:
                source_name_list = x.split(':')
                part_list = source_name_list[1].split('(')
                return part_list[0]


#################################################################
# Find the TYPE
def get_type(x):
            if ':"' in x:
                source_name_list = x.split(':"')
                part_list = source_name_list[1].split('"(')
                return part_list[1].replace(')', '')
            elif ':' in x:
                source_name_list = x.split(':')
                part_list = source_name_list[1].split('(')
                return part_list[1].replace(')', '')


################################################################################
# Populate INTERACTION_MAP Table
#  
def etl_interaction_map(interaction_df):

    # Duplicate a row if Interaction Xref(s) column contains special character '|' 
    # (In case of a '|' present in any cell of the Interaction Xref(s) column, 
    # replicate the row since there is a gene symbol before or after the '|'.
    # Then split that Interaction Xref(s) value into two values, with one for each row.)
    interaction_df = interaction_df[ ['interaction_id', 'Interaction Xref(s)','Interaction annotation(s)'] ]

    get_unique_values(interaction_df)

    interaction_map_df = interaction_df.drop('Interaction Xref(s)', axis=1).join(interaction_df['Interaction Xref(s)']
                        .str
                        .split('|', expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .rename('Interaction Xref(s)')).reset_index(drop=True)
    interaction_map_df2 = interaction_df[['interaction_id', 'Interaction annotation(s)']] 
    interaction_map_df2['interaction_xref_source'] = ''

    # chop up go:"GO:0005576"(extracellular region) into go, GO:0005576, extracellular region
    interaction_map_df['interaction_xref_source'] = interaction_map_df['Interaction Xref(s)'].apply(get_source)
    interaction_map_df['interaction_xref_id']     = interaction_map_df['Interaction Xref(s)'].apply(get_xref_id)
    interaction_map_df['interaction_term']        = interaction_map_df['Interaction Xref(s)'].apply(get_term)
    interaction_map_df = interaction_map_df.drop('Interaction Xref(s)', axis=1)

    ###### interaction_map_df2 = interaction_map_df[['interaction_id', 'interaction_xref_source', 'Interaction annotation(s)', 'interaction_term']] 
   
    # correct the source to 'reactome'
    interaction_map_df2 ['interaction_xref_source'] =   interaction_map_df2 ['interaction_xref_source'].apply(lambda x: 'reactome')
    interaction_map_df = interaction_map_df[['interaction_id', 'interaction_xref_source', 'interaction_xref_id', 'interaction_term']] 
    
    
    
    interaction_map_df.to_csv('data/tmp/interaction_map_df.csv', sep='\t', encoding='utf-8')
    interaction_map_df2.to_csv('data/tmp/unsplit_interaction_map_df2.csv', sep='\t', encoding='utf-8')



#   Merge "interaction annotation(s)" column into "interaction_xref_id"
#   This second dataframe will be used to save data from 'interaction annotation(s)' column into the 'interaction_xref_id' column
    interaction_map_df2 = interaction_map_df2.drop('Interaction annotation(s)', axis=1).join(interaction_df['Interaction annotation(s)']
                                                                                .str
                                                                                .split('|', expand=True)
                                                                                .stack()
                                                                                .reset_index(level=1, drop=True)
                                                                                .rename('Interaction annotation(s)')).reset_index(drop=True)
                            
    interaction_map_df2 = interaction_map_df2[['interaction_id', 'interaction_xref_source', 'Interaction annotation(s)']]                                                                          
    
    
    interaction_map_df2.to_csv('data/tmp/interaction_map_df2.csv', sep='\t', encoding='utf-8')

    
    column_values  = list(interaction_map_df.itertuples(index=False, name=None))
    column_values2 = list(interaction_map_df2.itertuples(index=False, name=None))
    column_values2_list = list(set(column_values2))

#### TO POPULATE INTERACTION_MAP Table
    create_interaction_map_table()
    cursor = db_connection.cursor()
    for i in range(0, interaction_map_df.shape[0]):
        cursor.execute('''INSERT INTO INTERACTION_MAP (interaction_id, interaction_xref_source, interaction_xref_id, interaction_term) VALUES(?,?,?,?)''', column_values[i])
    for i in range(0, len(column_values2_list)):
        if len(str(column_values2_list[i][2]).strip()) > 1 and not pd.isna(column_values2_list[i][2]): # (i.e., filter out the NULL values and the '-' values)
            cursor.execute('''INSERT INTO INTERACTION_MAP (interaction_id, interaction_xref_source, interaction_xref_id) VALUES(?,?,?)''', column_values2_list[i])
    db_connection.commit()   
#### TO POPULATE INTERACTION_MAP Table

####################### 
# get the interaction xref source
def get_source(x):
    xref_list = x.split(':')
    return xref_list[0]

####################### 
# get the interaction xref id
def get_xref_id(x):
    xref_list = x.split('"')
    return xref_list[1]

####################### 
# get the interaction xref term
def get_term(x):
    xref_list = x.split('"')
    return xref_list[2].replace('(', '').replace(')','')

####################### 
# filter out duplicates
def get_unique_values(df):
    column_values = list(df.itertuples(index=False, name=None))
    data = list(set(column_values))
    df = pd.DataFrame(data, columns = ['interaction_id', 'Interaction Xref(s)', 'Interaction annotation(s)'])



####################### 
# CREATE INTERACTOR TABLE
# removed interaction_id column
def create_interactor_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS INTERACTOR''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE INTERACTOR( 
                    interactor_id TEXT COLLATE NOCASE, 
                    entity_stable_identifier TEXT PRIMARY KEY, 
                    interactor_taxid TEXT,  
                    interactor_type TEXT,   
                    interactor_xref TEXT, 
                    interactor_annotations TEXT)''')
    cursor.execute('''CREATE INDEX index_interactor ON INTERACTOR (interactor_id)''')
    cursor.execute('''CREATE INDEX index_interactor_2 ON INTERACTOR (entity_stable_identifier)''')
    db_connection.commit()


####################### 
# CREATE INTERACTOR_ID TABLE
def create_interactor_id_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS INTERACTOR_ID''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE INTERACTOR_ID(
                    entity_stable_identifier TEXT,  
                    alt_id_interactor TEXT)''')
    cursor.execute('''CREATE INDEX index_interactor_id ON INTERACTOR_ID (entity_stable_identifier)''')
    db_connection.commit()


####################### 
# CREATE INTERACTOR_NAME TABLE
def create_interactor_name_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS INTERACTOR_NAME''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE INTERACTOR_NAME(
                        entity_stable_identifier TEXT, 
                        source TEXT,
                        name TEXT,
                        type TEXT)''')
    cursor.execute('''CREATE INDEX index_interactor_name ON INTERACTOR_NAME (name)''')
    cursor.execute('''CREATE INDEX index_interactor_name_2 ON INTERACTOR_NAME (entity_stable_identifier)''')
    db_connection.commit()


####################### 
# CREATE INTERACTION TABLE
def create_interaction_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS INTERACTION''')
    db_connection.commit()    
    cursor.execute('''CREATE TABLE INTERACTION(interaction_id INTEGER PRIMARY KEY, 
                                                             entity_stable_identifier_interactor_A TEXT, 
                                                             entity_stable_identifier_interactor_B TEXT,
                                                             interaction_detection_method TEXT, 
                                                             publication_first_author TEXT, 
                                                             publication_identifier  TEXT,
                                                             interaction_type TEXT, 
                                                             source_database  TEXT, 
                                                             interaction_identifier  TEXT, 
                                                             confidence_value  TEXT, 
                                                             expansion_method  TEXT, 
                                                             biological_role_interactor_A  TEXT, 
                                                             biological_role_interactor_B  TEXT, 
                                                             experimental_role_interactor_A TEXT, 
                                                             experimental_role_interactor_B TEXT, 
                                                            -- interaction_annotation TEXT, 
                                                             host_organism TEXT,
                                                             interaction_parameter TEXT, 
                                                             negative TEXT, 
                                                             feature_interactor_A TEXT, 
                                                             feature_interactor_B TEXT, 
                                                             stoichiometry_interactor_A INTEGER, 
                                                             stoichiometry_interactor_B INTEGER, 
                                                             identification_method TEXT )''')
    cursor.execute('''CREATE INDEX index_interaction ON INTERACTION (interaction_id)''')
    cursor.execute('''CREATE INDEX index_interaction_A ON INTERACTION (entity_stable_identifier_interactor_A)''')
    cursor.execute('''CREATE INDEX index_interaction_B ON INTERACTION (entity_stable_identifier_interactor_B)''')                                                                                   

    db_connection.commit()


####################### 
# CREATE INTERACTION_MAP TABLE   interaction_id, interaction_xref_source, interaction_xref_id, interaction_term
def create_interaction_map_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS INTERACTION_MAP''')
    db_connection.commit()   
    cursor.execute('''CREATE TABLE INTERACTION_MAP(interaction_id INTEGER, 
                                                                 interaction_xref_source TEXT, 
                                                                 interaction_xref_id TEXT, 
                                                                 interaction_term TEXT)''')
    cursor.execute('''CREATE INDEX index_interaction_map ON INTERACTION_MAP (interaction_id)''')
    db_connection.commit()


def find_go_ancestor():
    go_tuple_list = []

    query = """
        SELECT DISTINCT interaction_xref_id, interaction_term
        FROM INTERACTION_MAP
        WHERE interaction_xref_source = "go"
        ORDER BY interaction_xref_id ASC
    """
    cursor = db_connection.execute(query,)
    for row in cursor.fetchall():
        go_tuple = (row['interaction_xref_id'],row['interaction_term'])
        go_tuple_list.append(go_tuple)

    go_dictionary = {}
    for go_tuple in go_tuple_list:
        go_identifier = go_tuple[0]
        api_url = f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_identifier}/ancestors?relations=is_a%2Cpart_of%2Coccurs_in%2Cregulates"
        request_headers = "application/json"
        response = requests.get(api_url, request_headers)
        json_obj = json.loads(response.content.decode('utf-8'))

        for results in json_obj['results']:
            go_key = {}
            go_key['name'] = results.get('name')
            go_key['aspect'] = results.get('aspect')
            go_dictionary[go_tuple[0]] = go_key

        # save JSON Object json_obj into a json file.
        with open('data/config/go_dictionary.json', 'w') as json_file:
            json.dump(go_dictionary, json_file, indent=2)


def main():
    interaction_file_df = etl_interaction()
    etl_interaction_map(interaction_file_df)
    etl_interactor(interaction_file_df)
    etl_interactor_id(interaction_file_df)
    etl_interactor_name(interaction_file_df)
    find_go_ancestor()

if __name__ == '__main__':
    main()