import sqlite3

from transformers.transformer import Transformer

from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.gene_info import GeneInfo
from openapi_server.models.gene_info_identifiers import GeneInfoIdentifiers


class HmdbTargets(Transformer):


    def __init__(self):
        super().__init__([], definition_file='targets_transformer_info.json')
        self.load_ids()


    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            metabolite = self.find_metabolite(compound)
            if metabolite is not None:
                targets = self.find_targets(metabolite[0])
                for target in targets:
                    gene_id = target['entrez']
                    gene = genes.get(gene_id)
                    if gene is None:
                        gene = GeneInfo(
                            gene_id = gene_id,
                            identifiers = GeneInfoIdentifiers(entrez=gene_id),
                            attributes = [Attribute(name='UniProtKB', value=target['uniprot'],source=self.info.name)]
                        )
                        gene_list.append(gene)
                        genes[gene_id] = gene
                    url = 'http://www.hmdb.ca/metabolites/'+metabolite[1][5:]
                    gene.attributes.append(
                        Attribute(name='mechanism of action', value='target of '+metabolite[2], source=self.info.name, url=url)
                    )
        return gene_list


    def find_metabolite(self, compound_info: CompoundInfo):
        if compound_info.identifiers is not None:
            if compound_info.identifiers.hmdb is not None:
                for metabolite in find_metabolite_by_hmdb_id(compound_info.identifiers.hmdb):
                    return metabolite
            if compound_info.identifiers.chebi is not None:
                for metabolite in find_metabolite_by_id(compound_info.identifiers.chebi):
                    return metabolite
            if compound_info.identifiers.drugbank is not None:
                for metabolite in find_metabolite_by_id(compound_info.identifiers.drugbank):
                    return metabolite
            if compound_info.identifiers.cas is not None:
                for metabolite in find_metabolite_by_id('CAS:'+compound_info.identifiers.cas):
                    return metabolite
        return None


    def find_targets(self, bcid):
        target_list = []
        for target in find_targets(bcid):
            if target[1].startswith('UniProtKB:'):
                uniprot = target[1][10:]
                entrez = self.id_map.get(uniprot)
                if entrez is not None:
                    target_list.append(
                        {'uniprot':uniprot, 'entrez': 'NCBIGene:'+entrez, 'name': target[2]}
                    )
        return target_list


    def load_ids(self):
        self.id_map = {}
        with open("UniProt2Entrez.txt",'r') as f:
            first_line = True
            for line in f:
                if not first_line:
                    row = line.strip().split('\t')
                    uniprot = row[0]
                    entrez = row[1]
                    self.id_map[uniprot] = entrez
                first_line = False


class HmdbIndications(Transformer):


    def __init__(self):
        super().__init__([], definition_file='indications_transformer_info.json')


class HmdbIndications(Transformer):


    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='metabolites_transformer_info.json')


connection = sqlite3.connect("HMDB-KS.db", check_same_thread=False)


def find_targets(bcid):
    query = """
        SELECT BEACON_CONCEPT.BEACON_CONCEPT_ID, BEACON_CONCEPT.ID, BEACON_CONCEPT.NAME
        FROM BEACON_STATEMENT
        INNER JOIN BEACON_CONCEPT ON BEACON_CONCEPT.BEACON_CONCEPT_ID = BEACON_STATEMENT.OBJECT_CONCEPT_ID
        WHERE SUBJECT_CONCEPT_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(bcid,))
    return cur.fetchall()

def find_metabolite_by_hmdb_id(id):
    query = """
        SELECT BEACON_CONCEPT_ID, ID, NAME
        FROM BEACON_CONCEPT
        WHERE ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def find_metabolite_by_id(id):
    query = """
        SELECT BEACON_CONCEPT.BEACON_CONCEPT_ID, BEACON_CONCEPT.ID, BEACON_CONCEPT.NAME
        FROM BEACON_CONCEPT_SYNONYM
        INNER JOIN BEACON_CONCEPT ON BEACON_CONCEPT.BEACON_CONCEPT_ID = BEACON_CONCEPT_SYNONYM.BEACON_CONCEPT_ID
        WHERE SYNONYM = ? AND EXACT_MATCH = 1
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()

