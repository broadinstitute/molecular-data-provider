#/usr/bin/python3
import os
import sys
import MSigDBparser
import MsigDBcsv2SQLite

 # TO RUN THIS FILE YOU NEED TO HAVE TWICE THE MEMORY OF THE FILE ON THE FILE SOURCE DISK AS THIS CODE WILL SPLIT THE FILE AND MAKE COPIES OF THE CHUNCKS
p = os.path.split(sys.argv[0])[0]
os.chdir(p)
path_in =  p + "/data/" # location for input .csv files
path_in = path_in.replace('\\', '/')
path_out = p + '/data/' # location to store SQLite DB
path_out = path_out.replace('\\', '/')
source_name = 'msigdb_v7.4.xml'
config_file = "config_file"
DB_IDs = "DB_IDs"
part_size = 500
headers_num = 4 # number of header lines expected in file
to_parse = True #False #

db_name = 'MSigDB.sqlite'

os.chdir(os.path.dirname(__file__))

MSigDBparser.parse_MSigDB(path_in,path_out,source_name,config_file,DB_IDs,part_size,headers_num,to_parse)

MsigDBcsv2SQLite.csv2SQLite(path_in,path_out,db_name,config_file)
