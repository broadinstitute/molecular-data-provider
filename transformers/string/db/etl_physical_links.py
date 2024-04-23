import sqlite3
import re
import pandas as pd
from collections import defaultdict
import os
import math


######################  
# PATHS
db_folder = 'data'
rootpath = os.path.dirname(os.path.abspath(__file__))
databasepath = os.path.join(rootpath,db_folder,"STRING.sqlite")

######################  
# DATABASE CONNECTION
db_connection = sqlite3.connect(databasepath, check_same_thread=False)
db_connection.row_factory = sqlite3.Row
CHUNK_SIZE = 25000000
DO_IF_EXISTS = 'append'
nocase='NOCASE'

####################### 
# Extract, Transform and Load into PHYSICAL_LINKS table
def etl_physical_links():
    create_physical_links_table()
    df = pd.read_csv('9606.protein.physical.links.full.v12.0.tsv', sep="\t", header=None, names=['protein1','protein2','homology','experiments','experiments_transferred','database','database_transferred','textmining','textmining_transferred','combined_score'])
    df['taxon_id1'] = ''  # add new column
    df['taxon_id2'] = ''  # add new column
    df['taxon_id1'] = df['protein1'].map(lambda x: x.split('.')[0]) # capture species versioning
    df['taxon_id2'] = df['protein2'].map(lambda x: x.split('.')[0]) # capture species versioning
    df['protein1'] = df['protein1'].map(lambda x: x.lstrip(x.split('.')[0]+'.')) # strip species versioning
    df['protein2'] = df['protein2'].map(lambda x: x.lstrip(x.split('.')[0]+'.')) # strip species versioning
  
    df = df[1:] #take the data less the header row
    df = df.rename(columns={'protein1': 'string_protein_id1', 'protein2': 'string_protein_id2', 'homology': 'homology_score', 'experiments': 'experiments_score', 'database': 'database_score', 'textmining': 'textmining_score'})
    df.to_sql("PHYSICAL_LINKS", db_connection, if_exists=DO_IF_EXISTS, index=False)  # copy the data into the table


 ####################### 
 # CREATE PHYSICAL_LINKS TABLE
def create_physical_links_table():
       cursor = db_connection.cursor()
       cursor.execute('''CREATE TABLE IF NOT EXISTS PHYSICAL_LINKS(taxon_id1,string_protein_id1,taxon_id2,string_protein_id2,homology_score,experiments_score,experiments_transferred,database_score,'database_transferred',textmining_score,textmining_transferred,combined_score,FOREIGN KEY (string_protein_id1) REFERENCES PROTEINS(string_protein_id),FOREIGN KEY (string_protein_id2) REFERENCES PROTEINS(string_protein_id))''')
       db_connection.commit()



def main():
    etl_physical_links()

if __name__ == '__main__':
    main()