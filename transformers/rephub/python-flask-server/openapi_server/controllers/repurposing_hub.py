import sqlite3
import re

from transformers.transformer import Transformer, Producer


connection = sqlite3.connect("data/RepurposingHub.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

class RepurposingHubProducer(Producer):

    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compounds_transformer_info.json')


    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


    def find_names(self, name):
        if self.has_prefix('pubchem', name, self.OUTPUT_CLASS):
            cid = self.de_prefix('pubchem', name, self.OUTPUT_CLASS)
            return self.find_compound_by_pubchem_cid(cid)
        if self.inchikey_regex.match(name) is not None:
            return self.find_compound_by_inchi_key(name)
        if name.upper().startswith('BRD-'):
            return self.find_compound_by_broad_cpd_id(name)
        return self.find_compound_by_name(name)


    def create_element(self, sample_id):
        sample = self.get_sample(sample_id)
        if sample is not None:
            return self.get_element(sample)
        return None


    def find_compound_by_name(self, name):
        query = """
            SELECT DISTINCT SAMPLE_ID 
            FROM DRUG
            JOIN SAMPLE ON SAMPLE.DRUG_ID = DRUG.DRUG_ID
            WHERE PERT_INAME = ?
        """
        cur = connection.cursor()
        cur.execute(query,(name,))
        compounds = [row['SAMPLE_ID'] for row in cur.fetchall()]
        # if not found by name, try synonyms
        if len(compounds)==0:
            return self.find_compound_by_synonym(name)
        return compounds


    def find_compound_by_synonym(self, synonym):
        query = """
            SELECT DISTINCT SAMPLE.SAMPLE_ID 
            FROM NAME
            JOIN SAMPLE ON SAMPLE.SAMPLE_ID = NAME.SAMPLE_ID
            WHERE NAME = ?
        """
        cur = connection.cursor()
        cur.execute(query,(synonym,))
        return [row['SAMPLE_ID'] for row in cur.fetchall()]


    def find_compound_by_pubchem_cid(self, id):
        query = """
            SELECT DISTINCT SAMPLE_ID
            FROM SAMPLE
            WHERE PUBCHEMCID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(id,))
        return [row['SAMPLE_ID'] for row in cur.fetchall()]


    def find_compound_by_inchi_key(self, inchi_key):
        query = """
            SELECT DISTINCT SAMPLE_ID
            FROM SAMPLE
            WHERE INCHIKEY = ?
        """
        cur = connection.cursor()
        cur.execute(query,(inchi_key,))
        return [row['SAMPLE_ID'] for row in cur.fetchall()]


    def find_compound_by_broad_cpd_id(self, broad_id):
        query = """
            SELECT DISTINCT SAMPLE_ID
            FROM SAMPLE
            WHERE BROAD_CPD_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(broad_id,))
        return [row['SAMPLE_ID'] for row in cur.fetchall()]


    # helper function to connect names to samples through drug id 
    def get_sample(self, sample_id):
        query = """
            SELECT DRUG_ID, SAMPLE_ID, BROAD_CPD_ID, SMILES, INCHIKEY, PUBCHEMCID 
            FROM SAMPLE
            WHERE SAMPLE_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(sample_id,))
        for row in cur.fetchall():
            return row
        return None


    # creates element for compound
    def get_element(self, row):
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
        
        names= self.Names(name=name,synonyms=synonyms)

        compound = self.Element(
                    id = row['BROAD_CPD_ID'],
                    biolink_class='ChemicalSubstance',
                    identifiers = identifiers,
                    names_synonyms = [names]
                )
        self.add_attributes(row, compound)

        return compound


    clinical_phase_map = {
        'Launched': 'regular_fda_approval',
        'Phase 1': 'fda_clinical_research_phase_1',
        'Phase 1/Phase 2': 'fda_clinical_research_phase_1',
        'Phase 2': 'fda_clinical_research_phase_2',
        'Phase 2/Phase 3': 'fda_clinical_research_phase_2',
        'Phase 3': 'fda_clinical_research_phase_3',
        'Preclinical': 'preclinical_research_phase',
        'Withdrawn': 'post_approval_withdrawal'
    }

    feature_type_map = {
        'moa': 'biolink:mechanism_of_action',
        'disease_area': 'disease_area',
        'clinical_phase': 'biolink:highest_FDA_approval_status'
    }
    
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
            value= feature_row['FEATURE_NAME']
            if feature_row['FEATURE_TYPE'] == 'clinical_phase':
                value= self.clinical_phase_map.get(value, value)
            compound.attributes.append(self.Attribute(
                name= feature_row['FEATURE_TYPE'],
                value= value,
                type= self.feature_type_map[feature_row['FEATURE_TYPE']],
                value_type = 'String'
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
            for inchikey in self.get_identifiers(compound, 'inchikey', de_prefix=False):
                drug_id= self.get_drug_id(inchikey)
                # find feature_name information using drug_id 
                feature_type= self.get_feature_type(drug_id)
                for feature_row in feature_type:
                    feature_name= feature_row['FEATURE_NAME']
                    if feature_name not in output:
                        feature= self.add_element(feature_row, output_list)[-1]
                        # add connection object after building feature element
                        self.add_connections(drug_id, feature_row, feature, compound)
                        output[feature_name]= feature
                    else:
                        # create new connection to a gene or disease already in the dictionary
                        feature= output[feature_name]
                        self.add_connections(drug_id, feature_row, feature, compound)
        return output_list


    def get_feature_type(self, drug_id, feature_type = None):
        if feature_type is None:
            feature_type = self.feature_type
        query = """
            SELECT FEATURE_NAME, FEATURE_XREF, PRIMARY_NAME, FEATURE_ACTION FROM FEATURE
            INNER JOIN FEATURE_MAP ON FEATURE.FEATURE_ID = FEATURE_MAP.FEATURE_ID
            WHERE FEATURE_TYPE = ? AND FEATURE_MAP.DRUG_ID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(feature_type, drug_id,))
        return cur.fetchall()

    # Takes compound and returns drug_id 
    def get_drug_id(self, inchikey):
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
        names.append(self.Names(name=row['FEATURE_NAME'],synonyms=synonyms))
        if row['PRIMARY_NAME'] is not None and row['PRIMARY_NAME'] != '':
            names.append(self.Names(name=row['PRIMARY_NAME'],synonyms=synonyms))
        return names


# Creates element object for feature type
    def add_element(self, row, output_list, ):
        # Add only if HGNC_ID is present (human target)
        if row['FEATURE_XREF'] is not None: 
            # fix identifiers for each transformer
            names= self.get_names(row)
            output_element = self.Element(
                        id = row['FEATURE_XREF'],
                        biolink_class= self.biolink_class,
                        identifiers = self.identifiers(row),
                        names_synonyms = names
                    )       
            output_list.append(output_element) 
            return output_list

    def add_connections (self, drug_id, row, element, compound):
        (predicate, inv_predicate) = self.get_predicates(drug_id, row['FEATURE_ACTION'])
        connection= self.Connection(
            source_element_id= compound.id,
            predicate= predicate, 
            inv_predicate= inv_predicate
        )
        # add attributes
        if  row['FEATURE_ACTION'] is not None and row['FEATURE_ACTION'] != '':
            connection.attributes.append(self.Attribute(
            name= 'FEATURE_ACTION',
            value= row['FEATURE_ACTION'],
            type= 'FEATURE_ACTION',
            value_type = 'String'
            )
            )
        connection.attributes.append(self.Attribute(
            name = 'biolink:primary_knowledge_source',
            value = 'infores:drug-repurposing-hub',
            type = 'biolink:primary_knowledge_source',
            url = 'https://repo-hub.broadinstitute.org/repurposing-app',
            value_type = 'biolink:InformationResource'
            )
        )
        connection.attributes.append(self.Attribute(
            name = 'biolink:knowledge_level',
            value = self.KNOWLEDGE_LEVEL,
            type = 'biolink:knowledge_level',
            value_type = 'String'
            )
        )
        connection.attributes.append(self.Attribute(
            name = 'biolink:agent_type',
            value = self.AGENT_TYPE,
            type = 'biolink:agent_type',
            value_type = 'String'
            )
        )
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

    def get_predicates(self, drug_id, feature_action):
        return (self.PREDICATE, self.INVERSE_PREDICATE)


class IndicationsTransformer(FeaturesTransformer):

    clinical_phases = [
        ['Launched', 'Withdrawn'],
        ['Phase 1','Phase 3','Phase 2','Phase 1/Phase 2','Phase 2/Phase 3','Phase 2/Phase 3'],
        ['Preclinical']
    ]

    feature_map = {
        'agent for': ('biolink:affects', 'biolink:affected_by'),
        'aid for': ('biolink:ameliorates_condition', 'biolink:condition_ameliorated_by'),
        'control for': ('biolink:treats', 'biolink:treated_by'),
        'diagnostic for': ('biolink:diagnoses', 'biolink:is_diagnosed_by'),
        'reversal for': ('biolink:disrupts', 'biolink:disrupted_by'),
        'support for': ('biolink:ameliorates_condition', 'biolink:condition_ameliorated_by')
    }

    def __init__(self):
        super().__init__('info/indications_transformer_info.json')
        self.feature_type= 'indication'
        self.biolink_class= 'DiseaseOrPhenotypicFeature'
        self.clinical_phase_map = {}
        for i, cp in enumerate(self.clinical_phases):
            for phase in cp:
                self.clinical_phase_map[phase] = i

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

    def get_predicates(self,drug_id, feature_action):
        if feature_action == 'indication for':
            for row in self.get_feature_type(drug_id, 'clinical_phase'):
                phase = row['FEATURE_NAME']
                index = self.clinical_phase_map.get(phase,1)
                edge = self.info.knowledge_map.edges[index]
                return (edge.predicate, edge.inverse_predicate)
        if feature_action in self.feature_map:
            return self.feature_map[feature_action]
        return (self.PREDICATE, self.INVERSE_PREDICATE)
