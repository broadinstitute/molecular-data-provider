import requests
import json
from contextlib import closing

from openapi_server.models.message import Message
from openapi_server.models.knowledge_graph import KnowledgeGraph
from openapi_server.models.edge import Edge
from openapi_server.models.node import Node
from openapi_server.models.result import Result
from openapi_server.models.edge_binding import EdgeBinding
from openapi_server.models.node_binding import NodeBinding

BASE_URL = 'https://translator.broadinstitute.org/molecular_data_provider'

class MolePro:

    def __init__(self, query_graph):
        self.query_graph = query_graph
        self.results = []
        self.knowledge_graph = KnowledgeGraph(nodes=[], edges=[])
        self.nodes = {}
        self.edges = {}


    def get_results(self):
        message = Message(results=self.results, query_graph=self.query_graph, knowledge_graph=self.knowledge_graph)
        return message


    def execute_transformer_chain(self, edge, chain):
        source = edge['source']
        collection_id = None
        if source.type == 'chemical_substance':
            collection = self.compound_collection(source.curie)
            if collection is None or len(collection['elements']) == 0:
                return
            source_node = self.add_element(collection['elements'][0])
            collection_id = collection.get('id')
        else:
            source_node = self.add_node(source.curie, None, source.type)
        for transformer in chain:
            response_id = self.execute_transformer(source.curie, transformer, collection_id)
            collection_id = response_id
        collection = self.getCollection(collection_id)
        for element in collection['elements']:
            self.add_result(source_node, edge, element)


    def compound_collection(self, curie):
        url = BASE_URL+'/compound/by_id/'+curie
        with closing(requests.get(url)) as id_response_obj:
            if id_response_obj.status_code != 200:
                return None
            response = id_response_obj.json()
            if 'structure' in response and 'inchikey' in response['structure'] and response['structure']['inchikey'] is not None:
                url = BASE_URL+'/compound/by_name/'+response['structure']['inchikey']
                with closing(requests.get(url)) as name_response_obj:
                    if name_response_obj.status_code != 200:
                        return None
                    response = name_response_obj.json()
                    return self.getCollection(response.get('id'))
        return None


    def execute_transformer(self, src_subject, transformer, collection_id):
        url = BASE_URL+'/transform'
        controls = []
        for control in transformer['controls']:
            if control['value'] == '#subject':
                control['value'] = src_subject
        query = {
            'name': transformer['name'],
            'collection_id': collection_id,
            'controls': transformer['controls']
        }
        with closing(requests.post(url, json=query)) as response_obj:
            return response_obj.json().get('id')


    def getCollection(self, collection_id):
        url = BASE_URL+'/collection/'+collection_id
        with closing(requests.get(url)) as response_obj:
            return response_obj.json()


    def add_result(self, source_node, query_edge, element):
        target_node = self.add_element(element)
        edge = self.add_edge(source_node.id, target_node.id, query_edge['type'])
        source_binding = NodeBinding(qg_id=query_edge['source'].id, kg_id=source_node.id)
        edge_binding = EdgeBinding(qg_id=query_edge['id'], kg_id=edge.id)
        target_binding = NodeBinding(qg_id=query_edge['target'].id, kg_id=target_node.id)
        result = Result(node_bindings=[source_binding, target_binding], edge_bindings=[edge_binding])
        self.results.append(result)

    def add_element(self, element):
        id = element['id']
        name = get_name(element)
        type = snake_case(element['biolink_class'])
        return self.add_node(id, name, type)


    def add_node(self, id, name, type):
        if id not in self.nodes:
            node = Node(id=id, name=name, type=type)
            self.nodes[id] = node
            self.knowledge_graph.nodes.append(node)
            return node
        return self.nodes[id]


    def add_edge(self, source_id, target_id, type):
        if (source_id, target_id) not in self.edges:
            id = 'e'+str(len(self.knowledge_graph.edges))
            edge = Edge(id=id, type=type, source_id=source_id, target_id=target_id)
            self.knowledge_graph.edges.append(edge)
            self.edges[(source_id, target_id)] = edge
            return edge
        return self.edges[(source_id, target_id)]


def get_name(element):
    if element['names_synonyms'] is not None:
        for names in element['names_synonyms']:
            if names['name'] is not None:
                return names['name']
    return None


def snake_case(string):
    return str(string).replace(' ','_').lower()
