import sys
import sqlite3
import json
import pandas as pd

db_connection = sqlite3.connect("data/reactome.sqlite", check_same_thread=False)
db_connection.row_factory = sqlite3.Row

################################################################################
# POPULATE REACTION Table
#  
def etl_reactions():
    reaction_db_dict = { 'uniprot': 'UniProt2Reactome_PE_Reactions.txt',
                         'chebi': 'ChEBI2Reactome_PE_Reactions.txt',
                         'miRBase': 'miRBase2Reactome_PE_Reactions.txt',
                         'gtopdb': 'GtoP2Reactome_PE_Reactions.txt',
                         'entrez' : 'NCBI2Reactome_PE_Reactions.txt',
                         'ensembl' : 'Ensembl2Reactome_PE_Reactions.txt'}
    reaction_df = pd.DataFrame({})
    physical_entity_df = pd.DataFrame({})
    
    for data_source, file in reaction_db_dict.items():
        prefix = ''
        print(data_source)

        # get JSON mapping of Biolink class to MolePro & Biolink prefixes
        prefixMap = get_prefix_mapping()

        #   - Gene (entrez, )
        #   - SmallMolecule (gtopdb, chebi, )
        #   - Protein (uniprot, )
        if data_source != 'miRBase':
            if data_source in ['entrez']:
                prefix = get_prefix(prefixMap, data_source, 'Gene',  'molepro_prefix')
            if data_source in ['gtopdb', 'chebi']:
                prefix = get_prefix(prefixMap, data_source, 'SmallMolecule', 'molepro_prefix')
            if data_source in ['uniprot']:
                prefix = get_prefix(prefixMap, data_source, 'Protein',  'molepro_prefix')
            if data_source in ['ensembl']:
                prefix = get_prefix(prefixMap, data_source, 'Gene',  'molepro_prefix')
        elif data_source == 'miRBase':
            prefix = 'mirbase:'
        reaction_file_df = pd.read_csv('data/download/'+file, sep="\t", dtype = str, names=['Source database identifier', 'Reactome Physical Entity Stable Identifier',
        'Reactome Physical Entity Name', 'Reactome Pathway Stable identifier', 'URL', 'Event (Pathway or Reaction) Name', 'Evidence Code', 'Species'])
        # Add 'source' column and set to value of data_source
        reaction_file_df['source'] = data_source
        # Add prefix to 'Source database identifier' column                                        # 
        reaction_file_df['Source database identifier'] = reaction_file_df['Source database identifier'].apply(lambda x: add_prefix(x, prefix))     #.apply(add_prefix, addition=prefix)  # instead of .apply(lambda x: prefix + str(x))
        reaction_file_df['Reactome Pathway Stable identifier'] = reaction_file_df['Reactome Pathway Stable identifier'].apply(lambda x: 'pathway:' + str(x))
        reaction_file_df['Reactome Physical Entity Stable Identifier'] = reaction_file_df['Reactome Physical Entity Stable Identifier'].apply(lambda x: 'reactome:' + str(x))        
 
        if physical_entity_df.shape[0] == 0:
            physical_entity_df = reaction_file_df
        if physical_entity_df.shape[0] > 0:
            physical_entity_df = physical_entity_df.append(reaction_file_df, ignore_index=True)    

        temp_df = reaction_file_df[['Reactome Pathway Stable identifier', 'URL', 'Event (Pathway or Reaction) Name', 'Species']]
        if reaction_df.shape[0] == 0:
            reaction_df = temp_df
        if reaction_df.shape[0] > 0:
            reaction_df = reaction_df.append(temp_df, ignore_index=True)

    #   Populate REACTION table
    column_values = list(reaction_df.itertuples(index=False, name=None))
    #   Filter out duplicate values
    column_value_list = list(set(column_values))
    create_reaction_table()
    cursor = db_connection.cursor()
    for element in column_value_list:
        cursor.execute('''INSERT INTO REACTION(pathway_stable_identifier, reaction_url, reaction_name, species) VALUES(?,?,?,?)''', element)
    db_connection.commit()
    #   Populate REACTION table

    etl_reaction_map(reaction_file_df)
    etl_physical_entity(physical_entity_df)




#################################################################
# Find the prefix
#
def get_prefix_mapping():      
    with open('data/prefixMap.json') as json_file:
        prefixMap = json.load(json_file)                           
    return prefixMap


#######################################################
#   molepro_class:
#   - Gene (entrez, )
#   - MolecularEntity (gtopdb, chebi, )
#   - Protein (uniprot, )
#   - (miRBase)
def get_prefix(prefix_map, fieldname, biolink_class, source):
    if biolink_class not in prefix_map:
        return None
    if fieldname not in prefix_map[biolink_class]:
        return None
    return prefix_map[biolink_class][fieldname][source]


#######################################################
#
def add_prefix(x, prefix):
    if 'DDB_' in x: # in case the source identifier is from dictybase like DDB_G0267522
        return 'dictybase.gene:' + x
    else:
        return prefix + x


################################################################################
# Populate PHYSICAL_ENTITY Table
def etl_physical_entity(reaction_file_df):
    physical_entity_df = reaction_file_df[['source','Source database identifier','Reactome Physical Entity Stable Identifier', 'Reactome Physical Entity Name']]
    # Break out "Reactome Physical Entity Name" into 'name' and 'compartment' such as "let-7b [cytosol]"
    physical_entity_df_copy = physical_entity_df.copy()   # Use copy() to avoid "SettingWithCopyWarning"
    physical_entity_df_copy['name']  = physical_entity_df['Reactome Physical Entity Name'].apply(get_name)
    physical_entity_df_copy['name']  = physical_entity_df_copy['name'].apply(lambda x: x.strip())
    physical_entity_df_copy['compartment'] = physical_entity_df['Reactome Physical Entity Name'].apply(get_compartment)
    physical_entity_df_copy = physical_entity_df_copy.drop('Reactome Physical Entity Name', axis=1)
    create_physical_entity_table()
    column_values = list(physical_entity_df_copy.itertuples(index=False, name=None))
    cursor = db_connection.cursor()

    column_value_set = set()
    # Filter out duplicate values
    for i in range(0, physical_entity_df_copy.shape[0]):
        column_value_set.add(column_values[i])

    # Populate with unique values    
    column_value_list = list(set(column_values))
    for element in column_value_list:
        cursor.execute('''INSERT INTO PHYSICAL_ENTITY ( 
                            source, 
                            entity_native_identifier, 
                            entity_stable_identifier,
                            entity_name,
                            compartment) VALUES(?,?,?,?,?)''', element)
    db_connection.commit()


#################################################################
# Find the name
# let-7b [cytosol]
def get_name(x):
    entity_name_list = x.split(' [')
    return entity_name_list[0]


#################################################################
# Find the compartment
# alpha-D-Man-(1->3)-[alpha-D-Man-(1->3)-[alpha-D-Man-(1->6)]-alpha-D-Man-(1->6)]-beta-D-Man-(1->4)-beta-D-GlcNAc [cytosol]
def get_compartment(x):
    entity_name_list = x.split(' [')
    compartment = entity_name_list[1].replace('[','').replace(']','')
    return compartment


############################################################################### 
# POPULATE REACTION_MAP Table
def etl_reaction_map(reaction_file_df):
    reaction_map_df = reaction_file_df[['Reactome Physical Entity Stable Identifier', 'Reactome Pathway Stable identifier', 'Evidence Code']]
    column_values = list(reaction_map_df.itertuples(index=False, name=None))
    column_value_set = set()
    # Filter out duplicate values
    for i in range(0, reaction_map_df.shape[0]):
        column_value_set.add(column_values[i])
    # Populate with unique values    
    column_value_list = list(column_value_set)
    cursor = db_connection.cursor()
    create_reaction_map_table()
    for element in column_value_list:
        cursor.execute('''INSERT INTO REACTION_MAP ( 
                            entity_stable_identifier, 
                            pathway_stable_identifier,
                            evidence_code
                            ) VALUES(?,?,?)''', element)
    db_connection.commit()


####################### 
# CREATE PHYSICAL_ENTITY Table
def create_physical_entity_table():
    cursor = db_connection.cursor()
    cursor.execute('''DROP TABLE IF EXISTS PHYSICAL_ENTITY''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE PHYSICAL_ENTITY(
                        source TEXT,
                        entity_native_identifier TEXT,
                        entity_stable_identifier TEXT,
                        entity_name TEXT COLLATE NOCASE,
                        compartment TEXT)''')
    cursor.execute('''CREATE INDEX index_physical_entity ON PHYSICAL_ENTITY (entity_native_identifier)''')
    cursor.execute('''CREATE INDEX index_physical_entity_2 ON PHYSICAL_ENTITY (entity_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_physical_entity_3 ON PHYSICAL_ENTITY (entity_name)''')
    db_connection.commit()
    cursor.execute('''VACUUM''')
    db_connection.commit()


####################### 
# CREATE REACTION_MAP Table
def create_reaction_map_table():
    cursor = db_connection.cursor()
    cursor.execute('''DROP TABLE IF EXISTS REACTION_MAP''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE REACTION_MAP(
                        entity_stable_identifier TEXT,
                        pathway_stable_identifier TEXT,
                        evidence_code TEXT)''')
    cursor.execute('''CREATE INDEX index_reaction_map ON REACTION_MAP (entity_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_reaction_map_2 ON REACTION_MAP (pathway_stable_identifier)''')
    db_connection.commit()
    cursor.execute('''VACUUM''')
    db_connection.commit()


####################### 
# CREATE REACTION Table 
def create_reaction_table():
    cursor = db_connection.cursor()
    cursor.execute('''DROP TABLE IF EXISTS REACTION''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE REACTION(
                        pathway_stable_identifier TEXT PRIMARY KEY,
                        reaction_url TEXT,
                        reaction_name TEXT,
                        species TEXT)''')
    cursor.execute('''CREATE INDEX index_reaction ON REACTION (reaction_name)''')
    cursor.execute('''CREATE INDEX index_reaction_2 ON REACTION (pathway_stable_identifier)''')    
    db_connection.commit()
    cursor.execute('''VACUUM''')
    db_connection.commit()


def main():
    etl_reactions()

if __name__ == '__main__':
    main()

