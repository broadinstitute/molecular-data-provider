import sqlite3
import re
import json
import copy

from copy import deepcopy
from openapi_server.models.names import Names
from transformers.transformer import Producer # noqa: E501
from transformers.transformer import Transformer
from collections import defaultdict

db_connection = sqlite3.connect("data/pharmgkb.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
db_connection.row_factory = sqlite3.Row

with open('info/pharmgkb_source.json') as json_file:
    df_source = json.load(json_file)


###################################################################
class PharmgkbCompoundProducer(Producer):
    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compounds_transformer_info.json')


    ###########################################################################
    # Called by Producer Base Class' produce() method
    # name
    #
    def find_names(self, name):
        ids = []
        self.find_compound(name, ids)
        return ids


    ###########################################################################
    # Called by Producer Base Class' produce() method
    #
    #    select id, name, source, parent_id, pharmgkb_accession,
    #    status, definition, star, modified_on, created_by
    def create_element(self, compound_id):
        identifiers = {}
        compound_name = None
        for row in get_compound(compound_id):
            compound_name = row['name']
        names = get_names(compound_id, compound_name, self.SOURCE, self.PROVIDED_BY)
        chemical_identifiers = get_identifiers(compound_id)
        id = self.add_prefix('pharmgkb',str(compound_id))
        biolink_class = self.biolink_class('ChemicalEntity')
        identifiers['pharmgkb'] = id
        if chemical_identifiers.get('ChEBI') is not None:
            identifiers['chebi'] = chemical_identifiers.get('ChEBI')
        if chemical_identifiers.get('Chemical Abstracts Service') is not None:
            identifiers['cas'] = self.get_prefix('cas') + chemical_identifiers.get('Chemical Abstracts Service')
        if chemical_identifiers.get('DrugBank') is not None:
            identifiers['drugbank'] = self.get_prefix('drugbank') + chemical_identifiers.get('DrugBank')
        if chemical_identifiers.get('KEGG Compound') is not None:
            identifiers['kegg'] = self.get_prefix('kegg') + chemical_identifiers.get('KEGG Compound')
        if chemical_identifiers.get('KEGG Drug') is not None:
            identifiers['kegg'] = 'KEGG.DRUG:' + chemical_identifiers.get('KEGG Drug')   
        if chemical_identifiers.get('PubChem Compound') is not None:
            identifiers['pubchem'] = self.get_prefix('pubchem') + chemical_identifiers.get('PubChem Compound')           
        if chemical_identifiers.get('SMILES') is not None:
            identifiers['smiles'] = chemical_identifiers.get('SMILES')
            biolink_class = self.biolink_class('SmallMolecule')
        if chemical_identifiers.get('InChI') is not None:
            identifiers['inchi'] = chemical_identifiers.get('InChI')
            biolink_class = self.biolink_class('SmallMolecule')
        element = self.Element(id, biolink_class, identifiers, names)
        self.get_attributes(compound_id, element)
        return element


    ###########################################################################
    # Called by find_names() method to determine type of name submitted
    # in the query graph.
    #  
    def find_compound(self, name, ids):
        if name.startswith('InChI:'):
            structure = name[name.find('InChI='):]
            find_compound_by_structure(structure, ids)
            return
        if name.startswith('CHEBI:'):
            xref = name
            prefix = name[ : name.find(':')]
            find_compound_by_id(prefix, xref, ids)
            return
        if name.startswith('CID:'):
            xref = name[name.find(':')+1 : ]
            prefix = 'PubChem Compound'
            find_compound_by_id(prefix, xref, ids)
            return
        if name.startswith('DrugBank:'):
            xref = name[name.find(':')+1 : ]
            prefix = name[ : name.find(':')]
            find_compound_by_id(prefix, xref, ids)
            return
        if name.startswith('KEGG.COMPOUND:'):
            xref = name[name.find(':')+1:]
            prefix = name[ : name.find(':')]
            prefix = prefix.replace('.',' ')
            find_compound_by_id(prefix, xref, ids)
            return
        if name.startswith('PHARMGKB.CHEMICAL'):
            xref = name[name.find(':')+1:]
           # find_compound_by_id(xref, ids)
            compounds = get_compound(xref)
            for row in compounds:
                    ids.append(row['PharmGKB_Accession_Id'])
            return
        find_compound_by_name(name, ids)
        if len(ids) == 0:
            find_compound_by_synonym(name, ids)

    ########################################################
    # Find attributes of the compound from
    # compound_origins, comments, database_accession tables
    def get_attributes(self, pharmgkb_id, element):
        get_compound_attributes(self, pharmgkb_id, element) 



###################################################################
#
# Show relation between drug and gene  (PHARMGKB.GENE)
# with variant as a node qualifier to gene
# (and show "attribute_source": "infores:pharmgkb" )
#  
class PharmgkbRelationsTransformer(Transformer):
    variables = ["association level"]

    def __init__(self, definition_file=None):
        if definition_file is not None:
            super().__init__(self.variables, definition_file=definition_file)
        else:
            definition_file='info/relations_transformer_info.json'
            super().__init__(self.variables, definition_file)        

    ###############################################################
    #  As a child class of Transformer, this method is 
    #  called by default but returns gene targets.
    ###############################################################
    def map(self, collection, controls):
        association_level = controls['association level']
        relations_list = []     # List of all the elements to be in the knowledge graph
        var_drug_data = []          # List of retrieved variant relationship data
        variant_gene_set = set()
        for chemical_element in collection:
            pharmgkb_id = ''
            identifiers = chemical_element.identifiers
            if 'pharmgkb' in identifiers and identifiers['pharmgkb'] is not None:
                curie = identifiers['pharmgkb']
                if curie is not None:
                   pharmgkb_id = self.de_prefix('pharmgkb', identifiers['pharmgkb'])
            elif 'inchi' in identifiers and identifiers['inchi'] is not None:
                for compound in get_compound_by_inchi(identifiers['inchi']):
                    pharmgkb_id = compound['PharmGKB_Accession_Id']
            elif 'pubchem' in identifiers and identifiers['pubchem'] is not None:
                pharmgkb_ids = []
                find_compound_by_id('PubChem Compound', self.de_prefix('pubchem', identifiers['pubchem']), pharmgkb_ids)
                if len(pharmgkb_ids) > 0:
                    pharmgkb_id = pharmgkb_ids[0]
            if pharmgkb_id is not None:
                relationDict = {}
                # Results from relationships table 
                for var_drug_data in get_pharmacodynamics(pharmgkb_id, association_level):
                        gene_identifier = self.add_prefix('entrez', var_drug_data['NCBI_Gene_ID'], 'Gene')
                        pharmgkb_identifier =  self.add_prefix('pharmgkb', var_drug_data['gene_pharmgkb_id'], 'Gene') 
                        connection_tuple = (var_drug_data['Association'], str(var_drug_data['relation_PMIDs']), var_drug_data['Entity1_id'], var_drug_data['Entity1_name'], var_drug_data['gene_pharmgkb_id'], var_drug_data['ref_sequence'], var_drug_data['var_pharmgkb_id'], var_drug_data['Variant_Location'])
                        if gene_identifier is not None:
                            if gene_identifier in relationDict:    # add a new connection for that existing drug_gene element
                                drug_gene_element = relationDict[gene_identifier]
                                self.add_connection(chemical_element.id, drug_gene_element, connection_tuple, 'infores:pharmgkb')
                            else:                                       # create and add new drug_gene element to the dictionary
                                drug_gene_element = self.Element(
                                    id=gene_identifier,
                                    biolink_class='Gene',
                                    identifiers = {'entrez':gene_identifier, 'pharmgkb': pharmgkb_identifier},
                                    names_synonyms = self.get_names_synonyms(var_drug_data['gene_pharmgkb_id'], var_drug_data['Gene_Symbol']),   # TODO needs attention and verification
                                    attributes=[]
                                )
                                drug_gene_element.names_synonyms[0]._synonyms.append(var_drug_data['Name'])
                                add_attribute(self, drug_gene_element, var_drug_data['Gene_Symbol'], 'biolink:symbol', 'Gene.Symbol') 
                            # Get clinical annotations
                            # Then create a connection for each clinical annotation found                         
                                self.add_connection(chemical_element.id, drug_gene_element, connection_tuple, 'infores:pharmgkb')
                                relationDict[gene_identifier] = drug_gene_element   
                # Collect all the unique elements for drug-gene or variant-drug relationships
                for drug_gene_element in relationDict:
                    relations_list.append(relationDict[drug_gene_element])           
        return relations_list


    ###############################################################
    #  Construct the names and synonyms list
    #
    def get_names_synonyms(self, pharmgkb_id, pref_name):
        synonyms = defaultdict(list)
        for synonym in get_synonyms(pharmgkb_id):
            if synonym['name_type'] is None:
                synonyms['PharmGKB'].append(synonym['synonyms'])
            else:
                synonyms[synonym['name_type']].append(synonym['name'])
        names_synonyms = []
        names_synonyms.append(
            self.Names(
                name =pref_name,
                synonyms = synonyms['PharmGKB']
            ) 
        )
        for syn_type, syn_list in synonyms.items():
            names_synonyms.append(
                self.Names(
                    name = syn_list[0] if len(syn_list) == 1 else  None,
                    synonyms = syn_list if len(syn_list) > 1 else  None,
                    type = syn_type
                )
            )
        return names_synonyms


###########################################################################################################
#   Make the attribute value a list of urls. It should work - according to our specification 
#   (line 506 of https://github.com/broadinstitute/scb-kp-dev/blob/master/MoleProAPI/transformer_api.yml), 
#        value:
#          description: >-
#            Value of the attribute. May be any data type, including a list.
#          example: 0.000153
#
    def add_connection(self, source_element_id, element, tuple, primary_knowledge):
        association, pmids, drug_pharmgkb_accession_id, drug, gene_pharmgkb_accession_id, ref_sequence, variant_pharmgkb_accession_id, location = tuple

        # Primary Knowledge Source attribute
        primary_knowledge = self.Attribute('biolink:primary_knowledge_source',primary_knowledge)
        primary_knowledge.attribute_source = 'infores:molepro'

        if association == 'associated':
            predicate = self.PREDICATE
            inverse_predicate = self.INVERSE_PREDICATE
        else: 
            predicate = 'related_to_at_instance_level'
            inverse_predicate = 'related_to_at_instance_level'          

        connection = self.Connection(
            source_element_id = source_element_id,
            predicate = predicate,
            inv_predicate= inverse_predicate,
            attributes=[primary_knowledge]
        )
        if association == 'not associated':      
            add_attribute(self,connection, 'True', 'biolink:negated','association') 

        connection.qualifiers = []
        variant_drug_url_list = []

      # Variant-Drug annotation attribute 
        connection_copy = deepcopy(connection)
        variant_drug_url_list = get_var_drug_annotation(self, drug_pharmgkb_accession_id, variant_pharmgkb_accession_id, gene_pharmgkb_accession_id, element, connection, connection_copy)

      # Association attribute
        add_attribute(self,connection, association,'association','association')

      # Publication attribute
        if pmids is not None:
            list_of_publications = []
            for publication in pmids.split(';'):
                if publication != 'None':
                    list_of_publications.append('PMID:'+ publication)
                    reference = add_attribute(self, connection, list_of_publications, 'biolink:publications', 'PMIDs')

      # Variant attribute and variant location subattribute
        variant_attribute = add_attribute(self, connection, 'DBSNP:' + ref_sequence, 'variant_reference_sequence', 'variant_reference_sequence')
        subattributes = []
        if location is not None:
            subattributes.append(self.Attribute(
                                name = 'variant_location',
                                value= location,
                                type = 'variant_location', url=None))
        variant_attribute.attributes = subattributes

      # Variant annotation attribute
        variant_url_list = get_value_URL(drug_pharmgkb_accession_id, drug, ref_sequence, variant_pharmgkb_accession_id)
        variant_annotations = add_attribute(self, connection, variant_url_list, 'biolink:annotation', 'Variant_Annotation')
        
        connection.qualifiers.append(self.Qualifier(qualifier_type_id='object_form_or_variant_qualifier', qualifier_value= 'DBSNP:' + ref_sequence))

        element.connections.append(connection)

      # Clinical evidence attribute
        connection_copy = deepcopy(connection)
        clinical_url_list = get_clinical_annotation(self, drug_pharmgkb_accession_id, variant_pharmgkb_accession_id, gene_pharmgkb_accession_id, element, connection, connection_copy)

      # Include Variant Annotation URLs, Clinical Annotation URLs & Variant-Drug URLs in the primary knowledge attribute
        primary_knowledge.value_url = list_to_string(variant_url_list, clinical_url_list, variant_drug_url_list)



###################################################################
# Retrieve from Automated Annotation Table
# Show relation between drug and gene  (PHARMGKB.GENE)
# with variant as a node qualifier to gene
# (and show "attribute_source": "infores:pharmgkb" )
#  
class PharmgkbTextMineTransformer(PharmgkbRelationsTransformer):
    variables = []
    def __init__(self):
        super().__init__(definition_file='info/text_mining_transformer_info.json')

    ###############################################################
    #  As a child class of Transformer, this method is 
    #  called by default but returns gene targets.
    ###############################################################
    def map(self, collection, controls):
        relations_list = []     # List of all the elements to be in the knowledge graph
        gene_data = []          # List of retrieved variant relationship data
        variant_gene_set = set()
        for chemical_element in collection:
            pharmgkb_id = ''
            identifiers = chemical_element.identifiers
            if 'pharmgkb' in identifiers and identifiers['pharmgkb'] is not None:
                curie = identifiers['pharmgkb']
                if curie is not None:
                   pharmgkb_id = self.de_prefix('pharmgkb', identifiers['pharmgkb'])
            elif 'inchi' in identifiers and identifiers['inchi'] is not None:
                for compound in get_compound_by_inchi(identifiers['inchi']):
                    pharmgkb_id = compound['PharmGKB_Accession_Id']
            elif 'pubchem' in identifiers and identifiers['pubchem'] is not None:
                pharmgkb_ids = []
                find_compound_by_id('PubChem Compound', self.de_prefix('pubchem', identifiers['pubchem']), pharmgkb_ids)
                if len(pharmgkb_ids) > 0:
                    pharmgkb_id = pharmgkb_ids[0]    
            if pharmgkb_id is not None:
                geneDict = {}
                # from automated annotation table which comes from pgxmine source         
                for gene_data in get_automated_annotations(pharmgkb_id):
                        gene_identifier = self.add_prefix('entrez', gene_data['NCBI_Gene_ID'], 'Gene')
                        pharmgkb_identifier =  self.add_prefix('pharmgkb', gene_data['gene_pharmgkb_id'], 'Gene') 
                        connection_tuple = (None, str(gene_data['PMID']), gene_data['Chemical_PharmGKB_Accession_ID'], gene_data['Chemical_Name'], gene_data['gene_pharmgkb_id'], gene_data['ref_sequence'], gene_data['Variant_PharmGKB_Accession_ID'], gene_data['Variant_Location']) 
                        if gene_identifier is not None:
                            if gene_identifier in geneDict:                            # add a new connection 
                                drug_gene_element = geneDict[gene_identifier] # to a drug_gene element
                                self.add_connection(chemical_element.id, drug_gene_element, connection_tuple, 'infores:pgxmine')
                            else:                                                      # else create and add
                                drug_gene_element = self.Element(                      # new drug_gene element to the dictionary
                                    id=gene_identifier,
                                    biolink_class='Gene',
                                    identifiers = {'entrez':gene_identifier, 'pharmgkb': pharmgkb_identifier},
                                    names_synonyms = self.get_names_synonyms(gene_data['gene_pharmgkb_id'], gene_data['Gene_Symbol']),   # TODO needs attention and verification
                                    attributes=[]
                                ) 
                                self.add_connection(chemical_element.id, drug_gene_element, connection_tuple, 'infores:pgxmine')
                                geneDict[gene_identifier] = drug_gene_element
                for drug_gene_element in geneDict:
                    relations_list.append(geneDict[drug_gene_element])
        return relations_list





#######################################  Common Functions  #################################################

connection = sqlite3.connect("data/pharmgkb.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


#####################################################
#
# Find curie identifiers for each disease name in a list
#
#
def get_curie(phenotype_list):
    curie_list = []
    for phenotype in phenotype_list:
        curie_list.append(find_indentifier(phenotype))
    return curie_list


#####################################################
#
# Custom order a list of identifiers and find the 
# preferred identifier according to
# https://biolink.github.io/biolink-model/docs/Disease.html
#
#
def find_indentifier(phenotype):
    query = """
        SELECT Distinct Prefix, Xref
        FROM phenotype
        JOIN identifier ON phenotype.PharmGKB_Accession_Id = identifier.PharmGKB_Accession_Id
        WHERE Name = ?;    
    """
    identifiers_list = []
    curie_list = ["MONDO","DOID","OMIM","OMIM.PS","ORPHANET","EFO","UMLS","MESH","MEDDRA","NCIT","SNOMEDCT","MEDGEN","ICD10","ICD9","KEGG.DISEASE","HP","MP","PHARMGKB.DISEASE"]
    cur = connection.cursor()
    cur.execute(query,(phenotype,))
    for row in cur.fetchall():
        identifiers_list.append((row['Prefix'].upper(), row['Xref']))
    result= [tuple for i in curie_list for tuple in identifiers_list if tuple[0] == i]
    if len(result) == 0:
        return 'PHARMGKB.DISEASE' + ':' + get_indentifier(phenotype)
    else:
        return result[0][0]+":"+result[0][1]



#####################################################
#
# find the pharmgkb_id for a phenotype
# 
def get_indentifier(phenotype):
    query = """
        SELECT Distinct PharmGKB_Accession_Id
        FROM phenotype
        WHERE Name = ?;    
    """
    pharmgkb_id = ''
    cur = connection.cursor()
    cur.execute(query,(phenotype,))
    for row in cur.fetchall():
        pharmgkb_id = row['PharmGKB_Accession_Id']
    return pharmgkb_id



#####################################################
def list_to_string(url_list1, url_list2, url_list3):
    url_list1.extend(url_list2)
    url_list1.extend(url_list3)
    delimiter = '\t'
    url_string = delimiter.join(url_list1)
    return url_string


#####################################################
# Put new attributes into elements and connections
# and called by:
# add_connection()
# map()
#
def add_attribute(self, element, value, type, name):
    if value is not None and type is not None:
        attribute = self.Attribute(
                name = name,
                value = value,
                type = type,
                url = None
            )
        element.attributes.append(attribute)
        return attribute
    return None


####################################################################################
# ref_sequence
# and called by:
# add_connection()
#
def get_value_URL(drug_pharmgkb_accession_id, drug, reference_sequence, variant_pharmgkb_accession_id):
    url_list = []
    query = """
            SELECT DISTINCT Variant_Annotation_ID
            FROM var_drug_ann
            WHERE Chemical_PharmGKB_Accession_ID = ?
            AND Variant_PharmGKB_Accession_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_pharmgkb_accession_id, variant_pharmgkb_accession_id,))
    for row in cur.fetchall():
        url_list.append('https://www.pharmgkb.org/variantAnnotation/' + row['Variant_Annotation_ID'])
    if len(url_list) == 0:
        query = """
                SELECT DISTINCT Variant_Annotation_ID
                FROM var_pheno_ann
                WHERE Variant_or_Haplotypes = ?
                AND Drugs = ?
        """        
        cur = connection.cursor()
        cur.execute(query,(reference_sequence,drug,))
        for row in cur.fetchall():
            url_list.append('https://www.pharmgkb.org/variantAnnotation/' + row['Variant_Annotation_ID'])
        if len(url_list) == 0:  # if a Variant Annotation ID cannot be located then form a label URL
            url_list.append('https://www.pharmgkb.org/variant/' + variant_pharmgkb_accession_id + '/labelAnnotation')
    return url_list



####################################################################################
# Because the PharmGKB text mining (PGxMine) is flawed with duplicate database
# entries of sentences, this method will query for distinct sentences in journals.
# 
#
def get_textmined_sentence(drug, reference_sequence):
    sentence_list = []
    query = """
    SELECT DISTINCT
        Chemical_Name,
        Variation_Name,
        PMID,
        Literature_Title,
        Publication_Year,
        Journal,
        Sentence
    FROM automated_annotation
    WHERE Chemical_Name = ?
    AND Variation_Name = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug, reference_sequence,))
    return sentence_list


 ####################################################################################
# Obtain the following from Clinical Annotations:
#   Level_of_Evidence
#   Score
#   Evidence_Count
#   Clinical Annotation URL
# 
#  and create multiple connections corresponding to the multiple clinical annotations
#  for a combination of drug, Variant_PharmGKB_Accession_ID, and Gene_PharmGKB_Accession_ID
#
def get_clinical_annotation(this, drug, Variant_PharmGKB_Accession_ID, Gene_PharmGKB_Accession_ID, element, top_connection, a_connection):
    url_list = []
    query = """
        SELECT DISTINCT
            Level_of_Evidence,
            Score,
            Phenotype_Category,
            PMID_Count,
            Evidence_Count,
            Drugs,
            Phenotypes,
            URL,
            Specialty_Population
        FROM clinical_ann
        WHERE Chemical_PharmGKB_Accession_ID = ?
        AND Variant_PharmGKB_Accession_ID = ?
        AND Gene_PharmGKB_Accession_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug, Variant_PharmGKB_Accession_ID, Gene_PharmGKB_Accession_ID,))
    connection_index = 0                                        # also assume a connection exist already
    for row in cur.fetchall():
        url_list.append(row['URL'])
        subattributes = []
        if row['Phenotypes'] != None:
            if connection_index == 0:
                new_connection = top_connection 
            else:
                new_connection = deepcopy(a_connection)        # make a working copy from the copy and then
                element.connections.append(new_connection)     # add it to the list of connections
            phenotype_list_split = str(row['Phenotypes']).split(';')  # A list of disease names
            phenotype_curie_list = get_curie(phenotype_list_split)    # convert list of disease names into list of phenotype curies
            phenotypes = add_attribute(this, new_connection, phenotype_curie_list, 'biolink:Disease', 'Clinical_Annotation.Phenotypes')
            phenotypes.description = row['Phenotypes']                # A string of disease names

          # Make evidence information into sub-attribute
            subattributes.append(this.Attribute(
                        name = 'Level_of_Evidence',
                        value= row['Level_of_Evidence'],
                        type = 'Level_of_Evidence', 
                        url=row['URL'])
                        )
            subattributes.append(this.Attribute(
                        name = 'Evidence_Count',
                        value= row['Evidence_Count'],
                        type = 'biolink:evidence_count', 
                        url=row['URL'])
                        )     
            subattributes.append(this.Attribute(
                        name = 'Score',
                        value= row['Score'],
                        type = 'Score', 
                        url=row['URL'])
                        )         
            phenotypes.attributes = subattributes

          # Add more qualifiers
            for phenotype in phenotype_curie_list:
                new_connection.qualifiers.append(this.Qualifier(qualifier_type_id='disease_or_phenotypic_feature_context_qualifier', qualifier_value= phenotype))
            if row['Specialty_Population'] != None:
                new_connection.qualifiers.append(this.Qualifier(qualifier_type_id='population_context_qualifier', qualifier_value= row['Specialty_Population']))

            connection_index = connection_index + 1
    return url_list


####################################################################################
# PharmGKB automated annotations report the possible relationship between a variant 
# and a drug in a sentence from an abstract in PubMed or an article in PubMed Central. 
# Sentences are identified automatically by a text mining system and have not been 
# reviewed or validated manually by PharmGKB. For more information about how these 
# annotations are generated, please see the FAQ. For manually curated variant-drug 
# phenotype relationships, please see the "Variant Annotations" tab.
# 
def get_automated_annotations(chem_pharmgkb_id):
    query = """
        SELECT DISTINCT    
            automated_annotation.Chemical_PharmGKB_Accession_ID,
            Chemical_Name,
            Chemical_in_Text,
            automated_annotation.Variant_PharmGKB_Accession_ID,
            Variation_Name as ref_sequence,
            Variation_Type,
            Variation_in_Text,
            Variant_Location,
            variant_gene_map.Gene_PharmGKB_Accession_Id as gene_pharmgkb_id,
            NCBI_Gene_ID,
            Gene_ID,
            automated_annotation.Gene_Symbol,
            Gene_in_Text,
            Literature_ID,
            automated_annotation.PMID,
            Literature_Title,
            Publication_Year,
            Journal,
            Source
        FROM automated_annotation
        JOIN variant_gene_map ON variant_gene_map.Variation_Id = automated_annotation.Variant_PharmGKB_Accession_ID
        JOIN gene ON variant_gene_map.Gene_PharmGKB_Accession_Id = gene.PharmGKB_Accession_Id
        WHERE automated_annotation.Chemical_PharmGKB_Accession_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(chem_pharmgkb_id,))
    return cur.fetchall()


##############################################################
# Find all the relations (associations) of a drug to variants.
# 
# Query will be configured by the value of association_level
#  1. associated
#  2. associated_and_ambiguous
#  3. all
#
def get_pharmacodynamics(chem_pharmgkb_id, association_level):
    query_0 = """
        SELECT DISTINCT
            Entity1_id,
            Entity1_name,
            Entity2_id as var_pharmgkb_id,
            Entity2_name as ref_sequence,
            Entity2_type,
            Association,
            relation_PMIDs,
            Variation_Id,
            Variant_Location,
            variant_gene_map.Gene_PharmGKB_Accession_Id as gene_pharmgkb_id,
            Gene_Symbol,
            NCBI_Gene_ID,
            Name
        FROM relationship
        LEFT JOIN variant_gene_map ON  variant_gene_map.Variation_Id = relationship.Entity2_id
        LEFT JOIN gene ON variant_gene_map.Gene_PharmGKB_Accession_Id = gene.PharmGKB_Accession_Id
        WHERE Entity1_id = ?
        and Entity2_type = 'Variant'
    """
    subquery1 = """and Association = "associated"
        ORDER BY Gene_Symbol;
        """
    subquery2 = """and (Association = "associated"
        or Association = "ambiguous")
        ORDER BY Gene_Symbol;
        """
    if association_level == 'associated':
        query = query_0 + subquery1
    elif association_level == 'associated_ambiguous':
        query = query_0 + subquery2
    else:
        query = query_0 + 'ORDER BY Gene_Symbol;'
    cur = connection.cursor()
    cur.execute(query,(chem_pharmgkb_id,))
    return cur.fetchall()



####################################################################################
#
# This query gets the genes associated with a chemical by querying var_drug_ann table
# that contains associations in which the variant affects a drug dose, response, 
# metabolism, etc
# 
def get_var_drug_annotation(this, chem_pharmgkb_id, variant_pharmgkb_id, gene_pharmgkb_id, element, top_connection, a_connection):
    query = """
    SELECT DISTINCT
        Variant_or_Haplotypes,
        Gene,
        PMID,
        Phenotype_Category,
        Significance,
        Notes,
        Sentence as var_drug_Association,
        Specialty_Population,
        Variant_Location
    FROM var_drug_ann
    JOIN variant_gene_map ON variant_gene_map.Variant_Name = var_drug_ann.Variant_or_Haplotypes
    JOIN gene ON var_drug_ann.Gene = gene.Symbol
    WHERE var_drug_ann.Chemical_PharmGKB_Accession_ID = ?
    AND var_drug_ann.Variant_PharmGKB_Accession_ID = ?
    AND var_drug_ann.Gene_PharmGKB_Accession_ID = ?;
"""
    cur = connection.cursor()
    cur.execute(query,(chem_pharmgkb_id, variant_pharmgkb_id, gene_pharmgkb_id,))
    connection_index = 0                                        # also assume a connection exist already
    variant_drug_url_list = []
    for row in cur.fetchall():
        phenotype_category = ''
        if row['Phenotype_Category'] != None:
            if connection_index == 0:
                new_connection = top_connection
            else:
                new_connection = deepcopy(a_connection)         # make a working copy from the copy and then
                element.connection.append(new_connection)       # add it to the list of connections
            phenotype_category = row['Phenotype_Category'].replace('"','')
            if row['Significance'] == 'not stated':
                significance = 'The study does not report on the significance of this association'
            elif row['Significance'] == 'yes':
                significance = 'The study reports this association is significant'
            elif row['Significance'] == 'no':
                significance = 'The study reports this association is not significant'
            variant_drug_url = 'https://www.pharmgkb.org/chemical/' + chem_pharmgkb_id + '/variantAnnotation'
            variant_drug_url_list.append(variant_drug_url)
            add_attribute(this, new_connection, variant_drug_url, 'biolink:annotation', 'Variant_Drug_Annotation')
            add_attribute(this, new_connection, row['var_drug_Association'], 'biolink:annotation', 'Sentence')
            add_attribute(this, new_connection, phenotype_category, 'phenotype_category', 'Phenotype_Category')
            add_attribute(this, new_connection, significance, 'significance', 'Significance')
            add_attribute(this, new_connection, row['Notes'], 'notes', 'Notes')
            add_attribute(this, new_connection, row['Variant_or_Haplotypes'], 'reference_sequence', 'Variant_or_Haplotypes')
    return variant_drug_url_list


#################################################################
# To create compound attribute & subattributes
# 
# 
def get_compound_attributes(this, pharmgkb_accession_id, element):
    query = """
        select PharmGKB_Accession_Id, Type
        from chemical where PharmGKB_Accession_Id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(pharmgkb_accession_id,))
    for row in cur.fetchall():
        chemical_type = row['Type']

        attribute = this.Attribute(
                name = 'chemical.type',
                value = chemical_type,
                type = 'ChemicalRole'
            )
        element.attributes.append(attribute)


#################################################################
# Called by create_element()
#
def get_identifiers(id):
    query = """
        SELECT Xref, Prefix
        FROM identifier
        WHERE PharmGKB_Accession_Id = ?
    """
    structures = {}
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    for (Xref, Prefix) in cur.fetchall():
        if Prefix != 'mol':
            structures[Prefix] = Xref
    return structures


#################################################################
# Called by find_compound()
#
def find_compound_by_name(name, ids):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id FROM chemical
        WHERE name = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(name,))
    for row in cur.fetchall():
        ids.append(row['PharmGKB_Accession_Id'])


#################################################################
# Called by create_element()
#
def get_names(id, primary_name, source, transformer_name):
    name_map = {
        'en@@ChEBI': Names(
            name=primary_name,
            synonyms=[],
            name_type= None,
            source = df_source.get(source,'infores:pharmgkb'),
            provided_by= transformer_name,
            language= 'en'
        )
    }
    names_list = [name_map['en@@ChEBI']]
    synonyms = get_synonyms(id)
    for row in synonyms:
        name = row['name']
        type = row['name_type']
        source = row['name_source']
        if row['language'] == None:
            language = ''
        else:
            language = row['language']
        name_type = '' if type=='NAME' or type=='SYNONYM' else type
        key = language+'@'+name_type+'@'+source
        if key not in name_map.keys():
            name_map[key] = Names(
                name = None,
                synonyms =[],
                name_type = name_type if name_type != '' else None,
                source = df_source.get(source,'infores:pharmgkb'),
                provided_by = transformer_name,
                language = language  
            )
            names_list.append(name_map[key])
        names = name_map[key]
        if type=='SYNONYM' or names.name is not None:
            names.synonyms.append(name)
        else:
            names.name = name
    return names_list


#####################################################
# 
# Query the synonym table for the id's other names
# 
def get_synonyms(id):
    query = """
            SELECT DISTINCT
                PharmGKB_Accession_Id,
                name,
                name_type,
                language,
                name_source
            FROM synonym
            WHERE PharmGKB_Accession_Id = ?;
    """
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


#####################################################
#  called by find_compound()
# 
def find_compound_by_synonym(synonym, ids):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id 
        FROM synonym
        WHERE name = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(synonym,))
    for row in cur.fetchall():
        ids.append(row['PharmGKB_Accession_Id'])


#####################################################
#  called by find_compound()
# 
def find_compound_by_structure(xref, ids):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id 
        FROM identifier
        WHERE Xref = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(xref,))
    for row in cur.fetchall():
        ids.append(row['PharmGKB_Accession_Id'])


#####################################################
#  called by find_compound()
# 
def find_compound_by_id(prefix, xref, ids):
    query = """
        SELECT DISTINCT PharmGKB_Accession_Id 
        FROM identifier
        WHERE Xref = ?
        and Prefix = ?
        COLLATE NOCASE
    """
    cur = db_connection.cursor()
    cur.execute(query,(xref,prefix,))
    for row in cur.fetchall():
        ids.append(row['PharmGKB_Accession_Id'])
    return ids


#####################################################
#  called by find_compound()
#  and producer's create_element()
# 
def get_compound(id):
    query = """
        SELECT PharmGKB_Accession_Id, Name FROM chemical
        WHERE PharmGKB_Accession_Id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()

#####################################################
#  called by map()
#  
def get_compound_by_inchi(inchi):
    query = """
        SELECT 
            PharmGKB_Accession_Id,
            Prefix,
            Xref
        FROM identifier
        WHERE Xref = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(inchi,))
    return cur.fetchall()
