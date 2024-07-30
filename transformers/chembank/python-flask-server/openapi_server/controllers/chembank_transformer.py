import sqlite3
from collections import defaultdict

from transformers.transformer import Transformer


connection = sqlite3.connect("data/ChemBank.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


class ChemBankProducer(Transformer):

    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compounds_transformer_info.json')


    def produce(self, controls):
        element_list = []
        elements = {}
        names  = controls[self.variables[0]]
        for name in names:
            name = name.strip()
            for element in self.find_compound_by_name(name):
                if element.id not in elements:
                    elements[element.id] = element
                    element_list.append(element)
                elements[element.id].attributes.append(self.Attribute(
                    name= 'query name',
                    value= name,
                    type=''
                ))
        return element_list

    def find_compound_by_name(self, name):
        """
            Find compound by a name
        """
        compound_list = []
        compounds = self.find_compound_by_id(name) if self.has_prefix('chembank', str(name), "compound") else find_compound_by_name(name)
        for compound in compounds:
            chembank_id = compound['CHEMBANK_ID']
            compound_id = self.add_prefix('chembank', str(chembank_id))
            names = self.get_names(chembank_id)
            identifiers = {}
            if compound[ 'CHEMBANK_ID'] is not None and compound['CHEMBANK_ID'] != '':
                identifiers['chembank'] = self.add_prefix('chembank', str(compound['CHEMBANK_ID']))
            if compound['SMILES'] is not None and compound['SMILES'] != '':
                identifiers['smiles'] = compound['SMILES']
            if compound['INCHI'] is not None and compound['INCHI'] != '':
                identifiers['inchi'] = compound['INCHI']
            if compound['INCHI_KEY'] is not None and compound['INCHI_KEY'] != '':
                identifiers['inchikey'] = compound['INCHI_KEY']
            if 'DrugBank' in names:
                identifiers['drugbank'] = self.add_prefix('drugbank', str(names['DrugBank'][0]))
            if 'PubChem' in names: 
                identifiers['pubchem'] = self.add_prefix('pubchem', str(names['PubChem'][0]))
            if 'CAS' in names:
                identifiers['cas'] = self.add_prefix('cas', names['CAS'][0])
            element = self.Element(
                id= compound_id,
                biolink_class= self.biolink_class('ChemicalSubstance'),
                identifiers= identifiers,
                names_synonyms= self.get_names_synonyms(names)
            )
            compound_list.append(element)
        return compound_list


    def get_names(self, chembank_id):
        """
            Build names and synonyms list
        """
        names = defaultdict(list)
        for name in get_names(chembank_id):
            names[name['CPD_NAME_TYPE']].append(name['CPD_NAME'])
        return names


    def get_names_synonyms(self, names):
        """
            Build names and synonyms list
        """
        names_synonyms = []
        if 'primary-common' in names or 'common' in names:
            names_synonyms.append(
                self.Names(
                    name = names['primary-common'][0] if 'primary-common' in names else None,
                    synonyms = names['common'] if 'common' in names else None
                )
            )

        if 'primary-brand' in names or 'brand' in names:
            names_synonyms.append(
                self.Names(
                    name = names['primary-brand'][0] if 'primary-brand' in names else None,
                    synonyms = names['brand'] if 'brand' in names else None,
                    type= 'brand name'
                )
            )

        if 'primary-chemical' in names or 'chemical' in names:
            names_synonyms.append(
                self.Names(
                    name = names['primary-chemical'][0] if 'primary-chemical' in names else None,
                    synonyms = names['chemical'] if 'chemical' in names else None,
                    type= 'chemical name'
                )
            )

        for name_type, name_list in names.items():
            if name_type not in {'DrugBank','PubChem','CAS','primary-common','common','primary-brand','brand','primary-chemical','chemical'}:
                names_synonyms.append(
                    self.Names(
                        name = name_list[0] if len(name_list) == 1 else  None,
                        synonyms = name_list if len(name_list) > 1 else  None,
                        type= name_type if name_type != 'ChemBank' else 'ChemBank ID'
                    )
                )
        return names_synonyms


    def find_compound_by_id(self, id):
        chembank_id = self.de_prefix('chembank', str(id), 'compound')
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

