from contextlib import closing
import requests

from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.gene_info import GeneInfo
from openapi_server.models.gene_info_identifiers import GeneInfoIdentifiers
from openapi_server.models.attribute import Attribute

CMAP_URL = 'https://s3.amazonaws.com/macchiato.clue.io/builds/touchstone/v1.1/arfs/{}/pert_id_summary.gct'

class CmapExpander(Transformer):

    variables = ['score threshold']

    def __init__(self, input_class, output_class):
        super().__init__(self.variables)
        self.info.function = 'expander' if input_class == output_class else 'transformer'
        self.info.knowledge_map.input_class = input_class
        self.info.knowledge_map.predicates[0].subject = input_class
        self.info.knowledge_map.output_class = output_class
        self.info.knowledge_map.predicates[0].object = output_class
        self.info.name = self.info.name + input_class + '-to-' + output_class + ' ' + self.info.function
        self.load_ids(input_class, output_class)
        if input_class == 'gene':
            self.get_id = self.get_gene_id
            self.get_name = self.get_gene_symbol
        if input_class == 'compound':
            self.get_id = self.get_compound_id
            self.get_name = self.get_compound_name
        if output_class == 'gene':
            self.create_element = self.create_gene
        if output_class == 'compound':
            self.create_element = self.create_compound


    def map(self, collection, controls):
        list = []
        elements = {}
        return self.connections(list, elements, collection, controls)

    def expand(self, collection, controls):
        list = []
        elements = {}
        for query in collection:
            query_id = self.get_id(query)
            list.append(query)
            elements[query_id]=query
        return self.connections(list, elements, collection, controls)


    def connections(self, list, elements, collection, controls):
        for query in collection:
            query_id = self.get_id(query)
            if query_id in self.input_id_map:
                hits = self.cmap_connections(self.input_id_map[query_id], controls)
                for (score, hit_id) in hits:
                    element = self.get_element(hit_id, elements, list)
                    self.add_score(element, score, query)
        return list


    def cmap_connections(self, pert_id, controls):
        min_score = controls['score threshold']
        url = CMAP_URL.format(pert_id)
        hits = []
        with closing(requests.get(url)) as response:
            row_no = 0
            for line in response.iter_lines():
                if row_no >= 3:
                    row = line.decode().strip().split('\t')
                    pert_id = row[0]
                    score = row[1]
                    if float(score) >= float(min_score) and pert_id in self.output_id_map:
                        hits.append((float(score), self.output_id_map[pert_id]))
                row_no = row_no + 1
        hits.sort(reverse=True)
        return hits


    def get_element(self, hit_id, elements, list):
        if hit_id in elements:
            return elements[hit_id]
        element = self.create_element(hit_id)
        elements[hit_id] = element
        list.append(element)
        return element


    def add_score(self, element, score, query):
        if element.attributes is None:
            element.attributes = []
        element.attributes.append(
            Attribute(
                name = 'CMAP similarity score with '+self.get_name(query),
                value = str(score),
                source = self.info.name
            )
        )


    def get_id(self, element):
        raise NotImplementedError('CMAP expander not configured')


    def get_compound_id(self, element):
        return element.identifiers.pubchem


    def get_gene_id(self, element):
        return element.identifiers.entrez


    def get_name(self, element):
        raise NotImplementedError('CMAP expander not configured')


    def get_compound_name(self, compound):
        if compound.names_synonyms is not None:
            for name in compound.names_synonyms:
                if name.name is not None:
                    return name.name
        return compound.compound_id


    def get_gene_symbol(self, element):
        for attribute in element.attributes:
            if attribute.name == 'gene_symbol':
                return attribute.value
        return element.id


    def create_element(self, hit):
        raise NotImplementedError('CMAP expander not configured')


    def create_compound(self, id):
        return CompoundInfo(
            compound_id = id,
            identifiers = CompoundInfoIdentifiers(pubchem=id),
            attributes = [],
        )


    def create_gene(self, id):
        return GeneInfo(
            gene_id = id,
            attributes = [],
            identifiers = GeneInfoIdentifiers(entrez = id)
        )


    def load_ids(self, input_class, output_class):
        self.input_id_map = {}
        self.output_id_map = {}
        with open("data/CMAP_pert_ids.txt",'r') as f:
            first_line = True
            for line in f:
                if not first_line:
                    row = line.strip().split('\t')
                    pert_class = row[3]
                    pert_id = row[1]
                    id = row[4]
                    if pert_class == input_class:
                        self.input_id_map[id] = pert_id
                    if pert_class == output_class:
                        self.output_id_map[pert_id] = id
                first_line = False
