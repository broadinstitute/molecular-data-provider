import sqlite3

from transformers.transformer import Transformer
from openapi_server.models.element import Element

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.connection import Connection


class CTRPTransformer(Transformer):

    variables = ['maximum FDR','disease context','limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='ctrp_transformer_info.json')
        self.info.knowledge_map.nodes['ChemicalSubstance'].count = get_compound_count()


    def expand(self, collection, controls):
        fdr_threshold = float(controls['maximum FDR'])
        context = find_context(controls['disease context'])
        limit = controls['limit'] - 1
        if context is None:
            msg = "unknown disease context '"+controls['disease context']+"'"
            return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )
        cpd_list = []
        compounds = {}
        cpd_id_map = {}
        for compound in collection:
            compound.connections = []
            cpd_list.append(compound)
            if compound.identifiers is not None:
                ctrp_compound = self.find_compound(compound.identifiers)
                if len(ctrp_compound) > 0:
                    cpd_id = ctrp_compound[0]['CPD_ID']
                    compounds[cpd_id] = compound
                    cpd_id_map[compound.id] = cpd_id

        for compound in collection:
            if compound.id in cpd_id_map:
                cpd_id = cpd_id_map[compound.id]
                hits = find_correlated_compounds(cpd_id, context, fdr_threshold)
                if limit > 0 and limit < len(hits):
                    hits = hits[0:limit]
                for hit in hits:
                    hit_id = hit['CPD_ID_2']
                    connected_compound = compounds.get(hit_id)
                    if connected_compound is None:
                        connected_compound = self.get_compound(hit_id)
                        cpd_list.append(connected_compound)
                        compounds[hit_id] = connected_compound
                    connected_compound.connections.append(self.create_connection(compound.id, hit))

        return cpd_list


    def find_compound(self, identifiers):
        if 'pubchem' in identifiers and identifiers['pubchem'] is not None:
            return find_compound_by_cid(identifiers['pubchem'])
        if 'inchikey' in identifiers and identifiers['inchikey'] is not None:
            return find_compound_by_inchi_key(identifiers['inchikey'])
        return []


    def get_compound(self, cpd_id):
        compound = get_compound(cpd_id)[0]
        element = Element(
                id = compound['PUBCHEM_CID'],
                biolink_class='ChemicalSubstance',
                identifiers = {
                    "pubchem": compound['PUBCHEM_CID'],
                    "smiles": compound['SMILES'],
                    "inchi": compound['INCHI'],
                    "inchikey": compound['INCHI_KEY'],
                },
                names_synonyms = [Names(
                    name=compound['COMPOUND_NAME'], 
                    synonyms = [compound['BROAD_CPD_ID']], 
                    source = self.info.label)],
                attributes = [],
                connections=[],
                source = self.info.name
            )
        return element


    def create_connection(self, source_element_id, hit):
        connection = Connection(
            source_element_id = source_element_id,
            type = self.info.knowledge_map.predicates[0].predicate,
            relation=self.info.knowledge_map.predicates[0].predicate,
            source=self.info.label,
            provided_by = self.info.name,
            attributes = []
        )
        self.add_attribute(connection, 'correlation', hit['CORRELATION_VALUE'])
        self.add_attribute(connection, 'z-score', hit['FISHER_Z'])
        self.add_attribute(connection, 'FDR', hit['FDR'])
        self.add_attribute(connection, 'sample size', hit['N_SAMPLES'])
        self.add_reference(connection,'26656090')
        self.add_reference(connection,'26482930')
        self.add_reference(connection,'23993102')
        return connection


    def add_attribute(self, connection, name, value):
        attribute = Attribute(
            name = name, 
            value = str(value),
            type = name, 
            source = self.info.label,
            provided_by = self.info.name
        )
        connection.attributes.append(attribute)


    def add_reference(self, connection, pmid):
        attribute = Attribute(
            name = 'reference', 
            value = 'PMID:'+(pmid),
            type = 'reference', 
            source = self.info.label,
            url = 'https://pubmed.ncbi.nlm.nih.gov/'+str(pmid),
            provided_by = self.info.name
        )
        connection.attributes.append(attribute)

connection = sqlite3.connect("data/CTRP.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def get_compound(cpd_id):
    query = """
        SELECT CPD_ID, COMPOUND_NAME, BROAD_CPD_ID, PUBCHEM_CID, SMILES, INCHI, INCHI_KEY
        FROM COMPOUND
        WHERE CPD_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(cpd_id,))
    return cur.fetchall()


def find_compound_by_cid(pubchem_cid):
    query = """
        SELECT CPD_ID, COMPOUND_NAME, BROAD_CPD_ID, PUBCHEM_CID, SMILES, INCHI, INCHI_KEY
        FROM COMPOUND
        WHERE PUBCHEM_CID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(pubchem_cid,))
    return cur.fetchall()


def find_compound_by_inchi_key(inchi_key):
    query = """
        SELECT CPD_ID, COMPOUND_NAME, BROAD_CPD_ID, PUBCHEM_CID, SMILES, INCHI, INCHI_KEY
        FROM COMPOUND
        WHERE INCHI_KEY = ?
    """
    cur = connection.cursor()
    cur.execute(query,(inchi_key,))
    return cur.fetchall()


def find_context(context):
    query = """
        SELECT CONTEXT_ID
        FROM CONTEXT
        WHERE CONTEXT_NAME = ?
    """
    cur = connection.cursor()
    cur.execute(query,(context,))
    results = cur.fetchall()
    return results[0][0] if len(results) > 0 else None


def find_correlated_compounds(cpd_id, context, fdr_threshold):
    query = """
        SELECT CPD_ID_1, CPD_ID_2, CONTEXT_ID, N_SAMPLES, CORRELATION_VALUE, FISHER_Z, FDR
        FROM CORRELATION
        WHERE CPD_ID_1 = ? AND CONTEXT_ID = ? AND FDR < ?
        ORDER BY FDR
    """
    cur = connection.cursor()
    cur.execute(query,(cpd_id,context,fdr_threshold))
    return cur.fetchall()


def get_compound_count():
    query = "SELECT COUNT(DISTINCT CPD_ID_1) AS COUNT FROM CORRELATION"
    cur = connection.cursor()
    cur.execute(query)
    count = 0
    for row in cur.fetchall():
        count = row['COUNT']
    return count
