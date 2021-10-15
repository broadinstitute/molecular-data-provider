import sqlite3
import json

from transformers.transformer import Transformer
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.connection import Connection



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
            return find_disease_query('UMLS_CUI', self.de_prefix('umls', query) )
        if self.has_prefix('snomed', query, 'disease'):
            return find_disease_query('SNOMEDCT_CUI', self.de_prefix('snomed', query))
        if self.has_prefix('disease_ontology', query, 'disease'):
            return find_disease_query('DOID',query)
        return []
    else:
        return find_disease_query('DISEASE_NAME',query)
