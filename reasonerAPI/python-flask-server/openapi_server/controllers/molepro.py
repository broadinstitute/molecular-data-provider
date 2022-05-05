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
from openapi_server.controllers.utils import node_attributes, edge_attributes
from openapi_server.controllers.utils import get_logger
import os

# constants
logger = get_logger(__name__)

# environment variables
MOLEPRO_BASE_URL = os.environ.get('MOLEPRO_BASE_URL')

BASE_URL = 'https://translator.broadinstitute.org/molecular_data_provider'
if MOLEPRO_BASE_URL:
    BASE_URL = MOLEPRO_BASE_URL
logger.info("using molepro base URL: {}".format(BASE_URL))

class MolePro:

    debug = False

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


    def execute_transformer_chain(self, mole_edge, transformer_list):
        ''' passes the query through the transformers (one transformer per service/data) '''
        collection_info = None

        # handle special case of chemical substance as source
        if mole_edge.source_type == 'biolink:SmallMolecule' or mole_edge.source_type == 'biolink:MolecularMixture':
            collection_info = self.compound_collection(translate_curie(mole_edge.source_id, mole_edge.source_type))
            if collection_info is None or collection_info['size'] == 0:
                return
            collection = self.getCollection(collection_info, cache='yes')
            source_node = self.add_element(collection['elements'][0], source_id=mole_edge.source_id)
        else:
            source_node = self.add_node(mole_edge.source_id, None, mole_edge.source_type)

        # loop through the transformers
        for transformer in transformer_list:
            # TODO - only use id, so could come from first xcall
            response_info = self.execute_transformer(translate_curie(mole_edge.source_id, mole_edge.source_type), transformer, collection_info)
            collection_info = response_info

        # apply constraints
        for constraint in mole_edge.target_constraints:
            logger.info('Filtering {} nodes'.format(collection_info['size']))
            collection_info = self.apply_constraint('Element attribute filter', constraint, collection_info)
        for constraint in mole_edge.edge_constraints:
            logger.info('Filtering {} edges'.format(collection_info['size']))
            collection_info = self.apply_constraint('Connection attribute filter', constraint, collection_info)

        # for each element in a collection response, add an edge and associated nodes
        collection = self.getCollection(collection_info, cache='no')
        collection_id = collection.get('id')
        if collection.get('elements') is not None:
            for element in collection['elements']:
                self.add_result(source_node, mole_edge, element, collection_id)


    def compound_collection(self, curie):
        ''' specialized method for chem/compounds calls '''
        # BATCH FRIENDLY
        url = BASE_URL+'/compound/by_id'
        query = [curie]
        with closing(requests.post(url, json=query)) as id_response_obj:
            if id_response_obj.status_code != 200:
                return None

            # all that is needed in response is 'id' and 'size'
            response = id_response_obj.json()
            return response

        # return if nothing
        return None


    def apply_constraint(self, filter_name, constraint, collection_info):
        transformer_controls = []
        transformer_controls.append({'name':'id', 'value':constraint.id})
        transformer_controls.append({'name':'name', 'value':constraint.name})
        if constraint._not is not None:
            transformer_controls.append({'name':'not', 'value':constraint._not})
        transformer_controls.append({'name':'operator', 'value':constraint.operator})
        if isinstance(constraint.value, str):
            transformer_controls.append({'name':'value', 'value':constraint.value})
        if isinstance(constraint.value, list):
            for value in constraint.value:
                if isinstance(value, str):
                    transformer_controls.append({'name':'value', 'value':value})
        if constraint._not is not None:
            transformer_controls.append({'name':'unit_id', 'value':constraint.unit_id})
        if constraint.unit_name is not None:
            transformer_controls.append({'name':'unit_name', 'value':constraint.unit_name})
        transformer = {'name': filter_name, 'controls': transformer_controls}
        return self.execute_transformer(None, transformer, collection_info)


    def execute_transformer(self, src_subject, transformer, collection_info):
        url = BASE_URL+'/transform?cache=no'
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

        if self.debug:
            print("querying transformer {} with id {}".format(transformer['name'], collection_id))
        with closing(requests.post(url, json=query)) as response_obj:
            response_json = response_obj.json()
            if response_obj.status_code != 200:
                return None
            return response_json


    def getCollection(self, collection_info, cache):
        """ queries REST endpoint for collection data """ 
        if collection_info is None or collection_info.get('id') is None:
            return {'elements':[]}
        collection_id = collection_info.get('id')
        url = BASE_URL+'/collection/'+collection_id+'?cache='+cache

        # call and close the request
        with closing(requests.get(url)) as response_obj:
            if response_obj.status_code != 200:
                return {'elements':[]}
            return response_obj.json()


    def add_result(self, source_node, mole_edge, element, collection_id):
        """ for each given element in a collection result, add the edge and corresponding nodes to the result list """

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
                if connection_list is not None and len(connection_list) > 0:
                    connections = connection_list[0]

                    # add the edge
                    edge = self.add_edge(source_node.id, target_node.id, mole_edge.edge_type, collection_id, connections)

                    # updated for trapi v1.0.0
                    source_binding = NodeBinding(id=source_node.id)
                    edge_binding = EdgeBinding(id=edge.id)
                    target_binding = NodeBinding(id=target_node.id)

                    edge_map = {mole_edge.edge_key: [edge_binding]}
                    nodes_map = {mole_edge.source_key: [source_binding], mole_edge.target_key: [target_binding]}

                    # trapi 1.0 changes for the result formating (from list of nodes/edges to map of nodes/edges)
                    result = Result(node_bindings=nodes_map, edge_bindings=edge_map)
                    self.results.append(result)

    def add_element(self, element, source_id=None):
        """ pulls out the target node from the element data """
        # look for the connections
        node_attribute_list = []
        if 'compound_id' in element:
            id = element['compound_id']
            element_type = 'SmallMolecule'
        else:
            id = element['id']
            element_type = element['biolink_class']
        name = get_name(element)
        if source_id is not None:
            id = source_id
        # get the attributes
        if 'attributes' in element:
            node_attribute_list = self.pull_attributes(element, node_attributes())

        # return
        return self.add_node(id, name, element_type, attributes=node_attribute_list)

    def pull_attributes(self, node, biolink_attributes):
        """ build a list of attributes from the values in the object """
        attribute_list = []
        if node is not None and 'attributes' in node and node.get('attributes') is not None:
            for attribute in node.get('attributes'):
                # print("got attribute: {}".format(attribute))
                if attribute.get('attribute_type_id') is not None and attribute.get('attribute_type_id') in biolink_attributes:
                    if attribute.get('value') is not None and attribute.get('value') != '':
                        attribute_list.append(Attribute.from_dict(attribute))

        return attribute_list


    def add_node(self, id, name, type, attributes=None):
        """ adds a node to the knwledge graph of the response
            updated for trapi v1.0.0 """

        # map type
        category=translate_type(type, False)

        # translate the curie from molepro to biolink
        translated_curie = translate_curie(id, category, False)

        if self.debug:
            print("adding {} node {}".format(category, id))

        if translated_curie not in self.nodes:
            node = Node(name=name, categories=[category], attributes=attributes)
            node.id = translated_curie                    # added for trapi v1.0.0
            self.nodes[translated_curie] = node           
            self.knowledge_graph.nodes[translated_curie] = node
            return node
        return self.nodes[translated_curie]


    def add_edge(self, source_id, target_id, type, batch_id, connections=None):
        """adds a new edge to the knowledge graph of the response
            updated for trapi v1.0.0"""
        # print("edge connection: {}".format(connections))
        # 20210301 - add all edges; source/target uniqueness not enough
        # set the id of the edge; this will be the key in the knowledge graph
        edge_id = 'e' + str(len(self.knowledge_graph.edges)) + '-' + batch_id

        # add in the attributes
        attribute_list = self.pull_attributes(connections, edge_attributes())

        # add the relation
        predicate = type
        if type is None and connections is not None and 'biolink_predicate' in connections:
            predicate = connections.get('biolink_predicate')

        # create the edge object
        edge = Edge(predicate=translate_type(predicate, False), subject=source_id, object=target_id, attributes=attribute_list)
        edge.id = edge_id                # added for trapi v1.0.0

        # add the edge to the graph and results collections
        self.knowledge_graph.edges[edge_id] = edge
        self.edges[(source_id, target_id)] = edge

        # return
        return edge


def get_name(element):
    if element['names_synonyms'] is not None:
        for names in element['names_synonyms']:
            if names['name'] is not None:
                return names['name']
    return None

