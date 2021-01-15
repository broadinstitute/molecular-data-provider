from transformers.transformer import Transformer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

import re
import sqlite3

SOURCE = 'GtoPdb'
connection = sqlite3.connect("data/GtoPdb.db", check_same_thread=False)
connection.row_factory = sqlite3.Row

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

class GtoPdbProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')

#   Invoked by Transformer.transform(query) method because "function":"producer" is specified in the openapi.yaml file
    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')
    #   find drug data for each compound name that were submitted
        for name in names:
            name = name.strip()
            if name.upper().startswith('CID:'):
                name= name[4:]
                compound_list.extend(self.get_compound_by_cid(name))
            elif name.upper().startswith('GTOPDB:'):
                name=name[7:]
                compound_list.extend(self.get_compound_by_ligand_id(name))
            elif inchikey_regex.match(name) is not None:
                compound_list.extend(self.get_compound_by_inchikey(name))
            else:
                compound_list.extend(self.find_compound_by_name(name))
        return compound_list
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
                    PUBCHEMSID,
                    PUBCHEMCID,
                    UNIPROT_ID,
                    IUPAC,
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

# Get compound by cid
    def get_compound_by_cid(self,name):
        where= "WHERE LIGAND.PUBCHEMCID = ?"
        return self.get_compound(where, name)

# Get compound by ligand id
    def get_compound_by_ligand_id(self,name):
        where= "WHERE LIGAND.LIGAND_ID=?"
        return self.get_compound(where, name)

# Get compound by inchikey
    def get_compound_by_inchikey(self,name):
        where= "WHERE LIGAND.INCHIKEY=?"
        return self.get_compound(where, name)


# Get compound by name
    def find_compound_by_name(self, name):
        """
            Find compound by a name
        """
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
                    PUBCHEMSID,
                    PUBCHEMCID,
                    UNIPROT_ID,
                    IUPAC,
                    INN,
                    SMILES,
                    INCHIKEY,
                    INCHI
                FROM LIGAND
                WHERE LIGAND.NAME = ? OR LIGAND.INN = ? OR LIGAND.IUPAC = ?;
                """
        cur = connection.execute(query1,(name,name,name)) 
        for row in cur.fetchall():
            self.add_element(row,compounds)
        if len(compounds)==0:
            return self.find_compounds_by_synonym(name)
        return compounds


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
            PUBCHEMSID,
            PUBCHEMCID,
            UNIPROT_ID,
            IUPAC,
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
        # Set up identifiers
        identifiers = {}
        if row['PUBCHEMCID'] is not None and row['PUBCHEMCID'] != '':
            identifiers['pubchem']= 'CID:'+str(row['PUBCHEMCID'])
        if row['SMILES'] is not None and row['SMILES'] != '':
            identifiers['smiles']= row['SMILES']
        if row['INCHIKEY'] is not None and row['INCHIKEY'] != '':
            identifiers['inchikey']= row['INCHIKEY']
        if row['INCHI'] is not None and row['INCHI'] != '':
            identifiers['inchi']= row['INCHI']   
        if row['PUBCHEMSID'] is not None and row['PUBCHEMSID'] != '':
            identifiers['pubchem.substance']= 'SID:'+str(row['PUBCHEMSID'])  
        # gtopdb prefix
        if row['LIGAND_ID'] is not None and row['LIGAND_ID'] != '': 
            identifiers['gtopdb']= 'GTOPDB:'+str(row['LIGAND_ID'])
        # Set up proper name if inn is available     
        name= row['NAME']
        synonyms=[]
        if row['INN'] is not None and row['INN'] != '':
            synonyms.append(name)
            name= row['INN']
        # Set up synonyms 
        if row['IUPAC'] is not None and row['IUPAC'] != '':
            synonyms.append(row['IUPAC'])
        for synonym in self.get_names_synonyms(row['LIGAND_ID']):
            synonyms.append(synonym)
        
        names= Names(name=name,synonyms=synonyms, source=SOURCE)
        
        compound = Element(
                    id = "GTOPDB:"+ str(row['LIGAND_ID']),
                    biolink_class='ChemicalSubstance',
                    identifiers = identifiers,
                    names_synonyms = [names],
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
                compound.attributes.append(Attribute(
                    name= attribute,
                    value= row[attribute],
                    provided_by=self.info.name,
                    type= attribute,
                    source= SOURCE
                    )
                )


# Get synonyms 
    def get_names_synonyms(self,id):
        """
            Build names and synonyms list
        """
    # Query for data to fill the Names class
        query3 = """
            SELECT 
                SYNONYM_NAME,
                LIGAND_ID
            FROM LIGAND_SYNONYM
            WHERE LIGAND_SYNONYM.LIGAND_ID= ?;
        """
        cur=connection.execute(query3,(id,))
        synonyms=[]
        for row in cur.fetchall():
            if row['SYNONYM_NAME'] is not None and row['SYNONYM_NAME'] != '':
                synonyms.append(row['SYNONYM_NAME'])
        return synonyms

        






class GtoPdbTargetsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/targets_transformer_info.json')


    def map(self, compound_list, controls):
        """
            Find targets by compound names
        """
        gene_list = []
        genes = {}
        for compound in compound_list:
            if compound.identifiers.get('pubchem') == None:
                continue
            cid= self.get_pubchemCID(compound)
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
            WHERE LIGAND.PUBCHEMCID = ?;
            """
            cur=connection.execute(query,(cid,))
            for row in cur.fetchall():
                target_id= row["TARGET_ID"]
                if target_id not in genes:   
                    target= self.get_target(target_id)[0]
                    gene_list.append(target)
                    genes[target_id]= target
                target= genes[target_id]
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
                SUBUNITS, 
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
        gene_list=[]
        cur=connection.execute(query,(target_id,))
        for row in cur.fetchall():
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
        attributes_list= ['TYPE', 'FAMILY_NAME', 'SUBUNITS', 'HGNC_SYMBOL', 'HUMAN_GENETIC_LOCALISATION', 'HUMAN_NUCLEOTIDE_REFSEQ', 'HUMAN_PROTEIN_REFSEQ', 'HUMAN_SWISSPROT', 
                        'HUMAN_ENTREZ_GENE', 'RGD_SYMBOL', 'RAT_GENETIC_LOCALISATION', 'RAT_NUCLEOTIDE_REFSEQ', 'RAT_PROTEIN_REFSEQ',
                        'RAT_SWISSPROT', 'RAT_ENTREZ_GENE', 'MGI_SYMBOL', 'MOUSE_GENETIC_LOCALISATION', 'MOUSE_NUCLEOTIDE_REFSEQ', 'MOUSE_PROTEIN_REFSEQ',
                        'MOUSE_SWISSPROT', 'MOUSE_ENTREZ_GENE']
        for attribute in attributes_list:
            if  row[attribute] is not None and row[attribute] != '':
                gene.attributes.append(Attribute(
                    name= attribute,
                    value= row[attribute],
                    provided_by=self.info.name,
                    type= attribute,
                    source= SOURCE
                    )
                )

    # Function to get connections from interactions table 
    def add_connections (self, row, gene, compound):
        connection= Connection(
            source_element_id= compound.id,
            type= self.info.knowledge_map.predicates[0].predicate,
            attributes= []
        )

        self.get_connections_attributes(row,connection)
        gene.connections.append(connection)

    # Function to get attributes from remaining characteristics in Interactions table (currently appending attributes to element object)
    def get_connections_attributes (self,row,connection):
        attributes_list= ['TARGET_ID', 'TARGET_SPECIES', 'LIGAND_ID', 'TYPE', 'ACTION', 'ACTION_COMMENT', 
        'SELECTIVITY', 'ENDOGENOUS', 'PRIMARY_TARGET', 'CONCENTRATION_RANGE', 'AFFINITY_UNITS', 'AFFINITY_HIGH', 'AFFINITY_MEDIAN', 
        'AFFINITY_LOW', 'ORIGINAL_AFFINITY_UNITS', 'ORIGINAL_AFFINITY_LOW_NM', 'ORIGINAL_AFFINITY_MEDIAN_NM','ORIGINAL_AFFINITY_HIGH_NM',
        'ORIGINAL_AFFINITY_RELATION', 'ASSAY_DESCRIPTION', 'RECEPTOR_SITE', 'LIGAND_CONTEXT', 'PUBMED_ID']
        for attribute in attributes_list:
            if  row[attribute] is not None and row[attribute] != '':
                connection.attributes.append(Attribute(
                    name= attribute,
                    value= row[attribute],
                    provided_by=self.info.name,
                    type= attribute,
                    source= SOURCE
                    )
                )





        


    

class GtoPdbInhibitorsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/inhibitors_transformer_info.json')


    def map(self, gene_list, controls):
        compound_list = []
        compounds = {}
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
                PUBCHEMSID,
                PUBCHEMCID,
                UNIPROT_ID,
                IUPAC,
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
        if row['PUBCHEMCID'] is not None and row['PUBCHEMCID'] != '':
            identifiers['pubchem']= 'CID:'+str(row['PUBCHEMCID'])
        if row['SMILES'] is not None and row['SMILES'] != '':
            identifiers['smiles']= row['SMILES']
        if row['INCHIKEY'] is not None and row['INCHIKEY'] != '':
            identifiers['inchikey']= row['INCHIKEY']
        if row['INCHI'] is not None and row['INCHI'] !='':
            identifiers['inchi']= row['INCHI']   
        if row['PUBCHEMSID'] is not None and row['PUBCHEMSID'] !='':
            identifiers['pubchem.substance']= 'SID:'+str(row['PUBCHEMSID'])
        if row['LIGAND_ID'] is not None and row['LIGAND_ID'] != '':
            identifiers['gtopdb']= 'GTOPDB:'+str(row['LIGAND_ID'])
        # Set up proper name if inn is available     
        name= row['NAME']
        synonyms=[]
        if row['INN'] is not None and row['INN'] != '':
            synonyms.append(name)
            name= row['INN']
        # Set up synonyms 
        if row['IUPAC'] is not None and row['IUPAC'] !='':
            synonyms.append(row['IUPAC'])
        for synonym in self.get_names_synonyms(row['LIGAND_ID']):
            synonyms.append(synonym)
            
        names= Names(name=name,synonyms=synonyms, source=SOURCE)
        # Id as CID
        Element()
        compound = Element(
                    id = "GTOPDB:"+ str(row['LIGAND_ID']),
                    biolink_class='ChemicalSubstance',
                    identifiers = identifiers,
                    names_synonyms = [names],
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
                    LIGAND_ID
                FROM LIGAND_SYNONYM
                WHERE LIGAND_SYNONYM.LIGAND_ID= ?;
            """
            cur=connection.execute(query,(ligand_id,))
            synonyms=[]
            for row in cur.fetchall():
                if row['SYNONYM_NAME'] is not None and row['SYNONYM_NAME'] != '':
                    synonyms.append(row['SYNONYM_NAME'])
            return synonyms
    
    # Function to get attributes
    def get_element_attributes (self,row,compound):
        attributes_list= ['LIGAND_ID','TYPE', 'APPROVED', 'WITHDRAWN', 'LABELLED', 'RADIOACTIVE']
        for attribute in attributes_list:
            if  row[attribute] is not None and row[attribute] != '':
                compound.attributes.append(Attribute(
                    name= attribute,
                    value= row[attribute],
                    provided_by=self.info.name,
                    type= attribute,
                    source= SOURCE
                    )
                )

 # Function to get connections from interactions table 
    def add_connections (self, row, gene, compound):
        connection= Connection(
            source_element_id= gene.id,
            type= self.info.knowledge_map.predicates[0].predicate,
            attributes= []
        )

        self.get_connections_attributes(row,connection)
        compound.connections.append(connection)

    # Function to get attributes from remaining characteristics in Interactions table (currently appending attributes to element object)
    def get_connections_attributes (self,row,connection):
        attributes_list= ['TARGET_SPECIES', 'LIGAND_ID', 'TYPE', 'ACTION', 'ACTION_COMMENT', 
        'SELECTIVITY', 'ENDOGENOUS', 'PRIMARY_TARGET', 'CONCENTRATION_RANGE', 'AFFINITY_UNITS', 'AFFINITY_HIGH', 'AFFINITY_MEDIAN', 
        'AFFINITY_LOW', 'ORIGINAL_AFFINITY_UNITS', 'ORIGINAL_AFFINITY_LOW_NM', 'ORIGINAL_AFFINITY_MEDIAN_NM','ORIGINAL_AFFINITY_HIGH_NM',
        'ORIGINAL_AFFINITY_RELATION', 'ASSAY_DESCRIPTION', 'RECEPTOR_SITE', 'LIGAND_CONTEXT', 'PUBMED_ID']
        for attribute in attributes_list:
            if  row[attribute] is not None and row[attribute] != '':
                connection.attributes.append(Attribute(
                    name= attribute,
                    value= row[attribute],
                    provided_by=self.info.name,
                    type= attribute,
                    source= SOURCE
                    )
                )

    
