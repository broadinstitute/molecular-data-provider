#/usr/bin/python3
import xml.sax
import numpy as np
import pandas as pd
import csv
import re
import os
import sys
import warnings


def handler2list(hd,cols):   # from handler class to a list
    my_list = []
    for i in range(0,len(cols)):
        exec('my_list.insert(i,hd.' + cols[i] + ')')
    return my_list

def list2df(l,cols):                                    # from list to dataframe
    # when data input of dataframe is a simple list, each cells is interpreted as a row entry. To make each cell a value for a column, that function transposes the dataframe. 
    df = pd.DataFrame(data = l, index = cols)
    df = df.T
    return df

def extract_subfields(ptrn,str_val):
    # function that parses a string str_val according to a string pattern ptrn and returns a list of string tuples. each tupple represents the variable subfields. 
    # The pattern ptrn MUST start and end with a look up regular expression to ensure correct parsing
    sepst = ptrn[5]
    sepend = ptrn[len(ptrn)-2]
    str_extracted = re.findall(ptrn,sepst + str_val + sepend)
    
    return str_extracted

def wcsv(foo,cols): 
    # function to write a csv file from list
    with open(foo, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(cols)

def write_headers(pin,variable_lookup, tbl, parsing_bool):
    # function to write the headers of the files according to the variables look up btable
    column_out = [] # list of output tables columns
    column_in = []
    file_paths_list = [] # list of file paths for output tables
    for cpt,t in enumerate(tbl): # pass through tables
        file_paths_list.append(pin + t + ".csv")
        mask = variable_lookup['table'] == t
        column_out.append(variable_lookup.variable_out[mask].tolist())
        __column_in__ = variable_lookup.variable_in[mask].tolist() # vdict.variable_in[(vdict ['table'] == t)&(vdict.variable_in.isnull()==False)].tolist()

        column_in.append(__column_in__)
        if parsing_bool:
            wcsv(file_paths_list[cpt],column_out[cpt]) # write columns headers

    return file_paths_list, column_in, column_out

def encode2utf8(pin,src_name,tgt_name):
# source :
    pout = pin + tgt_name + ".xml"
    fout = open(pout,'w',encoding = 'utf8')
    with open(pin + src_name, "r",encoding = 'utf8') as f: # retrieve start and end of file markups
        for i,line in enumerate(f):
            line = line.replace('\\u','u') # \u is a special code fr xml escaping
            line = line.encode('ascii', "ignore").decode("utf-8")
            fout.write(line)
        f.close()
        fout.close()

def file2parts(filename,n_lines,Hnum): # partitioning the file 
# inspired from source : https://stackoverflow.com/questions/8096614/split-large-files-using-python
    with open(filename + ".xml", encoding='utf8') as f: # retrieve start and end of file markups
        H = []
        for i,line in enumerate(f):
            if i < Hnum:# keep start of file markup
                H.append(line)
        last_line = line
        f.close()
    with open(filename + ".xml", encoding='utf8') as fin:
        fpparts = []
        fpparts.append(filename + "_0.xml")
        fout = open(fpparts[0],"w", encoding='utf8')
        cpt = 1
        for i,ln in enumerate(fin):
            fout.write(ln)
            if (i+1)%n_lines == 0:
                fout.write(last_line) # write end of file markup
                fout.close()
                fout = open(filename + "_" + str(cpt) + ".xml","w", encoding='utf8') # open new partition
                for el in H: # write headers
                    fout.write(el)
                fpparts.append(filename + "_"+ str(cpt) +".xml")
                cpt += 1
        fout.close()
    return fpparts

def replace_pipped_member_names(dataset,database_name_source_list):
    # function that finds pipped MEMBER names and replaces them with the corresponding ID by priority order ensembl>linc>tc. Update the CHIP accordingly to reflect naming source
    df =  dataset['MEMBERS_1'].str.split('|',expand=True)
    idx = df[1].notnull().tolist()
    dff = dataset.iloc[idx] # subset dataframe with pipped names
    dff2 = dff['MEMBERS_1'].str.split('|', expand=True)
    for id in dff2.index:
        list_of_available_sources = dff2.loc[id,np.arange(0, np.sum(dff2.loc[id,:].values!=None), 2).tolist()].tolist()
        if 'ens' in list_of_available_sources:
            idx_source = list_of_available_sources.index('ens')*2+1 # look for ensembl IDs
            if 'CHIP' in dataset:
                dataset.loc[id,'CHIP'] = database_name_source_list.loc[database_name_source_list.MEMBER_1_label=='ens','CHIP'].values[0] # replace source name in CHIP
        elif 'linc' in list_of_available_sources:
            idx_source = list_of_available_sources.index('linc')*2+1 # look for linc if ensembl IDs not present
            if 'CHIP' in dataset:
                dataset.loc[id,'CHIP'] = database_name_source_list.loc[database_name_source_list.MEMBER_1_label=='linc','CHIP'].values[0] # replace source name in CHIP
        else:
            idx_source = 1
            if 'CHIP' in dataset:
                dataset.loc[id,'CHIP'] = dff2.loc[id,0] # replace source name in CHIP
            
        dataset.loc[id,'MEMBERS_1'] = dff2.loc[id,idx_source] # replace pipped value
    return dataset

def get_MEMBER_name(dataset):
    dfsub = dataset.loc[dataset.MEMBERS_1.duplicated(keep=False)]
    for MEMBERS_1_duplicated in dfsub.MEMBERS_1:
        df = dfsub.MEMBERS_1.loc[dfsub.MEMBERS_1==MEMBERS_1_duplicated]
        if not df.empty:
            l = [np.sum([str(y)!='nan' for y in dataset.loc[x].values.tolist()]) for x in df.index] # number of pipped names available
            if len(l) > 1:
                min_ind = df.loc[l == np.min(l)].index
                dataset = dataset.drop(min_ind)
                dfsub = dfsub.drop(min_ind)
    return dataset


class MSigDBHandler(xml.sax.ContentHandler):
    
    def __init__(self):
        self.CurrentData = ""
        for i in col:
            exec('self.' + i + ' = ""') 

    ######################### START OF ELEMENT
    def startElement(self, tag,attributes):
        if tag == 'GENESET':
            # function that saves in an object the attributes found in each element
            self.CurrentData = tag
            # col: all possible columns to parse
            for i in col:
                __s__ = attributes[i]
                __s__ = __s__.replace("\"","")
                __s__ = 'self.' + i + ' = "' + __s__ + '"'
                exec(__s__)

    ######################### END OF ELEMENT:
    def endElement(self, tag):
        # function that take the self object, makes the corresponding dataframe and append it to file
        if tag == 'GENESET':
            
            for colnum,colint in enumerate(colin): # get columns of each table
                coldef = [not isinstance(out,float) for out in colint] # check for nans
                colindef = list(set([i for (i,v) in zip(colint,coldef) if v]))# get headers in input that map to something
                dtl = handler2list(self,colindef) # load data
                dt = list2df(dtl,colindef)

                __ci__ = colin[colnum]
                __co__ = colout[colnum]
                
                for cc  in colindef: # go through variables in table

                    ####### boolean indexation of configuration parameters for the current variable + strores the mapping between variables naming in and out:
                    mask = (vdict ['table'] == tables[colnum]) & (vdict.variable_in==cc) # find config requirements for the variable_in
                    cmap = [v for (i,v) in zip(__ci__,__co__) if i==cc]
                    cmap_length = len(cmap)                 
                    
                    ####### extract separator and verify it is the same for all subfields
                    sep_ptrn = list(set(vdict[mask].variable_sep_ptrn.values))
                    if len(sep_ptrn) != 1:
                        warnings.warn('separators are not the same for the same field')
                    else:
                        sep_ptrn = sep_ptrn[0]
                    
                    ####### extract current row value
                    dtcont = dt[cc].values[0]
                                                
                    if (not pd.isna(sep_ptrn)) & (sep_ptrn != []):# is existing tree separator -> create new headers

                        ####### extract subfields according to string pattern ptrn 
                        sp = extract_subfields(sep_ptrn,dtcont)
                        
                        ####### tuples length in sp:
                        if sp == []:
                            sp = [('')]
                            sp_length = 1
                        else:
                            sp_length = max([len(ss) for ss in sp]) # if not all separated values are assigned, create blanks

                        ####### fill output columns with blank when data missing
                        if (sp_length < cmap_length):
                            sp = np.concatenate([sp,np.repeat('',cmap_length-sp_length,axis=0)])
                            sp = [tuple(sp)]

                        ####### if output dimension smaller than input, remove the n-i last tuple members
                        if (sp_length > cmap_length):
                            sp = [x[0:cmap_length] for x in sp]

                        ####### from list of tuples to dataframe according to output column names mapping:
                        df = pd.DataFrame(sp,columns = cmap)
                        df_length = len(df)

                        ####### duplication of rows for all subfield created
                        if df_length>1:
                            dt = pd.DataFrame(dt.values.repeat(df_length, axis=0), columns=dt.columns)

                        ####### concatenation of created dataframe with current    
                        dt = pd.concat([dt, df], axis=1)
                        dt = dt.drop([cc], axis=1) # removing current column (duplicate)

                    
                if __ci__ != []: # if key is defined
                    d = pd.DataFrame(index = dt.index,columns=__co__) # create empty dataframe with columns placed as defined in config file
                    d.update(dt) # update data values in the appropriate columns when specified
                    d.to_csv(fp[colnum], mode = 'a', header = False, index=False)
        
        self.CurrentData = "" # reinitialize variable for next element
        for i in col:
            exec('self.' + i + ' = ""')

def parse_MSigDB(path_in,path_out,source_name,config_file,DB_source_file,part_size,headers_num,to_parse):

    global col, colin, colout, vdict, tables, fp

    print("loading config file...")
    vdict = pd.read_csv(config_file + ".csv",dtype=str,index_col=False) # load config file
    col = pd.Series(vdict.variable_in.values[vdict.variable_in.isnull()==False]).values # load in col the list of variables to parse
    col = list(set(col))
    tables = pd.Series(vdict.table.values).unique() # load in col the list of tables
    print("loading config file... done.")

    print("loading database sources LUT file...")
    dbdict = pd.read_csv(DB_source_file + ".csv",dtype=str,index_col=False) # load config file
    print("loading database sources LUT file... done.")

    print("create output files and write headers...")
    fp,colin,colout = write_headers(path_out,vdict, tables, to_parse)
    print("create output files and write headers...done.")

    if to_parse:
        ######################################## ENCODING:
        print("forcing file encoding...")
        encode2utf8(path_in,source_name,source_name + "_encoded")
        print("forcing file encoding...done.")
        
        ############## partition file in chuncks and UTF-8 encoding(to prevent overloading SAX buffer):
        print("partition file in chunks...")
        filepaths_partitions = file2parts(path_in + source_name + "_encoded",part_size,headers_num)
        print("partition file in chunks...done.")

        ######################################## INIT MSIGDB XML PARSER:
        print("parser initialization...")
        parser = xml.sax.make_parser()
        # turn off namepsaces
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        # override the default ContextHandler
        Handler = MSigDBHandler()
        parser.setContentHandler( Handler )
        print("parser initialization...done.")

        ######################################## PARSE FILE:
        print("parsing the file...this take a while, go get a coffee...")
        for partnum,part in enumerate(filepaths_partitions):
            try:
                parser.parse(part)
                print("Part " + str(partnum) + "...complete.")
                os.remove(part)
            except:
                print("could not parse the file partition " + str(partnum))
        print("parsing...done.")

    ######################################## READ CREATED TABLES, NORMALIZE AND SAVE:
    print("starting tables normalization...")
    fp_normalized = []
    for cpt,p in enumerate(fp):
        dt = pd.read_csv(p,dtype = {'MEMBERS_1':str}) # read csv

        ## remove duplicates
        dt_length_redundant = len(dt)
        dt = dt.drop_duplicates()

        ## find pipped gene names and replace by only one (by priority ensembl IDs, linc IDs, tc IDs):
        if ('MEMBERS_1' in dt):
            dt = replace_pipped_member_names(dt,dbdict) 

        ## find duplicated mapping in MEMBER table, take the row with most info:
        if tables[cpt] == 'MEMBER':
            dt = get_MEMBER_name(dt)
        print("normalization ended...")

        ## calculate amount of memory saving
        print("calculating memory saving...")
        dt_length_normalized = len(dt)
        print("Table ",tables[cpt], " : reduction of ",round((dt_length_redundant-dt_length_normalized)/dt_length_redundant*100,2), "%")

        ## save new tables
        print("saving tables...")
        fp_normalized.append(path_in + tables[cpt] + "_normalized.csv")
        dt.to_csv(fp_normalized[cpt], mode = 'w', header = True, index=False)
        print("saving tables...done.")


if ( __name__ == "__main__"):


    # TO RUN THIS FILE YOU NEED TO HAVE TWICE THE MEMORY OF THE FILE ON THE FILE SOURCE DISK AS THIS CODE WILL SPLIT THE FILE AND MAKE COPIES OF THE CHUNCKS

###################################################################### SCRIPT ####################################################################### 

    ######################### Variables initalization:
    p = os.path.split(sys.argv[0])[0]
    os.chdir(p)
    path_in = p + '/data/' # location for input .csv files
    source_name = 'msigdb_v7.4'
    config_file = "config_file"
    DB_IDs = "DB_IDs"
    part_size = 500
    headers_num = 4 # number of header lines expected in file 
    to_parse = False #True #
    parse_MSigDB(path_in,source_name,config_file,DB_IDs,part_size,headers_num,to_parse)






    
        


