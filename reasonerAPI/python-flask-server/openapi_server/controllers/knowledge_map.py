import requests
import json
from contextlib import closing
from openapi_server.controllers.utils import get_logger

from openapi_server.models.query_graph import QueryGraph

from openapi_server.controllers.utils import translate_type
from openapi_server.controllers.molepro_edge import MoleproEdgeModel
import openapi_server.controllers.biolink_utils as bio_utils

from openapi_server.models.meta_node import MetaNode
from openapi_server.models.meta_attribute import MetaAttribute

import os

# environment variables
MOLEPRO_URL_TRANSFORMERS = os.environ.get('MOLEPRO_URL_TRANSFORMERS')

# constants
definition_file = 'conf/transformer_chains.json'
moleprodb_transformer = 'MoleProDB connections transformer'
logger = get_logger(__name__)

# url constants
url_transformers = "https://translator.broadinstitute.org/molecular_data_provider/transformers"
if MOLEPRO_URL_TRANSFORMERS:
    url_transformers = MOLEPRO_URL_TRANSFORMERS
logger.info("using transformer URL: {}".format(url_transformers))


class KnowledgeMap:

    debug = False

    def __init__(self):
        self.moleprodb_knowledge_map = {}
        self.kmap, self.list_chain_names = self.read_knowledge_map()
        self.nodes, self.edges, self.map_edge_attributes = self.build_nodes_edges_data()
        if self.debug:
            print("got chain names: {}".format(self.list_chain_names))

    def read_knowledge_map(self):
        kmap = {}
        list_chain_names = [moleprodb_transformer]

        with open(definition_file,'r') as f:
            json_chains = json.loads(f.read())
            for chain in json_chains:
                add_predicate(kmap, chain)

                # add the chain names
                if chain.get("transformer_chain"):
                    for item in chain.get("transformer_chain"):
                        list_chain_names.append(item.get("name"))

        return kmap, list(set(list_chain_names))


    def predicates(self):
        return {
            subject: {
                object: list({predicate['predicate'] for predicate in predicates})
                for (object, predicates) in objects.items()
            }
            for (subject, objects) in self.kmap.items()
        }

    def build_meta_attribute(self, transformer_attribute):
        ''' simple method to build and return a trapi meta attribute '''
        meta_attribute = MetaAttribute(attribute_type_id=transformer_attribute.get("attribute_type_id"), 
            attribute_source=transformer_attribute.get("source"), 
            original_attribute_names=transformer_attribute.get("names"))

        # return
        return meta_attribute

    def get_node_prefixes(self, input_json, log=False):
        ''' method to get the id prefix map for all node types '''
        # initialize
        map_nodes = {}
        map_edge_attributes = {}

        # build out the edge attributes
        for item in input_json:
            # only add if transformer in trapi list
            if item.get("name") and item.get("name") in self.list_chain_names:
                if item.get("knowledge_map").get("edges"):
                    for item_edg in item.get("knowledge_map").get("edges"):
                        if item_edg.get("attributes"):
                            subject = translate_type(input_type=item_edg.get("subject"), is_input=False)
                            target = translate_type(input_type=item_edg.get("object"), is_input=False)
                            predicate = translate_type(input_type=item_edg.get("predicate"), is_input=False)
                            for item_att in item_edg.get("attributes"):
                                meta_attribute = self.build_meta_attribute(item_att)
                                if map_edge_attributes.get((subject, target, predicate)):
                                    map_edge_attributes.get((subject, target, predicate)).append(meta_attribute)
                                else:
                                    map_edge_attributes[(subject, target, predicate)] = [meta_attribute]

        # log
        # print("got edge predicates: {}".format(map_edge_attributes))

        # loop through the json
        for item in input_json:
            if item.get("name") in self.list_chain_names:
                nodes = item.get('knowledge_map').get('nodes')
                if nodes:
                    for key, value in nodes.items():
                        # add in prefixes
                        if value.get('id_prefixes'):
                            # check if list already built for this node type
                            biolink_key = translate_type(input_type=key, is_input=False)
                            if map_nodes.get(biolink_key):
                                map_nodes.get(biolink_key).id_prefixes.extend(value.get('id_prefixes'))
                            else:
                                map_nodes[biolink_key] = MetaNode(id_prefixes=value.get('id_prefixes'))

                        # add in nodes
                        if value.get("attributes"):
                            list_attribute = []
                            for item_att in value.get("attributes"):
                                list_attribute.append(self.build_meta_attribute(item_att))
                            if map_nodes.get(biolink_key):
                                if map_nodes.get(biolink_key).attributes:
                                    map_nodes.get(biolink_key).attributes.extend(list_attribute)
                                else:
                                    map_nodes.get(biolink_key).attributes = list_attribute
                            else:
                                map_nodes[biolink_key] = MetaNode(attributes=list_attribute)

            # TODO - ODD PLACE TO HAVE THIS, REFACTOR - add in the metadata for the moleprodb since have the web transformers json handy
            if item.get('name') == moleprodb_transformer:
                self.moleprodb_knowledge_map = item.get('knowledge_map')

        # make sure the lists are unique
        for key, value in map_nodes.items():
            value.id_prefixes = list(set(value.id_prefixes))

        # return
        return map_nodes, map_edge_attributes


    def meta_knowledge_graph(self):
        ''' returns the nodes/edges for the meta knowledge map '''
        return self.nodes, self.edges, self.map_edge_attributes


    def build_nodes_edges_data(self):
        ''' will build the edge/nodes of the meta knowledge graph and return '''
        # initialize
        nodes = {}
        edges = []
        map_edge_attributes = {}

        # build the nodes
        with requests.get(url_transformers) as response:
            logger.warn('Loading transformer list from {}, status_code = {}'.format(url_transformers, response.status_code))
            if response.status_code != 200:
                logger.warn('Failed to load transformer list. {}: {}'.format(response.reason,response.text))
            nodes, map_edge_attributes = self.get_node_prefixes(response.json())        

        # add MoleProDB predicates
        for moleprodb_edge in self.moleprodb_knowledge_map.get('edges',[]):
            subject = translate_type(moleprodb_edge.get('subject'), False)
            target = translate_type(moleprodb_edge.get('object'), False)
            predicate = translate_type(moleprodb_edge.get('predicate'), False)
            #print('MoleProDB predicate:',subject, target, predicate,sep=' ')
            edges.append((subject, target, predicate))

        # build the edges
        for (subject, targets) in self.kmap.items():
            for (target, predicates) in targets.items():
                for predicate in predicates:
                    edges.append((subject, target, predicate.get('predicate')))
        # make sure they are unique
        edges = list(set(edges))

        # return
        return nodes, edges, map_edge_attributes

    def get_transformers(self, subject_class, predicate, object_class):
        transformers = []
        if subject_class in self.kmap and object_class in self.kmap[subject_class]:
            for transformer in self.kmap[subject_class][object_class]:
                if predicate is None or predicate == transformer['predicate']:
                    transformers.append(transformer)

        # return
        return transformers


    def match_query_graph(self, query_graph: QueryGraph):
        ''' transforms the trapi query into a neutral application form '''
        # trapi v1.0.0 - nodes are now keyed map by id, so no translation needed
        # nodes = {node.id:node for node in query_graph.nodes}
        nodes = query_graph.nodes
        for key, value in nodes.items(): 
            value.node_id = key
            #print("key: {} with value {}".format(key, value))

        # trapi v.1.0.0 - edges are map keyed by id, so convert to list
        # edge = query_graph.edges[0]
        edge_list = []
        for key, value in query_graph.edges.items():
            value.edge_id = key
            edge_list.append(value)

        # build the edge object that will be returned; add node 
        edge = edge_list[0]
        edge_id = edge.edge_id
        source = nodes[edge.subject]
        target = nodes[edge.object]

        if self.debug:
            print("edge: {}".format(edge))
            print("source: {}".format(source))
            print("target: {}".format(target))

        # add in the ancestry type conversion here
        source_type_list = source.categories if source.categories else ["all"]
        target_type_list = target.categories if target.categories else ["all"]
        edge_type_list = edge.predicates if edge.predicates else ["all"]
        #print("s {}, t {}, e {}, ids {}".format(source_type_list, target_type_list, edge_type_list, source.ids))

        # make sure there is a source id; if not, do nothing
        mole_edge_list = []
        accepted_predicate_list = []
        if source.ids is not None:
            # get all the possible queries based on the predicates supported
            accepted_predicate_list = bio_utils.get_overlap_queries_for_parts_list(source_type_list, target_type_list, edge_type_list, self.predicates(), False)            

            # build the molepro edge list
            for item in accepted_predicate_list:
                stype, etype, ttype = item.split()
                for sid in source.ids:
                    transformer_list = self.get_transformers(stype, etype, ttype)
                    #print("got mole edge {} - {} - {} - {} -> with transformer length {}".format(sid, stype, etype, ttype, len(transformer_list)))
                    if transformer_list is not None and len(transformer_list) > 0:
                        mole_edge_list.append(MoleproEdgeModel(edge_id, source.node_id, target.node_id, sid, None, etype, stype, ttype, target.constraints, edge.attribute_constraints, transformer_list))


        # return
        #print("========= got edge model list of size {}".format(len(mole_edge_list)))
        return mole_edge_list


def transformer_as_chain(transformer):
    name = transformer['name']
    controls = []
    for parameter in transformer['parameters']:
        value = parameter['default'] if parameter['biolink_class'] is None else '#subject'
        controls.append({'name':parameter['name'], 'value':value})
    return [{'name':name, 'controls': controls}]


def add_predicate(kmap, predicate):
    subject = predicate['subject']
    object = predicate['object']
    if subject not in kmap:
        kmap[subject] = {}
    if object not in kmap[subject]:
        kmap[subject][object] = []
    kmap[subject][object].append(predicate)


knowledge_map = KnowledgeMap()




