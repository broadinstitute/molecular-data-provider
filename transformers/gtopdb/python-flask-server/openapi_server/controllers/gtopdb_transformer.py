from transformers.transformer import Transformer
from transformers.transformer import Producer 
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

from collections import defaultdict

import re
import sqlite3
import json

SOURCE = 'GtoPdb'
connection = sqlite3.connect("data/GtoPdb.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

#########################################################################
# 1. This class provides all the GtoPdb information about the  
# substances in the request query to the GtoPdb Transformer REST API
# The Producer function takes each name and returns an element of substance
# information
# GitHub Issue #52 The producers should accept name, InChIKeys, 
# and native CURIES (RXCUI, UNII, CID) as query input.
#########################################################################
class GtoPdbProducer(Producer):
    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')


    ###########################################################################
    # Called by Producer Base Class' produce() method
    # use name from the query graph
    #
    def find_names(self, name):
        ids = set()
        search_string = ''
        find_substance_ids(ids, name)
        return ids 


    ###########################################################################
    # Called by Producer Base Class' produce() method, which was invoked by 
    # Transformer.transform(query) method because "function":"producer" is 
    # specified in the openapi.yaml file
    #
    def create_element(self, ligand_id):
        compound_name = None
        id = None
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)       # set default
        identifiers = {}        # dict of substance_uuid's various identifiers 
        names_synonyms = None   # dict of substance_uuid's various names & synonyms 
        compound = self.Element(id, 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
        self.get_compound_by_ligand_id(ligand_id, compound)
        return compound

############################################################################
# DOES NOT SEEM TO BE CALLED ANYWHERE
# Get compound query (to plug in where clause from cid, ligand id, and inchikey functions)
    def get_compound(self, where, name):
        compounds = []
        query1 = """
                SELECT DISTINCT
                    LIGAND_ID,
                    NAME,
                    SPECIES,
                    TYPE,
                    APPROVED,
                    WITHDRAWN,
                    LABELLED,
                    RADIOACTIVE,
                    PUBCHEM_SID,
                    PUBCHEM_CID,
                    UNIPROT_ID,
                    IUPAC_NAME,
                    INN,
                    SMILES,
                    INCHIKEY,
                    INCHI
                FROM LIGAND
                {}
                """.format(where)
        cur = connection.execute(query1,(name,)) 
        for row in cur.fetchall():
            self.add_element(row,compounds)
        return compounds

##############################################################
# Called by Producer.create_element()
# Get compound by ligand id
#
    def get_compound_by_ligand_id(self,ligand_id, compound):
        biolink_class = 'ChemicalSubstance'
        query = """
                SELECT DISTINCT
                    LIGAND_ID,
                    NAME,
                    SPECIES,
                    TYPE,
                    APPROVED,
                    WITHDRAWN,
                    LABELLED,
                    RADIOACTIVE,
                    PUBCHEM_SID,
                    PUBCHEM_CID,
                    UNIPROT_ID,
                    IUPAC_NAME,
                    INN,
                    SMILES,
                    INCHIKEY,
                    INCHI
                FROM LIGAND
                WHERE LIGAND.LIGAND_ID=?
                """
        cur=connection.execute(query,(ligand_id,))
        for row in cur.fetchall():
            # Set up identifiers, names & synonyms and biolink_class
            identifiers = {}
            synonyms_tuples = []
            if row['PUBCHEM_CID'] is not None and row['PUBCHEM_CID'] != '':
                identifiers['pubchem']= 'CID:'+str(row['PUBCHEM_CID'])
            if row['SMILES'] is not None and row['SMILES'] != '':
                identifiers['smiles']= row['SMILES']
            if row['INCHIKEY'] is not None and row['INCHIKEY'] != '':
                identifiers['inchikey']= row['INCHIKEY']
            if row['INCHI'] is not None and row['INCHI'] != '':
                identifiers['inchi'] = row['INCHI']   
            if row['PUBCHEM_SID'] is not None and row['PUBCHEM_SID'] != '':
                identifiers['pubchem-sid']= 'SID:'+str(row['PUBCHEM_SID'])  
            # gtopdb prefix
            if row['LIGAND_ID'] is not None and row['LIGAND_ID'] != '': 
                identifiers['gtopdb']= 'GTOPDB:'+str(row['LIGAND_ID'])

            # Set up proper name if inn is available     
            primary_name = row['NAME']
            synonyms_dict_set = defaultdict(set)  # a dictionary of sets
            names_synonyms = []
            if row['INN'] is not None and row['INN'] != '' and primary_name is None:
                synonyms_dict_set['INN'].add(row['INN'])
                primary_name = row['INN']
            if row['IUPAC_NAME'] is not None and row['IUPAC_NAME'] != '':
                synonyms_dict_set['IUPAC'].add(row['IUPAC_NAME'])

            # Add more synonyms into dictionary of tuples (NAME_TYPE, SYNONYM_NAME) from LIGAND_SYNONYM table
            for synonym_tuple in self.get_names_synonyms(row['LIGAND_ID']):  # Query the LIGAND_SYNONYM table
                synonyms_dict_set[synonym_tuple[0]].add(synonym_tuple[1])
            synonyms_dict_list = defaultdict(list, ((key, list(value)) for key, value in synonyms_dict_set.items()))

            # Rule: if there is only one synonym then it becomes the “name”,
            # e.g. “insulin human” of INN and if there are multiple synonyms then leave “name” empty
            if primary_name is not None:
                names_synonyms.append(
                    self.Names(
                        name = primary_name,
                        type = 'primary name'
                    )
                )                             
            for syn_type, syn_list in synonyms_dict_list.items():
                    names_synonyms.append(
                        self.Names(
                            name = syn_list[0] if len(syn_list) == 1 else  None,
                            synonyms = syn_list if len(syn_list) > 1 else  None,
                            type = syn_type
                        )
                    )
            compound.id = "GTOPDB:"+ str(row['LIGAND_ID'])
            # Small molecules are signified by SMILES, inchikey or inchi identifiers
            if 'smiles' in identifiers.keys() or 'inchikey' in identifiers.keys() or 'inchi' in identifiers.keys():
                compound.biolink_class = 'SmallMolecule'
            compound.identifiers = identifiers
            compound.names_synonyms = names_synonyms
            self.get_attributes(row,compound) 
        return compound

############################################################################
# DOES NOT SEEM TO BE CALLED ANYWHERE
#
#   Get the compound's synonyms (aliases) and attributes data
    def find_compounds_by_synonym(self, name):
        """
            Find compound by a synonym
        """
        compounds = []
        query2 = """
        SELECT DISTINCT
            LIGAND.LIGAND_ID,
            NAME,
            TYPE,
            APPROVED,
            WITHDRAWN,
            LABELLED,
            RADIOACTIVE,
            PUBCHEM_SID,
            PUBCHEM_CID,
            UNIPROT_ID,
            IUPAC_NAME,
            INN,
            SMILES,
            INCHIKEY,
            INCHI
        FROM LIGAND
        JOIN LIGAND_SYNONYM ON LIGAND.LIGAND_ID = LIGAND_SYNONYM.LIGAND_ID
        WHERE LIGAND_SYNONYM.SYNONYM_NAME = ?;
        """
        cur = connection.execute(query2,(name,))
        for row in cur.fetchall():
            self.add_element(row,compounds)
        return compounds

# Gets element
    def add_element(self, row, compounds):
        # Set up for collecting identifiers
        identifiers = {}
        if row['PUBCHEM_CID'] is not None and row['PUBCHEM_CID'] != '':
            identifiers['pubchem']= 'CID:'+str(row['PUBCHEM_CID'])
        if row['SMILES'] is not None and row['SMILES'] != '':
            identifiers['smiles']= row['SMILES']
        if row['INCHIKEY'] is not None and row['INCHIKEY'] != '':
            identifiers['inchikey']= row['INCHIKEY']
        if row['INCHI'] is not None and row['INCHI'] != '':
            identifiers['inchi']= row['INCHI']   
        if row['PUBCHEM_SID'] is not None and row['PUBCHEM_SID'] != '':
            identifiers['pubchem.substance']= 'SID:'+str(row['PUBCHEM_SID'])  
        # gtopdb prefix
        if row['LIGAND_ID'] is not None and row['LIGAND_ID'] != '': 
            identifiers['gtopdb']= 'GTOPDB:'+str(row['LIGAND_ID'])

        # Set up proper name if inn is available     
        primary_name= row['NAME']
        synonyms_dict_set = defaultdict(set)
        names_synonyms = []
        if row['INN'] is not None and row['INN'] != '':
            synonyms_dict_set['INN'].add(row['INN'])
            primary_name = row['INN']
        if row['IUPAC_NAME'] is not None and row['IUPAC_NAME'] != '':
            synonyms_dict_set['IUPAC'].add(row['IUPAC_NAME'])

        # Get more synonyms into dictionary of tuples (NAME_TYPE, SYNONYM_NAME) from LIGAND_SYNONYM table
        for synonym_tuple in self.get_names_synonyms(row['LIGAND_ID']):  # Query the LIGAND_SYNONYM table
            synonyms_dict_set[synonym_tuple[0]].add(synonym_tuple[1])
        synonyms_dict_list = defaultdict(list, ((key, list(value)) for key, value in synonyms_dict_set.items()))

        # Rule: if there is only one synonym then it becomes the “name”,
        # e.g. “insulin human” of INN and if there are multiple synonyms then leave “name” empty
        # 
        if primary_name is not None:
            names_synonyms.append(
            self.Names(
                name = primary_name,
                type = 'primary name'
            )
        )                     
        for syn_type, syn_list in synonyms_dict_list.items():
                names_synonyms.append(
                    self.Names(
                        name = primary_name if len(syn_list) > 1 else syn_list[0],
                        synonyms = syn_list if len(syn_list) > 1 else  None,
                        type = syn_type
                    )
                )
        compound = Element(
                    id = "GTOPDB:"+ str(row['LIGAND_ID']),
                    biolink_class='ChemicalSubstance',
                    identifiers = identifiers,
                    names_synonyms = [names_synonyms],
                    attributes= [
                    ],
                    connections=[],
                    source=self.info.name
                )
        self.get_attributes(row,compound)          
        compounds.append(compound) 
               

# Function to get attributes
    def get_attributes (self,row,compound):
        attributes_list= ['TYPE', 'APPROVED', 'WITHDRAWN', 'LABELLED', 'RADIOACTIVE']
        for attribute in attributes_list:
            if  row[attribute] is not None and row[attribute] != '':
                value = row[attribute]
                compound.attributes.append(self.Attribute(
                    name = attribute,
                    value= value,
                    type = attribute
                    )
                ) 
                attribute_type = None
                if attribute == 'APPROVED':
                    if row[attribute] == 'yes':
                        value = 'fda_approved_for_condition'
                        attribute_type = 'biolink:highest_FDA_approval_status'
                if attribute == 'WITHDRAWN':
                    if row[attribute] == 'yes':
                        value = 'post_approval_withdrawal'
                        attribute_type = 'biolink:highest_FDA_approval_status'
                if attribute_type is not None:     
                    compound.attributes.append(self.Attribute(
                        name = attribute,
                        value= value,
                        type = attribute_type
                        )
                    )     


# Get synonyms 
    def get_names_synonyms(self,ligand_id):
        """
            Build names and synonyms list
        """
        # Query for data to fill the Names class
        query = """
            SELECT 
                SYNONYM_NAME,
                NAME_TYPE,
                LIGAND_ID
            FROM LIGAND_SYNONYM
            WHERE LIGAND_SYNONYM.LIGAND_ID= ?;
        """
        # Set up for collecting the names and synonyms
        synonyms_tuples=[]
        cur=connection.execute(query,(ligand_id,))
        for row in cur.fetchall():
            if row['SYNONYM_NAME'] is not None and row['SYNONYM_NAME'] != '':
                # synonyms_tuples.append(row['SYNONYM_NAME'])
                synonyms_tuples.append((row['NAME_TYPE'],row['SYNONYM_NAME']))
        return synonyms_tuples
        




class GtoPdbTargetsTransformer(Transformer):

    variables = []
    relations_map = None   # JSON mapping of GtoPdb relationship types to Biolink CURIES and qualifiers
    species_map = None     # JSON mapping of species name to NCBI Taxon ID

    def __init__(self):
        super().__init__(self.variables, definition_file='info/targets_transformer_info.json')


    def map(self, compound_list, controls):
        """
            Find targets by compound names
        """
        gene_list = []
        genes = {}
        get_relations_mapping(self)         # load the relations_map
        get_species_mapping(self)           # load the species_map
        for compound in compound_list:
            ids = set()
            for key in compound.identifiers:
                name = compound.identifiers.get(key)
                find_substance_ids(ids, name)
            query = """
            SELECT DISTINCT
                TARGET_ID,
                INTERACTION.INTERACTION_ID, 
                INTERACTION.TARGET_SPECIES, 
                INTERACTION.LIGAND_ID,
                INTERACTION.TYPE, 
                INTERACTION.ACTION, 
                INTERACTION.ACTION_COMMENT, 
                INTERACTION.SELECTIVITY, 
                INTERACTION.ENDOGENOUS, 
                INTERACTION.PRIMARY_TARGET,
                INTERACTION.CONCENTRATION_RANGE, 
                INTERACTION.AFFINITY_UNITS, 
                INTERACTION.AFFINITY_HIGH, 
                INTERACTION.AFFINITY_MEDIAN, 
                INTERACTION.AFFINITY_LOW, 
                INTERACTION.ORIGINAL_AFFINITY_UNITS,
                INTERACTION.ORIGINAL_AFFINITY_LOW_NM,
                INTERACTION.ORIGINAL_AFFINITY_MEDIAN_NM,
                INTERACTION.ORIGINAL_AFFINITY_HIGH_NM,
                INTERACTION.ORIGINAL_AFFINITY_RELATION, 
                INTERACTION.ASSAY_DESCRIPTION,
                INTERACTION.RECEPTOR_SITE, 
                INTERACTION.LIGAND_CONTEXT, 
                INTERACTION.PUBMED_ID    
            FROM LIGAND
            JOIN INTERACTION ON LIGAND.LIGAND_ID = INTERACTION.LIGAND_ID
            WHERE LIGAND.LIGAND_ID= ?;
            """
            for id in ids:
                cur=connection.execute(query,(id,))
                for row in cur.fetchall():
                    target_id= row["TARGET_ID"]
                    target_list= self.get_target(target_id)
                    for target in target_list:
                        if target.id not in genes:  
                            gene_list.append(target)
                            genes[target.id]= target
                        target= genes[target.id]
                        # add connection element here by calling add_connection function
                        self.add_connections(row, target, compound)
        return gene_list
    

    # Takes a compound and returns a pubchemCID
    def get_pubchemCID(self, compound):
        cid= compound.identifiers['pubchem']
        if cid.startswith('CID:'):
            cid=cid[4:]
        return cid

    # Gets information about target from target id and creates element and adds to gene_list
    def get_target(self,target_id): 
        query = """
            SELECT DISTINCT
                TYPE,
                FAMILY_ID,
                FAMILY_NAME, 
                TARGET_ID, 
                TARGET_NAME,
                SUBUNIT_NAME, 
                TARGET_SYSTEMATIC_NAME, 
                TARGET_ABBREVIATED_NAME, 
                HGNC_ID,  
                HGNC_SYMBOL, 
                HGNC_NAME, 
                HUMAN_GENETIC_LOCALISATION, 
                HUMAN_NUCLEOTIDE_REFSEQ,
                HUMAN_PROTEIN_REFSEQ,
                HUMAN_SWISSPROT, 
                HUMAN_ENTREZ_GENE, 
                RGD_ID, 
                RGD_SYMBOL, 
                RGD_NAME, 
                RAT_GENETIC_LOCALISATION, 
                RAT_NUCLEOTIDE_REFSEQ, 
                RAT_PROTEIN_REFSEQ,
                RAT_SWISSPROT, 
                RAT_ENTREZ_GENE, 
                MGI_ID, 
                MGI_SYMBOL, 
                MGI_NAME, 
                MOUSE_GENETIC_LOCALISATION, 
                MOUSE_NUCLEOTIDE_REFSEQ,
                MOUSE_PROTEIN_REFSEQ,
                MOUSE_SWISSPROT, 
                MOUSE_ENTREZ_GENE 
            FROM TARGET
            WHERE TARGET.TARGET_ID = ?;
            """
        
        cur = connection.execute(query,(target_id,))
        myResults = cur.fetchall()
        gene_list=[]
        for row in myResults:
            if row['HGNC_ID'] != '':
                self.add_element(row,gene_list)
        return gene_list


    # Creates element for genes
    def add_element(self, row, gene_list):
        # Set up identifiers
        identifiers={}
        # Add only if HGNC_ID is present (human target)
        if row['HGNC_ID'] is not None: 
            identifiers['hgnc']= 'HGNC:'+ str(row['HGNC_ID'])

            # Set up synonyms 
            synonyms=[]
            for syn in ['TARGET_SYSTEMATIC_NAME', 'TARGET_ABBREVIATED_NAME', 'HGNC_NAME']:
                if row[syn] is not None and row[syn] != '': 
                    synonyms.append(row[syn])   
            for synonym in self.get_target_synonyms(row['TARGET_ID']):
                synonyms.append(synonym)
            
            names= Names(name=row['TARGET_NAME'],synonyms=synonyms, source=SOURCE)
            
            Element()
            gene = Element(
                        id = 'HGNC:'+ str(row['HGNC_ID']),
                        biolink_class='Gene',
                        identifiers = identifiers,
                        names_synonyms = [names],
                        attributes= [],
                        connections=[],
                        source=self.info.name
                    )
            self.get_element_attributes(row,gene)       
        
            gene_list.append(gene)        


    # Get synonyms from target_synonym table 
    def get_target_synonyms(self,id):
        """
            Build names and synonyms list
        """
    # Query for data to fill the Names class
        query = """
            SELECT 
                SYNONYM_NAME,
                TARGET_ID
            FROM TARGET_SYNONYM
            WHERE TARGET_SYNONYM.TARGET_ID= ?;
        """
        cur=connection.execute(query,(id,))
        synonyms=[]
        for row in cur.fetchall():
            if row['SYNONYM_NAME'] is not None and row['SYNONYM_NAME'] != '':
                synonyms.append(row['SYNONYM_NAME'])
        return synonyms


    # Function to get attributes from remaining characteristics in Target table
    def get_element_attributes (self,row,gene):
        attributes_list= ['TYPE', 'FAMILY_NAME', 'SUBUNIT_NAME', 'HGNC_SYMBOL', 'HUMAN_GENETIC_LOCALISATION', 'HUMAN_NUCLEOTIDE_REFSEQ', 'HUMAN_PROTEIN_REFSEQ', 'HUMAN_SWISSPROT', 
                        'HUMAN_ENTREZ_GENE', 'RGD_SYMBOL', 'RAT_GENETIC_LOCALISATION', 'RAT_NUCLEOTIDE_REFSEQ', 'RAT_PROTEIN_REFSEQ',
                        'RAT_SWISSPROT', 'RAT_ENTREZ_GENE', 'MGI_SYMBOL', 'MOUSE_GENETIC_LOCALISATION', 'MOUSE_NUCLEOTIDE_REFSEQ', 'MOUSE_PROTEIN_REFSEQ',
                        'MOUSE_SWISSPROT', 'MOUSE_ENTREZ_GENE']
        for attribute in attributes_list:
            if  row[attribute] is not None and row[attribute] != '':
                gene.attributes.append(self.Attribute(
                    name= attribute,
                    value= row[attribute],
                    type= attribute
                    )
                )


    # Function to get connections from interactions table 
    def add_connections (self, row, gene, compound):

        for relation in self.relations_map[row['TYPE'] + '|' + row['ACTION']]:
            connection= self.Connection(
                source_element_id= compound.id,
                predicate = relation['predicate'],
                inv_predicate = relation['inv_predicate'], 
                attributes= []
            )
            self.get_connections_attributes(row,connection)

            for qualifier in relation.get('qualifiers'):
                connection.qualifiers.append(qualifier)

            gene.connections.append(connection)


    # Function to get attributes from remaining characteristics in Interactions table (currently appending attributes to element object)
    def get_connections_attributes (self,row,connection):
        attributes_list= ['TARGET_SPECIES', 'TYPE', 'ACTION', 'ACTION_COMMENT', 
        'SELECTIVITY', 'ENDOGENOUS', 'PRIMARY_TARGET', 'CONCENTRATION_RANGE', 'AFFINITY_UNITS', 'AFFINITY_HIGH', 'AFFINITY_MEDIAN', 
        'AFFINITY_LOW', 'ORIGINAL_AFFINITY_UNITS', 'ORIGINAL_AFFINITY_LOW_NM', 'ORIGINAL_AFFINITY_MEDIAN_NM','ORIGINAL_AFFINITY_HIGH_NM',
        'ORIGINAL_AFFINITY_RELATION', 'ASSAY_DESCRIPTION', 'RECEPTOR_SITE', 'LIGAND_CONTEXT', 'PUBMED_ID']
        for attribute in attributes_list:

            if  row[attribute] is not None and row[attribute] != '' and not row[attribute] == 'None':
                if attribute == 'TARGET_SPECIES': #or attribute == ('ACTION'): # make into qualifier instead of attribute
                    qualifier_type_id = 'species_context_qualifier'
                    qualifier_value = 'NCBITaxon:' + str(self.species_map[row[attribute]])
                    connection.qualifiers.append(self.Qualifier(qualifier_type_id=qualifier_type_id,
                                                                qualifier_value= qualifier_value))
                elif attribute == 'PUBMED_ID':
                    publications = str(row['PUBMED_ID']).split('|')
                    publications = ['PMID:'+ publication for publication in publications]
                    connection.attributes.append(self.Attribute(
                        name = attribute,
                        value= publications,
                        type = 'biolink:publications'
                        )
                    )
                else:
                    connection.attributes.append(self.Attribute(
                        name= attribute,
                        value= row[attribute],
                        type= attribute
                        )
                    )
        ligand_id = row['LIGAND_ID']
        primary_knowledge_source = self.Attribute(
            name= 'biolink:primary_knowledge_source',
            value= 'infores:gtopdb',
            value_type= 'biolink:InformationResource',
            type= 'biolink:primary_knowledge_source',
            url = 'https://www.guidetopharmacology.org/GRAC/LigandDisplayForward?tab=biology&ligandId={}'.format(ligand_id)
            )
        primary_knowledge_source.attribute_source = 'infores:molepro'
        connection.attributes.append(primary_knowledge_source)




    

class GtoPdbInhibitorsTransformer(Transformer):

    variables = []
    relations_map = None   # JSON mapping of GtoPdb relationship types to Biolink CURIES and qualifiers
    species_map = None     # JSON mapping of species name to NCBI Taxon ID

    def __init__(self):
        super().__init__(self.variables, definition_file='info/inhibitors_transformer_info.json')


    def map(self, gene_list, controls):
        compound_list = []
        compounds = {}
        get_relations_mapping(self)         # load the relations_map
        get_species_mapping(self)           # load the species_map
        for gene in gene_list:
            # Only search if gene has HGNC id
            if 'hgnc' in gene.identifiers and gene.identifiers['hgnc'] is not None:
                hgnc= self.get_hgnc(gene)
                query = """
                SELECT DISTINCT
                    LIGAND_ID,
                    INTERACTION.INTERACTION_ID, 
                    INTERACTION.TARGET_SPECIES, 
                    INTERACTION.LIGAND_ID,
                    INTERACTION.TYPE, 
                    INTERACTION.ACTION, 
                    INTERACTION.ACTION_COMMENT, 
                    INTERACTION.SELECTIVITY, 
                    INTERACTION.ENDOGENOUS, 
                    INTERACTION.PRIMARY_TARGET,
                    INTERACTION.CONCENTRATION_RANGE, 
                    INTERACTION.AFFINITY_UNITS, 
                    INTERACTION.AFFINITY_HIGH, 
                    INTERACTION.AFFINITY_MEDIAN, 
                    INTERACTION.AFFINITY_LOW, 
                    INTERACTION.ORIGINAL_AFFINITY_UNITS,
                    INTERACTION.ORIGINAL_AFFINITY_LOW_NM,
                    INTERACTION.ORIGINAL_AFFINITY_MEDIAN_NM,
                    INTERACTION.ORIGINAL_AFFINITY_HIGH_NM,
                    INTERACTION.ORIGINAL_AFFINITY_RELATION, 
                    INTERACTION.ASSAY_DESCRIPTION,
                    INTERACTION.RECEPTOR_SITE, 
                    INTERACTION.LIGAND_CONTEXT, 
                    INTERACTION.PUBMED_ID
                FROM TARGET
                JOIN INTERACTION ON TARGET.TARGET_ID = INTERACTION.TARGET_ID
                WHERE TARGET.HGNC_ID = ?;
                """
                cur=connection.execute(query,(hgnc,))
                for row in cur.fetchall():
                    ligand_id= row["LIGAND_ID"]
                    if ligand_id not in compounds:   
                        ligand= self.get_ligand(ligand_id)[0]
                        compound_list.append(ligand)
                        compounds[ligand_id]= ligand
                    ligand= compounds[ligand_id]
                    self.add_connections(row, gene, ligand)
        return compound_list
              

    # Takes a gene and returns a HGNC ID
    def get_hgnc(self, gene):
        hgnc= gene.identifiers['hgnc']
        if hgnc.startswith('HGNC:'):
            hgnc= hgnc[5:]
        return hgnc


    # Gets information about ligand from ligand id and creates element and adds to compound_list
    def get_ligand(self,ligand_id): 
        query = """
            SELECT DISTINCT 
                LIGAND_ID,
                NAME,
                SPECIES,
                TYPE,
                APPROVED,
                WITHDRAWN,
                LABELLED,
                RADIOACTIVE,
                PUBCHEM_SID,
                PUBCHEM_CID,
                UNIPROT_ID,
                IUPAC_NAME,
                INN,
                SMILES,
                INCHIKEY,
                INCHI
            FROM LIGAND
            WHERE LIGAND.LIGAND_ID = ?;
            """
        compound_list=[]
        cur=connection.execute(query,(ligand_id,))
        for row in cur.fetchall():
            self.add_element(row,compound_list)
        return compound_list
    
    
     # Creates element for genes
    def add_element(self, row, compound_list):
        # Set up identifiers
        identifiers={}
        # Add only if pubchemcid is present
        # Keys are lowercase, prefixes are uppercase
        if row['PUBCHEM_CID'] is not None and row['PUBCHEM_CID'] != '':
            identifiers['pubchem']= 'CID:'+str(row['PUBCHEM_CID'])
        if row['SMILES'] is not None and row['SMILES'] != '':
            identifiers['smiles']= row['SMILES']
        if row['INCHIKEY'] is not None and row['INCHIKEY'] != '':
            identifiers['inchikey']= row['INCHIKEY']
        if row['INCHI'] is not None and row['INCHI'] !='':
            identifiers['inchi']= row['INCHI']   
        if row['PUBCHEM_SID'] is not None and row['PUBCHEM_SID'] !='':
            identifiers['pubchem.substance']= 'SID:'+str(row['PUBCHEM_SID'])
        if row['LIGAND_ID'] is not None and row['LIGAND_ID'] != '':
            identifiers['gtopdb']= 'GTOPDB:'+str(row['LIGAND_ID'])

        # Set up proper name if inn is available     
        primary_name= row['NAME']
        synonyms_dict_set = defaultdict(set)
        names_synonyms = []
        if row['INN'] is not None and row['INN'] != '':
            synonyms_dict_set['INN'].add(row['INN']) 
        if row['IUPAC_NAME'] is not None and row['IUPAC_NAME'] !='':
           synonyms_dict_set['IUPAC'].add(row['IUPAC_NAME'])

        # Get more synonyms into dictionary of tuples (NAME_TYPE, SYNONYM_NAME) from LIGAND_SYNONYM table
        for synonym_tuple in self.get_names_synonyms(row['LIGAND_ID']):  # Query the LIGAND_SYNONYM table
            synonyms_dict_set[synonym_tuple[0]].add(synonym_tuple[1])
        synonyms_dict_list = defaultdict(list, ((key, list(value)) for key, value in synonyms_dict_set.items()))
                  
        # Rule: if there is only one synonym then it becomes the “name”,
        # e.g. “insulin human” of INN and if there are multiple synonyms then leave “name” empty 
#        names_synonyms= Names(name=primary_name,synonyms=synonyms_dict_list, source=SOURCE)
        if primary_name is not None:
            names_synonyms.append(
            self.Names(
                name = primary_name,
                type = 'primary name'
            )
        )  
        for syn_type, syn_list in synonyms_dict_list.items():
                names_synonyms.append(
                    self.Names(
                        name = primary_name if len(syn_list) > 1 else  syn_list[0],
                        synonyms = syn_list if len(syn_list) > 1 else  None,
                        type = syn_type
                    )
                )
        # Id as CID
        Element()
        compound = Element(
                    id = "GTOPDB:"+ str(row['LIGAND_ID']),
                    biolink_class='ChemicalSubstance',
                    identifiers = identifiers,
                    names_synonyms = [names_synonyms],
                    attributes= [],
                    connections=[],
                    source=self.info.name
                )
        self.get_element_attributes(row,compound)       
        compound_list.append(compound)  


    # Get ligand synonym 
    def get_names_synonyms(self,ligand_id):
            """
                Build names and synonyms list
            """
        # Query for data to fill the Names class
            query = """
                SELECT 
                    SYNONYM_NAME,
                    NAME_TYPE,
                    LIGAND_ID
                FROM LIGAND_SYNONYM
                WHERE LIGAND_SYNONYM.LIGAND_ID= ?;
            """
            cur=connection.execute(query,(ligand_id,))
            synonyms_tuples=[]
            for row in cur.fetchall():
                if row['SYNONYM_NAME'] is not None and row['SYNONYM_NAME'] != '':
                   # synonyms_tuples.append(row['SYNONYM_NAME'])
                   synonyms_tuples.append((row['NAME_TYPE'],row['SYNONYM_NAME']))
            return synonyms_tuples

    
    # Function to get attributes
    def get_element_attributes (self,row,compound):
        attributes_list= ['TYPE', 'APPROVED', 'WITHDRAWN', 'LABELLED', 'RADIOACTIVE']
        for attribute in attributes_list:
            if  row[attribute] is not None and row[attribute] != '':
                value = row[attribute]
                if attribute == 'APPROVED':
                    if row[attribute] == 'yes':
                        value = 'fda_approved_for_condition'
                    attribute = 'highest_FDA_approval_status'
                compound.attributes.append(self.Attribute(
                    name = attribute,
                    value= value,
                    type = attribute
                    )
                )

 # Function to get connections from interactions table 
    def add_connections (self, row, gene, compound):

        for relation in self.relations_map[row['TYPE'] + '|' + row['ACTION']]:
            connection= self.Connection(
                source_element_id= compound.id,
                predicate = relation['predicate'],
                inv_predicate = relation['inv_predicate'], 
                attributes= []
            )
            self.get_connections_attributes(row,connection)

            for qualifier in relation.get('qualifiers'):
                connection.qualifiers.append(qualifier)

        compound.connections.append(connection)



    # Function to get attributes from remaining characteristics in Interactions table (currently appending attributes to element object)
    def get_connections_attributes (self,row,connection):
        attributes_list= ['TARGET_SPECIES',  'TYPE', 'ACTION', 'ACTION_COMMENT', 
        'SELECTIVITY', 'ENDOGENOUS', 'PRIMARY_TARGET', 'CONCENTRATION_RANGE', 'AFFINITY_UNITS', 'AFFINITY_HIGH', 'AFFINITY_MEDIAN', 
        'AFFINITY_LOW', 'ORIGINAL_AFFINITY_UNITS', 'ORIGINAL_AFFINITY_LOW_NM', 'ORIGINAL_AFFINITY_MEDIAN_NM','ORIGINAL_AFFINITY_HIGH_NM',
        'ORIGINAL_AFFINITY_RELATION', 'ASSAY_DESCRIPTION', 'RECEPTOR_SITE', 'LIGAND_CONTEXT', 'PUBMED_ID']
        for attribute in attributes_list:

            if  row[attribute] is not None and row[attribute] != '' and row[attribute] != 'None':
                if attribute == 'TARGET_SPECIES' or attribute == ('ACTION'): # make into qualifier instead of attribute
                    if attribute == 'TARGET_SPECIES':
                        qualifier_type_id = 'species_context_qualifier'
                        qualifier_value = 'NCBITaxon:' + str(self.species_map[row[attribute]])
                    else:
                        qualifier_type_id = 'object_aspect_qualifier'
                    connection.qualifiers.append(self.Qualifier(qualifier_type_id=qualifier_type_id,
                                                                qualifier_value= qualifier_value))
                elif attribute == 'PUBMED_ID':
                    publications = str(row['PUBMED_ID']).split('|')
                    connection.attributes.append(self.Attribute(
                        name = attribute,
                        value= publications,
                        type = 'PUBLICATIONS'
                        )
                    )
                else:
                    connection.attributes.append(self.Attribute(
                        name= attribute,
                        value= row[attribute],
                        type= attribute
                        )
                    )
        ligand_id = row['LIGAND_ID']
        primary_knowledge_source = self.Attribute(
            name= 'biolink:primary_knowledge_source',
            value= 'infores:gtopdb',
            value_type= 'biolink:InformationResource',
            type= 'biolink:primary_knowledge_source',
            url = 'https://www.guidetopharmacology.org/GRAC/LigandDisplayForward?tab=biology&ligandId={}'.format(ligand_id)
            )
        primary_knowledge_source.attribute_source = 'infores:molepro'
        connection.attributes.append(primary_knowledge_source)

    

###########################################################################
# Called by find_names() method to determine type of name submitted
# in the query graph. name, InChIKey, or PubChem
#
def find_substance_ids(id_set, name_value):
    search_column = 'NAME'                 # by default, assume a search for substance by name
    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

#   check if submitted name is native CURIE, e.g., CID:2244
#   or InChiKey, e.g., BSYNRYMUTXBXSQ-UHFFFAOYSA-N
#   or else just a substance name, e.g., aspirin
    if name_value.upper().startswith('CID:'):  # a search for substance by CID, i.e., column 'PUBCHEM_CID'
        search_column = 'PUBCHEM_CID'
        name = name_value[4:]
    elif name_value.upper().startswith('GTOPDB:'):
        name = name_value[7:]                  # search & verify ligand id, i.e., column 'LIGAND_ID'
        search_column = 'LIGAND_ID'
    elif inchikey_regex.match(name_value) is not None:
        search_column = 'INCHIKEY'             # a search for substance by inchikey, i.e., column 'INCHIKEY'
        name = name_value
    else:
        name = name_value
        search_column = 'NAME'

    """
        Find ligand id
    """
    query = """
        SELECT DISTINCT 
            LIGAND_ID
        FROM LIGAND
        WHERE {search_column} = ?
        COLLATE NOCASE;
    """.format(search_column = search_column)
    if search_column is not None:
        cur = connection.execute(query, (name,))
    #   for each hit (i.e., of the same substance name, an unlikely but possible occurrence)
    for row in cur.fetchall():
        id_set.add(row["LIGAND_ID"])


########################################################################################################
# Lookup the table of GtoPdb relations and their qualifiers
# to find a relation's corresponding predicates
def get_predicates(self,relation):
#   create and return a tuple of predicates
    tuple = (self.relations_map[relation]['predicate'], self.relations_map[relation]['inv_predicate'])
    return tuple


#######################################################################################################
# 
# Read JSON file (config/relations.json) that contains mapping of GtoPdb relationship type
# with the  the spreadsheet prefixMap.csv.
#
# Then the JSON file is saved into a variable, relationsMap, for general usage by all class methods.
#
def get_relations_mapping(self):      
    with open('config/relations.json') as json_file:
        self.relations_map = json.load(json_file)                          


#######################################################################################################
# 
# Read JSON file (config/species.json) that contains mapping of GtoPdb species.
#
# Then the JSON file is saved into a variable, speciesMap, for general usage by all class methods.
#
def get_species_mapping(self):      
    with open('config/species.json') as json_file:
        self.species_map = json.load(json_file)      