import sqlite3
import re

from transformers.transformer import Transformer
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.connection import Connection
from openapi_server.models.attribute import Attribute

#Biolink class
CHEMICAL_SUBSTANCE = 'ChemicalSubstance'
DISEASE = 'Disease'
GENE = 'Gene'

# CURIE prefix
HMDB = 'HMDB:'

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

class HmdbTargets(Transformer):


    def __init__(self):
        super().__init__([], definition_file='info/targets_transformer_info.json')
        self.info.knowledge_map.nodes['ChemicalSubstance'].count = concept_count('metabolite')
        self.info.knowledge_map.nodes['Gene'].count = concept_count('protein')
        self.load_ids()


    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            metabolite = find_metabolite(compound)
            if metabolite is not None:
                targets = self.find_targets(metabolite, compound.id)
                for target in targets:
                    gene_id = target['entrez']
                    gene = genes.get(gene_id)
                    if gene is None:
                        gene = Element(
                            id = gene_id,
                            biolink_class=GENE,
                            identifiers = {'entrez': gene_id},
                            names_synonyms=[Names(name = target['name'])],
                            attributes = [Attribute(
                                name='UniProtKB', 
                                value=target['uniprot'],
                                source=self.info.label,
                                provided_by=self.info.name
                            )],
                            connections=[],
                            source = self.info.name
                        )
                        gene_list.append(gene)
                        genes[gene_id] = gene
                    gene.connections.append(target['connection'])
        return gene_list


    def find_targets(self, metabolite, source_element_id):
        bcid = metabolite['BEACON_CONCEPT_ID']
        target_list = []
        for target in find_statements(bcid,'protein'):
            if target['ID'].startswith('UniProtKB:'):
                uniprot = target['ID'][10:]
                entrez = self.id_map.get(uniprot)
                if entrez is not None:
                    connection = self.create_connection(source_element_id, target)
                    target_list.append({
                        'uniprot':uniprot, 
                        'entrez': 'NCBIGene:'+entrez, 
                        'name': target['NAME'], 
                        'connection': connection
                    })
        return target_list


    def create_connection(self, source_element_id, target):
        connection = Connection(
            source_element_id=source_element_id,
            type = self.info.knowledge_map.predicates[0].predicate,
            relation = self.info.knowledge_map.predicates[0].predicate,
            source = self.info.label,
            provided_by= self.info.name,
            attributes=[]
        )

        beacon_statement_id = target['BEACON_STATEMENT_ID']
        for reference in get_references(beacon_statement_id):
            connection.attributes.append(Attribute(
                name = 'reference',
                value = reference['PMID'],
                type = 'reference',
                source = self.info.label,
                provided_by= self.info.name
            ))
        return connection


    def load_ids(self):
        self.id_map = {}
        with open("data/UniProt2Entrez.txt",'r') as f:
            first_line = True
            for line in f:
                if not first_line:
                    row = line.strip().split('\t')
                    uniprot = row[0]
                    entrez = row[1]
                    self.id_map[uniprot] = entrez
                first_line = False


class HmdbDisorders(Transformer):


    def __init__(self):
        super().__init__([], definition_file='info/disorders_transformer_info.json')
        self.info.knowledge_map.nodes['ChemicalSubstance'].count = concept_count('metabolite')
        self.info.knowledge_map.nodes['Disease'].count = concept_count('disease')


    def map(self, compound_list, controls):
        disorder_list = []
        disorders = {}
        for compound in compound_list:
            metabolite = find_metabolite(compound)
            if metabolite is not None:
                for disorder in self.find_disorders(metabolite, compound.id):
                    disorder_id = disorder['name']
                    element = disorders.get(disorder_id)
                    if element is None:
                        element = self.create_element(disorder)
                        disorder_list.append(element)
                        disorders[disorder_id] = element
                    element.connections.append(disorder['connection'])
        return disorder_list

    
    def find_disorders(self, metabolite, source_element_id):
        bcid = metabolite['BEACON_CONCEPT_ID']
        disorders = []
        for statement in find_statements(bcid,'disease'):
            beacon_statement_id = statement['BEACON_STATEMENT_ID']
            connection = self.create_connection(source_element_id, beacon_statement_id)
            disorders.append({
                'beacon_statement_id':beacon_statement_id, 
                'beacon_concept_id': statement['BEACON_CONCEPT_ID'], 
                'name': statement['NAME'], 
                'id': statement['ID'], 
                'connection': connection
            })
        return disorders


    id_map = {
        'OMIM': 'omim',
        'DOID': 'disease_ontology',
        'NCIT': 'nci_thesaurus'
    }

    prefix_map = {
        'OMIM': 'OMIM',
        'DOID': 'DOID',
        'NCIT': 'NCIT'
    }


    def create_element(self, disorder):
        beacon_concept_id = disorder['beacon_concept_id']
        identifiers = {}
        synonyms = []
        for synonym in get_synonyms(beacon_concept_id):
            if synonym['EXACT_MATCH'] == 0:
                synonyms.append(synonym['SYNONYM'])
            if synonym['EXACT_MATCH'] == 1:
                (prefix, suffix) = parse_curie(synonym['SYNONYM'])
                if prefix is not None and prefix in self.id_map:
                    key = self.id_map[prefix]
                    curie = self.prefix_map[prefix]+suffix
                    add_identifier(identifiers, key, curie)
        disorder_id = self.disorder_id(disorder, identifiers)
        element = Element(
            id = disorder_id,
            biolink_class=DISEASE,
            identifiers = identifiers,
            names_synonyms=[Names(name = disorder['name'], synonyms=synonyms, source=self.info.label)],
            attributes = [],
            connections=[],
            source = self.info.name
        )
        return element


    def disorder_id(self, disorder, identifiers):
        if disorder['id'] is not None and disorder['id'] != '':
            identifiers['umls'] = disorder['id']
        if self.id_map['DOID'] in identifiers:
            return identifiers[self.id_map['DOID']]
        if self.id_map['OMIM'] in identifiers:
            return identifiers[self.id_map['OMIM']]
        if self.id_map['NCIT'] in identifiers:
            return identifiers[self.id_map['NCIT']]
        if 'umls' in identifiers:
            return disorder['id']
        return disorder['name']


    def create_connection(self, source_element_id, beacon_statement_id):
        connection = Connection(
            source_element_id=source_element_id,
            type = self.info.knowledge_map.predicates[0].predicate,
            relation = self.info.knowledge_map.predicates[0].predicate,
            source = self.info.label,
            provided_by= self.info.name,
            attributes=[]
        )
        for reference in get_references(beacon_statement_id):
            connection.attributes.append(Attribute(
                name = 'reference',
                value = reference['PMID'] if reference['PMID'] != 'PMID:' else reference['NAME'],
                type = 'reference',
                source = self.info.label,
                provided_by= self.info.name
            ))
        return connection





class HmdbMetabolites(Transformer):


    variables = ['metabolites']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/metabolites_transformer_info.json')
        self.info.knowledge_map.nodes['ChemicalSubstance'].count = concept_count('metabolite')


    def produce(self, controls):
        metabolite_list = []
        names = controls['metabolites'].split(';')
        for name in names:
            name = name.strip()
            for metabolite in self.find_metabolite(name):
                metabolite.attributes.append(Attribute(
                    name='query name', value=name, source=self.info.label, provided_by=self.info.name
                ))
                metabolite_list.append(metabolite)
        return metabolite_list


    def find_metabolite(self, name):
        if name.upper().startswith('HMDB:'):
            return self.metabolites(find_metabolite_by_hmdb_id(name))
        elif name.upper().startswith('HMDB'):
            return self.metabolites(find_metabolite_by_hmdb_id(HMDB+name))
        elif inchikey_regex.match(name) is not None:
            return self.metabolites(find_metabolite_by_inchikey(name))
        else:
            metabolites = self.metabolites(find_metabolite_by_name(name))
            if len(metabolites) != 0:
                return metabolites
            return self.metabolites(find_metabolite_by_synonym(name))


    def metabolites(self, results):
        compounds = []
        for row in results:
            compounds.append(self.row_to_element(row))
        return compounds


    id_map = {
        'smiles': 'smiles',
        'inchi': 'inchi',
        'inchikey': 'inchikey',
        'CAS': 'cas',
        'DrugBank': 'drugbank',
        'CHEBI': 'chebi',
        'kegg.compound': 'kegg'
    }

    prefix_map = {
        'CAS': 'CAS',
        'DrugBank': 'DrugBank',
        'CHEBI': 'ChEBI',
        'kegg.compound': 'KEGG.COMPOUND'
    }
    

    def row_to_element(self, row):
        id = row['ID']
        beacon_concept_id = row['BEACON_CONCEPT_ID']
        identifiers = {
            'hmdb': id,
        }
        synonyms = []
        for synonym in get_synonyms(beacon_concept_id):
            if synonym['EXACT_MATCH'] == 0:
                synonyms.append(synonym['SYNONYM'])
            if synonym['EXACT_MATCH'] == 1:
                (prefix, suffix) = parse_curie(synonym['SYNONYM'])
                if prefix is not None and prefix in self.id_map:
                    key = self.id_map[prefix]
                    curie = self.prefix_map[prefix]+suffix
                    if prefix == 'DrugBank' and not suffix.startswith(':DB'):
                        key = 'pubchem'
                        curie = 'CID'+suffix
                    add_identifier(identifiers, key, curie)

        attributes = []
        for detail in get_details(beacon_concept_id):
            if detail['TAG'] in self.id_map:
                add_identifier(identifiers, self.id_map[detail['TAG']], detail['VALUE'])
                if detail['TAG'] == 'inchi':
                    attributes.append(
                        Attribute(
                            name='structure source', 
                            value=self.info.label,
                            source=self.info.label,
                            provided_by=self.info.name
                        )
                    )

        element = Element(
            id=id,
            biolink_class=CHEMICAL_SUBSTANCE,
            identifiers=identifiers,
            names_synonyms=[Names(name=row['NAME'],synonyms=synonyms,source=self.info.label)],
            attributes = attributes,
            connections=[],
            source=self.info.name
        )

        return element


def parse_curie(curie):
    colon_index = curie.find(':')
    if colon_index <= 0:
        return None
    return (curie[0: colon_index],curie[colon_index:])


def add_identifier(identifiers, key, value):
    if value is not None:
        identifiers[key] = value


def find_metabolite(compound):
    if compound.identifiers is not None:
        if 'hmdb' in compound.identifiers and compound.identifiers['hmdb'] is not None:
            for metabolite in find_metabolite_by_hmdb_id(compound.identifiers['hmdb']):
                return metabolite
        if 'chebi' in compound.identifiers and compound.identifiers['chebi'] is not None:
            for metabolite in find_metabolite_by_id(compound.identifiers['chebi']):
                return metabolite
        if 'drugbank' in compound.identifiers and compound.identifiers['drugbank'] is not None:
            for metabolite in find_metabolite_by_id(compound.identifiers['drugbank']):
                return metabolite
        if 'cas' in compound.identifiers and compound.identifiers['cas'] is not None:
            for metabolite in find_metabolite_by_id(compound.identifiers['cas']):
                return metabolite
    return None


connection = sqlite3.connect("data/HMDB-KS.db", check_same_thread=False)
connection.row_factory = sqlite3.Row


def find_statements(bcid, category):
    query = """
        SELECT BEACON_CONCEPT.BEACON_CONCEPT_ID, BEACON_CONCEPT.ID, BEACON_CONCEPT.NAME, BEACON_STATEMENT.BEACON_STATEMENT_ID
        FROM BEACON_STATEMENT
        INNER JOIN BEACON_CONCEPT ON BEACON_CONCEPT.BEACON_CONCEPT_ID = BEACON_STATEMENT.OBJECT_CONCEPT_ID
        WHERE BEACON_CONCEPT.BEACON_CONCEPT_CATEGORY_ID = {} AND SUBJECT_CONCEPT_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query.format(category_id[category]),(bcid,))
    return cur.fetchall()


def find_metabolite_by_hmdb_id(id):
    query = """
        SELECT BEACON_CONCEPT_ID, ID, NAME, DESCRIPTION
        FROM BEACON_CONCEPT
        WHERE ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def find_metabolite_by_id(id):
    query = """
        SELECT BEACON_CONCEPT.BEACON_CONCEPT_ID, BEACON_CONCEPT.ID, BEACON_CONCEPT.NAME, BEACON_CONCEPT.DESCRIPTION
        FROM BEACON_CONCEPT_SYNONYM
        INNER JOIN BEACON_CONCEPT ON BEACON_CONCEPT.BEACON_CONCEPT_ID = BEACON_CONCEPT_SYNONYM.BEACON_CONCEPT_ID
        WHERE SYNONYM = ? AND EXACT_MATCH = 1
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_references(beacon_statement_id):
    query = """
        SELECT BEACON_REFERENCE.ID AS PMID, BEACON_REFERENCE.NAME AS NAME
        FROM BEACON_STATEMENT_CITATION
        JOIN BEACON_REFERENCE ON (BEACON_REFERENCE.BEACON_REFERENCE_ID = BEACON_STATEMENT_CITATION.BEACON_REFERENCE_ID)
        WHERE BEACON_STATEMENT_CITATION.BEACON_STATEMENT_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(beacon_statement_id,))
    return cur.fetchall()


def find_metabolite_by_inchikey(inchikey):
    query = """
        SELECT BEACON_CONCEPT.BEACON_CONCEPT_ID, BEACON_CONCEPT.ID, BEACON_CONCEPT.NAME, BEACON_CONCEPT.DESCRIPTION
        FROM BEACON_CONCEPT_DETAIL
        INNER JOIN BEACON_CONCEPT ON BEACON_CONCEPT.BEACON_CONCEPT_ID = BEACON_CONCEPT_DETAIL.BEACON_CONCEPT_ID
        WHERE VALUE = ? AND TAG = 'inchikey'
    """
    cur = connection.cursor()
    cur.execute(query,(inchikey,))
    return cur.fetchall()


def find_metabolite_by_name(name):
    query = """
        SELECT BEACON_CONCEPT_ID, ID, NAME, DESCRIPTION
        FROM BEACON_CONCEPT
        WHERE NAME = ? COLLATE NOCASE
    """
    cur = connection.cursor()
    cur.execute(query,(name,))
    return cur.fetchall()


def find_metabolite_by_synonym(synonym):
    query = """
        SELECT BEACON_CONCEPT.BEACON_CONCEPT_ID, BEACON_CONCEPT.ID, BEACON_CONCEPT.NAME, BEACON_CONCEPT.DESCRIPTION
        FROM BEACON_CONCEPT_SYNONYM
        INNER JOIN BEACON_CONCEPT ON BEACON_CONCEPT.BEACON_CONCEPT_ID = BEACON_CONCEPT_SYNONYM.BEACON_CONCEPT_ID
        WHERE SYNONYM = ? COLLATE NOCASE AND EXACT_MATCH = 0
    """
    cur = connection.cursor()
    cur.execute(query,(synonym,))
    return cur.fetchall()


def get_synonyms(beacon_concept_id):
    query = """
        SELECT SYNONYM, EXACT_MATCH
        FROM BEACON_CONCEPT_SYNONYM
        WHERE BEACON_CONCEPT_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(beacon_concept_id,))
    return cur.fetchall()    


def get_details(beacon_concept_id):
    query = """
        SELECT TAG, VALUE
        FROM BEACON_CONCEPT_DETAIL
        WHERE BEACON_CONCEPT_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(beacon_concept_id,))
    return cur.fetchall()    


def concept_count(concept):
    query = """
        SELECT COUNT(DISTINCT BEACON_CONCEPT.ID) AS COUNT
        FROM BEACON_CONCEPT
        JOIN BEACON_CONCEPT_CATEGORY ON (BEACON_CONCEPT_CATEGORY.BEACON_CONCEPT_CATEGORY_ID = BEACON_CONCEPT.BEACON_CONCEPT_CATEGORY_ID)
        WHERE BEACON_CONCEPT_CATEGORY.CATEGORY = ?
    """
    cur = connection.cursor()
    cur.execute(query, (concept,))
    count = -1
    for row in cur.fetchall():
        count = row['COUNT']
    return count


def beacon_categories():
    query = """ 
        SELECT BEACON_CONCEPT_CATEGORY_ID, CATEGORY
        FROM BEACON_CONCEPT_CATEGORY
    """
    category_id = {}
    cur = connection.cursor()
    cur.execute(query)
    for row in cur.fetchall():
        category_id[row['CATEGORY']] = row['BEACON_CONCEPT_CATEGORY_ID']
    return category_id


category_id = beacon_categories()
