from contextlib import closing
import requests
import time

from transformers.transformer import Transformer
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection
from openapi_server.models.attribute import Attribute

CMAP_URL = 'https://s3.amazonaws.com/macchiato.clue.io/builds/touchstone/v1.1/arfs/{}/pert_id_summary.gct'
VERSION_URL = 'https://api.clue.io/api/touchstone-version'

BIOLINK_CLASS = {'gene':'Gene','compound':'ChemicalSubstance'}
ID_KEY = {'gene':'entrez','compound':'pubchem'}

class CmapExpander(Transformer):

    variables = ['score threshold', 'limit']

    def __init__(self, input_class, output_class):
        super().__init__(self.variables)
        self.input_class = input_class
        self.output_class = output_class
        # update transformer_info
        self.info.function = 'expander' if input_class == output_class else 'transformer'
        self.info.knowledge_map.input_class = input_class
        self.info.knowledge_map.predicates[0].subject = BIOLINK_CLASS[input_class]
        self.info.knowledge_map.output_class = output_class
        self.info.knowledge_map.predicates[0].object = BIOLINK_CLASS[output_class]
        self.info.name = self.info.name + input_class + '-to-' + output_class + ' ' + self.info.function
        # load CMAP id map
        self.load_ids(input_class, output_class)


    def map(self, collection, controls):
        list = []
        elements = {}
        return self.connections(list, elements, collection, controls)


    def expand(self, collection, controls):
        list = []
        elements = {}
        for query in collection:
            query_id = self.get_id(query)
            query.connections = []
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
                    self.add_connection(element, score, query.id)
        return list


    def cmap_connections(self, pert_id, controls):
        min_score = controls['score threshold']
        limit = controls['limit']
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
        if limit > 0 and limit < len(hits):
            hits = hits[0:limit]
        return hits


    def get_element(self, hit_id, elements, list):
        if hit_id in elements:
            return elements[hit_id]
        element = self.create_element(hit_id)
        elements[hit_id] = element
        list.append(element)
        return element


    def get_id(self, query):
        return query.identifiers.get(ID_KEY[self.input_class])


    def add_connection(self, element, score, source_element_id):
        connection = Connection(
            source_element_id = source_element_id,
            type = self.info.knowledge_map.predicates[0].predicate,
            attributes = [
                Attribute(
                    name = 'CMAP similarity score',
                    value = str(score),
                    type = 'CMAP similarity score',
                    source = 'CMAP',
                    provided_by = self.info.name
                ),
                Attribute(
                    name = 'reference',
                    value = 'PMID:29195078',
                    type = 'reference',
                    source = 'CMAP',
                    provided_by = self.info.name
                ),
                Attribute(
                    name = 'about CMAP',
                    value = 'https://clue.io/cmap',
                    type = 'about CMAP',
                    source = 'CMAP',
                    url = 'https://clue.io/cmap',
                    provided_by = self.info.name
                ),
                Attribute(
                    name = 'CMAP touchstone data version',
                    value = self.get_version(),
                    type = 'CMAP touchstone data version',
                    source = 'CMAP',
                    url = 'https://api.clue.io/api/touchstone-version',
                    provided_by = self.info.name
                )
            ]
        )
        element.connections.append(connection)


    def create_element(self, hit_id):
        return Element(
            id = hit_id,
            biolink_class = BIOLINK_CLASS[self.output_class],
            identifiers = {ID_KEY[self.output_class]:hit_id},
            attributes = [],
            connections = [],
            source = self.info.name
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
