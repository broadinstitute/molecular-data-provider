from xml.dom.pulldom import END_ELEMENT
from transformers.transformer import Transformer

import sqlite3


class UniProtProducer(Transformer):


    variables = ['proteins']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/proteins_transformer_info.json')
        self.info.knowledge_map.nodes['Protein'].count = protein_count()
        self.UNIPROTKB = self.info.knowledge_map.nodes['Protein'].id_prefixes[0]
        self.ENSEMBL = self.info.knowledge_map.nodes['Protein'].id_prefixes[1]


    def produce(self, controls):
        protein_list = []
        proteins = {}
        for name in controls.get("proteins", []):
            for uniprot_ac in self.find_proteins(name):
                if uniprot_ac not in proteins:
                    protein = self.create_element(uniprot_ac)
                    if protein is not None:
                        proteins[uniprot_ac] = protein
                        protein_list.append(protein)
                if uniprot_ac in proteins:
                    proteins[uniprot_ac].attributes.append(self.Attribute(name='query name', value=name))   
        return protein_list


    def find_proteins(self, name):
        if name.startswith(self.UNIPROTKB):
            uniprot_ac = name[len(self.UNIPROTKB)+1:]
            return [uniprot_ac]
        if name.startswith(self.ENSEMBL):
            ensembl_id = name[len(self.ENSEMBL)+1:]
            return self.find_protein_by_ensembl(ensembl_id)
        return self.find_protein_by_name(name)


    def find_protein_by_name(self, name):
        proteins = []
        for row in find_protein_by_name(name):
            proteins.append(row['UNIPROT_AC'])
        return proteins


    def find_protein_by_ensembl(self, id):
        proteins = []
        for row in find_protein_by_ensembl(id):
            proteins.append(row['UNIPROT_AC'])
        return proteins

    
    def create_element(self, uniprot_ac):
        id = self.UNIPROTKB + ':' + uniprot_ac
        protein_name = None
        protein_length = None
        for row in get_protein(uniprot_ac):
            protein_name = row['PROTEIN_NAME']
            protein_length = row['PROTEIN_LENGTH']
        if protein_name is None:
            return None
        element = self.Element(
            id = id,
            biolink_class = self.biolink_class('Protein'),
            identifiers = self.get_identifiers(uniprot_ac),
            names_synonyms = [
                self.Names(
                    name = protein_name,
                    synonyms = [],
                    type = "",
                )
            ],
            attributes = [
                self.Attribute(
                    name = 'protein sequence length',
                    value = str(protein_length),
                    type = 'data:1249'
                )
            ] #,
            # connections = []
        )
        return element


    def get_identifiers(self, uniprot_ac):
        identifiers = {'uniprot': self.UNIPROTKB + ':' + uniprot_ac}
        for row in get_xrefs(uniprot_ac):
            if row['XREF_TYPE'] == 'Ensembl_PRO':
                identifiers['ensembl'] = self.ENSEMBL + ':' + row['XREF']
        return identifiers


connection = sqlite3.connect("data/UniProt.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def protein_count():
    query = """
        SELECT COUNT(DISTINCT UNIPROT_AC) AS PROTEIN_COUNT FROM (
            SELECT DISTINCT UNIPROT_AC FROM PROTEIN
            UNION
            SELECT DISTINCT UNIPROT_AC FROM XREF
        )
    """
    cur = connection.cursor()
    cur.execute(query)
    count = -1
    for row in cur.fetchall():
        count = row['PROTEIN_COUNT']
    return count


def find_protein_by_ensembl(id):
    query = "SELECT DISTINCT UNIPROT_AC FROM XREF WHERE XREF = ?"
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def find_protein_by_name(id):
    query = "SELECT DISTINCT UNIPROT_AC FROM PROTEIN WHERE PROTEIN_NAME = ? COLLATE NOCASE"
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_protein(uniprot_ac):
    query_id = uniprot_ac.split('-')[0]
    query = "SELECT PROTEIN_NAME, PROTEIN_LENGTH FROM PROTEIN WHERE UNIPROT_AC = ?"
    cur = connection.cursor()
    cur.execute(query,(query_id,))
    return cur.fetchall()


def get_xrefs(uniprot_ac):
    query = "SELECT XREF_TYPE, XREF FROM XREF WHERE UNIPROT_AC = ?"
    cur = connection.cursor()
    cur.execute(query,(uniprot_ac,))
    return cur.fetchall()

# class UniprotTransformer(Transformer):
#     variables = []
#     def __init__(self, definition_file):
#         super().__init__(self.variables, definition_file = definition_file)
    
#     def map(self, input_list, transformer_type, controls):
#         output_list = []
#         output = {}
#         for x in input_list:
            
            
class ProteinToGene(Transformer):
    variables = []
    def __init__(self):
        super().__init__(self.variables, definition_file = "info/proteintogene_transformer_info.json")
    
    def map(self, protein_list, controls):
        gene_list = []
        genes = {}
        for protein in protein_list:
            protein_id = self.de_prefix("uniprot", protein.identifiers.get('uniprot'))
            for row in self.get_gene_ids(protein_id):
                gene_id = row["XREF"]
                if gene_id not in genes:
                    gene_element = self.create_gene_elemnent(gene_id)
                    genes[gene_id] = gene_element
                    gene_list.append(gene_element)
                else:
                    gene_element = genes[gene_id]
                connection = self.Connection(protein.id,"gene_product_of", "has_gene_product", attributes= protein.attributes)
                connection.attributes.append(self.Attribute('biolink:primary_knowledge_source','infores:uniprot'))
                gene_element.connections.append(connection)
        return gene_list

    def get_gene_ids(self, element_id):
        query = "SELECT XREF FROM XREF WHERE UNIPROT_AC = ? and XREF_TYPE = 'HGNC'"
        cur = connection.cursor()
        cur.execute(query,(element_id,))
        return cur.fetchall()

    def create_gene_elemnent(self, gene_id):
        element = self.Element(
            id = gene_id,
            biolink_class = self.biolink_class('Gene'),
            identifiers = {"hgnc":gene_id}
        )
        return element

class GeneToProtein(Transformer):
    variables = []
    def __init__(self):
        super().__init__(self.variables, definition_file = "info/genetoprotein_transformer_info.json")
    
    def map(self, gene_list, controls):
        protein_list = []
        proteins = {}
        for gene in gene_list:
            for row in self.get_protein_ids(gene.identifiers.get('hgnc')):
                protein_id = self.add_prefix("uniprot", row["UNIPROT_AC"])
                if protein_id not in proteins:
                    protein_element = self.create_protein_elemnent(protein_id)
                    proteins[protein_id] = protein_element
                    protein_list.append(protein_element)
                else:
                    protein_element = proteins[protein_id]
                connection = self.Connection(gene.id, "has_gene_product", "gene_product_of", attributes= gene.attributes)
                connection.attributes.append(self.Attribute('biolink:primary_knowledge_source','infores:uniprot'))
                protein_element.connections.append(connection)
        return protein_list

    def get_protein_ids(self, element_id):
        query = "SELECT UNIPROT_AC FROM XREF WHERE XREF = ? and XREF_TYPE = 'HGNC'"
        cur = connection.cursor()
        cur.execute(query,(element_id,))
        return cur.fetchall()

    def create_protein_elemnent(self, protein_id):
        element = self.Element(
            id = protein_id,
            biolink_class = self.biolink_class('Protein'),
            identifiers = {"uniprot":protein_id}
        )
        return element