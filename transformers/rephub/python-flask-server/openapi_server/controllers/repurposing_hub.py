import sqlite3
import re

from transformers.transformer import Transformer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

# Data Source
SOURCE= 'Drug Repurposing Hub'

# CURIE prefixes
PUBCHEM = 'CID:'

# Biolink class
GENE = 'gene'

connection = sqlite3.connect("data/RepurposingHub.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

class RepurposingHubProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compounds_transformer_info.json')


    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


    def produce(self, controls):
        compound_list = []
        # compounds = {}
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            if name.upper().startswith('CID:'):
                name= name[4:]
                compound_list.extend(self.find_compound_by_pubchem_cid(name))
            elif self.inchikey_regex.match(name) != None:
                compound_list.extend(self.find_compound_by_inchi_key(name))
            elif name.upper().startswith('BRD-'):
                compound_list.extend(self.find_compound_by_broad_cpd_id(name))
            else: 
                compound_list.extend(self.find_compound_by_name(name))
        return compound_list

    def find_compound_by_name(self, name):
        compounds=[]
        query = """
            SELECT DISTINCT DRUG_ID FROM DRUG
            WHERE PERT_INAME = ?
        """
        cur = connection.cursor()
        cur.execute(query,(name,))
        for row in cur.fetchall():
            for sample in self.get_samples(row['DRUG_ID']):
                self.add_element(sample,compounds)
        # if not found by name, try synonyms
        if len(compounds)==0:
            return self.find_compound_by_synonym(name)
        return compounds


    def find_compound_by_synonym(self, synonym):
        compounds = []
        query = """
            SELECT DISTINCT DRUG_ID FROM NAME
            WHERE NAME = ?
        """
        cur = connection.cursor()
        cur.execute(query,(synonym,))
        for row in cur.fetchall():
            for sample in self.get_samples(row['DRUG_ID']):
                self.add_element(sample,compounds)
        return compounds

    def find_compound_by_pubchem_cid(self, id):
        compounds = []
        query = """
            SELECT DISTINCT DRUG_ID, SAMPLE_ID, BROAD_CPD_ID, SMILES, INCHIKEY, PUBCHEMCID FROM SAMPLE
            WHERE PUBCHEMCID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(id,))
        for row in cur.fetchall():
            self.add_element(row, compounds)
        return compounds


    def find_compound_by_inchi_key(self, inchi_key):
        compounds = []
        query = """
            SELECT DISTINCT DRUG_ID, SAMPLE_ID, BROAD_CPD_ID, SMILES, INCHIKEY, PUBCHEMCID FROM SAMPLE
            WHERE INCHIKEY = ?
        """
        cur = connection.cursor()
        cur.execute(query,(inchi_key,))
        for row in cur.fetchall():
            self.add_element(row, compounds)
        return compounds

    def find_compound_by_broad_cpd_id(self, broad_id):
        compounds = []
        query = """
            SELECT DRUG_ID, SAMPLE_ID, BROAD_CPD_ID, SMILES, INCHIKEY, PUBCHEMCID FROM SAMPLE
            WHERE BROAD_CPD_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(broad_id,))
        for row in cur.fetchall():
            self.add_element(row, compounds)
        return compounds

    # helper function to connect names to samples through drug id 
    def get_samples(self, drug_id):
        query = """
            SELECT DRUG_ID, SAMPLE_ID, BROAD_CPD_ID, SMILES, INCHIKEY, PUBCHEMCID FROM SAMPLE
            WHERE DRUG_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(drug_id,))
        return cur.fetchall()

    # creates element for compound
    def add_element(self, row, compounds):
        identifiers= {}
        if row['PUBCHEMCID'] is not None and row['PUBCHEMCID'] != '':
            identifiers['pubchem']= 'CID:'+str(row['PUBCHEMCID'])
        if row['SMILES'] is not None and row['SMILES'] != '':
            identifiers['smiles']= row['SMILES']
        if row['INCHIKEY'] is not None and row['INCHIKEY'] != '':
            identifiers['inchikey']= row['INCHIKEY']
        if row['BROAD_CPD_ID'] is not None and row['BROAD_CPD_ID'] != '': 
            identifiers['broad']= row['BROAD_CPD_ID']
        # use name in drug table
        for name_row in self.get_name(row['DRUG_ID']):
            name= name_row['PERT_INAME']
        # collect synonyms
        synonyms=[]
        for synonym in self.get_synonyms(row['SAMPLE_ID']):
            synonyms.append(synonym['NAME'])
        
        names= Names(name=name,synonyms=synonyms, source=SOURCE)

        compound = Element(
                    id = row['BROAD_CPD_ID'],
                    biolink_class='ChemicalSubstance',
                    identifiers = identifiers,
                    names_synonyms = [names],
                    attributes= [
                    ],
                    connections=[],
                    source=self.info.name
                )
        self.add_attributes(row, compound)

        compounds.append(compound)

    # add attribute object to element using drug_id obtained from previous queries
    def add_attributes (self, row, compound):
        drug_id= row['DRUG_ID']
        query= """
            SELECT DISTINCT MAP_ID, DRUG_ID, FEATURE.FEATURE_ID, FEATURE.FEATURE_TYPE, FEATURE.FEATURE_NAME FROM FEATURE_MAP
            JOIN FEATURE ON FEATURE.FEATURE_ID = FEATURE_MAP.FEATURE_ID
            WHERE FEATURE_TYPE IN ('moa','disease_area','clinical_phase') AND DRUG_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(drug_id,))
        for feature_row in cur.fetchall():
            compound.attributes.append(Attribute(
                name= feature_row['FEATURE_TYPE'],
                value= feature_row['FEATURE_NAME'],
                provided_by=self.info.name,
                type= feature_row['FEATURE_TYPE'],
                source= SOURCE
                )
            )

    # helper functions used to Names object while building element for compound
    def get_name(self, drug_id):
        query= """
            SELECT DISTINCT PERT_INAME FROM DRUG
            WHERE DRUG_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(drug_id,))
        return cur.fetchall()

    def get_synonyms(self, sample_id):
        query = """
            SELECT SAMPLE_ID, NAME FROM NAME
            WHERE SAMPLE_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(sample_id,))
        return cur.fetchall()

class FeaturesTransformer(Transformer):

    variables = []

    def __init__(self, definition_file):
        super().__init__(self.variables, definition_file= definition_file)

    def map(self, compound_list, controls):
        # output for target= gene
        # output for indication= disease
        output_list = []    
        output = {}
        for compound in compound_list:
            # find drug_id using inchikey identifier 
            if compound.identifiers.get('inchikey') is not None:
                drug_id= self.get_drug_id(compound)
                # find feature_name information using drug_id 
                feature_type= self.get_feature_type(drug_id)
                for feature_row in feature_type:
                    feature_name= feature_row['FEATURE_NAME']
                    if feature_name not in output:
                        feature= self.add_element(feature_row, output_list)[-1]
                        # add connection object after building feature element
                        self.add_connections(feature_row, feature, compound)
                        output[feature_name]= feature
                    else:
                        # create new connection to a gene or disease already in the dictionary
                        feature= output[feature_name]
                        self.add_connections(feature_row, feature, compound)
        return output_list


    def get_feature_type(self, drug_id):
        query = """
            SELECT FEATURE_NAME, FEATURE_XREF, PRIMARY_NAME, FEATURE_ACTION FROM FEATURE
            INNER JOIN FEATURE_MAP ON FEATURE.FEATURE_ID = FEATURE_MAP.FEATURE_ID
            WHERE FEATURE_TYPE = ? AND FEATURE_MAP.DRUG_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(self.feature_type, drug_id,))
        return cur.fetchall()

    # Takes compound and returns drug_id 
    def get_drug_id(self, compound):
        inchikey= compound.identifiers['inchikey']
        query= """
            SELECT DISTINCT DRUG_ID FROM SAMPLE 
            WHERE INCHIKEY = ?
        """
        cur = connection.cursor()
        cur.execute(query,(inchikey,))
        for row in cur.fetchall():
            return row['DRUG_ID']

    # creates the names object
    def get_names(self, row):
        names= []
        synonyms= []
        names.append(Names(name=row['FEATURE_NAME'],synonyms=synonyms, source=SOURCE))
        if row['PRIMARY_NAME'] is not None and row['PRIMARY_NAME'] != '':
            names.append(Names(name=row['PRIMARY_NAME'],synonyms=synonyms, source='molepro'))
        return names


# Creates element object for feature type
    def add_element(self, row, output_list, ):
        # Add only if HGNC_ID is present (human target)
        if row['FEATURE_XREF'] is not None: 
            # fix identifiers for each transformer
            names= self.get_names(row)
            Element()
            output_element = Element(
                        id = row['FEATURE_XREF'],
                        biolink_class= self.biolink_class,
                        identifiers = self.identifiers(row),
                        names_synonyms = names,
                        attributes= [],
                        connections=[],
                        source=self.info.name
                    )       
            output_list.append(output_element) 
            return output_list

    def add_connections (self, row, element, compound):
        connection= Connection(
            source_element_id= compound.id,
            type= self.info.knowledge_map.predicates[0].predicate,
            source= SOURCE,
            provided_by=self.info.name,
            attributes= []
        )
        # add attribute
        if  row['FEATURE_ACTION'] is not None and row['FEATURE_ACTION'] != '':
            connection.attributes.append(Attribute(
            name= 'FEATURE_ACTION',
            value= row['FEATURE_ACTION'],
            provided_by=self.info.name, 
            type= 'FEATURE_ACTION',
            source= SOURCE
            )
            )
            connection.relation = row['FEATURE_ACTION']
        element.connections.append(connection)
    

        

class TargetsTransformer(FeaturesTransformer):
    def __init__(self):
        super().__init__('info/targets_transformer_info.json')
        self.feature_type= 'target'
        self.biolink_class= 'Gene'
    def identifiers (self, row):
        identifiers= {}
        identifiers['hgnc']= row['FEATURE_XREF']
        return identifiers
    
class IndicationsTransformer(FeaturesTransformer):
    def __init__(self):
        super().__init__('info/indications_transformer_info.json')
        self.feature_type= 'indication'
        self.biolink_class= 'DiseaseOrPhenotypicFeature'
    def identifiers (self, row):
        identifiers= {}
        disease_id= row['FEATURE_XREF']
        # use prefix of id to properly assign identifier
        # identifiers prefixes in the biolink disease class
        #    disease_prefixes= ['MONDO', 'DOID','Orphanet','EFO','NCIT','HP']
        # identifiers prefixes in the biolink phenotypic feature class
        #   phenotype_prefixes= ['HP', 'EFO', 'NCIT']
        # all prefixes in database
        #   all_prefixes= ['MONDO','HGNC','NCIT','OMIT','HP','CHEBI','SYMP','GO','OAE','EFO','MAXO','DOID','GSSO','SCDO','TDRH','VT','NCBITaxon', 'N','Orphanet','ENM','PATO']
        # prefix in the database AND biolink model
        # GO??
        indication_prefixes= ['MONDO','HGNC','NCIT','HP','CHEBI','GO','EFO','Orphanet']
        for prefix in indication_prefixes:
            if disease_id.startswith(prefix):
                identifiers[prefix.lower()]= row['FEATURE_XREF']
                return identifiers
        # for identifiers not in biolink, put rephub as key for identifiers dictionary
        identifiers['rephub']= row['FEATURE_XREF']
        return identifiers

   