import sqlite3
import pandas as pd

db_connection = sqlite3.connect("data/reactome.sqlite", check_same_thread=False)
db_connection.row_factory = sqlite3.Row


################################################################################
# Populate COMPLEX_PATHWAY_MAP Table  from Complex_2_Pathway_human.txt
def etl_complex2pathway():
    complex2path_file_df = pd.read_csv('data/download/Complex_2_Pathway_human.txt', dtype = str, sep="\t")
    complex2path_file_df['taxon_id'] = '9606'
    complex2path_file_df['complex'] = complex2path_file_df['complex'].apply(lambda x: 'reactome:' + str(x))
    complex2path_file_df['pathway'] = complex2path_file_df['pathway'].apply(lambda x: 'pathway:' + str(x))
    complex2path_file_df['top_level_pathway'] = complex2path_file_df['top_level_pathway'].apply(lambda x: 'pathway:' + str(x))
    create_complex2pathway_table()
    column_values = list(complex2path_file_df.itertuples(index=False, name=None))
    cursor = db_connection.cursor()
    for i in range(0, complex2path_file_df.shape[0]):
        cursor.execute('''INSERT INTO COMPLEX_PATHWAY_MAP ('complex_stable_identifier','pathway_stable_identifier', 'top_level_pathway','taxon_id') 
        VALUES(?,?,?,?)''', column_values[i])
    db_connection.commit()


################################################################################
# Populate COMPLEX Table
# columns: identifier	name	participants	participatingComplex	pubMedIdentifiers
def etl_complex():
    complex_file_df = pd.read_csv('data/download/ComplexParticipantsPubMedIdentifiers_human.txt', dtype = str, sep="\t")
    complex_file_df['identifier'] = complex_file_df['identifier'].apply(lambda x: 'reactome:' + str(x))
    
    complex_table_df = complex_file_df[ ['identifier', 'name', 'pubMedIdentifiers'] ]
    complex_participant_table_df = complex_file_df[ ['identifier','participants','participatingComplex'] ]

#Parse out "name" into 'name' and 'compartment' such as "DOCK-GEFs:RAC1, CDC42 [cytosol]" (for the benefit of the Complex Producer)
    complex_table_df_copy = complex_table_df.copy()   # Use copy() to avoid "SettingWithCopyWarning"
    complex_table_df_copy['complex_name'] = complex_table_df['name'].apply(get_name)
    complex_table_df_copy['complex_name'] = complex_table_df_copy['complex_name'].apply(lambda x: x.strip())
    complex_table_df = complex_table_df_copy          # # Restore the copied dataframe
    complex_table_df['compartment'] = complex_table_df['name'].apply(get_compartment)
    complex_table_df = complex_table_df.drop('name', axis=1)

#### TO POPULATE COMPLEX Table
    create_complex_table()
    column_values = list(complex_table_df.itertuples(index=False, name=None))
    cursor = db_connection.cursor()
    for i in range(0, complex_table_df.shape[0]):
        cursor.execute('''INSERT INTO COMPLEX ('complex_stable_identifier','pubmed_ids','complex_name','compartment') 
        VALUES(?,?,?,?)''', column_values[i])
    db_connection.commit()
#### TO POPULATE COMPLEX Table  

#############################################################################################################################################
#   combine 'participants','participatingComplex' columns into one 'complex_participant_identifier' column in the  COMPLEX_PARTICIPANT Table
    participants_df         = complex_participant_table_df
    participatingComplex_df = complex_participant_table_df
#   parse out the |-delimited strings into separate rows in the participants and participatingComplex columns
    participants_df = participants_df.drop('participants', axis=1).drop('participatingComplex', axis=1).join(complex_participant_table_df['participants']
                        .str
                        .split('|', expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .rename('participants')).reset_index(drop=True)
    participants_df['participants'] = participants_df['participants'].apply(harmonize)
    participatingComplex_df = participatingComplex_df.drop('participants', axis=1).drop('participatingComplex', axis=1).join(complex_participant_table_df['participatingComplex']
                        .str
                        .split('|', expand=True)
                        .stack()
                        .reset_index(level=1, drop=True)
                        .rename('participatingComplex')).reset_index(drop=True)
    participatingComplex_df['participatingComplex'] = participatingComplex_df['participatingComplex'].apply(lambda x: 'reactome:' + str(x)  if len(x) > 1 else '')
    participatingComplex_df['participatingComplex'] = participatingComplex_df['participatingComplex'].apply(harmonize)

#### POPULATE COMPLEX_PARTICIPANT Table
    create_complex_participant_table()
    column_values_1 = list(participants_df.itertuples(index=False, name=None))
    column_values_2 = list(participatingComplex_df.itertuples(index=False, name=None))
    cursor = db_connection.cursor()
    for i in range(0, participants_df.shape[0]):
        cursor.execute('''INSERT INTO COMPLEX_PARTICIPANT ('complex_stable_identifier',
                                                            'complex_participant_identifier') 
                                                         VALUES(?,?)''', column_values_1[i])
    for i in range(0, participatingComplex_df.shape[0]):
        if len(column_values_2[i][1]) > 1:
            cursor.execute('''INSERT INTO COMPLEX_PARTICIPANT ('complex_stable_identifier',
                                                                'complex_participant_identifier') 
                                                         VALUES(?,?)''', column_values_2[i])
    db_connection.commit()
#### POPULATE COMPLEX_PARTICIPANT Table     


#################################################################
# Try to harmonize most of the prefixes with MolePro or 
# the PHYSICAL_ENTITY table.
# ChEBI  (CHEBI)
# ChemSpider
# EMBL
# ENSEMBL  (ENSEMBL)
# Guide to Pharmacology (GTOPDB)
# NCBI Entrez Gene  (NCBIGene)
# NCBI Nucleotide 
# NCIthesaurus  (NCIT)
# PubChem Compound  (CID)
# PubChem Substance  (SID)
# UniProt   (UniProtKB)
# miRBase   (mirbase)
# reactome  (REACT)
def harmonize(x):
    prefix_map = {
        'ChEBI':'CHEBI',
        'ChemSpider':'ChemSpider',
        'EMBL':'EMBL',
        'ENSEMBL':'ENSEMBL',
        'Guide to Pharmacology':'GTOPDB',
        'NCBI Entrez Gene':'NCBIGene',
        'NCBI Nucleotide': 'NCBI Nucleotide',
        'NCIthesaurus':'NCIT',
        'PubChem Compound':'CID',
        'PubChem Substance':'SID',
        'UniProt':'UniProtKB',
        'miRBase':'mirbase',
        'reactome':'reactome'
    }
    if len(x.split(':')[0])> 0:
        x = x.replace(x.split(':')[0], prefix_map[x.split(':')[0]])
    return x


#################################################################
# Find the name
# DOCK-GEFs:RAC1, CDC42 [cytosol]
def get_name(x):
    complex_name_list = x.split('[')
    return complex_name_list[0]

#################################################################
# Find the compartment
# DOCK-GEFs:RAC1, CDC42 [cytosol]
def get_compartment(x):
    entity_name_list = x.split('[')
    compartment = entity_name_list[1].replace('[','').replace(']','')
    return compartment



##################################################################################################################################
####################### 
# CREATE COMPLEX_PATHWAY_MAP TABLE
def create_complex2pathway_table():
    cursor = db_connection.cursor()
    #cursor.execute('''DROP TABLE IF EXISTS COMPLEX_PATHWAY_MAP''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE COMPLEX_PATHWAY_MAP(
                        complex_stable_identifier TEXT, 
                        pathway_stable_identifier TEXT,
                        top_level_pathway TEXT,
                        taxon_id TEXT)''')
    cursor.execute('''CREATE INDEX index_complex2pathway ON COMPLEX_PATHWAY_MAP (complex_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_complex2pathway_2 ON COMPLEX_PATHWAY_MAP (pathway_stable_identifier)''')
    db_connection.commit()



####################### 
# CREATE COMPLEX TABLE
def create_complex_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS COMPLEX''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE COMPLEX(
                        complex_stable_identifier TEXT PRIMARY KEY,
                        complex_name TEXT,
                        compartment TEXT, 
                        pubmed_ids TEXT)''')
    cursor.execute('''CREATE INDEX index_complex ON COMPLEX (complex_name)''')
    cursor.execute('''CREATE INDEX index_complex_2 ON COMPLEX (complex_stable_identifier)''')
    db_connection.commit()


####################### 
# CREATE COMPLEX_PARTICIPANT TABLE
def create_complex_participant_table():
    cursor = db_connection.cursor()
    # cursor.execute('''DROP TABLE IF EXISTS COMPLEX_PARTICIPANT''')
    db_connection.commit()
    cursor.execute('''CREATE TABLE COMPLEX_PARTICIPANT(
                        complex_stable_identifier TEXT, 
                        complex_participant_identifier TEXT)''')
    cursor.execute('''CREATE INDEX index_complex_participant ON COMPLEX_PARTICIPANT (complex_stable_identifier)''')
    cursor.execute('''CREATE INDEX index_complex_participant_2 ON COMPLEX_PARTICIPANT (complex_participant_identifier)''')
    db_connection.commit()



def main():
    etl_complex()
    etl_complex2pathway()

if __name__ == '__main__':
    main()