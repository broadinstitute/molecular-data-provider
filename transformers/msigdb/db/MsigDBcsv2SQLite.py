#/usr/bin/python3
# LIBRAIRIES:
from pathlib import Path
import sqlite3
import pandas as pd
import os
import sys
from os import path


def csv2SQLite(path_in,path_out,db_name,config_file):

    # LOAD CONFIG FILE:
    print("load config file...")
    vdict = pd.read_csv(config_file + ".csv",dtype=str,index_col=False)
    print("load config file...done.")

    # LOAD DATA:
    print("load data tables...")
    csv_files_in = list(set(vdict.table)) # this list should contain  the names of the files
    for table in csv_files_in:
        exec(table + ' = pd.read_csv("' + path_in + table + '_normalized.csv")')
    print("load data tables...done.")

    # REMOVE SQLite file if already exists, CREATE DB file AND CONNECT TO SQLite:
    print("overwrite database (if preexisting) and make connection...")
    db_path = path_out + db_name
    if path.exists(db_path):
        os.remove(db_path)
    Path(db_path).touch() # create empty DB file
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    print("overwrite database (if preexisting) and make connection...done.")

    # TABLES CREATION: use information from the dictionary to build the tables
    print("create tables...")
    table_creation_command = '' # this string with contain the command to execute the creation of tables
    for table in csv_files_in: # pass through tables
        l = vdict.variable_out.loc[(vdict ['table'] == table)].tolist()
        print(l)
        for cpt,j in enumerate(l): # pass through variables
            vtype = vdict.variable_out_type[(vdict ['variable_out'] == j) & (vdict ['table'] == table)].iloc[0]
            if cpt != (len(l)-1):
                table_creation_command = table_creation_command + j + ' ' + vtype + ', '
            else:
                table_creation_command = table_creation_command + j + ' ' + vtype
        exec('c.execute("""CREATE TABLE  IF NOT EXISTS  '+ table + ' (' + table_creation_command + ')""")')
        if table == 'MEMBER': #hardcoded
            c.execute('CREATE INDEX "MEMBER_MEMBER3_IDX" ON "MEMBER" ("MEMBERS_3");')
        if table == 'MEMBER_MAP':
            c.execute('CREATE INDEX "MEMBER_MAP_MEMBERS1_IDX" ON "MEMBER_MAP" ("MEMBERS_1");')
        table_creation_command = ''
    print("create tables...done.")

    # FILL DB FROM CSV:
    print("fill tables...")
    for csv_file in csv_files_in:
        exec(csv_file + ".to_sql('" + csv_file + "', conn, if_exists='append', index = False)") # write the data to a sqlite table
    print("fill tables...done.")
    
    print("create indexes...")
    c.execute('CREATE INDEX MEMBER_MAP_STANDARD_NAME_IDX ON MEMBER_MAP (STANDARD_NAME);')
    c.execute('CREATE INDEX MEMBER_MEMBERS1_IDX ON MEMBER (MEMBERS_1);')
    print("create indexes...done")

if ( __name__ == "__main__"):
    # VARIABLES INSTANSTATION:
    p = os.path.split(sys.argv[0])[0]
    os.chdir(p)
    path_in =  p + "/data/" # location for input .csv files
    path_in = path_in.replace('\\', '/')
    path_out = p + '/data/' # location to store SQLite DB
    config_file = "config_file"
    db_name = 'MSigDB.sqlite'

    csv2SQLite(path_in,path_out,db_name,config_file)
