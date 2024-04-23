import sqlite3
import re

from transformers.transformer import Transformer, Producer
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.connection import Connection

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

class DrugCentralIndicationsTransformer(Transformer):

    variables = ['disease']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/indications_transformer_info.json')

    


    def produce(self, controls):
        compound_list = []
        for source_element_id in controls['disease']:
            diseases = find_disease(self, source_element_id)
            for disease in diseases:
                disease_id = disease[0]
                for result in find_drugs(int(disease_id)):
                    msg ={}
                    drug = self.get_drug(result, msg)
                    if drug is None:
                        return ({ "status": 500, "title": "Internal Server Error", "detail": msg['message'], "type": "about:blank" }, 500 )
                    drug.attributes = []

                    connection = Connection(
                        source_element_id = source_element_id,
                        biolink_predicate = self.PREDICATE,
                        inverse_predicate = self.INVERSE_PREDICATE,
                        source = self.SOURCE,
                        provided_by = self.PROVIDED_BY,
                        attributes = [Attribute(            
                                        attribute_type_id =  "biolink:primary_knowledge_source",
                                        original_attribute_name = "primary_knowledge_source",
                                        value = "infores:drugcentral",
                                        attribute_source = "infores:molepro_kp",
                                        provided_by = "DrugCentral indications transformer"
                                        )
                        ]
                    )
                    drug.connections.append(connection)
                    compound_list.append(drug)
        return compound_list


    def get_drug(self, row, msg):
        drug_id = str(row['DRUG_CENTRAL_ID'])
        drug_name = row['DRUG_NAME']
        cas = row['CAS_RN']
        smiles = row['SMILES']
        inchi = row['INCHI']
        inchi_key = row['INCHI_KEY']
    #   Element object (replaces CompoundInfo object of MolePro 2.0)
        element = Element(
                id = self.add_prefix('drugcentral', drug_id),
                biolink_class  = self.biolink_class(self.OUTPUT_CLASS),
                names_synonyms = [],
                identifiers = {},
                attributes  = [],
                connections = [],
                source = self.SOURCE
        )
        element.identifiers['drugcentral'] = self.add_prefix('drugcentral', drug_id)
        element.identifiers['cas']      = self.add_prefix('cas', cas)
        element.identifiers['smiles']   = self.add_prefix('smiles', smiles)
        element.identifiers['inchi']    = self.add_prefix('inchi', inchi)
        element.identifiers['inchikey'] = self.add_prefix('inchikey', inchi_key)
        element.names_synonyms.append(Names(
                                            name = drug_name,
                                            synonyms = [],
                                            source = self.SOURCE)
                                    )
        return element


    ########################################################################################################
    # 
    # Annotate the transformer_info.json object with the drug and disease counts in the database
    #
    def update_transformer_info(self, jsonObj):    
        get_drug_counts(jsonObj)  
        get_disease_counts(jsonObj)


connection = sqlite3.connect("data/DrugCentral.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


########################################################################################################
# 
# Get the number of drugs in the Drug Central database for annotating the transformer_info.json file
#
def get_drug_counts(info):
    """
        count all the rows in DRUG table
    """
    query = """
        SELECT COUNT ( DISTINCT DRUG_CENTRAL_ID ) AS "Number of drugs" 
        FROM DRUG;
        """
#    connection.row_factory = sqlite3.Row
    cur = connection.execute(query)
#    info["knowledge_map"]["nodes"]["ChemicalSubstance"]["count"] = -1  # step 1, clear the old count
    info.knowledge_map.nodes['ChemicalSubstance'].count = -1 # step 1, clear the old count
    for row in cur.fetchall():
    #   step 2, fill the count value 
        info.knowledge_map.nodes['ChemicalSubstance'].count = (row["Number of drugs"])


########################################################################################################
# 
# Get the number of disease in the Drug Central database for annotating the transformer_info.json file
#
def get_disease_counts(info):
    """
        count all the rows in DISEASE table
    """
    query = """
        SELECT COUNT ( DISTINCT DISEASE_ID ) AS "Number of diseases" 
        FROM DISEASE;
        """
    connection.row_factory = sqlite3.Row
    cur = connection.execute(query)
    info.knowledge_map.nodes['Disease'].count = -1  # step 1, clear the old count
    for row in cur.fetchall():
    #   step 2, fill the count value 
        info.knowledge_map.nodes['Disease'].count  = (row["Number of diseases"])



def find_drugs(disease_id):
    query = """
        SELECT DRUG.DRUG_CENTRAL_ID, DRUG_NAME, CAS_RN, SMILES, INCHI, INCHI_KEY
        FROM INDICATION
        INNER JOIN DRUG ON DRUG.DRUG_CENTRAL_ID = INDICATION.DRUG_CENTRAL_ID
        WHERE INDICATION.DISEASE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(disease_id,))
    return cur.fetchall()


def find_disease_query(column, value):
    query = """
        SELECT DISEASE_ID, DISEASE_NAME, MONDO_ID FROM DISEASE
        WHERE {} = ?
    """.format(column)
    cur = connection.cursor()
    cur.execute(query,(value,))
    return cur.fetchall()


def find_disease(self, query):
    if ':' in query:
        results = find_disease_query('MONDO_ID',query)
        if len(results) > 0:
            return results
        if self.has_prefix('umls', query, 'disease'):
            return find_disease_query('UMLS_CUI', self.de_prefix('umls', query, 'disease') )
        if self.has_prefix('snomed', query, 'disease'):
            return find_disease_query('SNOMEDCT_CUI', self.de_prefix('snomed', query, 'disease'))
        if self.has_prefix('disease_ontology', query, 'disease'):
            return find_disease_query('DOID',query)
        return []
    else:
        return find_disease_query('DISEASE_NAME',query)


def get_disease(disease_id):
    query = """
        SELECT DISEASE_ID, DISEASE_NAME, MONDO_ID, UMLS_CUI, SNOMEDCT_CUI, DOID FROM DISEASE
        WHERE DISEASE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(disease_id,))
    return cur.fetchall()


def find_drug_query(column, value):
    query = """
        SELECT DRUG_CENTRAL_ID, DRUG_NAME, CAS_RN, SMILES, INCHI, INCHI_KEY
        FROM DRUG
        WHERE {} = ?
    """.format(column)
    cur = connection.cursor()
    cur.execute(query,(value,))
    return cur.fetchall()


class DrugCentralDiseaseProducer(Producer):

    variables = ['disease']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/disease_transformer_info.json')


    def update_transformer_info(self, transformer_info):   
        get_disease_counts(transformer_info)


    def find_names(self, name):
        ids = []
        for row in find_disease(self, name):
            ids.append(row['DISEASE_ID'])
        return ids


    def create_element(self, disease_id):
        element = None
        for row in get_disease(disease_id):
            disease_name = row['DISEASE_NAME']
            id = 'DrugCentral:'+ disease_name
            biolink_class = self.biolink_class(self.OUTPUT_CLASS)
            identifiers = {}
            if row['MONDO_ID'] is not None and row['MONDO_ID'].startswith('HP'):
                id = self.add_prefix('hpo',row['MONDO_ID'])
                identifiers['hpo'] = id
            if row['MONDO_ID'] is not None and row['MONDO_ID'].startswith('NCIT'):
                id = self.add_prefix('nci_thesaurus',row['MONDO_ID'])
                identifiers['nci_thesaurus'] = id
            if row['DOID'] is not None:
                id = self.add_prefix('disease_ontology',row['DOID'])
                identifiers['disease_ontology'] = id
            if row['MONDO_ID'] is not None and row['MONDO_ID'].startswith('MONDO'):
                id = self.add_prefix('mondo',row['MONDO_ID'])
                identifiers['mondo'] = id
            if row['UMLS_CUI'] is not None:
                id = self.add_prefix('umls',row['UMLS_CUI'])
                identifiers['umls'] = id
            if row['SNOMEDCT_CUI'] is not None:
                id = self.add_prefix('snomed',row['SNOMEDCT_CUI'])
                identifiers['snomed'] = id
            
            names = [self.Names(disease_name)]
            element = self.Element(id, biolink_class, identifiers, names)
        return element


class DrugCentralCompoundProducer(Producer):

    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compound_transformer_info.json')


    def update_transformer_info(self, transformer_info):   
        get_drug_counts(transformer_info)


    def produce(self, controls):
        self.map = {}
        return super().produce(controls)


    def find_names(self, name):
        ids = []
        for row in self.find_compound(name):
            self.map[row['DRUG_CENTRAL_ID']] = row
            ids.append(row['DRUG_CENTRAL_ID'])
        return ids


    def find_compound(self, name):
        if self.has_prefix('drugcentral', name, 'compound'):
            drug_central_id = self.de_prefix('drugcentral', name, 'compound')
            return find_drug_query('DRUG_CENTRAL_ID', drug_central_id)
        if inchikey_regex.match(name) is not None:
            return find_drug_query('INCHI_KEY', name)
        return find_drug_query('DRUG_NAME', name)


    def create_element(self, drug_central_id):
        element = None
        if drug_central_id in self.map:
            row = self.map[drug_central_id]
            id = self.add_prefix('drugcentral', str(drug_central_id))
            drug_name = row['DRUG_NAME']
            cas = row['CAS_RN']
            smiles = row['SMILES']
            inchi = row['INCHI']
            inchi_key = row['INCHI_KEY']
            biolink_class = self.biolink_class(self.OUTPUT_CLASS)
            identifiers = {'drugcentral' : id}
            if cas is not None:
                identifiers['cas'] = self.add_prefix('cas', cas)
            if smiles is not None:
                identifiers['smiles'] = self.add_prefix('smiles', smiles)
            if smiles is not None:
                identifiers['inchi'] = self.add_prefix('inchi', inchi)
            if smiles is not None:
                identifiers['inchikey'] = self.add_prefix('inchikey', inchi_key)                
            names = [self.Names(drug_name)]
            element = self.Element(id, biolink_class, identifiers, names)
        return element