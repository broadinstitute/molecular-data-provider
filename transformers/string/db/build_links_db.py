import sqlite3
from sqlite3 import Error
import pandas as pd
import os



def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    
    ########### PATHS
    db_folder = 'data'
    rootpath = os.path.dirname(os.path.abspath(__file__))
    databasepath = os.path.join(rootpath,db_folder,"STRING.sqlite")
    
    #TODO
    # Read and ingest 9606.protein.physical.links.full.v12.0.txt as a table

    interactions_filepath = os.path.join(rootpath,db_folder,"9606.protein.links.full.v12.0.txt")
    prot_name_mapping_filepath = os.path.join(rootpath,db_folder,"9606.protein.info.v12.0 2.txt")
    prot_name_aliases_filepath = os.path.join(rootpath ,db_folder,"9606.protein.aliases.v12.0.txt")
    delim = '\t'
    
    ########### CREATE CONNECTION
    create_connection(databasepath)

    ########### PROTEIN TABLE
    interactions_df = pd.read_csv(prot_name_mapping_filepath,delimiter=delim,dtype='str')
    interactions_df['#string_protein_id'] = interactions_df['#string_protein_id'].map(lambda x: x.lstrip('9606.')) # strip out Homo Sapiens NCBI Taxonomy ID 
    interactions_df.rename(columns = {'#string_protein_id':'string_protein_id'}, inplace = True)# rename ID column name
    interactions_df = interactions_df.drop(columns=['protein_size'])

    ####################### PRETREATMENT BEFORE DATABASE CREATION
    T_input_aliases = pd.read_csv(prot_name_aliases_filepath,delimiter=delim,dtype='str')
    T_input_aliases.rename(columns = {'#string_protein_id':'string_protein_id'}, inplace = True)# rename ID column name
    T_input_aliases_filtered = pd.DataFrame(T_input_aliases.query("source == 'Ensembl_gene'")) # filter for mapping: NCBI, UniProt do not give complete coverage, EnsemblGene source has complete mapping
    T_input_aliases_filtered.rename(columns = {'alias':'EnsemblGene'}, inplace = True)# rename ID column name
    T_input_aliases_filtered['string_protein_id'] = T_input_aliases_filtered['string_protein_id'].map(lambda x: x.lstrip('9606.')) # strip species versioning
    Tout = T_input_aliases_filtered.set_index('string_protein_id').join(interactions_df.set_index('string_protein_id'), on='string_protein_id', how='left',sort=False)
    Tout = Tout[Tout['preferred_name'].notnull()]

    prot_name_mapping_filepath = os.path.join(rootpath,db_folder,"9606.protein.info.v12.0.stripped.aliases.tsv")
    Tout.to_csv(prot_name_mapping_filepath, sep = "\t", index = True)# save as file
    H_prot_names = ['string_protein_id','EnsemblGene','preferred_name','annotation']
    
    ####################### CREATE AND FILL PROTEIN TABLE
    try: 
        conn = sqlite3.connect(databasepath)
            
        cursor = conn.cursor()
        
        interactions_df = pd.read_csv(prot_name_mapping_filepath,delimiter=delim)
        interactions_df = interactions_df.loc[:,H_prot_names]
        #H = list(interactions_df.columns)
        #H2 = list(interactions_df.columns)
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS PROTEINS(string_protein_id PRIMARY KEY,EnsemblGene,preferred_name,annotation)''')
        column_values = list(interactions_df.itertuples(index=False, name=None))
        for i in range(0,interactions_df.shape[0]-1):
            cur = conn.cursor()
            cur.execute('''INSERT INTO PROTEINS (string_protein_id,EnsemblGene,preferred_name,annotation) VALUES(?,?,?,?)''', column_values[i])
            if i % 10000 == 0:
                conn.commit()
        conn.commit()
        cursor.execute('''CREATE INDEX index_string_protein_id ON PROTEINS (string_protein_id);''')
        cursor.execute('''CREATE INDEX index_EnsemblGene ON PROTEINS (EnsemblGene);''')
        
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    
    ########### LINKS TABLE
    ####################### PRETREATMENT BEFORE DATABASE CREATION
    interactions_df = pd.read_csv(interactions_filepath,delimiter=' ',dtype='str')
    interactions_df['taxon_id1'] = ''  # add new column
    interactions_df['taxon_id2'] = ''  # add new column
    interactions_df['taxon_id1'] = interactions_df['protein1'].map(lambda x: x.split('.')[0]) # capture species versioning
    interactions_df['taxon_id2'] = interactions_df['protein2'].map(lambda x: x.split('.')[0]) # capture species versioning
    interactions_df['protein1'] = interactions_df['protein1'].map(lambda x: x.lstrip(x.split('.')[0]+'.')) # strip species versioning
    interactions_df['protein2'] = interactions_df['protein2'].map(lambda x: x.lstrip(x.split('.')[0]+'.')) # strip species versioning
    interactions_filepath_stripped = os.path.join(rootpath,db_folder,"9606.protein.links.full.v12.0.stripped.tsv")
    interactions_df.to_csv(interactions_filepath_stripped, sep = "\t", index = False) # save as file
    H_scores = ['taxon_id1','protein1','taxon_id2','protein2','combined_score','neighborhood','fusion','cooccurence','homology','coexpression','experiments','database','textmining','neighborhood_transferred','coexpression_transferred','experiments_transferred','database_transferred','textmining_transferred']
    
    ####################### CREATE AND FILL PROTEIN TABLE
    try: 
        conn = sqlite3.connect(databasepath)
            
        cursor = conn.cursor()
        
        interactions_df = pd.read_csv(interactions_filepath_stripped,delimiter=delim)
        interactions_df = interactions_df.loc[:,H_scores]
        #H = list(interactions_df.columns)
        #H2 = list(interactions_df.columns)
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS LINKS(taxon_id1,string_protein_id1,taxon_id2,string_protein_id2,combined_score,neighborhood_score,fusion_score,cooccurence_score,homology_score,coexpression_score,experiments_score,database_score,textmining_score,neighborhood_transferred,coexpression_transferred,experiments_transferred,database_transferred,textmining_transferred,FOREIGN KEY (string_protein_id1) REFERENCES PROTEINS(string_protein_id),FOREIGN KEY (string_protein_id2) REFERENCES PROTEINS(string_protein_id))''')
        column_values = list(interactions_df.itertuples(index=False, name=None))
        for i in range(0,interactions_df.shape[0]-1):
            cur = conn.cursor()
            cur.execute('''INSERT INTO LINKS (taxon_id1,string_protein_id1,taxon_id2,string_protein_id2,combined_score,neighborhood_score,fusion_score,cooccurence_score,homology_score,coexpression_score,experiments_score,database_score,textmining_score,neighborhood_transferred,coexpression_transferred,experiments_transferred,database_transferred,textmining_transferred) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', column_values[i])
            if i % 10000 == 0:
                conn.commit()
        conn.commit()
        cursor.execute('''CREATE INDEX index_string_protein_id1 ON LINKS (string_protein_id1);''')
        cursor.execute('''CREATE INDEX index_string_protein_id2 ON LINKS (string_protein_id2);''')
        cursor.execute('''CREATE INDEX index_protein_id1_combined_score ON LINKS (string_protein_id1,combined_score);''')
        
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


 

    
    
    