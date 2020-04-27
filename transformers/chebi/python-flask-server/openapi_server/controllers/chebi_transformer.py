import sqlite3
import re

from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure


class ChebiByNameProducer(Transformer):

    variables = ['compounds']

    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

    def __init__(self):
        super().__init__(self.variables, definition_file='compounds_transformer_info.json')


    def produce(self, controls):
        compound_list = []
        compounds = {}
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            for compound in self.find_compound(name):
                id = compound[0]
                if id not in compounds.keys():
                    compounds[id]= self.compound_info(id)
                    compound_list.append(compounds[id])
                compounds[id].attributes.append(Attribute(name='query name', value=name,source=self.info.name))
        return compound_list


    def find_compound(self, name):
        if name.startswith('InChI='):
            return find_compound_by_structure(name)
        if name.startswith('CHEBI:'):
            return find_compound_by_id(name)
        if self.inchikey_regex.match(name) is not None:
            return find_compound_by_structure(name)

        ids = find_compound_by_name(name)
        if len(ids) != 0:
            return ids
        else:
            return find_compound_by_synonym(name)

    def compound_info(self, id):
        compound = get_compound(id)[0]
        structure = get_structure(id)
        compound_info = CompoundInfo(
            compound_id = compound[2],
            identifiers = CompoundInfoIdentifiers(
                chebi = compound[2]
            ),
            structure = CompoundInfoStructure(
                smiles = structure.get('SMILES'),
                inchi = structure.get('InChI'),
                inchikey = structure.get('InChIKey'),
                source = self.info.label
            ),
            names_synonyms = self.names(id, compound[1]),
            attributes = [],
            source = self.info.name
        )
        return compound_info


    def names(self, id, name):
        name_map = {
            'ChEBI': Names(
                name=name,
                synonyms=[],
                source='ChEBI',
                url='https://www.ebi.ac.uk/chebi/searchId.do?chebiId={}'.format(id)
            )
        }
        names_list = [name_map['ChEBI']]
        synonyms = get_synonyms(id)
        for synonym, type, source, language in synonyms:
            if source not in name_map.keys():
                name_map[source] = Names(synonyms = [], source = source+'@ChEBI')
                names_list.append(name_map[source])
            names = name_map[source]
            if (type=='INN' or type=='NAME') and language=='en' and names.name is None:
                names.name = synonym
            else:
                names.synonyms.append(synonym)
        return names_list


connection = sqlite3.connect("ChEBI.sqlite", check_same_thread=False)


def find_compound_by_name(name):
    query = """
        SELECT DISTINCT id FROM compounds
        WHERE name = ?
    """
    cur = connection.cursor()
    cur.execute(query,(name,))
    return cur.fetchall()


def find_compound_by_id(id):
    query = """
        SELECT DISTINCT id FROM compounds
        WHERE chebi_accession = ?
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def find_compound_by_synonym(synonym):
    query = """
        SELECT DISTINCT compound_id FROM names
        WHERE name = ?
    """
    cur = connection.cursor()
    cur.execute(query,(synonym,))
    return cur.fetchall()


def find_compound_by_structure(structure):
    query = """
        SELECT DISTINCT compound_id FROM structures
        WHERE structure = ?
    """
    cur = connection.cursor()
    cur.execute(query,(structure,))
    return cur.fetchall()


def get_compound(id):
    query = """
        SELECT id, name, chebi_accession FROM compounds
        WHERE id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_synonyms(id):
    query = """
        SELECT name, type, source, language FROM names
        WHERE compound_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_structure(id):
    query = """
        SELECT structure, type FROM structures
        WHERE compound_id = ?
    """
    structures = {}
    cur = connection.cursor()
    cur.execute(query,(id,))
    for (structure, type) in cur.fetchall():
        if type != 'mol':
            structures[type] = structure
    return structures

