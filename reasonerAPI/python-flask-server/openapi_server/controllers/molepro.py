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
from openapi_server.models.response import Response
from openapi_server.models.attribute import Attribute

from openapi_server.controllers.utils import translate_type
from openapi_server.controllers.utils import translate_curie

BASE_URL = 'https://translator.broadinstitute.org/molecular_data_provider'

class MolePro:

    def __init__(self, query_graph):
        self.query_graph = query_graph
        self.results = []
        self.knowledge_graph = KnowledgeGraph(nodes={}, edges={})
        self.nodes = {}
        self.edges = {}


    def get_results(self):
        message = Message(results=self.results, query_graph=self.query_graph, knowledge_graph=self.knowledge_graph)
        results_response = Response(message = message)
        return results_response


    def execute_transformer_chain(self, edge, chain):
        source = edge['source']
        collection_info = None

        # handle special case of chemical substance as source
        if source.category == 'biolink:ChemicalSubstance':
            collection_info = self.compound_collection(translate_curie(source.id, source.category))
            if collection_info is None or collection_info['size'] == 0:
                return
            collection = self.getCollection(collection_info)
            source_node = self.add_element(collection['elements'][0])
        else:
            source_node = self.add_node(source.id, None, source.category)

        # loop through the transformers
        for transformer in chain:
            response_info = self.execute_transformer(translate_curie(source.id, source.category), transformer, collection_info)
            collection_info = response_info
        collection = self.getCollection(collection_info)

        #print("Molepro: got collection {}\n\n".format(collection))

        # for each element in a collection response, add an edge and associated nodes
        collection_id = collection.get('id')
        if collection.get('elements') is not None:
            for element in collection['elements']:
                self.add_result(source_node, edge, element, collection_id)


    def compound_collection(self, curie):
        # molepro 2.2 will combine both GET calls into 1
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
                    return name_response_obj.json()
        return None


    def execute_transformer(self, src_subject, transformer, collection_info):
        url = BASE_URL+'/transform'
        controls = []
        collection_id = collection_info.get('id') if collection_info is not None else None
        for control in transformer['controls']:
            ctrl = {}
            ctrl['name'] = control['name']
            ctrl['value'] = src_subject if control['value'] == '#subject' else control['value']
            controls.append(ctrl)
        query = {
            'name': transformer['name'],
            'collection_id': collection_id,
            'controls': controls
        }

        #print("Molepro: sending payload {}\n\n".format(query))
        with closing(requests.post(url, json=query)) as response_obj:
            response_json = response_obj.json()
            if response_obj.status_code != 200:
                return None
            return response_json


    def getCollection(self, collection_info):
        """ queries REST endpoint for collection data """ 
        if collection_info is None or collection_info.get('id') is None:
            return {'elements':[]}
        collection_id = collection_info.get('id')

        # get the REST service URL
        # if collection_info['element_class'] == 'compound':
        #     url = BASE_URL+'/compound/list/'+collection_id
        # else:
        #     url = BASE_URL+'/collection/'+collection_id
        url = BASE_URL+'/collection/'+collection_id

        # call and close the request
        with closing(requests.get(url)) as response_obj:
            if response_obj.status_code != 200:
                return {'elements':[]}
            return response_obj.json()


    def add_result(self, source_node, query_edge, element, collection_id):
        """ for each given element in a collection result, add the edge and corresponding nodes to the result list """
        # print("source node: {}".format(source_node))
        # print("query edge: {}\n".format(query_edge))
        # print("element: {}".format(element))

        target_node = self.add_element(element)
        if source_node is None:
            print("source node is none; do nothing")
        elif target_node is None:
            print("target node is none; do nothing")
        else:
            # get the connections for the element
            connections=None
            if 'connections' in element and element.get('connections') is not Node:
                connection_list = element.get('connections')
                # print("connection list: {}".format(connection_list))
                if connection_list is not None and len(connection_list) > 0:
                    connections = connection_list[0]

            # add the edge
            edge = self.add_edge(source_node.id, target_node.id, query_edge['type'], collection_id, connections)

            # print("\n\nsource node: {} with id {} and key {} of type {}".format(source_node, source_node.id, query_edge['source'].node_id, type(source_node)))
            # print("target node: {} with id {} of type {}".format(target_node, target_node.id, type(target_node)))
            # print("edge: {} with id {} of type {}".format(query_edge, query_edge['id'], type(query_edge)))
            # print("edge: {}\n\n".format(edge))

            # updated for trapi v1.0.0
            # source_binding = NodeBinding(qg_id=query_edge['source'].id, kg_id=source_node.id)
            # edge_binding = EdgeBinding(qg_id=query_edge['id'], kg_id=edge.id)
            # target_binding = NodeBinding(qg_id=query_edge['target'].id, kg_id=target_node.id)
            source_binding = NodeBinding(id=source_node.id)
            edge_binding = EdgeBinding(id=edge.id)
            target_binding = NodeBinding(id=target_node.id)

            edge_map = {query_edge["id"]: [edge_binding]}
            nodes_map = {query_edge['source'].node_id: [source_binding], query_edge['target'].node_id: [target_binding]}

            # trapi 1.0 changes for the result formating (from list of nodes/edges to map of nodes/edges)
            # result = Result(node_bindings=[source_binding, target_binding], edge_bindings=[edge_binding])
            result = Result(node_bindings=nodes_map, edge_bindings=edge_map)
            self.results.append(result)

    def add_element(self, element):
        """ pulls out the target node from the element data """
        # look for the connections
        # element_keys = list(element.keys())
        # print("element: {}".format(element))
        # print("got element keys: {} \n".format(element_keys))

        node_attribute_list = []
        if 'compound_id' in element:
            id = element['compound_id']
            element_type = 'ChemicalSubstance'
        else:
            id = element['id']
            element_type = element['biolink_class']
        name = get_name(element)

        # get the attributes
        if 'attributes' in element:
            node_attribute_list = self.pull_attributes(element)

        # return
        return self.add_node(id, name, element_type, attributes=node_attribute_list)

    def pull_attributes(self, node):
        """ build a list of attributes from the values in the object """
        attribute_list = []
        if node is not None and 'attributes' in node and node.get('attributes') is not None:
            for attribute in node.get('attributes'):
                # print("got attribute: {}".format(attribute))
                if 'type' in attribute and attribute.get('type') is not None and attribute.get('type') != '':
                    # print("===========adding attribute: {}".format(attribute))
                    node_attribute = Attribute(name=attribute.get('name'), value=attribute.get('value'), type=attribute.get('type'),
                        url=attribute.get('url'), source=attribute.get('source'))
                    attribute_list.append(node_attribute)

        return attribute_list


    def add_node(self, id, name, type, attributes=None):
        """ adds a node to the knwledge graph of the response
            updated for trapi v1.0.0 """

        # map type
        category=translate_type(type, False)

        # translate the curie from molepro to biolink
        translated_curie = translate_curie(id, category, False)

        if translated_curie not in self.nodes:
            # node = Node(id=id, name=name, type=type)
            node = Node(name=name, category=category, attributes=attributes)
            node.id = translated_curie                    # added for trapi v1.0.0
            self.nodes[translated_curie] = node           
            self.knowledge_graph.nodes[translated_curie] = node
            return node
        return self.nodes[translated_curie]


    def add_edge(self, source_id, target_id, type, batch_id, connections=None):
        """adds a new edge to the knowledge graph of the response
            updated for trapi v1.0.0"""
        # print("edge connection: {}".format(connections))
        if (source_id, target_id) not in self.edges:
            # set the id of the edge; this will be the key in the knowledge graph
            edge_id = 'e' + str(len(self.knowledge_graph.edges)) + '-' + batch_id

            # add in the attributes
            attribute_list = self.pull_attributes(connections)

            # add the relation
            relation = None
            if connections is not None and 'relation' in connections:
                relation = connections.get('relation')
                #if relation is not None:
                    #print("edge relation: {}".format(relation))

            # create the edge object
            # edge = Edge(id=id, type=type, source_id=source_id, target_id=target_id)
            # TODO - add 'relation' -> single string from the connections[0] object
            edge = Edge(predicate=translate_type(type, False), subject=source_id, object=target_id, attributes=attribute_list, relation=relation)
            edge.id = edge_id                # added for trapi v1.0.0

            # add the edge to the graph and results collections
            # self.knowledge_graph.edges.append(edge)
            self.knowledge_graph.edges[edge_id] = edge
            self.edges[(source_id, target_id)] = edge

            # return
            return edge
        return self.edges[(source_id, target_id)]


def get_name(element):
    if element['names_synonyms'] is not None:
        for names in element['names_synonyms']:
            if names['name'] is not None:
                return names['name']
    return None

