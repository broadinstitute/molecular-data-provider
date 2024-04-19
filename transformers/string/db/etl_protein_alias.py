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
# Extract, Transform and Load into PROTEIN_ALIAS table
# 1508\t0\t9606.ENSP00000345672\t9606\tHomo sapiens\tCTSB
#'input_gene', 'gene_index_in_input','STRING_ID','species_ID','species_name','STRING_preferred_name'
#
def etl_physical_links():
    create_protein_alias_table()
    df = pd.read_csv('9606.protein.aliases.v12.0.txt', sep="\t", header=None, names=['string_protein_id','alias','source'])
    df['taxon_id'] = ''  # add new column
    df['taxon_id'] = df['string_protein_id'].map(lambda x: x.split('.')[0]) # capture species versioning
    df['string_protein_id'] = df['string_protein_id'].map(lambda x: x.lstrip(x.split('.')[0]+'.')) # strip species versioning
  
    df = df[1:] #take the data less the header row
    df.to_sql("PROTEIN_ALIAS", db_connection, if_exists=DO_IF_EXISTS, index=False)  # copy the data into the table

 ####################### 
 # CREATE PROTEIN_ALIAS TABLE
def create_protein_alias_table():
       cursor = db_connection.cursor()
       cursor.execute('''CREATE TABLE IF NOT EXISTS PROTEIN_ALIAS(taxon_id, string_protein_id, alias, source, FOREIGN KEY (string_protein_id) REFERENCES PROTEINS(string_protein_id) )''')
       cursor.execute('CREATE INDEX index_string_alias_source ON PROTEIN_ALIAS (alias,source);')
       db_connection.commit()


def main():
    etl_physical_links()

if __name__ == '__main__':
    main()

