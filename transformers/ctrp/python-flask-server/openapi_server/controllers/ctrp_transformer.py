import sqlite3

from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure


class CTRPTransformer(Transformer):

    variables = ['maximum FDR','disease context','limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='ctrp_transformer_info.json')


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
            cpd_list.append(compound)
            pubchem_cid = compound.identifiers.pubchem if compound.identifiers is not None else None
            inchikey = compound.structure.inchikey if compound.structure is not None else None
            ctrp_compound = find_compound(pubchem_cid, inchikey)
            if len(ctrp_compound) > 0:
                cpd_id = ctrp_compound[0][0]
                compounds[cpd_id] = compound
                cpd_id_map[compound.compound_id] = (cpd_id,ctrp_compound[0][1])

        for compound in collection:
            if compound.compound_id in cpd_id_map:
                (cpd_id, query_name) = cpd_id_map[compound.compound_id]
                connections = find_correlated_compounds(cpd_id, context, fdr_threshold)
                if limit > 0 and limit < len(connections):
                    connections = connections[0:limit]
                for connection in connections:
                    connected_compound = compounds.get(connection[1])
                    if connected_compound is None:
                        connected_compound = self.get_compound(connection[1])
                        cpd_list.append(connected_compound)
                        compounds[connection[1]] = connected_compound

                    if connected_compound.attributes is None:
                        connected_compound.attributes = []
                    attr_name = "CTRP correlation with '"+query_name
                    connected_compound.attributes.append(Attribute(name=attr_name+"'", value=connection[4],source=self.info.name))
                    connected_compound.attributes.append(Attribute(name=attr_name+"' z-score", value=connection[5],source=self.info.name))
                    connected_compound.attributes.append(Attribute(name=attr_name+"' FDR", value=connection[6],source=self.info.name))
                    connected_compound.attributes.append(Attribute(name=attr_name+"' sample size", value=connection[3],source=self.info.name))

        return cpd_list


    def get_compound(self, cpd_id):
        compound = get_compound(cpd_id)[0]
        compound_info = CompoundInfo(
                compound_id = compound[3],
                identifiers = CompoundInfoIdentifiers(
                    pubchem = compound[3]
                ),
                names_synonyms = [Names(name=compound[1], synonyms = [compound[2]], source = self.info.name)],
                structure = CompoundInfoStructure(
                    smiles = compound[4],
                    inchi = compound[5],
                    inchikey = compound[6],
                    source = 'CTRP'
                ),
                attributes = [],
                source = self.info.name
            )
        return compound_info


connection = sqlite3.connect("CTRP.sqlite", check_same_thread=False)


def get_compound(cpd_id):
    query = """
        SELECT CPD_ID, COMPOUND_NAME, BROAD_CPD_ID, PUBCHEM_CID, SMILES, INCHI, INCHI_KEY
        FROM COMPOUND
        WHERE CPD_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(cpd_id,))
    return cur.fetchall()


def find_compound(pubchem_cid, inchi_key):
    if pubchem_cid is not None:
        return find_compound_by_cid(pubchem_cid)
    if inchi_key is not None:
        return find_compound_by_inchi_key(inchi_key)
    return []


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


