import sqlite3

from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure


class DrugCentralIndicationsTransformer(Transformer):

    variables = ['disease']

    def __init__(self):
        super().__init__(self.variables, definition_file='indications_transformer_info.json')


    def produce(self, controls):
        compound_list = []
        print(controls)
        diseases = find_disease(controls['disease'])
        for disease in diseases:
            disease_id = disease[0]
            disease_name = disease[1]
            for result in find_drugs(int(disease_id)):
                drug = self.get_drug(result)
                drug.attributes = [Attribute(name='indication', value=disease_name,source=self.info.name)]
                compound_list.append(drug)
        return compound_list


    def get_drug(self, row):
        drug_id = str(row[0])
        drug_name = row[1]
        cas = row[2]
        smiles = row[3]
        inchi = row[4]
        inchi_key = row[5]

        return CompoundInfo(
            compound_id = 'DrugCentral:'+drug_id,
            identifiers = CompoundInfoIdentifiers(
                drugcentral = 'DrugCentral:'+drug_id,
                cas = cas
            ),
            names_synonyms = [Names(
                name = drug_name,
                synonyms = [],
                source = 'DrugCentral',
                url = 'http://drugcentral.org/drugcard/'+drug_id
            )],
            structure = CompoundInfoStructure(
                smiles = smiles,
                inchi = inchi,
                inchikey = inchi_key,
                source = 'DrugCentral'
            ),
            source = self.info.name
        )


connection = sqlite3.connect("DrugCentral.sqlite", check_same_thread=False)


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


def find_disease(query):
    if ':' in query:
        results = find_disease_query('MONDO_ID',query)
        if len(results) > 0:
            return results
        if query.startswith('UMLS:'):
            return find_disease_query('UMLS_CUI',query[5:])
        if query.startswith('SNOMEDCT:'):
            return find_disease_query('SNOMEDCT_CUI',query[9:])
        if query.startswith('DOID:'):
            return find_disease_query('DOID',query)
        return []
    else:
        return find_disease_query('DISEASE_NAME',query)
