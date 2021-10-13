import collections
import sqlite3
from collections import defaultdict

from transformers.transformer import Transformer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

connection = sqlite3.connect("data/DepMap.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


class DepMapExpander(Transformer):

    variables = ['score threshold', 'direction', 'limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/correlations_transformer_info.json')
    
    def expand(self, collection, controls):
        element_list = []
        elements = {}
        for gene in collection:
            # add query gene to output list (connected to itself with 1.0 correlation)
            query_id = gene.id
            self.add_connection(gene, query_id, 1.0)
            element_list.append(gene)
            # only use NCBIGene identifier 
            if "entrez" in gene.identifiers:
                gene_id = gene.identifiers["entrez"]
                elements[gene_id] = gene
                # pass element_list and elements to add gene elements as they are created
                self.find_correlated_genes(controls, query_id, gene_id, element_list, elements)
        return element_list

    def find_correlated_genes(self, controls, query_id, gene_id, element_list, elements):
        gene_id_1 = self.de_prefix("entrez", str(gene_id), 'gene')
        threshold = float(controls["score threshold"])
        limit = int(controls["limit"])
        direction = controls["direction"]
        query = """
            SELECT entrez_gene_id_1, entrez_gene_id_2, correlation 
            FROM cor WHERE entrez_gene_id_1 = ? and {} 
            ORDER BY abs(correlation) DESC  
        """.format(self.above_threshold(direction))    
        cur = connection.cursor()
        cur.execute(query,(gene_id_1, threshold))
        i= 1
        for row in cur.fetchall():
            correlation_value = row["correlation"]
            if limit <= 0 or i < limit:
                gene_id_1 = gene_id
                gene_id_2 = self.add_prefix("entrez", str(row["entrez_gene_id_2"]), "gene")
                # To take out duplicate outputs if multiple genes are related to the same gene
                if gene_id_2 not in elements:
                    gene_element = self.Element(gene_id_2, self.biolink_class('Gene'), {"entrez": gene_id_2})
                    elements[gene_id_2] = gene_element
                    element_list.append(gene_element)
                else:
                    gene_element = elements[gene_id_2]
                self.add_connection(gene_element, query_id, correlation_value)
            i+=1

    
    def above_threshold(self, direction: str):
        """
            Compare correlation values with a threshold
        """
        if direction == 'correlation':
            return "correlation >= ?"
        if direction == 'anti-correlation':
            return "correlation <= ?"
        if direction == 'both':
            return "abs(correlation) >= abs(?)"
        return "correlation >= ?"
    
    def add_connection(self, gene_element, query_id, correlation_value):
        if gene_element.connections is None: 
            gene_element.connections = []
        attribute = self.Attribute("correlation", correlation_value)
        attribute.source = "infores:molepro"
        gene_element.connections.append(self.Connection(query_id, "biolink:correlated_with", "biolink:correlated_with", 
        attributes=[attribute]))
