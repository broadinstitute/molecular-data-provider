import sqlite3
from collections import defaultdict

from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure


class ChemBankProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='compounds_transformer_info.json')


    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            for compound_info in self.find_compound_by_name(name):
                compound_list.append(compound_info)
        return compound_list


    def find_compound_by_name(self, name):
        """
            Find compound by a name
        """
        compound_list = []
        compounds = find_compound_by_id(name) if name.upper().startswith('CHEMBANK:') else find_compound_by_name(name)
        for compound in compounds:
            chembank_id = compound[0]
            compound_id = 'ChemBank:'+str(chembank_id)
            smiles = compound[1]
            inchi = compound[2]
            inchi_key = compound[3]
            names = self.get_names(chembank_id)
            compound_info = CompoundInfo(
                compound_id = compound_id,
                identifiers = CompoundInfoIdentifiers(
                    drugbank = 'DrugBank:'+names['DrugBank'][0] if 'DrugBank' in names else None,
                    pubchem = names['PubChem'][0] if 'PubChem' in names else None,
                    chembank = compound_id,
                    cas = names['CAS'][0] if 'CAS' in names else None
                ),
                names_synonyms = self.get_names_synonyms(names),
                structure = CompoundInfoStructure(
                    smiles = smiles,
                    inchi = inchi,
                    inchikey = inchi_key,
                    source = 'ChemBank'
                ),
                attributes = [Attribute(name='query name', value=name,source=self.info.name)],
                source = self.info.name
            )
            compound_list.append(compound_info)
        return compound_list


    def get_names(self, chembank_id):
        """
            Build names and synonyms list
        """
        names = defaultdict(list)
        for name in get_names(chembank_id):
            names[name[2]].append(name[1])
        return names


    def get_names_synonyms(self, names):
        """
            Build names and synonyms list
        """
        names_synonyms = []
        if 'primary-common' in names or 'common' in names:
            names_synonyms.append(
                Names(
                    name = names['primary-common'][0] if 'primary-common' in names else None,
                    synonyms = names['common'] if 'common' in names else None,
                    source = 'ChemBank'
                )
            )

        if 'primary-brand' in names or 'brand' in names:
            names_synonyms.append(
                Names(
                    name = names['primary-brand'][0] if 'primary-brand' in names else None,
                    synonyms = names['brand'] if 'brand' in names else None,
                    source = 'brand-name@ChemBank'
                )
            )

        if 'primary-chemical' in names or 'chemical' in names:
            names_synonyms.append(
                Names(
                    name = names['primary-chemical'][0] if 'primary-chemical' in names else None,
                    synonyms = names['chemical'] if 'chemical' in names else None,
                    source = 'chemical-name@ChemBank'
                )
            )

        for name_type, name_list in names.items():
            if name_type not in {'DrugBank','PubChem','CAS','primary-common','common','primary-brand','brand','primary-chemical','chemical'}:
                names_synonyms.append(
                    Names(
                        name = name_list[0] if len(name_list) == 1 else  None,
                        synonyms = name_list if len(name_list) > 1 else  None,
                        source = name_type+'@ChemBank' if name_type != 'ChemBank' else 'ChemBank ID',
                    )
                )
        return names_synonyms


connection = sqlite3.connect("ChemBank.sqlite", check_same_thread=False)


def find_compound_by_name(name):
    query = """
        SELECT CHEMBANK_ID, SMILES, INCHI, INCHI_KEY
        FROM COMPOUND
        WHERE CHEMBANK_ID = (
            SELECT DISTINCT CHEMBANK_ID FROM COMPOUND_NAME
            WHERE CPD_NAME = ?
        )
    """
    cur = connection.cursor()
    cur.execute(query,(name,))
    return cur.fetchall()


def find_compound_by_id(id):
    chembank_id = int(id[9:] if id.upper().startswith('CHEMBANK:') else id)
    compound = get_compound(chembank_id)
    if len(compound) > 1:
        print("WARNING: found multiple compounds for '"+id+"'")
    if len(compound) > 0:
        return compound
    compound = find_compound_by_name(id)
    if len(compound) > 1:
        print("WARNING: found multiple compounds for '"+id+"'")
    if len(compound) > 0:
        return compound
    return []


def get_compound(chembank_id):
    query = """
        SELECT CHEMBANK_ID, SMILES, INCHI, INCHI_KEY FROM COMPOUND
        WHERE CHEMBANK_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(chembank_id,))
    return cur.fetchall()


def get_names(chembank_id):
    query = """
        SELECT COMPOUND_NAME.CHEMBANK_ID, COMPOUND_NAME.CPD_NAME, COMPOUND_NAME_TYPE.CPD_NAME_TYPE
        FROM COMPOUND_NAME
        INNER JOIN COMPOUND_NAME_TYPE ON COMPOUND_NAME.CPD_NAME_TYPE_ID = COMPOUND_NAME_TYPE.CPD_NAME_TYPE_ID
        WHERE CHEMBANK_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(chembank_id,))
    return cur.fetchall()

