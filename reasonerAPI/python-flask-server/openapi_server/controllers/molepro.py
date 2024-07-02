import requests
import datetime
import json
import yaml
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
from openapi_server.models.qualifier import Qualifier
from openapi_server.models.analysis import Analysis
from openapi_server.models.log_entry import LogEntry
from openapi_server.models.log_level import LogLevel
from openapi_server.models.retrieval_source import RetrievalSource
from openapi_server.models.resource_role_enum import ResourceRoleEnum

from openapi_server.controllers.utils import translate_type
from openapi_server.controllers.utils import translate_curie
from openapi_server.controllers.utils import node_attributes, edge_attributes
from openapi_server.controllers.utils import get_logger
import os

# constants
logger = get_logger(__name__)
infores_molepro = "infores:molepro"

# environment variables
MOLEPRO_BASE_URL = os.environ.get('MOLEPRO_BASE_URL')

BASE_URL = 'https://translator.broadinstitute.org/molecular_data_provider'
if MOLEPRO_BASE_URL:
    BASE_URL = MOLEPRO_BASE_URL
logger.info("using molepro base URL: {}".format(BASE_URL))

# read trapi and biolink versions
VERSION_BIOLINK = 0.1
VERSION_TRAPI = 1.0
with open("./openapi_server/openapi/openapi.yaml", "r") as stream:
    try:
        map_openapi = yaml.safe_load(stream)
        VERSION_BIOLINK = map_openapi.get('info').get('x-translator').get('biolink-version')
        VERSION_TRAPI = map_openapi.get('info').get('x-trapi').get('version')
        # print(yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        print(exc)
logger.info("Using biolink version: {} and trapi version: {}".format(VERSION_BIOLINK, VERSION_TRAPI))

class MolePro:

    debug = False

    def __init__(self, query_graph):
        self.query_graph = query_graph
        self.results = []
        self.knowledge_graph = KnowledgeGraph(nodes={}, edges={})
        self.nodes = {}
        self.edges = {}
        self.logs = []
        self.query_transformers = set()
        self.cache_name_map = {}

    def add_to_ancestry_names_map(self, map_ancestry, log=False):
        for map_item in map_ancestry.values():
            self.cache_name_map.update(map_item)

    def get_results(self):
        message = Message(results=self.results, query_graph=self.query_graph, knowledge_graph=self.knowledge_graph)
        results_response = Response(message = message, logs = self.logs, schema_version=VERSION_TRAPI, biolink_version=VERSION_BIOLINK)
        return results_response


    def execute_transformer_chain(self, mole_edge, transformer_list, map_original_query_id):
        ''' 
        passes the query through the transformers (one transformer per service/data) 
        '''
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
            if response_info is not None:
                for log_entry in self.get_logs(response_info.get('attributes')):
                    self.logs.append(log_entry)
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
                self.add_result(source_node, mole_edge, element, collection_id, map_original_query_id)


    def get_logs(self, collection_attributes):
        logs = []
        if collection_attributes is not None:
            for attr in collection_attributes:
                if attr.get('attribute_type_id') is not None and attr.get('attribute_type_id').startswith('molepro.log:'):
                    level = LogLevel.INFO
                    if attr.get('attribute_type_id') == 'molepro.log:warning':
                        level = LogLevel.WARNING
                    if attr.get('attribute_type_id') == 'molepro.log:error':
                        level = LogLevel.ERROR
                    logs.append(LogEntry(datetime.datetime.now(), level, str(attr.get('original_attribute_name')), attr.get('value')))
        return logs


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
        '''
        query a transformer
        return: will get a collection_id
        '''
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
            print("url: {}".format(url))
            print("payload: {}\n".format(query))
        if transformer['name'] not in self.query_transformers:
            log_msg = "querying transformer '{}' at {}".format(transformer['name'], url)
            self.query_transformers.add(transformer['name'])
            self.logs.append(LogEntry(datetime.datetime.now(), LogLevel.INFO, LogLevel.INFO, log_msg))

        with closing(requests.post(url, json=query)) as response_obj:
            response_json = response_obj.json()
            if response_obj.status_code != 200:
                log_msg = "failed querying transformer {} at {} with {}".format(transformer['name'], url, response_obj.status_code)
                self.logs.append(LogEntry(datetime.datetime.now(), LogLevel.WARNING, str(response_obj.status_code), log_msg))
                return None
            return response_json


    def getCollection(self, collection_info, cache):
        """ 
        queries REST endpoint for collection data 
        """ 
        if collection_info is None or collection_info.get('id') is None:
            return {'elements':[]}
        collection_id = collection_info.get('id')
        url = BASE_URL+'/collection/'+collection_id+'?cache='+cache

        if self.debug:
            print("query collection: {}\n".format(url))

        # call and close the request
        with closing(requests.get(url)) as response_obj:
            if response_obj.status_code != 200:
                return {'elements':[]}
            return response_obj.json()


    def get_unique_connections_map(self, list_connection, subject=None, object=None, edge_type=None, log=False):
        '''
        will return the unique connection map based on (sub, ob, pred, source) key
        '''
        # initialize
        map_connections = {}

        if log:
            print("object type: {} of size: {}".format(type(list_connection), len(list_connection)))

        for connection in list_connection:
            # print("build connection: \n{}".format(json.dumps(connection, indent=2)))
            # get the predicate
            predicate = edge_type
            if edge_type is None and connection is not None and 'biolink_predicate' in connection:
                predicate = connection.get('biolink_predicate')

            # get the source 
            source = connection.get('source')
            if source:
                # build the key
                key_connection = subject + '-' + object + '-' + predicate + '-' + source

                # make sure the key is unique, then add
                if key_connection not in map_connections.keys():
                    map_connections[key_connection] = connection
                    if log:
                        print("added connection with key: {}".format(key_connection))
                else:
                    if log:
                        print("skipped connection with key: {}".format(key_connection))

        # log
        if log:
            print("for input connection size: {}, return size: {} with input type: {}".format(len(list_connection), len(map_connections), type(list_connection)))

        # return
        return map_connections

    def add_result(self, source_node, mole_edge, element, collection_id, map_original_query_id, log=False):
        """ 
        for each given element in a collection result, add the edge and corresponding nodes to the result list 
        """

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
                    # log
                    if self.debug and False:
                        print("\nfor collection id: {} - have non empty connections: {}".format(collection_id, connection_list))

                    # TODO - change to add all connections/edges
                    # connections = connection_list[0]
                    # debug
                    if log:
                        print("for connection size: {} only using first".format(len(connection_list)))
                        print(type(connection_list))
                    map_connections = self.get_unique_connections_map(list_connection=connection_list, subject=source_node.id, object=target_node.id, edge_type=mole_edge.edge_type)

                    # debug
                    if log:
                        print("for connection size: {} only alternate count: {}".format(len(connection_list), len(map_connections.values())))
                    
                    # add the edge
                    # 20230214 - adding all edges
                    for connections in map_connections.values():
                        edge = self.add_edge(source_node.id, target_node.id, mole_edge.edge_type, collection_id, connections)

                        # updated for trapi v1.0.0
                        source_original_id = map_original_query_id.get(source_node.id) if source_node.id else None
                        source_binding = NodeBinding(id=source_node.id, query_id=source_original_id, attributes=[])
                        edge_binding = EdgeBinding(id=edge.id, attributes=[])
                        target_original_id = map_original_query_id.get(target_node.id) if target_node.id else None
                        target_binding = NodeBinding(id=target_node.id, query_id=target_original_id, attributes=[])

                        edge_map = {mole_edge.edge_key: [edge_binding]}
                        nodes_map = {mole_edge.source_key: [source_binding], mole_edge.target_key: [target_binding]}

                        # trapi1.4 - add analyses element
                        analysis = Analysis(resource_id=infores_molepro, edge_bindings=edge_map, support_graphs=[], attributes=[])

                        # trapi 1.0 changes for the result formating (from list of nodes/edges to map of nodes/edges)
                        result = Result(node_bindings=nodes_map, analyses=[analysis])
                        self.results.append(result)




    def add_element(self, element, source_id=None):
        """ pulls out the target node from the element data """
        # look for the connections
        list_node_attributes = []
        list_node_qualifiers = []
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
            list_node_attributes, list_node_qualifiers, list_sources = self.pull_attributes_qualifiers(element, node_attributes())

        # debug
        if self.debug:
            for qualifier in list_node_qualifiers:
                print("NODE: got qualifier: {}".format(qualifier))

        # return
        return self.add_node(id, name, element_type, attributes=list_node_attributes)

    def pull_attributes_qualifiers(self, node, biolink_attributes):
        """ 
        build a list of attributes and qualifiers from the values in the object 
        -- biolink_attributes is the list from the MKG, so filter attributes based on those
        """
        # initialize
        list_attributes = []
        list_qualifiers = []
        list_sources = []
        list_pubs_curie = []
        list_pubs_str = []
        xrefs = []
        source_aggregator = None
        if node is not None and 'attributes' in node and node.get('attributes') is not None:
            for attribute in node.get('attributes'):
                # print("\n\ngot attribute: {}".format(attribute))
                # TRAPI 1.4 - add in retrieval sources
                if attribute.get('attribute_type_id') is not None:
                    # populate qualifiers
                    if 'qualifier:' in attribute.get('attribute_type_id'):
                        if attribute.get('value') is not None and attribute.get('value') != '':
                            qualifier_type = attribute.get('attribute_type_id').replace('qualifier:', '')
                            if 'biolink' not in qualifier_type and ':' not in qualifier_type:
                                qualifier_type = 'biolink:' + qualifier_type
                            list_qualifiers.append(Qualifier(qualifier_type_id=qualifier_type, qualifier_value=attribute.get('value')))

                    # populate retrieval sources
                    # elif attribute.get('attribute_type_id') in [ResourceRoleEnum.AGGREGATOR_KNOWLEDGE_SOURCE, ResourceRoleEnum.PRIMARY_KNOWLEDGE_SOURCE, ResourceRoleEnum.SUPPORTING_DATA_SOURCE]:
                    elif any(src in attribute.get('attribute_type_id') for src in [ResourceRoleEnum.AGGREGATOR_KNOWLEDGE_SOURCE, ResourceRoleEnum.PRIMARY_KNOWLEDGE_SOURCE, ResourceRoleEnum.SUPPORTING_DATA_SOURCE]):
                        resource_role = attribute.get('attribute_type_id')
                        if resource_role.startswith('biolink:'):
                            resource_role = resource_role[8:]
                        source_temp = RetrievalSource(resource_id=attribute.get('value'), resource_role=resource_role, upstream_resource_ids=[], source_record_urls=[])
                        if ResourceRoleEnum.AGGREGATOR_KNOWLEDGE_SOURCE in attribute.get('attribute_type_id'):
                            source_aggregator = source_temp
                        else:
                            list_sources.append(source_temp)
                        if attribute.get('value_url') is not None and attribute.get('value_url') != '':
                            source_temp.source_record_urls = attribute.get('value_url').split('\t')

                    # populate publications
                    elif attribute.get('attribute_type_id') in {'biolink:Publication', 'biolink:publication', 'biolink:publications'}:
                        if attribute.get('value') is not None and attribute.get('value') != '':
                            values = []
                            url = attribute.get('value_url')
                            if isinstance(attribute.get('value'), str):
                                if attribute.get('original_attribute_name') == "ClinicalTrials" and attribute.get('value').startswith('NCT'):
                                    url = None
                                    for value in attribute.get('value').split(','):
                                        values.append('clinicaltrials:'+value)
                                else:
                                    values.append(attribute.get('value'))
                            if isinstance(attribute.get('value'), list):
                                values.extend(attribute.get('value'))

                            if attribute.get('value_type_id') is not None and ('uri' in attribute.get('value_type_id').lower() or 'url' in attribute.get('value_type_id').lower()):
                                list_pubs_curie.extend(values)
                            else:
                                for value in values:
                                    prefix = value[:value.find(':')] if ':' in value else ''
                                    if prefix in {'clinicaltrials','PMID','ATC','https','http'}:
                                        list_pubs_curie.append(value)
                                    else:
                                        list_pubs_str.append(value)
                            if url is not None:
                                list_pubs_curie.append(url)

                    # populate filtered attributes
                    elif attribute.get('attribute_type_id') in biolink_attributes:
                        if attribute.get('value') is not None and attribute.get('value') != '':
                            list_attributes.append(Attribute.from_dict(attribute))


        if node is not None and 'identifiers' in node and node.get('identifiers') is not None:
            category=translate_type(node.get('biolink_class'), False)
            for field, identifier in node.get('identifiers').items():
                if isinstance(identifier, str):
                    translated_curie = translate_curie(identifier, category, False, field)
                    xrefs.append(translated_curie)
                if isinstance(identifier, list):
                    for xref in identifier:
                        translated_curie = translate_curie(xref, category, False, field)
                        xrefs.append(translated_curie)


        # TODO - pull out sources from attributes
        # create the aggregator source if not present
        if not source_aggregator:
            source_aggregator = RetrievalSource(resource_id=infores_molepro, resource_role=ResourceRoleEnum.AGGREGATOR_KNOWLEDGE_SOURCE, upstream_resource_ids=[], source_record_urls=[])

        # add the reference sources to the aggregator source
        # TODO - why is source_node never asigned a value?
        source_node: RetrievalSource = None
        source_aggregator.upstream_resource_ids = []
        for source_node in list_sources:
            source_aggregator.upstream_resource_ids.append(source_node.resource_id)

        # add the aggregator source to the final list
        list_sources.append(source_aggregator)

        # add publications
        if len(list_pubs_curie) > 0:
            list_attributes.append(Attribute('biolink:publications', None, list(set(list_pubs_curie)), 'linkml:Uriorcurie'))
        if len(list_pubs_str) > 0:
            list_attributes.append(Attribute('biolink:publications', None, list(set(list_pubs_str)), 'linkml:String'))

        # add xrefs
        if len(xrefs) > 0:
            list_attributes.append(Attribute('biolink:xref', 'identifiers', xrefs, 'linkml:Curie'))

        return list_attributes, list_qualifiers, list_sources


    def add_node(self, id, name, type, attributes=[]):
        """ adds a node to the knwledge graph of the response
            updated for trapi v1.0.0 """

        # map type
        category=translate_type(type, False)

        # get the name from the cache if none given
        if not name:
            name = self.cache_name_map.get(id)

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
        """
        adds a new edge to the knowledge graph of the response
            updated for trapi v1.0.0
        """
        # print("edge connection: {}".format(connections))
        # 20210301 - add all edges; source/target uniqueness not enough
        # set the id of the edge; this will be the key in the knowledge graph
        edge_id = 'e' + str(len(self.knowledge_graph.edges)) + '-' + batch_id

        # add in the attributes
        list_attributes, list_qualifiers, list_sources = self.pull_attributes_qualifiers(connections, edge_attributes())

        # debug
        if self.debug:
            for qualifier in list_qualifiers:
                print("EDGE: got qualifier: {}".format(qualifier))

        # add the relation
        predicate = type
        if type is None and connections is not None and 'biolink_predicate' in connections:
            predicate = connections.get('biolink_predicate')

        # add qualifiers
        qualifier_set = []
        for qualifier in connections.get('qualifiers',[]):
            qualifier_set.append(Qualifier.from_dict(qualifier))
        for qualifier in list_qualifiers:
            qualifier_set.append(qualifier)
        for qualifier in qualifier_set:
            if not qualifier.qualifier_type_id.startswith('biolink:'):
                qualifier.qualifier_type_id = 'biolink:' + qualifier.qualifier_type_id

        # create the edge object
        # edge = Edge(predicate=translate_type(predicate, False), subject=source_id, object=target_id, attributes=list_attributes)
        edge = Edge(predicate=translate_type(predicate, False), subject=source_id, object=target_id, attributes=list_attributes, qualifiers=qualifier_set, sources=list_sources)
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

