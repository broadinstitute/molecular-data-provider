import sqlite3
import requests
import time
import re

from contextlib import closing
from transformers.transformer import Transformer, Producer


CMAP_URL = 'https://s3.amazonaws.com/macchiato.clue.io/builds/touchstone/v1.1/arfs/{}/pert_id_summary.gct'
VERSION_URL = 'https://api.clue.io/api/touchstone-version'

connection = sqlite3.connect("data/cmap.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

BIOLINK_CLASS = {'gene':'Gene','compound':'SmallMolecule'}
OUTPUT_CLASS_TABLE = {'gene':'GENE','compound':'COMPOUND'}
ID_KEY = {'gene':'entrez','compound':'pubchem'}

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


class CmapProducer(Producer):

    variables = ['compound']

    def __init__(self, definition_file='info/compound_producer_info.json'):
        super().__init__(self.variables, definition_file)


    def find_names(self, name):
        if self.has_prefix('pubchem', name, self.OUTPUT_CLASS):
            return find_cid( name)
        if inchikey_regex.match(name) is not None:
            return find_compound_by_inchikey(name)
        else:
            return self.find_name(name)


    def find_name(self, name):
        pert_ids = find_pert_ids('COMPOUND', 'cmap_name', [name])
        if len(pert_ids) > 0:
            return pert_ids
        pert_ids = find_pert_ids('COMPOUND', 'pert_iname', [name])
        if len(pert_ids) > 0:
            return pert_ids
        pert_ids = find_pert_ids('COMPOUND', 'pert_id', [name])
        if len(pert_ids) > 0:
            return pert_ids
        pert_ids = find_pert_ids('COMPOUND', 'aliases', [name])
        return pert_ids


    def create_element(self, pert_id):
        return create_compound_element(self, pert_id)



class CmapExpander(Transformer):

    variables = ['score threshold', 'limit']

    def __init__(self, input_class, output_class):
        super().__init__(self.variables,'info/transformer_info.json')
        self.input_class = input_class
        self.output_class = output_class
        # update transformer_info
        nodes = self.info.knowledge_map.nodes
        self.info.function = 'expander' if input_class == output_class else 'transformer'
        self.info.knowledge_map.input_class = input_class
        self.info.knowledge_map.edges[0].subject = BIOLINK_CLASS[input_class]
        self.info.knowledge_map.output_class = output_class
        self.info.knowledge_map.edges[0].object = BIOLINK_CLASS[output_class]
        self.info.knowledge_map.nodes = {}
        self.info.knowledge_map.nodes[BIOLINK_CLASS[input_class]] = nodes[BIOLINK_CLASS[input_class]]
        self.info.knowledge_map.nodes[BIOLINK_CLASS[output_class]] = nodes[BIOLINK_CLASS[output_class]]
        self.info.name = self.info.name + input_class + '-to-' + output_class + ' ' + self.info.function
        self.PROVIDED_BY  = self.info.name
        self.qualifiers = []
        if input_class == 'gene':
            self.get_pert_ids = self.get_gene_pert_ids
            self.qualifiers.append(self.Qualifier('subject_aspect_qualifier','gene_knockdown'))
        if input_class == 'compound':
            self.get_pert_ids = self.get_compound_pert_ids
            self.qualifiers.append(self.Qualifier('subject_aspect_qualifier','compound_treatment'))
        if output_class == 'gene':
            self.create_element = create_gene_element
            self.qualifiers.append(self.Qualifier('object_aspect_qualifier','gene_knockdown'))
        if output_class == 'compound':
            self.create_element = create_compound_element
            self.qualifiers.append(self.Qualifier('object_aspect_qualifier','compound_treatment'))


    def map(self, collection, controls):
        list = []
        elements = {}
        return self.connections(list, elements, collection, controls)


    def expand(self, collection, controls):
        list = []
        elements = {}
        for query in collection:
            query.connections = []
            list.append(query)
            elements[query.id]=query
        return self.connections(list, elements, collection, controls)


    def connections(self, list, elements, collection, controls):
        for query in collection:
            for pert_id in self.get_pert_ids(query):
                if query.id in elements:
                    elements[pert_id] = query
                hits = self.cmap_connections(pert_id, controls)
                for (score, hit_id) in hits:
                    element = self.get_element(hit_id, elements, list)
                    self.add_connection(element, score, query.id, pert_id)
        return list


    def get_compound_pert_ids(self, element):
        pubchem_ids = self.get_identifiers(element, 'pubchem', de_prefix=False)
        pert_ids = find_pert_ids('COMPOUND', 'xref_id', pubchem_ids)
        if len(pert_ids) > 0:
            return pert_ids
        inchikeys = self.get_identifiers(element, 'inchikey', de_prefix=True)
        pert_ids = find_pert_ids('COMPOUND', 'inchi_key', inchikeys)
        return pert_ids


    def get_gene_pert_ids(self, element):
        entrez_ids = self.get_identifiers(element, 'entrez', de_prefix=False)
        pert_ids = find_pert_ids('GENE', 'xref_id', entrez_ids)
        if len(pert_ids) > 0:
            return pert_ids
        ensembl_ids = self.get_identifiers(element, 'ensembl', de_prefix=True)
        pert_ids = find_pert_ids('GENE', 'ensembl_id', entrez_ids)
        return pert_ids


    def cmap_connections(self, pert_id, controls):
        min_score = controls['score threshold']
        limit = controls['limit']
        output_class_table = OUTPUT_CLASS_TABLE[self.output_class]
        return find_connections(output_class_table, pert_id, min_score, limit)


    def get_element(self, hit_id, elements, list):
        if hit_id in elements:
            return elements[hit_id]
        element = self.create_element(self, hit_id)
        elements[hit_id] = element
        list.append(element)
        return element


    def get_id(self, query):
        return query.identifiers.get(ID_KEY[self.input_class])


    def add_connection(self, element, score, source_element_id, pert_id):
        connection = self.Connection(
            source_element_id = source_element_id,
            predicate = self.PREDICATE,
            inv_predicate = self.INVERSE_PREDICATE,
            attributes = [
                self.Attribute(
                    name = 'biolink:primary_knowledge_source',
                    value = 'infores:cmap',
                    type = 'biolink:primary_knowledge_source',
                    url = 'https://clue.io/connection?url=macchiato.clue.io/builds/touchstone/v1.1/arfs/{}'.format(pert_id),
                    value_type = 'biolink:InformationResource'
                ),
                self.Attribute(
                    name = 'knowledge level',
                    value = self.KNOWLEDGE_LEVEL,
                    type = 'biolink:knowledge_level',
                    value_type = 'String'
                ),
                self.Attribute(
                    name = 'agent type',
                    value = self.AGENT_TYPE,
                    type = 'biolink:agent_type',
                    value_type = 'String'
                ),
                self.Attribute(
                    name = 'CMAP similarity score',
                    value = score,
                    type = 'CMAP:similarity_score',
                    value_type = 'Double'
                ),
                self.Attribute(
                    name = 'reference',
                    value = 'PMID:29195078',
                    type = 'biolink:Publication',
                    value_type = 'String'
                ),
                self.Attribute(
                    name = 'about CMAP',
                    value = 'https://clue.io/cmap',
                    type = 'about CMAP',
                    url = 'https://clue.io/cmap',
                    value_type = 'String'
                ),
                self.Attribute(
                    name = 'CMAP touchstone data version',
                    value = self.get_version(),
                    type = 'CMAP touchstone data version',
                    url = 'https://api.clue.io/api/touchstone-version',
                    value_type = 'String'
                )
            ],
            qualifiers = self.qualifiers
        )
        element.connections.append(connection)


    data_version = '1.1'
    version_timestamp = 0

    def get_version(self):
        now = time.time()
        if now - self.version_timestamp > 24*60*60: # 1 day
            try:
                with closing(requests.get(VERSION_URL)) as response:
                    if response.status_code == 200:
                        version = response.json()['version']
                        if version.startswith('1.1'):
                            self.data_version = version
                            self.version_timestamp = now
                    else:
                        print("WARNING: failed to obtain CMAP data version :"+response.status())
            except:
                print("WARNING: failed to obtain CMAP data version")
                data_version = '1.1'
        return self.data_version


def find_cid(cid):
    return find_pert_ids('COMPOUND', 'xref_id', [cid])


def find_compound_by_inchikey(inchikey):
    return find_pert_ids('COMPOUND', 'inchi_key', [inchikey])


def find_compounds(where_column, values):
    query = """
    SELECT pert_id
    FROM COMPOUND
    WHERE {} in ('{}')
    """.format(where_column, "','".join(values))
    cur = connection.cursor()
    cur.execute(query)
    return [row['pert_id'] for row in cur.fetchall()]


def find_pert_ids(table, where_column, values):
    if len(values) == 0:
        return []
    query = """
    SELECT pert_id
    FROM {}
    WHERE {} in ('{}')
    """.format(table, where_column, "','".join(values))
    cur = connection.cursor()
    cur.execute(query)
    return [row['pert_id'] for row in cur.fetchall()]


def create_compound_element(transformer, pert_id):
    query = """
    SELECT
        pert_iname,
        xref_id,
        cmap_name,
        smiles,
        inchi_key,
        aliases
    FROM COMPOUND
    WHERE pert_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(pert_id,))
    element = None
    for row in cur.fetchall():
        xref_id = row['xref_id']
        identifiers = {'pubchem': xref_id, 'smiles': row['smiles'], 'inchikey': row['inchi_key']}
        name = row['pert_iname']
        synonyms = []
        if row['cmap_name'] != name:
            synonyms.append(row['cmap_name'])
        if row['aliases']:
            synonyms.append(row['aliases'])
        names = transformer.Names(name=name, synonyms=synonyms)
        element = transformer.Element(
            id = xref_id,
            biolink_class = "SmallMolecule",
            identifiers = identifiers,
            names_synonyms = [names],
            attributes = []
        )
    return element


def create_gene_element(transformer, pert_id):
    query = """
    SELECT
        xref_id,
        gene_symbol,
        gene_title,
        ensembl_id
    FROM GENE
    WHERE pert_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(pert_id,))
    element = None
    for row in cur.fetchall():
        xref_id = row['xref_id']
        ensembl = transformer.add_prefix('ensembl', row['ensembl_id'])
        identifiers = {'entrez': xref_id, 'ensembl': ensembl}
        name = row['gene_title']
        synonyms = []
        if row['gene_symbol']:
            synonyms.append(row['gene_symbol'])
        names = transformer.Names(name=name, synonyms=synonyms)
        element = transformer.Element(
            id = xref_id,
            biolink_class = "Gene",
            identifiers = identifiers,
            names_synonyms = [names],
            attributes = [transformer.Attribute(
                name = 'gene_symbol',
                value = row['gene_symbol'],
                type = 'biolink:symbol',
                value_type = 'String'
            )]
        )
    return element


def find_connections(output_class_table, pert_id_1, threshold, limit):
    limit_clause = ''
    if limit > 0:
        limit_clause = 'LIMIT {}'.format(limit)
    query = """
    SELECT pert_id_2, cmap_score
    FROM CMAP_SCORE
    JOIN {} ON {}.pert_id = CMAP_SCORE.pert_id_2
    WHERE pert_id_1 = ?
    AND cmap_score >= ?
    AND pert_id_1 != pert_id_2
    ORDER BY cmap_score DESC
    {}    
    """.format(output_class_table, output_class_table, limit_clause)
    cur = connection.cursor()
    cur.execute(query, (pert_id_1, threshold))
    return [(row['cmap_score'], row['pert_id_2']) for row in cur.fetchall()]
