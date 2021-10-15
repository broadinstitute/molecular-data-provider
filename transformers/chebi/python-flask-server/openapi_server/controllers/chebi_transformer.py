import sqlite3
import re

from openapi_server.models.names import Names
from transformers.transformer import Producer # noqa: E501


db_connection = sqlite3.connect("data/ChEBI.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
db_connection.row_factory = sqlite3.Row

class ChebiCompoundProducer(Producer):
    variables = ['compounds']
    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compounds_transformer_info.json')



    ###########################################################################
    #
    # Called by Producer Base Class' produce() method
    # name
    #
    #
    def find_names(self, name):
        ids = []
        self.find_compound(name, ids)

        return ids


    ###########################################################################
    #
    # Called by Producer Base Class' produce() method
    #
    def create_element(self, compound_id):
        compound_name = None
        for row in get_compound(compound_id):
            compound_name = row['name']
        names = self.names(compound_id, compound_name)
        structures = get_structure(compound_id)
        id = self.add_prefix('chebi',str(compound_id))
        identifiers = {
            'chebi': id,
            'smiles': structures.get('SMILES'),
            'inchi':  structures.get('InChI'),
            'inchikey': structures.get('InChIKey'),
        }
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)

        element = self.Element(id, biolink_class, identifiers, names)

        return element


    def find_compound(self, name, ids):
        if name.startswith('InChI='):
            find_compound_by_structure(name, ids)
            return
        if name.startswith('CHEBI:'):
            find_compound_by_id(name, ids)
            return
        if self.inchikey_regex.match(name) is not None:
            find_compound_by_structure(name, ids)
            return
        find_compound_by_name(name, ids)
        if len(ids) == 0:
            find_compound_by_synonym(name, ids)


    def names(self, id, primary_name):
        name_map = {
            'en@@ChEBI': Names(
                name=primary_name,
                synonyms=[],
                name_type= None,
                source=self.SOURCE,
                provided_by= self.PROVIDED_BY,
                language= 'en'
            )
        }
        names_list = [name_map['en@@ChEBI']]
        synonyms = get_synonyms(id)
        for row in synonyms:
            name = row['name']
            type = row['type']
            source = row['source']
            language = row['language']
            name_type = '' if type=='NAME' or type=='SYNONYM' else type
            key = language+'@'+name_type+'@'+source

            if key not in name_map.keys():
                name_map[key] = Names(
                    name=None,
                    synonyms=[],
                    name_type= name_type if name_type != '' else None,
                    source=source,
                    provided_by= self.PROVIDED_BY,
                    language= language  
                )
                names_list.append(name_map[key])
            names = name_map[key]
            if type=='SYNONYM' or names.name is not None:
                names.synonyms.append(name)
            else:
                names.name = name
                
        return names_list


def find_compound_by_name(name, ids):
    query = """
        SELECT DISTINCT id FROM compounds
        WHERE name = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(name,))
    for row in cur.fetchall():
        ids.append(row['id'])


def find_compound_by_id(chebi_id, ids):
    query = """
        SELECT DISTINCT id FROM compounds
        WHERE chebi_accession = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))
    for row in cur.fetchall():
        ids.append(row['id'])


def find_compound_by_synonym(synonym, ids):
    query = """
        SELECT DISTINCT compound_id FROM names
        WHERE name = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(synonym,))
    for row in cur.fetchall():
        ids.append(row['compound_id'])


def find_compound_by_structure(structure, ids):
    query = """
        SELECT DISTINCT compound_id FROM structures
        WHERE structure = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(structure,))
    for row in cur.fetchall():
        ids.append(row['compound_id'])


def get_compound(id):
    query = """
        SELECT id, name, chebi_accession FROM compounds
        WHERE id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_synonyms(id):
    query = """
        SELECT name, type, source, language FROM names
        WHERE compound_id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_structure(id):
    query = """
        SELECT structure, type FROM structures
        WHERE compound_id = ?
    """
    structures = {}
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    for (structure, type) in cur.fetchall():
        if type != 'mol':
            structures[type] = structure
    return structures

