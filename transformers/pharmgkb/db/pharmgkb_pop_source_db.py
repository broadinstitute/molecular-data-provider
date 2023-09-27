import sqlite3
import re
import pandas as pd
from collections import defaultdict
import os
import math



db_connection = sqlite3.connect("pharmgkb_source2.sqlite", check_same_thread=False)
db_connection.row_factory = sqlite3.Row
CHUNK_SIZE = 25000000
DO_IF_EXISTS = 'append'
nocase='NOCASE'

def exec():

### Genes
     df = pd.read_csv('genes/genes.tsv', sep="\t", header=None, names=['PharmGKB_Accession_Id','NCBI_Gene_ID','HGNC_ID','Ensembl_Id','Name','Symbol','Alternate_Names','Alternate_Symbols','Is_VIP','Has_Variant_Annotation','Cross_references','Has_CPIC_Dosing_Guideline','Chromosome','Chromosomal_Start_GRCh37','Chromosomal_Stop_GRCh37','Chromosomal_Start_GRCh38','Chromosomal_Stop_GRCh38'])
     fix_array_of_strings(df, 'Alternate_Symbols')
     fix_array_of_strings(df, 'Alternate_Names')
     fix_array_of_strings(df, 'Cross_references')
     df = df.set_index('PharmGKB_Accession_Id')         # set the 'PharmGKB Accession Id' column in file as the index
     df = df[1:] #take the data less the header row
     df.to_sql("genes", db_connection, if_exists=DO_IF_EXISTS, index=True)


##########################################################################################################################################
#   HOW TO USE:
#   The following ~110 lines of commented code is used to read from PharmGKB furnished .tsv data files to populate
#   corresponding data tables in a temporary SQLite database. Un-comment each set of code to run the reading and the table populating 
#   sequentially and separately.
# 
#  1. drugs table from 'drugs/drugs.tsv'
#  2. chemicals table from 'chemicals/chemicals.tsv'
#  3. phenotypes table from 'phenotypes/phenotypes.tsv'
#  4. relationships table from 'relationships/relationships.tsv'
#  5. automated_annotations table from 'automated_annotations/automated_annotations.tsv'
#  6. variant_gene_map table from 'automated_annotations/automated_annotations.tsv'
#  7. variant_gene_map table from 'variantAnnotations/var_drug_ann.tsv'
#  8. clinical_variants table from 'clinicalVariants/clinicalVariants.tsv'
#  9. variants table from 'variants/variants.tsv'
# 10. var_drug_ann table from 'variantAnnotations/var_drug_ann.tsv'
# 11. var_fa_ann table from 'variantAnnotations/var_fa_ann.tsv'
# 12. var_pheno_ann table from 'variantAnnotations/var_pheno_ann.tsv' 
# 	

### 1. Drugs
#    df = pd.read_csv('drugs/drugs.tsv', sep="\t", header=None, names=['PharmGKB_Accession_Id','Name','Generic_Names','Trade_Names','Brand_Mixtures','Type','Cross_references','SMILES','InChI','Dosing_Guideline','External_Vocabulary','Clinical_Annotation_Count','Variant_Annotation_Count','Pathway_Count','VIP_Count','Dosing_Guideline_Sources','Top_Clinical_Annotation_Level','Top_FDA_Label_Testing_Level','Top_Any_Drug_Label','Testing_Level','Label_Has_Dosing_Info','Has_Rx_Annotation','RxNorm_Identifiers','ATC_Identifiers', 'PubChem_Compound_Identifiers'])
#    fix_array_of_strings(df, 'Generic_Names')
    # fix_array_of_strings(df, 'Trade_Names')
    # fix_array_of_strings(df, 'Brand_Mixtures')
    # fix_array_of_strings(df, 'Cross_references')
    # fix_array_of_strings(df, 'External_Vocabulary')
    # fix_array_of_strings(df, 'RxNorm_Identifiers')
#    df = df.set_index('PharmGKB_Accession_Id')         # set the 'PharmGKB Accession Id' column in file as the index
#    df = df[1:] #take the data less the header row
#    df.to_sql("drugs", db_connection, if_exists=DO_IF_EXISTS, index=True)    

### 2. Chemicals
    # df = pd.read_csv('chemicals/chemicals.tsv', sep="\t", header=None, names=['PharmGKB_Accession_Id','Name','generic_name','trade_name','brand_mixture','Type','Cross_references','SMILES','InChI','Dosing_Guideline','External_Vocabulary','Clinical_Annotation_Count','Variant_Annotation_Count','Pathway_Count','VIP_Count','Dosing_Guideline_Sources','Top_Clinical_Annotation_Level','Top_FDA_Label_Testing_Level','Top_Any_Drug_Label_Testing_Level','Label_Has_Dosing_Info','Has_Rx_Annotation','RxNorm_Identifiers','ATC_Identifiers', 'PubChem_Compound_Identifiers'])
    # fix_array_of_strings(df, 'generic_name')
    # fix_array_of_strings(df, 'trade_name')
    # fix_array_of_strings(df, 'brand_mixture')
    # fix_array_of_strings(df, 'Cross_references')
    # fix_array_of_strings(df, 'External_Vocabulary')
    # fix_array_of_strings(df, 'RxNorm_Identifiers')
    # df = df.set_index('PharmGKB_Accession_Id')         # set the 'PharmGKB Accession Id' column in file as the index
    # df = df[1:] #take the data less the header row
    # df.to_sql("chemicals", db_connection, if_exists=DO_IF_EXISTS, index=True)   

### 3. Phenotypes
#     df = pd.read_csv('phenotypes/phenotypes.tsv', sep="\t", header=None, names=['PharmGKB_Accession_Id','Name','Alternate_Names','Cross_References','External_Vocabulary'])
#     fix_array_of_strings(df, 'Alternate_Names')
#     fix_array_of_strings(df, 'Cross_References')
#     fix_array_of_strings(df, 'External_Vocabulary')
#     df = df.set_index('PharmGKB_Accession_Id')         # set the 'PharmGKB Accession Id' column in file as the index
#     df = df[1:] #take the data less the header row
#     df.to_sql("phenotypes", db_connection, if_exists=DO_IF_EXISTS, index=True, chunksize=CHUNK_SIZE)

### 4. Relationships   
    # df = pd.read_csv('relationships/relationships.tsv', sep="\t", header=None, names=['Entity1_id','Entity1_name','Entity1_type','Entity2_id','Entity2_name','Entity2_type','Evidence','Association','PK','PD','PMIDs'])
    # df = df.set_index('Entity1_id')         # set the 'Entity1_id' column in file as the index
    # df = df[1:] #take the data less the header row
    # df.to_sql("relationships", db_connection, if_exists=DO_IF_EXISTS, index=True, chunksize=CHUNK_SIZE)

### 5. Automated Annotations
    # df = pd.read_csv('automated_annotations/automated_annotations.tsv', sep="\t", header=None, names=['Chemical_ID','Chemical_Name','Chemical_in_Text',	'Variation_ID',	'Variation_Name',	'Variation_Type',	'Variation_in_Text',	'Gene_IDs','Gene_Symbols','Gene_in_Text','Literature_ID','PMID','Literature_Title','Publication_Year','Journal','Sentence','Source'])
    # df = df.set_index('Chemical_ID')         # set the 'Chemical_ID' column in file as the index
    # df = df[1:] #take the data less the header row
    # df.to_sql("automated_annotations", db_connection, if_exists=DO_IF_EXISTS, index=True, chunksize=CHUNK_SIZE)

### 6. Variant-Gene Map from Automated Annotations
    # Assigned column names to the dataframe after reading the tsv file                                                                                             'Variation_ID',                                                                 'Gene_IDs', 'Variation_Name', 'Gene_Symbols'
    # source_df = pd.read_csv('automated_annotations/automated_annotations.tsv', sep="\t", header=None, names=['Chemical_ID','Chemical_Name','Chemical_in_Text',	'Variation_ID',	'Variation_Name',	'Variation_Type',	'Variation_in_Text',	'Gene_IDs','Gene_Symbols','Gene_in_Text','Literature_ID','PMID','Literature_Title','Publication_Year','Journal','Sentence','Source'])
    # map_dataframe = pd.DataFrame()
    # add_variant_gene_Ids(source_df, 'Variation_Name')
    # create_map(source_df, map_dataframe, 'Variation_ID', 'Gene_PharmGKB_Accession_Id', 'Variation_Name', 'Gene_Symbol')
    # map_dataframe = map_dataframe[1:] #take the data less the header row
    # map_dataframe.to_sql("variant_gene_map_source", db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

### 7. Variant-Gene Map from Variant-Drug Annotations
    # Assigned column names to the dataframe after reading the tsv file
    # 
    # source_df = pd.read_csv('variantAnnotations/var_drug_ann.tsv', sep="\t", header=None, names=[ 'Variant_Annotation_ID',	'Variant_Haplotypes',	'Gene',	'Drugs',	'PMID',	'Phenotype_Category',	'Significance',	'Notes',	'Sentence',	'Alleles',	'Specialty_Population'])
    # map_dataframe = pd.DataFrame()
    # add_variant_gene_Ids(source_df, 'Variant_Haplotypes')
    # create_map(source_df, map_dataframe, 'Variant_Id','Gene_PharmGKB_Accession_Id','Variant_Haplotypes','Gene_Symbol')
    # map_dataframe = map_dataframe[1:] #take the data less the header row
    # map_dataframe.to_sql("variant_gene_map_source", db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

### 8. clinical_variants
    # df = pd.read_csv('clinicalVariants/clinicalVariants.tsv', sep="\t", header=None, names=['Variant','Gene','Type','Level_Of_Evidence','Chemicals','Phenotypes'])
    # df = cleanup_clinical_variants(df)
    # df = df[1:] #take the data less the header row
    # df.to_sql("clinical_variants", db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

### 9. Variants
    # df = pd.read_csv('variants/variants.tsv', sep="\t", header=None, names=['Variant_ID','Variant_Name','Gene_IDs','Gene_Symbols','Location','Variant_Annotation_count','Clinical_Annotation_count','Level_1_2_Clinical_Annotation_count','Guideline_Annotation_count','Label_Annotation_count','Synonyms'])
    # df = df.set_index('Variant_ID')         # set the 'Variant_ID' column in file as the index
    # df = df[1:] #take the data less the header row
    # df.to_sql("variants", db_connection, if_exists=DO_IF_EXISTS, index=True, chunksize=CHUNK_SIZE)

### 10. var_drug_ann
    #  df = pd.read_csv('variantAnnotations/var_drug_ann.tsv', sep="\t", header=None, names=['Variant_Annotation_ID','Variant_or_Haplotypes','Gene','Drugs','PMID','Phenotype_Category','Significance','Notes','Sentence','Alleles','Specialty_Population'])
    #  fix_array_of_strings(df, 'Drugs')
    #  fix_array_of_strings(df, 'Phenotype_Category')
    #  fix_array_of_strings(df, 'Gene')
    #  df = cleanup_variant_drugs_annotation(df)
    #  df = df.set_index('Variant_Annotation_ID')         # set the 'Variant_Annotation_ID' column in file as the index
    #  df = df[1:] #take the data less the header row
    #  df.to_sql("var_drug_ann", db_connection, if_exists=DO_IF_EXISTS, index=True, chunksize=CHUNK_SIZE)

### 11. var_fa_ann
    # df = pd.read_csv('variantAnnotations/var_fa_ann.tsv', sep="\t", header=None, names=['Variant_Annotation_ID','Variant_or_Haplotypes','Gene','Drugs','PMID','Phenotype_Category','Significance','Notes','Sentence','Alleles','Specialty_Population'])
    # fix_array_of_strings(df, 'Drugs')
    # fix_array_of_strings(df, 'Phenotype_Category')
    # df = df.set_index('Variant_Annotation_ID')         # set the 'Variant_Annotation_ID' column in file as the index
    # df = df[1:] #take the data less the header row
    # df.to_sql("var_fa_ann", db_connection, if_exists=DO_IF_EXISTS, index=True, chunksize=CHUNK_SIZE)

### 12. var_pheno_ann
    # df = pd.read_csv('variantAnnotations/var_pheno_ann.tsv', sep="\t", header=None, names=['Variant_Annotation_ID','Variant_or_Haplotypes','Gene','Drugs','PMID','Phenotype_Category','Significance','Notes','Sentence','Alleles','Specialty_Population'])
    # fix_array_of_strings(df, 'Drugs')
    # fix_array_of_strings(df, 'Phenotype_Category')
    # df = df.set_index('Variant_Annotation_ID')         # set the 'Variant_Annotation_ID' column in file as the index
    # df = df[1:] #take the data less the header row
    # df.to_sql("var_pheno_ann", db_connection, if_exists=DO_IF_EXISTS, index=True, chunksize=CHUNK_SIZE)


#########################################################
#  Read all 206 pathway files  - NOT USED
# PharmGKB_Accession_Id
# Pathway
# From
# To	
# Reaction Type	
# Controller	
# Control Type	
# Cell Type	
# PMIDs	
# Genes	
# Drugs	
# Diseases	
# Summary
def get_pathways():
    # Get the list of all files and directories
    path = 'pathways-tsv'
    dir_list = os.listdir(path)
    # prints all files
    for index in range(len(dir_list)):
        if dir_list[index].find('tsv') > 0:
            split_array = dir_list[index].split('-')
            #print(split_array[0], ':', split_array[1][: split_array[1].find('.tsv')] ,':', dir_list[index])
            pathway = split_array[1][: split_array[1].find('.tsv')]
            #print(pathway)
            df = pd.read_csv(path+ '/' + dir_list[index], sep="\t", header=None, names=['From_','To_','Reaction_Type','Controller','Control_Type','Cell_Type','PMIDs','Genes','Drugs','Diseases','Summary'])
            df['PharmGKB_Accession_Id'] = split_array[0]
            df['Pathway'] = pathway
            df = df.set_index('PharmGKB_Accession_Id') 
            df = df[1:] #take the data less the header row
            df.to_sql("pathways", db_connection, if_exists=DO_IF_EXISTS, index=True)
db_connection.commit()


#########################################################
# Clean up data and Split up the comma-separated values
# into 
    # Variant_Annotation_ID TEXT,
    # Variant_or_Haplotypes TEXT,
    # Gene                  TEXT,
    # Drugs                 TEXT,
    # PMID                  TEXT,
    # Phenotype_Category    TEXT,
    # Significance          TEXT,
    # Notes                 TEXT,
    # Sentence              TEXT,
    # Alleles               TEXT,
    # Specialty_Population  TEXT 
#'Variant_Annotation_ID','Variant_or_Haplotypes','Gene','Drugs','PMID','Phenotype_Category','Significance','Notes','Sentence','Alleles','Specialty_Population
#
def cleanup_variant_drugs_annotation(dataframe):
    Variant_Annotation_ID_array = []
    Variant_or_Haplotypes_array = []
    Gene_array = []
    Drugs_array = []
    Phenotype_Category_array = []
    Significance_array = []
    Notes_array = []
    Sentence_array = []
    Alleles_array = []
    Specialty_Population_array = []
    dict = {
            'Variant_Annotation_ID': Variant_Annotation_ID_array,
            'Variant_or_Haplotypes': Variant_or_Haplotypes_array,            
            'Gene' : Gene_array,
            'Drug' : Drugs_array,
            'Phenotype_Category' : Phenotype_Category_array,
            'Significance' : Significance_array,
            'Notes' : Notes_array,
            'Sentence' : Sentence_array,
            'Alleles' : Alleles_array,
            'Specialty_Population' : Specialty_Population_array
    }
    for row in range(len(dataframe)):  
        variant_split_array = breakup_array(dataframe['Variant_or_Haplotypes'][row], ',')
        drugs_split_array = breakup_array(dataframe['Drugs'][row], ',"')
        for drug_index in range(len(drugs_split_array)):
            if drugs_split_array[drug_index].find('"') == 0:
                    drug_string = find_between(drugs_split_array[drug_index],'"','"')
            else:
                    drug_string = drugs_split_array[drug_index].strip('"')
            for index in range(len(variant_split_array)):
                Variant_Annotation_ID_array.append(dataframe['Variant_Annotation_ID'][row])
                Variant_or_Haplotypes_array.append(variant_split_array[index].strip())
                Gene_array.append(dataframe['Gene'][row])
                Drugs_array.append(drug_string)
                Phenotype_Category_array.append(dataframe['Phenotype_Category'][row])
                Significance_array.append(dataframe['Significance'][row])
                Notes_array.append(dataframe['Notes'][row])
                Sentence_array.append(dataframe['Sentence'][row])
                Alleles_array.append(dataframe['Alleles'][row])
                Specialty_Population_array.append(dataframe['Specialty_Population'][row])

    new_df = pd.DataFrame(dict) 
    return new_df



#########################################################
# Clean up data and Split up the comma-separated values
# into rows
#
def cleanup_clinical_variants(dataframe):
    Variant_array = []
    Gene_array = []
    Type_array = []
    Level_of_Evidence_array = []
    Chemicals_array = []
    Phenotypes_aray = []
    dict = {
            'Variant': Variant_array,
            'Gene' : Gene_array,
            'Type' : Type_array,
            'Level_of_Evidence' : Level_of_Evidence_array,
            'Chemicals' : Chemicals_array,
            'Phenotypes' : Phenotypes_aray
    }
    for row in range(len(dataframe)):
        if str(dataframe['Variant'][row]) == 'nan':
            dataframe['Variant'][row] = None
        else:
            variant_split_array = str(dataframe['Variant'][row]).split(',')
            chemical_stirng = str(dataframe['Chemicals'][row]).replace(', ', '#@#')  # hide ', ' substring as in "Ace Inhibitors, Plain"
            chemical_split_array = chemical_stirng.split(',')
            if chemical_split_array != None :
                for chem_index in range(len(chemical_split_array)):
                    chemical = chemical_split_array[chem_index].replace('#@#',', ') # unhide ', ' substring as in "Ace Inhibitors, Plain"
                    if variant_split_array != None :
                        for index in range(len(variant_split_array)):
                            Variant_array.append(variant_split_array[index])
                            Gene_array.append(dataframe['Gene'][row])
                            Type_array.append(dataframe['Type'][row])
                            Level_of_Evidence_array.append(dataframe['Level_Of_Evidence'][row])
                            Chemicals_array.append(chemical)
                            Phenotypes_aray.append(dataframe['Phenotypes'][row])
                    else:
                        Variant_array.append(dataframe['Variant'][row])
                        Gene_array.append(dataframe['Gene'][row])
                        Type_array.append(dataframe['Type'][row])
                        Level_of_Evidence_array.append(dataframe['Level_Of_Evidence'][row])
                        Chemicals_array.append(dataframe['Chemicals'][row])
                        Phenotypes_aray.append(dataframe['Phenotypes'][row])

  
    new_df = pd.DataFrame(dict) 
    return new_df





#########################################################
# 
#  Add Variation_IDs, Gene_IDs, & Gene_Symbols to source_df
# (which are missing in the var_drug_ann tsv file)
#
# 
def add_variant_gene_Ids(source_df, Variant_Haplotypes):
    Variant_ID_list = []
    Gene_ID_list = []
    Gene_Symbol_list = []
    for i in range(len(source_df)):
        variant_haplotypes_string = source_df[Variant_Haplotypes][i]
        print(variant_haplotypes_string)
        var_tuple = get_variant_id(variant_haplotypes_string)
        if var_tuple != None:
            variant_id, gene_id, gene_symbol = var_tuple
            print('variant_id',variant_id, 'gene_id',gene_id, 'gene_symbol', gene_symbol)
            Variant_ID_list.append(variant_id)
            Gene_ID_list.append(gene_id)
            Gene_Symbol_list.append(gene_symbol)
        else:
            Variant_ID_list.append('')
            Gene_ID_list.append('')
            Gene_Symbol_list.append('')
    source_df['Variant_Id'] = Variant_ID_list
    source_df['Gene_PharmGKB_Accession_Id'] = Gene_ID_list
    source_df['Gene_Symbol'] = Gene_Symbol_list

        # if variant_haplotypes_string.find(',') > -1 :
        #     variant_id_list = variant_haplotypes_string.split(',')
        #     for index in range(len(variant_id_list)):
        #         print('1:  ',variant_id_list[index].strip(' '))
        #         tuple = get_variant_id(variant_id_list[index])
        #         if tuple != None:
        #             variant_id, gene_id, gene_symbol = tuple
        #             if gene_id != None and gene_id.find(',') > -1:
        #                 gene_id_list = gene_id.split(',')
        #                 gene_symbol_list = gene_symbol.split(',')
        #                 for index in range(len(gene_id_list)):
        #                     print()
        #                  #print('variant_id',variant_id, 'gene_id',gene_id_list[index], 'gene_symbol', gene_symbol_list[index])
        #             else:
        #                 if gene_id == None:
        #                     print
        #                     #print('variant_id',variant_id, 'NONE gene_id',gene_id, 'gene_symbol', gene_symbol)
        #         else:
        #             print('-----', '-----', '-----' )
        #             tuple1 = lookup_map(variant_id_list[index])
        #             if tuple1 != None:
        #                 variant_id, gene_id, gene_symbol = tuple1
        #               #  print('variant_id',variant_id, 'gene_id',gene_id, 'gene_symbol', gene_symbol)
        #             else:
        #                 print('-----', '-----', '-----' )
        # else:
        #     print('2. ',variant_haplotypes_string)
        #     tuple2 = get_variant_id(variant_haplotypes_string)
            
        #     if tuple2 != None:
        #         variant_id, gene_id, gene_symbol = tuple2
        #         print('variant_id',variant_id, 'NONE gene_id',gene_id, 'gene_symbol', gene_symbol)
        #     else:
        #         print('-----', '-----', '-----' )


#########################################################
#
# Get variant_id from variant_name
#
def get_variant_id(variant_name):
    query =  """
        SELECT DISTINCT Variant_ID, Variant_Name, Gene_IDs, Gene_Symbols
        FROM variants 
        WHERE variants.Variant_Name = ?
        """
    cur = db_connection.cursor()
    cur.execute(query,(variant_name,))
    for row in cur.fetchall():
       return (row['Variant_ID'],row['Gene_IDs'],row['Gene_Symbols'])






#########################################################
#  get Variation IDs, Gene IDs, Variant Name, Gene Symbol
#  for insertion into variant-gene-map table
#
#                                       'Variant_Id','Gene_PharmGKB_Accession_Id','Variant_Haplotypes','Gene_Symbol')
def create_map(source_df, map_dataframe, variant_column, gene_column, variant_name, gene_symbol_column):
    Variant_ID_list = []
    Variant_Name_list = []
    Gene_ID_list = []
    Gene_Symbol_list = []
    for row_idx in range(len(source_df)):
        variant_string = source_df[variant_column][row_idx]
        if  not pd.isna(variant_string):
          #  print(source_df[variant_column][i])
            if pd.isna(source_df[gene_column][row_idx]):
                source_df[gene_column][row_idx] = None
            split_geneID_list = breakup_array(source_df[gene_column][row_idx], ',')
            if split_geneID_list != None and len(split_geneID_list) > 1:
                split_geneSym_list = breakup_array(source_df[gene_symbol_column][row_idx], ',')
                for index in range(len(split_geneID_list)):
                    Gene_ID_list.append(split_geneID_list[index])
                    Variant_ID_list.append(source_df[variant_column][row_idx])
                    Variant_Name_list.append(source_df[variant_name][row_idx])
                    Gene_Symbol_list.append(split_geneSym_list[index])
                    print('gene_id', split_geneID_list[index], 'gene_symbol', split_geneSym_list[index])
            else:
                Gene_ID_list.append(source_df[gene_column][row_idx])
                Variant_ID_list.append(source_df[variant_column][row_idx])
                Variant_Name_list.append(source_df[variant_name][row_idx])
                Gene_Symbol_list.append(source_df[gene_symbol_column][row_idx])
    map_dataframe['Variant_Id'] = Variant_ID_list
    map_dataframe['Gene_PharmGKB_Accession_Id'] = Gene_ID_list
    map_dataframe['Variant_Name'] = Variant_Name_list
    map_dataframe['Gene_Symbol'] = Gene_Symbol_list




#########################################################
# Fix a column that has a list of values such as:
# CYP2A7P1,"CYP2B6"
# and changed it to:
# "CYP2A7P1","CYP2B6"
# by adding quotes around the first element
#
def fix_array_of_strings(dataframe, column):
    for i in range(len(dataframe)):
        fixed_array = ''
        if str(dataframe[column][i]) == 'nan':
            dataframe[column][i] = None
        else:
            split_array = str(dataframe[column][i]).split(',"')
            for index in range(len(split_array)):
                # Check each split_array[i] for quotes
                # and then recombine as an array

            #    print(split_array[index])
                if index == 0:
                    new_string = '"' + split_array[index] + '"'
                    split_array[0] = new_string
                if (index < len(split_array) - 1):
                    fixed_array = (fixed_array + split_array[index] + ',"')
                else:
                    fixed_array = (fixed_array + split_array[index])
            dataframe[column][i] = fixed_array



def create_index(table, column, colate=None):                                                                                                                                                                                                                                                                                   
    colate_nocase = 'COLLATE ' + nocase if colate == nocase else ''
    stmt = """
        CREATE INDEX {}_{}_idx 
        ON {} ({} {});    
    """.format(table, column,table, column, colate_nocase)
    cur = db_connection.cursor()
 #   print(stmt)
    cur.executescript(stmt)
    cur.close()



#########################################################
# Just split up the comma-separated name values
#
def breakup_array(name_row, delimiter):
    if name_row != None:
        return name_row.split(delimiter)
    else:
        return None



############################################################
#
# Ad hoc function to list the generic names that contain
# strings surrounded by '[' and ']' and write to a text file
#
def get_generic_names(table):
    query = """
        SELECT Generic_Names
        FROM {}
    """.format(table)
    cur = db_connection.cursor()
    cur.execute(query)
    output = table + '.txt'
    with open(output, 'w') as f:
        for row in cur.fetchall():
            split_array = str(row['Generic_Names']).split(',"')
            for index in range(len(split_array)):
                if split_array[index].find("]") != -1:
                  #  print(split_array[index])
                    if ( len(str(split_array[index])) - split_array[index].find("]") ) == 2:
                        f.write(split_array[index] + " : " + str(split_array[index].find("]")) + ':' +  str(len(str(split_array[index]))) + '\r')




#########################################################
#
# Find a string betweewn 'first' and 'last' characters
#
def find_between( s, first_char, last_char ):
    try:
        start = s.index( first_char ) + len( first_char )
        end = s.index( last_char, start )
        return s[start:end]
    except ValueError:
        return ""



def main():
    exec()


    # csv_files = sys.argv[1]

    # with db_connection:
    #     with open(csv_files,'r') as f:
    #         for csv_file in f:
    #             print(csv_file.rstrip())
    #             exec(csv_file.rstrip())

    #sql_files = sys.argv[1]
    #with db_connection:
        # with open(sql_files,'r') as f:
        #     for sql_file in f:
        #         print(sql_file.rstrip())
        #         exec(sql_file.rstrip())



if __name__ == '__main__':
    main()