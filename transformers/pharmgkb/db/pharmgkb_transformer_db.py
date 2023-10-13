import sqlite3
import re
import pandas as pd
import langcodes
from langcodes import *
from collections import defaultdict
import os
import requests
import json
import re
import time

source_db_connection = sqlite3.connect("pharmgkb_source2.sqlite", check_same_thread=False)
source_db_connection.row_factory = sqlite3.Row
transformer_db_connection = sqlite3.connect("pharmgkb.sqlite", check_same_thread=False)
transformer_db_connection.row_factory = sqlite3.Row
A_connection = sqlite3.connect("pharmgkb_A.sqlite", check_same_thread=False)
A_connection.row_factory = sqlite3.Row

CHUNK_SIZE = 25000
DO_IF_EXISTS = 'append'
nocase='NOCASE'

def exec():
    print('exec')


##########################################################################################################################################
#   HOW TO USE:
#   The following ~1500 lines of commented code is for data wrangling the data from the PharmGKB SQLite source database.
#   The results are saved to the "Source" PharmGKB SQLite database. It was later used for additional data wrangling and
#   for populating the PharmGKB Transformer's SQLite database.
#   Un-comment each set of code to run the reading and the table populating sequentially and separately.
# 
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

#    compare_pubchem_columns()
# 


#   var_fa_ann from source db copied to Variant table


#   var_pheno_ann from source db copied to Variant table


#   clinical_variants from source db copied to Variant table


# Fix Variant IDs
#    variant_dataframe = pd.DataFrame()
#    fix_variant_id(variant_dataframe)
#    variant_dataframe.to_sql("variant_test", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


# Copy from variant_gene_map to Variant table
    # variant_dataframe = pd.DataFrame()
    # copy_variant_genes(variant_dataframe)
    # variant_dataframe.to_sql("variant", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


#   Variant_Gene_Map data from var_drug_ann table
    # variant_dataframe = pd.DataFrame()
    # get_variants_genes(variant_dataframe, 'var_drug_ann')
    # variant_dataframe.to_sql("variant_gene_map", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


#   Variant_Gene_Map data from source db table
    # variant_dataframe = pd.DataFrame()
    # get_variants_genes(variant_dataframe, 'variant_gene_map_source')
    # variant_dataframe.to_sql("variant_gene_map", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


#   Variant_Gene_Map data contaminated with bad data from automated annotation.tsv, e.g., wrong Gene IDs associated with Gene Symbols
#   Gene_IDs	        Gene_Symbols
#   PA245,PA26551	    CLCN6,MTHFR
    # variant_dataframe = pd.DataFrame()
    # fix_genes_id(variant_dataframe, 'variant_gene_map')
    # variant_dataframe.to_sql("variant_gene_map_new", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


#   Generic_Names
    # names_df = pd.DataFrame()
    # get_names('generic_name','chemicals',names_df)
    # names_df.to_sql("synonym", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Trade_Names
    # names_df = pd.DataFrame()
    # get_names('trade_name','chemicals', names_df)
    # names_df.to_sql("synonym", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Brand_Mixture
    # names_df = pd.DataFrame()
    # get_names('brand_mixture','chemicals',names_df)
    # names_df.to_sql("synonym", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   External_Vocabulary
#   chemicals, phenotypes
    # identifiers_df = pd.DataFrame()
#    names_df = get_external_vocabulary('phenotypes', identifiers_df)
#    identifiers_df.to_sql("identifier", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    # names_df.to_sql("synonym", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   SMILES
#   chemicals
    # identifiers_df = pd.DataFrame()
    # get_smiles('chemicals', identifiers_df)
    # identifiers_df.to_sql("identifier", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   InChI
    # identifiers_df = pd.DataFrame()
    # get_inchi('chemicals', identifiers_df)
    # identifiers_df.to_sql("identifier", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   genes.alternate_name  
#   genes.alternate_symbol   
    # names_df = get_alternates('alternate_name', 'genes')
    # names_df.to_sql("synonym", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Identifiers
#   chemicals, genes
    # identifiers_df = pd.DataFrame()
    # get_identifiers('chemicals', identifiers_df)
    # identifiers_df.to_sql("identifier", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
#     identifiers_df = pd.DataFrame()
    # get_identifiers('genes', identifiers_df)
    # identifiers_df.to_sql("identifier", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Chemical
#    chemical_df = get_chemicals()
#    chemical_df.to_sql("chemical", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Variant
#    variant_df = get_variants()
#    variant_df.to_sql("variant", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Relationship
#    variant_df = get_relationships()
#    variant_df.to_sql("relationship", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Gene
#    gene_df = get_genes()
#    gene_df.to_sql("gene", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Automated_annotation
#    annotations_df =  get_auto_annotations()
#    annotations_df.to_sql("automated_annotation", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

#   Clinical_variant
#    clin_variants_df =  get_clinical_variants()
#    clin_variants_df.to_sql("clinical_variant", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


#   Variant_Drug_annotation
    # variant_drug_df = pd.DataFrame()
    # get_variant_drug_ann(variant_drug_df)
    # variant_drug_df.to_sql("var_drug_ann", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


# Fix Variant_Gene_Map table where some of the Variant IDs should be Variant_PharmGKB_Accession_ID
# instead of dsSNP IDs, e.g., DBSNP:rs77149876
    # variant_dataframe = pd.DataFrame()
    # fix_variants_genes(variant_dataframe)
    # variant_dataframe.to_sql("variant_gene_map_new", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


# Recover data from previous version of variant_gene_map  --- THROWAWAY code
    variant_dataframe = pd.DataFrame()
    recover_variant_gene_map(variant_dataframe)
    variant_dataframe.to_sql("variant_gene_map", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)

# Recover data from variant  --- THROWAWAY code
    # variant_dataframe = pd.DataFrame()
    # recover_variants(variant_dataframe)
    # variant_dataframe.to_sql("variant_gene_map", transformer_db_connection, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)


def recover_variants(variant_dataframe):
    query = """
            SELECT DISTINCT
                PharmGKB_Accession_Id,
                Variant_Name,
                Gene_PharmGKB_Accession_Id,
                Gene_Symbol,
                Location
            FROM variant
            """    
    cur = A_connection.cursor()
    cur.execute(query,())
    variation_id_list      = []
    variant_name_list      = []
    variant_location_list  = [] 
    gene_pharmGKB_accession_id_list = [] 
    gene_symbol_list = []
    for row in cur.fetchall():
        if must_recover(row['Variant_Name'], row['Gene_Symbol']):
            variant_id = row['PharmGKB_Accession_Id']
            variation_id_list.append(variant_id)
            variant_name_list.append(row['Variant_Name'])
            variant_location_list.append(row['Location']) 
            gene_pharmGKB_accession_id_list.append(row['Gene_PharmGKB_Accession_Id'])
            gene_symbol_list.append(row['Gene_Symbol'])   
    variant_dataframe['Variation_Id']     = variation_id_list
    variant_dataframe['Variant_Name']     = variant_name_list
    variant_dataframe['Variant_Location'] = variant_location_list
    variant_dataframe['Gene_PharmGKB_Accession_Id']    = gene_pharmGKB_accession_id_list
    variant_dataframe['Gene_Symbol']    =  gene_symbol_list 


def must_recover(variant_name, gene_symbol):
    must_recover = False
    rowcount = 0
    query_0 = """
            SELECT DISTINCT
                Variation_Id,
                Variant_Name,
                Variant_Location,
                Gene_PharmGKB_Accession_Id,
                Gene_Symbol
            FROM variant_gene_map
            WHERE Variant_Name = ?
            """   
    normal_gene_symbol = ' AND Gene_Symbol = ?'
    null_gene_symbol = ' AND Gene_Symbol ISNULL'
    cur = transformer_db_connection.cursor()
    if gene_symbol == None:
        query = query_0 + null_gene_symbol
        cur.execute(query,(variant_name,))
    else:
        query = query_0 + normal_gene_symbol
        cur.execute(query,(variant_name,gene_symbol,))

    for row in cur.fetchall():
        rowcount = rowcount + 1
    
    if rowcount < 1:  # not found a record or the variant id is blank
        must_recover = True
    else:
        must_recover = False
    return must_recover



def recover_variant_gene_map(variant_dataframe):
    query = """
            SELECT DISTINCT
                Variation_Id,
                Variant_Name,
                Variant_Location,
                Gene_PharmGKB_Accession_Id,
                Gene_Symbol
            FROM variant_gene_map_new
            """    
    cur = transformer_db_connection.cursor()
    cur.execute(query,())
    variation_id_list      = []
    variant_name_list      = []
    variant_location_list  = [] 
    gene_pharmGKB_accession_id_list = [] 
    gene_symbol_list = []
    for row in cur.fetchall():
        variant_id = row['Variation_Id']
        variation_id_list.append(variant_id)
        variant_name_list.append(row['Variant_Name'])
        variant_location_list.append(row['Variant_Location']) 
        gene_pharmGKB_accession_id_list.append(row['Gene_PharmGKB_Accession_Id'])
        gene_symbol_list.append(row['Gene_Symbol'])   
    variant_dataframe['Variation_Id']     = variation_id_list
    variant_dataframe['Variant_Name']     = variant_name_list
    variant_dataframe['Variant_Location'] = variant_location_list
    variant_dataframe['Gene_PharmGKB_Accession_Id']    = gene_pharmGKB_accession_id_list
    variant_dataframe['Gene_Symbol']      =  gene_symbol_list 




#########################################################
# Retrieve variant-gene from map in db
# The Variant table will provide the proper Variant_PharmGKB_Accession_ID
# by calling "get_variant_id(row['Variant_Name'])"
#
def fix_variants_genes(variant_dataframe):
    print('fix_variants_genes')
    query = """
            SELECT DISTINCT
                Variation_Id,
                Variant_Name,
                Variant_Location,
                Gene_PharmGKB_Accession_Id,
                Gene_Symbol
            FROM variant_gene_map
            """
    cur = transformer_db_connection.cursor()
    cur.execute(query,())
    variation_id_list      = []
    variant_name_list      = []
    variant_location_list  = [] 
    gene_pharmGKB_accession_id_list = [] 
    gene_symbol_list = []

    for row in cur.fetchall():
        if row['Variation_Id'].startswith('DBSNP') or row['Variation_Id'].startswith('rs'):
            variant_id = get_variant_id(row['Variant_Name'])
        else:
            variant_id = row['Variation_Id']
        variation_id_list.append(variant_id)
        variant_name_list.append(row['Variant_Name'])
        variant_location_list.append(row['Variant_Location']) 
        gene_pharmGKB_accession_id_list.append(row['Gene_PharmGKB_Accession_Id'])
        gene_symbol_list.append(row['Gene_Symbol'])    
    variant_dataframe['Variation_Id']     = variation_id_list
    variant_dataframe['Variant_Name']     = variant_name_list
    variant_dataframe['Variant_Location'] = variant_location_list
    variant_dataframe['Gene_PharmGKB_Accession_Id']    = gene_pharmGKB_accession_id_list
    variant_dataframe['Gene_Symbol']    =  gene_symbol_list       
     

#########################################################
# Retrieve variant-gene from map in source db
# Find missing genes of variants to populate the
# variant_gene_map table of transformer db.
#
def get_variant_drug_ann(variant_drug_dataframe):
        query = """
            SELECT DISTINCT
                Variant_Annotation_ID,
                Variant_or_Haplotypes,
                Gene,
                Drug,
                PMID,
                Phenotype_Category,
                Significance,
                Notes,
                Sentence,
                Alleles,
                Specialty_Population
            FROM var_drug_ann
            """
        cur = source_db_connection.cursor()
        cur.execute(query,())  
        chemical_pharmGKB_accession_id_list = []
        variant_pharmGKB_accession_id_list  = []
        gene_pharmGKB_accession_id_list     = [] 
        variant_annotation_id_list          = []
        variant_or_haplotypes_list          = [] 
        gene_list   = []
        drug_list   = [] 
        pmid_list   = []
        phenotype_category_list   = [] 
        significance_list = []
        notes_list    = [] 
        sentence_list = []
        alleles_list  = []
        specialty_population_list  = []       
        for row in cur.fetchall():
                split_list = breakup_array(row['Gene'], ',"')
                if split_list != None :
                    for index in range(len(split_list)):
                        chemical_pharmGKB_accession_id_list.append(get_chemical_id(row['Drug']))  
                        variant_pharmGKB_accession_id_list.append(get_variant_id(row['Variant_or_Haplotypes']))   
                        gene_pharmGKB_accession_id_list.append(get_gene_id(split_list[index].strip('"')))
                        variant_annotation_id_list.append(row['Variant_Annotation_ID'])
                        variant_or_haplotypes_list.append(row['Variant_or_Haplotypes'])
                        gene_list.append(split_list[index].strip('"'))
                        drug_list.append(row['Drug'])
                        pmid_list.append(row['PMID'])
                        phenotype_category_list.append(row['Phenotype_Category'])
                        significance_list.append(row['Significance'])
                        notes_list.append(row['Notes'])
                        sentence_list.append(row['Sentence'])
                        alleles_list.append(row['Alleles'])
                        specialty_population_list.append(row['Specialty_Population']) 
                else:
                    if row['Gene'] != None:
                         gene_symbol = row['Gene']
                    else:
                         print('else, no gene name')
                    chemical_pharmGKB_accession_id_list.append(get_chemical_id(row['Drug']))  
                    variant_pharmGKB_accession_id_list.append(get_variant_id(row['Variant_or_Haplotypes']))   
                    gene_pharmGKB_accession_id_list.append(get_gene_id(gene_symbol))
                    variant_annotation_id_list.append(row['Variant_Annotation_ID'])
                    variant_or_haplotypes_list.append(row['Variant_or_Haplotypes'])
                    gene_list.append(gene_symbol)
                    drug_list.append(row['Drug'])
                    pmid_list.append(row['PMID'])
                    phenotype_category_list.append(row['Phenotype_Category'])
                    significance_list.append(row['Significance'])
                    notes_list.append(row['Notes'])
                    sentence_list.append(row['Sentence'])
                    alleles_list.append(row['Alleles'])
                    specialty_population_list.append(row['Specialty_Population'])                
        variant_drug_dataframe['Chemical_PharmGKB_Accession_ID'] = chemical_pharmGKB_accession_id_list 
        variant_drug_dataframe['Variant_PharmGKB_Accession_ID']  = variant_pharmGKB_accession_id_list
        variant_drug_dataframe['Gene_PharmGKB_Accession_ID']     = gene_pharmGKB_accession_id_list
        variant_drug_dataframe['Variant_Annotation_ID'] = variant_annotation_id_list
        variant_drug_dataframe['Variant_or_Haplotypes'] = variant_or_haplotypes_list
        variant_drug_dataframe['Gene'] = gene_list
        variant_drug_dataframe['Drug'] = drug_list
        variant_drug_dataframe['PMID'] = pmid_list
        variant_drug_dataframe['Phenotype_Category']   = phenotype_category_list
        variant_drug_dataframe['Significance']         = significance_list
        variant_drug_dataframe['Notes']                = notes_list
        variant_drug_dataframe['Sentence']             = sentence_list
        variant_drug_dataframe['Alleles']              = alleles_list
        variant_drug_dataframe['Specialty_Population'] = specialty_population_list
    







#########################################################
# Retrieve retrieve InChI strings from a table
#
def get_inchi(table, identifier_df):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id, InChI
        FROM {}
    """.format(table)
    cur = source_db_connection.cursor()
    cur.execute(query,())
    id_list    = []
    prefix_list = []
    xref_list   = []
    for row in cur.fetchall():
        if row['InChI'] != None:
            id_list.append(row['PharmGKB_Accession_Id'])
            prefix_list.append('InChI')
            xref_list.append(row['InChI'])
    identifier_df['PharmGKB_Accession_Id'] = id_list
    identifier_df['Prefix'] = prefix_list
    identifier_df['Xref'] = xref_list


#########################################################
# Retrieve retrieve SMILE strings from a table
#
def get_smiles(table, identifier_df):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id, SMILES
        FROM {}
    """.format(table)
    cur = source_db_connection.cursor()
    cur.execute(query,())
    id_list    = []
    prefix_list = []
    xref_list   = []
    for row in cur.fetchall():
        if row['SMILES'] != None:
            id_list.append(row['PharmGKB_Accession_Id'])
            prefix_list.append('SMILES')
            xref_list.append(row['SMILES'])
    identifier_df['PharmGKB_Accession_Id'] = id_list
    identifier_df['Prefix'] = prefix_list
    identifier_df['Xref'] = xref_list


#########################################################
# Retrieve Relationships and Automated annotations
#
def get_clinical_variants():
    query = """
        SELECT DISTINCT
            Variant,
            Gene,
            Type,
            Level_of_Evidence,
            Chemicals,
            Phenotypes,
            Evidence,
            Association,
            Pharmacokinetic,
            Pharmacodynamic,
            relation_PMIDs
        FROM clinical_variants
        LEFT JOIN relationships ON clinical_variants.Variant = relationships.Entity1_name
        AND clinical_variants.Chemicals = relationships.Entity2_name;
        """
    cur = source_db_connection.cursor()
    cur.execute(query,())
    Variant_list = []
    Gene_list = []
    Type_list = []
    Level_of_Evidence_list = []
    Chemical_list = []
    Phenotype_list = []
    Evidence_list = []
    Association_list = []
    Pharmacokinetics_list = []
    Pharmacodynamics_list = []
    relation_PMIDs_list = []
    dict = {
            'Variant': Variant_list,
            'Gene' : Gene_list,
            'Type' : Type_list,
            'Level_of_Evidence' : Level_of_Evidence_list,
            'Chemical' : Chemical_list,
            'Phenotype' : Phenotype_list,
            'Evidence'  : Evidence_list,
            'Association' : Association_list,
            'Pharmacokinetics' : Pharmacokinetics_list,
            'Pharmacodynamics' : Pharmacodynamics_list,
            'relation_PMIDs'   : relation_PMIDs_list          
    }
    for row in cur.fetchall():
            Variant_list.append(str(row['Variant']).strip())
            Gene_list.append(row['Gene'])
            Type_list.append(row['Type'])
            Level_of_Evidence_list.append(row['Level_Of_Evidence'])
            Chemical_list.append(row['Chemicals'])
            Phenotype_list.append(row['Phenotypes'])
            Evidence_list.append(row['Evidence'])
            Association_list.append(row['Association'])
            Pharmacokinetics_list.append(row['Pharmacokinetic'])
            Pharmacodynamics_list.append(row['Pharmacodynamic'])
            relation_PMIDs_list .append(row['relation_PMIDs'])
    df = pd.DataFrame(dict)   
    return df  



#########################################################
# Retrieve rows from var_pheno table of transformer, add
# the 'DBSNP:' prefix and then import into variant
def get_variant_from_pheno(variant_dataframe):
    query = """
    SELECT 
        Variant_or_Haplotypes,
        Gene,
        Drugs,
        PMID,
        Phenotype_Category,
        Significance,
        Notes,
        Sentence,
        Alleles,
        Specialty_Population
    FROM var_pheno_ann
        """


#########################################################
# Retrieve rows from variant table of transformer, add
# the 'DBSNP:' prefix and then import into variant_test 
# table.
# 
#
def fix_variant_id(variant_dataframe):
    query = """
    SELECT 
        PharmGKB_Accession_Id,
        Variant_Name,
        Gene_PharmGKB_Accession_Id,
        Gene_Symbol,
        Location,
        Clinical_Annotation_Count,
        Variant_Annotation_Count,
        Level_1_2_Clinical_Annotation_count,
        Label_Annotation_count
    FROM variant
    """
    PharmGKB_Accession_Id_list = []
    Variant_Name_list = []
    Gene_PharmGKB_Accession_Id_list = []
    Gene_Symbol_list = []
    Location_list = []
    Clinical_Annotation_Count_list = []
    Variant_Annotation_Count_list = []
    Level_1_2_Clinical_Annotation_count_list = []
    Label_Annotation_count_list = []
    cur = transformer_db_connection.cursor()
    cur.execute(query,())
    for row in cur.fetchall():
        if row['PharmGKB_Accession_Id'].startswith('rs'):
            variant_id = 'DBSNP:' + row['PharmGKB_Accession_Id']
        else:
            variant_id = row['PharmGKB_Accession_Id']
        PharmGKB_Accession_Id_list.append(variant_id)
        Variant_Name_list.append(row['Variant_Name'])
        Gene_PharmGKB_Accession_Id_list.append(row['Gene_PharmGKB_Accession_Id']) 
        Gene_Symbol_list.append(row['Gene_Symbol'])     
        Location_list.append(row['Location'])
        Clinical_Annotation_Count_list.append(row['Clinical_Annotation_Count'])
        Variant_Annotation_Count_list.append(row['Variant_Annotation_Count'])
        Level_1_2_Clinical_Annotation_count_list.append(row['Level_1_2_Clinical_Annotation_count'])
        Label_Annotation_count_list.append(row['Label_Annotation_count'])
    variant_dataframe['PharmGKB_Accession_Id'] = PharmGKB_Accession_Id_list
    variant_dataframe['Variant_Name'] = Variant_Name_list
    variant_dataframe['Gene_PharmGKB_Accession_Id'] = Gene_PharmGKB_Accession_Id_list
    variant_dataframe['Gene_Symbol'] = Gene_Symbol_list
    variant_dataframe['Location'] = Location_list
    variant_dataframe['Clinical_Annotation_Count'] = Clinical_Annotation_Count_list
    variant_dataframe['Variant_Annotation_Count'] = Variant_Annotation_Count_list
    variant_dataframe['Level_1_2_Clinical_Annotation_count'] = Level_1_2_Clinical_Annotation_count_list
    variant_dataframe['Label_Annotation_count'] = Label_Annotation_count_list
 


#########################################################
# Find gene ID and gene name variant_gene_map table 
# 
# 
def lookup_variant_genes(variant_dataframe):
    query = """
      SELECT DISTINCT Variation_Id,
            Variant_Name,
            Variant_Location,
            Gene_PharmGKB_Accession_Id,
            Gene_Symbol 
       FROM variant_gene_map 
        """
    cur = transformer_db_connection.cursor()
    cur.execute(query,())
    for row in cur.fetchall():
        var_gene_tuple  = (row['Gene_PharmGKB_Accession_Id'], row['Gene_Symbol'] ) 


#########################################################
# Retrieve rows from variant_gene_map table of transformer
# for import into variant table if they are not there.
# 
#
def copy_variant_genes(variant_dataframe):
    query = """
      SELECT DISTINCT Variation_Id,
            Variant_Name,
            Variant_Location,
            Gene_PharmGKB_Accession_Id,
            Gene_Symbol 
       FROM variant_gene_map 
        """
    Variation_ID_list = []
    Variation_Name_list = []
    Gene_ID_list = []
    Gene_Symbol_list = []
    Variation_Location_list = []

    cur = transformer_db_connection.cursor()
    cur.execute(query,())
    for row in cur.fetchall():
        print('check the variant table')
        if is_needed(row['Variation_Id'], row['Gene_PharmGKB_Accession_Id'],) : 
            Variation_ID_list.append(row['Variation_Id'])
            Variation_Name_list.append(row['Variant_Name'])
            Gene_ID_list.append(row['Gene_PharmGKB_Accession_Id'])
            Gene_Symbol_list.append(row['Gene_Symbol'])
            Variation_Location_list.append(row['Variant_Location'])
    variant_dataframe['PharmGKB_Accession_Id'] = Variation_ID_list
    variant_dataframe['Variant_Name'] = Variation_Name_list
    variant_dataframe['Gene_PharmGKB_Accession_Id'] = Gene_ID_list
    variant_dataframe['Gene_Symbol'] = Gene_Symbol_list
    variant_dataframe['Location'] = Variation_Location_list




#########################################################
# Retrieve variant-gene from map transformer db.
# 
# Find missing genes of variants to populate the
# variant_gene_map table of transformer db.
#
# Need to invoke call_dbSNP( ) because the map in source db
# has some instances of missing Gene_PharmGKB_Accession_Id
# and Gene Symbol for variants.
#
def fix_genes_id(variant_dataframe, table):  
        query1 = """
            SELECT DISTINCT
                Variation_Id,
                Variant_Name,
                Variant_Location,
                Gene_PharmGKB_Accession_Id,
                Gene_Symbol
            FROM variant_gene_map
            ORDER BY Variation_Id
            """           
        if table == 'variant_gene_map':
            query =  query1
            cur = transformer_db_connection.cursor()
        cur.execute(query,())
        Variation_ID_list = []
        Variation_Name_list = []
        Variation_Location_list = []
        Gene_ID_list = []
        Gene_Symbol_list = []

        for row in cur.fetchall():
            gene_id = get_gene_id(row['Gene_Symbol'])            # check gene table for gene id of gene
            Variation_ID_list.append(row['Variation_Id'])
            Variation_Location_list.append(row['Variant_Location'])
            Variation_Name_list.append(row['Variant_Name'])
            Gene_ID_list.append(gene_id)
            Gene_Symbol_list.append(row['Gene_Symbol']) 
        variant_dataframe['Variation_Id'] = Variation_ID_list
        variant_dataframe['Variant_Name'] = Variation_Name_list
        variant_dataframe['Gene_PharmGKB_Accession_Id'] = Gene_ID_list
        variant_dataframe['Gene_Symbol'] = Gene_Symbol_list
        variant_dataframe['Variant_Location'] = Variation_Location_list




#########################################################
# Retrieve variant-gene from map in source db or from
# transformer db.
# Find missing genes of variants to populate the
# variant_gene_map table of transformer db.
#
# Need to invoke call_dbSNP( ) because the map in source db
# has some instances of missing Gene_PharmGKB_Accession_Id
# and Gene Symbol for variants.
#
def get_variants_genes(variant_dataframe, table):
        query1 = """
            SELECT DISTINCT
                Variant_Id,
                Variant_Name,
                Gene_PharmGKB_Accession_Id,
                Gene_Symbol
            FROM variant_gene_map_source
            ORDER BY Variant_Id
            """
        query2 = """
            SELECT DISTINCT
                Variant_PharmGKB_Accession_ID as Variant_Id,
                Variant_or_Haplotypes as Variant_Name,
                Gene_PharmGKB_Accession_ID as Gene_PharmGKB_Accession_Id,
                Gene as Gene_Symbol
            FROM var_drug_ann
            ORDER BY Variant_Id
            """    
        query3 = """
            SELECT DISTINCT
                Variation_Id,
                Variant_Name,
                Gene_PharmGKB_Accession_Id,
                Gene_Symbol
            FROM variant_gene_map
            ORDER BY Variation_Id
            """           
        if table == 'variant_gene_map_source':
            query =  query1
            cur = source_db_connection.cursor()
        elif table == 'var_drug_ann':
            query =  query2
            cur = transformer_db_connection.cursor()
        elif table == 'variant_gene_map':
            query =  query3
            cur = transformer_db_connection.cursor()
        cur.execute(query,())
        Variation_ID_list = []
        Variation_Name_list = []
        Variation_Location_list = []
        Gene_ID_list = []
        Gene_Symbol_list = []
        variant_gene_set = set()

        for row in cur.fetchall():
            if row['Variation_Id'] != None:
                variant_gene_set.add( (row['Variation_Id'], row['Variant_Name'], row['Gene_PharmGKB_Accession_Id'], row['Gene_Symbol'] ) )
        for variant_gene_tuple in variant_gene_set:
            variant_id, variant_name, gene_id, gene_symbol = variant_gene_tuple
        #    if is_needed(variant_id, gene_id):
            time.sleep(1)                                               # pause, because dbSNP will throttle our queries if they are sent too fast
            gene_set = set()
            location_dict = {'location':''}
            location = ''
            if variant_id.startswith('rs'):                              # no gene_id, use variant_id to
                call_dbSNP(variant_id, gene_set,location_dict)           # get gene names with reference seq #
                variant_id = 'DBSNP:' + variant_id
            else:
                if variant_name.startswith('rs'):                        # no variant_id, use variant_name to
                    call_dbSNP(variant_name, gene_set,location_dict)     # get gene names with reference seq #
                    variant_id = 'DBSNP:' + variant_name
                else:
                    variant_id = variant_name                            # variant name must be haplotype like 'CYP2C19*2'
            for gene_symbol_string in gene_set:                          # one of what could be several genes from dbSNP
                location = location_dict['location']
                if gene_id == None: 
                    gene_id = get_gene_id(gene_symbol_string)            # check gene table for gene id of gene
                Variation_ID_list.append(variant_id)
                Variation_Location_list.append(location)
                Variation_Name_list.append(variant_name)
                Gene_ID_list.append(gene_id)
                Gene_Symbol_list.append(gene_symbol_string)
            if  variant_id.find(',') > 0:                                # there are multiple haplotypes listed
                    split_variantID_list = breakup_array(variant_id, ',')
                    for index in range (len(split_variantID_list)):
                        Variation_ID_list.append(split_variantID_list[index])
                        Variation_Location_list.append(location)
                        Variation_Name_list.append(variant_name)
                        Gene_ID_list.append(gene_id)
                        Gene_Symbol_list.append(gene_symbol)  
        variant_dataframe['Variation_Id'] = Variation_ID_list
        variant_dataframe['Variant_Name'] = Variation_Name_list
        variant_dataframe['Gene_PharmGKB_Accession_Id'] = Gene_ID_list
        variant_dataframe['Gene_Symbol'] = Gene_Symbol_list
        variant_dataframe['Variant_Location'] = Variation_Location_list



#########################################################
# Check for existing record in the variant table
# to preclude adding a duplicate record
# 
#########################################################
def is_needed(variant_id, gene_id):
    is_needed_in_variant_table = False
    rowcount = 0
    if variant_id.startswith('rs'):                              # no gene_id, use variant_id to
        variant_id = 'DBSNP:' + variant_id
    query_0 =  """
            SELECT DISTINCT PharmGKB_Accession_Id, Gene_PharmGKB_Accession_Id
            FROM variant 
            WHERE PharmGKB_Accession_Id = ?
    """
    normal_gene_id = ' AND Gene_PharmGKB_Accession_Id = ?'
    null_gene_id = ' AND Gene_PharmGKB_Accession_Id ISNULL'

    cur = transformer_db_connection.cursor()
    if gene_id == None:
        query = query_0 + null_gene_id
        cur.execute(query,(variant_id,))
    else:
        query = query_0 + normal_gene_id
        cur.execute(query,(variant_id,gene_id,))

    for row in cur.fetchall():
        rowcount = rowcount + 1
    
    if (rowcount < 1 or len(variant_id.strip()) < 0):  # found a record or the variant id is blank
        is_needed_in_variant_table = True
    else:
        is_needed_in_variant_table = False
    print(is_needed_in_variant_table, rowcount, len(variant_id.strip()), variant_id, gene_id )
    return is_needed_in_variant_table


#########################################################
# Retrieve Automated annotations from source db
# for mapping variant to gene
# JSON nested levels:
# primary_snapshot_data > allele_annotations > assembly_annotation > genes > locus 
#
# Reference sequences have a format like NC_000023.10, where NC_000023 is the 
# accession number of the reference sequence and “.10” its version number. 
# Version numbers are required since we started to use reference sequences at a 
# time our knowledge of the human genome was far from complete. The version number 
# directly follows the accession number and increases over time.
#
# genomic (nucleotide)
# NC_ a genomic reference sequence based on a chromosome
#   NC_000023.9:g.32317682G>A (Mar.2006: hg18, NCBI36)
#   NC_000023.10:g.32407761G>A (Feb.2009: h19, GRCh37)
#   NC_000023.11:g.32389644G>A (Dec.2013: hg38, GRCh38)
#   NC_000006.12:31758911 
def call_dbSNP(variant_id, gene_set, location):
    variant_id = variant_id[variant_id.find('s')+1:]   # strip off 'rs' from reference sequence id
    print('---->',variant_id)
    response = requests.get("https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/" + variant_id)
    try:
        json_string = json.loads(response.content)
    except json.decoder.JSONDecodeError:
        json_string = json.loads(response.content)
    try:
        json_string = json.loads(response.content)
    except json.decoder.JSONDecodeError:
        json_string = json.loads(response.content)
    try:
        for json2_string in json_string['primary_snapshot_data']['allele_annotations']:
            for json3_string in json2_string['assembly_annotation']:
                for json4_string in json3_string['genes']:
                    gene_set.add(json4_string['locus'])
        # get variant's NC_ location
        for json2_string in json_string['primary_snapshot_data']['placements_with_allele']:
            for json3_string in json2_string['alleles']: 
  
                version = 14  # looking for the latest available version by starting with version 14 and decrementing
                while (json3_string['hgvs'].find('NC_') == 0 and json3_string['hgvs'].find('.'+str(version)+':') < 0 and version > 7):
                    second_split_list = []
                    hgvs_string = json3_string['hgvs']
                #   To handle something like NC_000023.10:g.66766357_66766405GGC[16]GCG[17] 
                    hgvs_string = hgvs_string[: hgvs_string.find('[')]

                    NC_split_list = hgvs_string.split(':')
                    if NC_split_list[1].find('_') > 0:                                # might be like "NC_000003.12:g.101857187_101857188insTTCTAG"
                        second_split_list = NC_split_list[1].split('_')
                        part1 = ''.join(re.findall(r'\d+', second_split_list[0])) 
                        part2 = ''.join(re.findall(r'\d+', second_split_list[1]))     # remove non-numeric characters
                        position = part1 + '_' + part2
                    else:
                        position = ''.join(re.findall(r'\d+', NC_split_list[1]))      # remove non-numeric characters
                    location['location'] = NC_split_list[0] + ':' + position
                    version = version - 1

    except KeyError:
        return ""


#########################################################
# Retrieve just PharmGKB_Accession_Id for a chemical name
#
#
def get_chemical_id(chemical_name):
        print('chemical_name', chemical_name)
        query = """
            SELECT 
                PharmGKB_Accession_Id,
                Name
            FROM chemical
            WHERE Name = ?
            """
        cur = transformer_db_connection.cursor()
        cur.execute(query,(chemical_name,))
        for row in cur.fetchall():
            return row['PharmGKB_Accession_Id']
        

#########################################################
# Retrieve just PharmGKB_Accession_Id for a variant name
#
#
def get_variant_id(variant_name):
        print('variant_name', variant_name)
        query = """
            SELECT 
                PharmGKB_Accession_Id,
                Variant_Name
            FROM variant
            WHERE Variant_Name = ?
            """
        cur = transformer_db_connection.cursor()
        cur.execute(query,(variant_name,))
        for row in cur.fetchall():
            return row['PharmGKB_Accession_Id']
        

#########################################################
# Retrieve just PharmGKB_Accession_Id for a gene
#
#
def get_gene_id(gene_symbol):
        print('gene_symbol', gene_symbol)
        query = """
            SELECT 
                PharmGKB_Accession_Id,
                Name,
                Symbol
            FROM gene
            WHERE Symbol = ?
            """
        cur = transformer_db_connection.cursor()
        cur.execute(query,(gene_symbol,))
        for row in cur.fetchall():
            return row['PharmGKB_Accession_Id']




#########################################################
# Retrieve Relationships and Automated annotations
#
def get_auto_annotations():
        query = """
            SELECT 
                Chemical_ID,
                Chemical_Name,
                Chemical_in_Text,
                Variation_ID,
                Variation_Name,
                Variation_Type,
                Variation_in_Text,
                Gene_IDs,
                Gene_Symbols,
                Gene_in_Text,
                Literature_ID,
                PMID,
                Literature_Title,
                Publication_Year,
                Journal,
                Sentence,
                Source,
                Evidence,
                Association,
                PK,
                PD,
                PMIDs
            FROM automated_annotations
            LEFT JOIN relationships ON Chemical_ID = Entity1_id AND Variation_ID = Entity2_id
            """
        cur = source_db_connection.cursor()
        cur.execute(query,())
        Chemical_ID_array = []
        Chemical_Name_array = []
        Chemical_in_Text_array = []
        Variation_ID_array = []
        Variation_Name_array = []
        Variation_Type_array = []
        Variation_in_Text_array = []
        Gene_ID_array = []
        Gene_Symbol_array = []
        Gene_in_Text_array = []
        Literature_ID_array = []
        PMID_array = []
        Literature_Title_array = []
        Publication_Year_array = []
        Journal_array = []
        Sentence_array = []
        Source_array = []
        Evidence_array = []
        Association_array = []
        Pharmacokinetic_array = []
        Pharmacodynamic_array = []
        Relation_PMIDs_array  = []
        dict = { 'Chemical_ID'  : Chemical_ID_array,
                 'Chemical_Name' : Chemical_Name_array,
                 'Chemical_in_Text' : Chemical_in_Text_array,
                 'Variation_ID' : Variation_ID_array,
                 'Variation_Name' : Variation_Name_array,
                 'Variation_Type' : Variation_Type_array,
                 'Variation_in_Text' : Variation_in_Text_array,
                 'Gene_ID' : Gene_ID_array,
                 'Gene_Symbol' : Gene_Symbol_array,
                 'Gene_in_Text' : Gene_in_Text_array,
                 'Literature_ID' : Literature_ID_array,
                 'PMID' : PMID_array,
                 'Literature_Title' : Literature_Title_array,
                 'Publication_Year' : Publication_Year_array,
                 'Journal' : Journal_array,
                 'Sentence' : Sentence_array,
                 'Source' : Source_array,
                 'Evidence' : Evidence_array,
                 'Association' : Association_array,
                 'Pharmacokinetics' : Pharmacokinetic_array,
                 'Pharmacodynamics' : Pharmacodynamic_array,
                 'Relation_PMIDs'   : Relation_PMIDs_array
        }  
        for row in cur.fetchall():
            split_geneID_array = breakup_array(row['Gene_IDs'], ',')
            if split_geneID_array != None and len(split_geneID_array) > 1:
                    split_geneSym_array = breakup_array(row['Gene_Symbols'], ',')
                    for index in range(len(split_geneID_array)):
                        Gene_ID_array.append(split_geneID_array[index])
                        Chemical_ID_array.append(row['Chemical_ID'])
                        Chemical_Name_array.append(row['Chemical_Name'])
                        Chemical_in_Text_array.append(row['Chemical_in_Text'])
                        Variation_ID_array.append(row['Variation_ID'])
                        Variation_Name_array.append(row['Variation_Name'])
                        Variation_Type_array.append(row['Variation_Type'])
                        Variation_in_Text_array.append(row['Variation_in_Text'])
                        Gene_Symbol_array.append(split_geneSym_array[index])
                        Gene_in_Text_array.append(row['Gene_in_Text'])
                        Literature_ID_array.append(row['Literature_ID'])
                        PMID_array.append(row['PMID'])
                        Literature_Title_array.append(row['Literature_Title'])
                        Publication_Year_array.append(row['Publication_Year'])
                        Journal_array.append(row['Journal'])
                        Sentence_array.append(row['Sentence'])
                        Source_array.append(row['Source'])
                        Evidence_array.append(row['Evidence'])
                        Association_array.append(row['Association'])
                        Pharmacokinetic_array.append(row['PK'])
                        Pharmacodynamic_array.append(row['PD'])
                        Relation_PMIDs_array.append(row['PMIDs'])
            else:
                        Gene_ID_array.append(row['Gene_IDs'])
                        Chemical_ID_array.append(row['Chemical_ID'])
                        Chemical_Name_array.append(row['Chemical_Name'])
                        Chemical_in_Text_array.append(row['Chemical_in_Text'])
                        Variation_ID_array.append(row['Variation_ID'])
                        Variation_Name_array.append(row['Variation_Name'])
                        Variation_Type_array.append(row['Variation_Type'])
                        Variation_in_Text_array.append(row['Variation_in_Text'])
                        Gene_Symbol_array.append(row['Gene_Symbols'])
                        Gene_in_Text_array.append(row['Gene_in_Text'])
                        Literature_ID_array.append(row['Literature_ID'])
                        PMID_array.append(row['PMID'])
                        Literature_Title_array.append(row['Literature_Title'])
                        Publication_Year_array.append(row['Publication_Year'])
                        Journal_array.append(row['Journal'])
                        Sentence_array.append(row['Sentence'])
                        Source_array.append(row['Source'])
                        Evidence_array.append(row['Evidence'])
                        Association_array.append(row['Association'])
                        Pharmacokinetic_array.append(row['PK'])
                        Pharmacodynamic_array.append(row['PD'])
                        Relation_PMIDs_array.append(row['PMIDs'])
        df = pd.DataFrame(dict)   
        return df     


#########################################################
# Retrieve Phenotypes
#
def get_phenotypes():
      print("test phenotypes")
      query = """
      SELECT DISTINCT     
            PharmGKB_Accession_Id,
            Name
      FROM phenotypes 
        """ 
      cur = source_db_connection.cursor()
      cur.execute(query,())
      PharmGKB_Accession_Id_array = []
      Name_array = []
      dict = { 'PharmGKB_Accession_Id' : PharmGKB_Accession_Id_array,
               'Name' : Name_array
      }  
      for row in cur.fetchall():
            PharmGKB_Accession_Id_array.append(row['PharmGKB_Accession_Id'])
            Name_array.append(row['Name'])
      df = pd.DataFrame(dict)   
      return df     


#########################################################
# Retrieve Genes
#
def get_genes():
      query = """
      SELECT DISTINCT     
            PharmGKB_Accession_Id,
            NCBI_Gene_ID,
            Name,
            Symbol,
            Is_VIP,
            Has_Variant_Annotation,
            Has_CPIC_Dosing_Guideline,
            Chromosome,
            Chromosomal_Start_GRCh37,
            Chromosomal_Stop_GRCh37,
            Chromosomal_Start_GRCh38,
            Chromosomal_Stop_GRCh38
        FROM genes 
        """      
      cur = source_db_connection.cursor()
      cur.execute(query,())
      PharmGKB_Accession_Id_array = []
      NCBI_Gene_ID_array = []
      Name_array = []
      Symbol_array = []
      Is_VIP_array = []
      Has_Variant_Annotation_array = []
      Has_CPIC_Dosing_Guideline_array = []
      Chromosome_array = []
      Chromosomal_Start_GRCh37_array = []
      Chromosomal_Stop_GRCh37_array = []
      Chromosomal_Start_GRCh38_array = []
      Chromosomal_Stop_GRCh38_array = []
      dict = { 'PharmGKB_Accession_Id' : PharmGKB_Accession_Id_array,
               'NCBI_Gene_ID' : NCBI_Gene_ID_array,
               'Name' : Name_array,
               'Symbol' : Symbol_array,
               'Is_VIP' : Is_VIP_array,
               'Has_Variant_Annotation' : Has_Variant_Annotation_array,
               'Has_CPIC_Dosing_Guideline' : Has_CPIC_Dosing_Guideline_array,
               'Chromosome' : Chromosome_array,
               'Chromosomal_Start_GRCh37' : Chromosomal_Start_GRCh37_array,
               'Chromosomal_Stop_GRCh37' : Chromosomal_Stop_GRCh37_array,
               'Chromosomal_Start_GRCh38' : Chromosomal_Start_GRCh38_array,
               'Chromosomal_Stop_GRCh38' : Chromosomal_Stop_GRCh38_array
      }  
      for row in cur.fetchall():
            PharmGKB_Accession_Id_array.append(row['PharmGKB_Accession_Id'])
            NCBI_Gene_ID_array.append(row['NCBI_Gene_ID'])
            Name_array.append(row['Name'])
            Symbol_array.append(row['Symbol'])
            Is_VIP_array.append(row['Is_VIP'])
            Has_Variant_Annotation_array.append(row['Has_Variant_Annotation'])
            Has_CPIC_Dosing_Guideline_array.append(row['Has_CPIC_Dosing_Guideline'])
            Chromosome_array.append(row['Chromosome'])
            Chromosomal_Start_GRCh37_array.append(row['Chromosomal_Start_GRCh37'])
            Chromosomal_Stop_GRCh37_array.append(row['Chromosomal_Stop_GRCh37'])
            Chromosomal_Start_GRCh38_array.append(row['Chromosomal_Start_GRCh38'])
            Chromosomal_Stop_GRCh38_array.append(row['Chromosomal_Stop_GRCh38'])
      df = pd.DataFrame(dict)   
      return df            


#########################################################
# Retrieve from relationships table
#
def get_relationships():
      query = """
      SELECT DISTINCT     
            Entity1_id,
            Entity1_name,
            Entity1_type,
            Entity2_id,
            Entity2_name,
            Entity2_type,
            Evidence,
            Association,
            PK,
            PD,
            PMIDs
        FROM relationships 
        """
      cur = source_db_connection.cursor()
      cur.execute(query,())
      Entity1_id_array = []
      Entity1_name_array = []
      Entity1_type_array = []
      Entity2_id_array = []
      Entity2_name_array = []
      Entity2_type_array = []
      Evidence_array = []
      Association_array = []
      Pharmacokinetic_array = []
      Pharmacodynamic_array = []
      PMIDs_array = []
      dict = { 'Entity1_id' : Entity1_id_array,
               'Entity1_name' :  Entity1_name_array,
               'Entity1_type' : Entity1_type_array,
               'Entity2_id' : Entity2_id_array,
               'Entity2_name' : Entity2_name_array,
               'Entity2_type' : Entity2_type_array,
               'Evidence' : Evidence_array,
               'Association' : Association_array,
               'Pharmacokinetic' : Pharmacokinetic_array,
               'Pharmacodynamic' : Pharmacodynamic_array,
               'PMIDs' : PMIDs_array
      }     
      for row in cur.fetchall():
            Entity1_id_array.append(row['Entity1_id'])
            Entity1_name_array.append(row['Entity1_name'])
            Entity1_type_array.append(row['Entity1_type'])
            Entity2_id_array.append(row['Entity2_id'])
            Entity2_name_array.append(row['Entity2_name'])
            Entity2_type_array.append(row['Entity2_type'])
            Evidence_array.append(row['Evidence'])
            Association_array.append(row['Association'])
            Pharmacokinetic_array.append(row['PK'])
            Pharmacodynamic_array.append(row['PD'])
            PMIDs_array.append(row['PMIDs'])      
      df = pd.DataFrame(dict)   
      return df


#########################################################
# Retrieve from source db variants table
#
#
def get_variants():
      query = """
      SELECT DISTINCT Variant_Id,
            Variant_Name,
            Gene_IDs,
            Gene_Symbols,
            Location,
            Variant_Annotation_count,
            Clinical_Annotation_count,
            Level_1_2_Clinical_Annotation_count,
            Guideline_Annotation_count,
            Label_Annotation_count  
        FROM variants 
        """
      cur = source_db_connection.cursor()
      cur.execute(query,())
      id_array = []
      Variant_Name_array = []
      Gene_IDs_array = []
      Gene_Symbols_array = []
      Location_array = []
      Variant_Annotation_count_array = []
      Clinical_Annotation_count_array = []
      Level_1_2_Clinical_Annotation_count_array = []
      Guideline_Annotation_count_array = []
      Label_Annotation_count_array = []
      dict = { 'PharmGKB_Accession_Id' : id_array,
               'Variant_Name' :  Variant_Name_array,
               'Gene_ID' : Gene_IDs_array,
               'Gene_Symbol' : Gene_Symbols_array,
               'Location' : Location_array,
               'Clinical_Annotation_Count' : Clinical_Annotation_count_array,
               'Variant_Annotation_Count' : Variant_Annotation_count_array,
               'Level_1_2_Clinical_Annotation_count' : Level_1_2_Clinical_Annotation_count_array,
               'Label_Annotation_count' : Label_Annotation_count_array
      }
      for row in cur.fetchall():
        gene_id_split_array = breakup_array(row['Gene_IDs'], ',')
        gene_symbol_split_array = breakup_array(row['Gene_Symbols'], ',')
        if gene_id_split_array != None :
            for index in range(len(gene_id_split_array)):
                id_array.append(row['Variant_Id'])
                Variant_Name_array.append(row['Variant_Name'])
                Gene_IDs_array.append(gene_id_split_array[index]) 
                Gene_Symbols_array.append(gene_symbol_split_array[index])     
                Location_array.append(row['Location'])
                Clinical_Annotation_count_array.append(row['Clinical_Annotation_Count'])
                Variant_Annotation_count_array.append(row['Variant_Annotation_Count'])
                Level_1_2_Clinical_Annotation_count_array.append(row['Level_1_2_Clinical_Annotation_count'])
                Label_Annotation_count_array.append(row['Label_Annotation_count'])
        else:
                id_array.append(row['Variant_Id'])
                Variant_Name_array.append(row['Variant_Name'])
                Gene_IDs_array.append(row['Gene_IDs']) 
                Gene_Symbols_array.append(row['Gene_Symbols'])     
                Location_array.append(row['Location'])
                Clinical_Annotation_count_array.append(row['Clinical_Annotation_Count'])
                Variant_Annotation_count_array.append(row['Variant_Annotation_Count'])
                Level_1_2_Clinical_Annotation_count_array.append(row['Level_1_2_Clinical_Annotation_count'])
                Label_Annotation_count_array.append(row['Label_Annotation_count'])
      df = pd.DataFrame(dict)
      print(df) 
      return df
   

#########################################################
# Retrieve from chemicals table
#
def get_chemicals():
      query = """
      SELECT DISTINCT PharmGKB_Accession_Id,
                      Name,
                      Type,
                      Dosing_Guideline,
                      Clinical_Annotation_Count,
                      Variant_Annotation_Count,
                      Pathway_Count,
                      VIP_Count,
                      Dosing_Guideline_Sources,
                      Top_Clinical_Annotation_Level,
                      Top_FDA_Label_Testing_Level,
                      Top_Any_Drug_Label_Testing_Level,
                      Label_Has_Dosing_Info,
                     Has_Rx_Annotation    
        FROM chemicals 
        """
      cur = source_db_connection.cursor()
      cur.execute(query,())
      id_array = []
      Name_array = []
      Type_array = []
      Dosing_Guideline_array = []
      Clinical_Annotation_Count_array = []
      Variant_Annotation_Count_array = []
      Pathway_Count_array = []
      VIP_Count_array = []
      Dosing_Guideline_Sources_array = []
      Top_Clinical_Annotation_Level_array = []
      Top_FDA_Label_Testing_Level_array = []
      Top_Any_Drug_Label_Testing_Level_array = []
      Label_Has_Dosing_Info_array = []
      Has_Rx_Annotation_array = [] 
      dict = { 'PharmGKB_Accession_Id' : id_array,
               'Name' : Name_array,
               'Type' : Type_array,
               'Dosing_Guideline' : Dosing_Guideline_array,
               'Clinical_Annotation_Count' : Clinical_Annotation_Count_array,
               'Variant_Annotation_Count' : Variant_Annotation_Count_array,
               'Pathway_Count' : Pathway_Count_array,
               'VIP_Count' : VIP_Count_array,
               'Dosing_Guideline_Sources' : Dosing_Guideline_Sources_array,
               'Top_Clinical_Annotation_Level' :  Top_Clinical_Annotation_Level_array,
               'Top_FDA_Label_Testing_Level' : Top_FDA_Label_Testing_Level_array,
               'Top_Any_Drug_Label_Testing_Level' : Top_Any_Drug_Label_Testing_Level_array,
               'Label_Has_Dosing_Info' : Label_Has_Dosing_Info_array,
               'Has_Rx_Annotation' : Has_Rx_Annotation_array  
      }
      for row in cur.fetchall():
            id_array.append(row['PharmGKB_Accession_Id'])
            Name_array.append(row['Name'])  
            Type_array.append(row['Type'])                       
            Dosing_Guideline_array.append(row['Dosing_Guideline'])  
            Clinical_Annotation_Count_array.append(row['Clinical_Annotation_Count'])  
            Variant_Annotation_Count_array.append(row['Variant_Annotation_Count'])
            Pathway_Count_array.append(row['Pathway_Count'])  
            VIP_Count_array.append(row['VIP_Count'])  
            Dosing_Guideline_Sources_array.append(row['Dosing_Guideline_Sources'])                       
            Top_Clinical_Annotation_Level_array.append(row['Top_Clinical_Annotation_Level'])  
            Top_FDA_Label_Testing_Level_array.append(row['Top_FDA_Label_Testing_Level'])  
            Top_Any_Drug_Label_Testing_Level_array.append(row['Top_Any_Drug_Label_Testing_Level'])
            Label_Has_Dosing_Info_array.append(row['Label_Has_Dosing_Info'])  
            Has_Rx_Annotation_array.append(row['Has_Rx_Annotation'])                        
      df = pd.DataFrame(dict)   
      return df


#########################################################
# Retrieve External_Vocabulary like
# "ATC:N02AF02(nalbuphine)",
# "UMLS:C0027348(Nalbuphine)",
# "RxNorm:7238(Nalbuphine)",
# "NDFRT:N0000147937(NALBUPHINE)"
# and separate into synonyms and identifiers
# 
# 
def get_external_vocabulary(table, identifier_df):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id, External_Vocabulary
        FROM {}
    """.format(table)
    cur = source_db_connection.cursor()
    cur.execute(query,())
    id_array   = []
    name_array = []
    name_type_array = []    # "External Vocabulary"
    language_array = [] 
    name_source_array = [] 

    id2_array    = []
    prefix_array = []
    xref_array   = []
    
    dict = { 'PharmGKB_Accession_Id' : id_array,
             'Name'      : name_array,
             'Name_Type' : name_type_array,
             'Language'  : language_array,
             'Name_Source' : name_source_array,
    } 
    for row in cur.fetchall():
        split_array = breakup_array(row['External_Vocabulary'], ',')
        if row['External_Vocabulary'] != None:
            for index in range (len(split_array)):
                ext_vocabulary = find_between(split_array[index],'"','"')
                source_and_name = breakup_array(ext_vocabulary, '(')
                if len(source_and_name) > 1:
                    xref = source_and_name[0][source_and_name[0].find(':') + 1 : ext_vocabulary.find('(')]
                    name = source_and_name[1][: source_and_name[1].find(')')]
                    prefix = source_and_name[0][:source_and_name[0].find(':')]
                    id2_array.append(row['PharmGKB_Accession_Id'])
                    prefix_array.append(prefix)
                    xref_array.append(xref)
                    if xref != name:    # We don't want to ingest synomyms like 'C0038048' in UMLS:C0038048(C0038048)
                        id_array.append(row['PharmGKB_Accession_Id'])
                        name_array.append(name)
                        name_source_array.append(prefix)
                        name_type_array.append('external_vocabulary')
                        language_array.append('')
    identifier_df['PharmGKB_Accession_Id'] = id2_array
    identifier_df['Prefix'] = prefix_array
    identifier_df['Xref'] = xref_array
    df = pd.DataFrame(dict) 
    return df


#########################################################
# Retrieve alternate names from a table:
#
def get_alternates(column, table):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id, {}
        FROM {}
    """.format(column,table)
    cur = source_db_connection.cursor()
    cur.execute(query,())
    id_array   = []
    name_array = []
    language_array  = []
    name_type_array = []
    name_source_array = []
    dict = { 'PharmGKB_Accession_Id' : id_array,
             'Name'      : name_array,
             'Name_Type' : name_type_array,
             'Language'  : language_array,
             'Name_Source' : name_source_array,
    }
    for row in cur.fetchall():
        split_array = breakup_array(row[column], ',"')
        if split_array != None :
            for index in range(len(split_array)):
                id_array.append(row['PharmGKB_Accession_Id'])  
                name_array.append(split_array[index].strip('"'))
                language_array.append(None)
                name_type_array.append(column)
                name_source_array.append('PharmGKB')
    df = pd.DataFrame(dict)   
    return df


#########################################################
# Retrieve one of the following:
# Generic_Names
# Trade_Names
# Brand_Mixtures
def get_names(column, table, dataframe):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id, {}
        FROM {}
    """.format(column,table)
    cur = source_db_connection.cursor()
    cur.execute(query,())
    id_array   = []
    name_array = []
    language_array  = []
    name_type_array = []
    name_source_array = []
    for row in cur.fetchall():
        split_array = breakup_array(row[column], ',"')
        if split_array != None :
            for index in range(len(split_array)):
                id_array.append(row['PharmGKB_Accession_Id'])  
                name_string = split_array[index]
                name_string = extract_name_type_lang(name_source_array, language_array, name_type_array, name_string, column)
                name_array.append(name_string.strip('"'))
    dataframe['PharmGKB_Accession_Id']  = id_array
    dataframe['Name']  = name_array
    dataframe['Name_Type']  = name_type_array
    dataframe['Language']  = language_array
    dataframe['Name_Source']  = name_source_array


#########################################################
# Retrieve Identifiers
#
#
def get_identifiers(table, dataframe_identifier):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id, Cross_references
        FROM {}
    """.format(table)
    cur = source_db_connection.cursor()
    cur.execute(query,())
    id_array = []
    xref_array = []
    prefix_array = []
    for row in cur.fetchall():
        split_array = breakup_array(row['Cross_references'], ",")
        if split_array != None :
            for index in range(len(split_array)):
                if row['PharmGKB_Accession_Id'] == None:
                    id_array.append('')
                else:
                    id_array.append(row['PharmGKB_Accession_Id'])
                cross_ref_string = find_between(split_array[index], '"','"')
                prefix_array.append(cross_ref_string[:cross_ref_string.find(':')])
                xref_array.append( cross_ref_string[cross_ref_string.find(':') + 1:]) 
    dataframe_identifier['PharmGKB_Accession_Id'] =  id_array
    dataframe_identifier['Xref'] =   xref_array
    dataframe_identifier['Prefix']   =   prefix_array
    

#########################################################
# Just split up the comma-separated name values
#
def breakup_array(name_row, delimiter):
    if name_row != None:
        return name_row.split(delimiter)
    else:
        return None


#########################################################
# Extract the language, name type name source strings in 
# the name string
# TODO: 
# (1) Create config/lookup file of name types
# (2) Search for 'INN' and other name types in Generic_Names
# (3) Indicate name_type
#
def extract_name_type_lang(name_source_array, language_array, name_type_array, name_string, column):
    if name_string.find("]") != -1:
        if ( len(name_string) - name_string.rfind("]") ) == 2:        # "[ ]"-string is near the end of name_string
            name_metadata = find_between(name_string, '[', ']')
            name_string = name_string[:name_string.rfind("[")]
            if name_metadata.find("-") > -1:
               name_type = name_metadata[:name_metadata.rfind("-")] 
               language = name_metadata[name_metadata.rfind("-") + 1:] 
               name_type_array.append(name_type)
               try:
                    langcodes.find(language)
                    language_array.append(language)
               except LookupError:
                    #return ""
                    language_array.append("")
            else:
                name_type_array.append(column)
                try:                                    
                    langcodes.find(name_metadata)
                    #return name_metadata
                    language_array.append(name_metadata)
                except LookupError:
                    #return ""
                    language_array.append("")
        else:
            name_type_array.append(column)
            language_array.append("")
    else:
        name_type_array.append(column)
        language_array.append("")
    if column != 'External_Vocabulary':
        name_source_array.append("PharmGKB")
    else:
        name_source_array.append("TBD")
    return name_string


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


#########################################################
# Confirm that the pubchem values in Cross_references are 
# the same as in the PubChem_Compound_Identifiers column
# and therefore we can just use PubChem_Compound_Identifiers 
# column
# 
def compare_pubchem_columns():
    print('test')
    query = """
        SELECT DISTINCT Cross_references, PubChem_Compound_Identifiers
        FROM chemicals;
    """
    cur = source_db_connection.cursor()
    cur.execute(query,())
    for row in cur.fetchall():
        if row['Cross_references'] != None and row['Cross_references'].find("PubChem Compound:") > -1:
            position = row['Cross_references'].find("PubChem Compound:") 

            pubchem_list = []
            pubchem_list2 = []
            for match in re.finditer('PubChem Compound:', row['Cross_references']):
                pubchem_xref = row['Cross_references'][match.end():]
                pubchem_xref = pubchem_xref[:pubchem_xref.find('"')]
                pubchem_list.append(pubchem_xref)
            split_list = row['PubChem_Compound_Identifiers'].split(',"')
            if len(pubchem_list) == len(split_list):
                for i in range(len(split_list)):
                    if split_list[i].find('"') > -1:
                        pubchem_list2.append(split_list[i][:split_list[i].find('"')])
                    else:
                        pubchem_list2.append(split_list[i])
                if pubchem_list == pubchem_list2:
                    print(pubchem_list, pubchem_list2)
                else:
                    print('NOT EQUAL ', pubchem_list, pubchem_list2)
            else:
                print('NOT EQUAL ', pubchem_list, split_list)



def main():
    exec()

if __name__ == '__main__':
    main()