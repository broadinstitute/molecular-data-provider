import requests
import json
from contextlib import closing

from openapi_server.models.query_graph import QueryGraph

from openapi_server.controllers.utils import translate_type

definition_file = 'transformer_chains.json'


class KnowledgeMap:


    def __init__(self):
        self.kmap = self.read_knowledge_map()


    def read_knowledge_map(self):
        kmap = {}
        with open(definition_file,'r') as f:
            for chain in json.loads(f.read()):
                add_predicate(kmap, chain)
        return kmap


    def load_knowledge_map(self):
        url = 'http://localhost:9200/molecular_data_provider/transformers'
        kmap = {}
        with closing(requests.get(url)) as response_obj:
            response = response_obj.json()
            for transformer in response:

                for predicate in transformer['knowledge_map']['predicates']:
                    predicate['transformer_chain'] = transformer_as_chain(transformer)
                    add_predicate(kmap, predicate)

        return kmap


    def predicates(self):
        return {
            subject: {
                object: list({predicate['predicate'] for predicate in predicates})
                for (object, predicates) in objects.items()
            }
            for (subject, objects) in self.kmap.items()
        }


    def get_transformers(self, subject_class, predicate, object_class):
        transformers = []
        if subject_class in self.kmap and object_class in self.kmap[subject_class]:
            for transformer in self.kmap[subject_class][object_class]:
                if predicate is None or predicate == transformer['predicate']:
                    transformers.append(transformer)
        return transformers


    def match_query_graph_old(self, query_graph: QueryGraph):
        nodes = {node.id:node for node in query_graph.nodes}
        edge = query_graph.edges[0]
        id = edge.id
        source = nodes[edge.source_id]
        target = nodes[edge.target_id]
        subject_class = source.type
        predicate = edge.type
        object_class = target.type
        edge = {'id':id, 'source':source, 'type':predicate, 'target':target}
        return (edge,self.get_transformers(subject_class, predicate, object_class))

    def match_query_graph(self, query_graph: QueryGraph):
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
        #subject_class = translate_type(source.category)
        predicate = edge.predicate
        #object_class = translate_type(target.category)
        edge = {'id':edge_id, 'source':source, 'type':predicate, 'target':target}
        return (edge, self.get_transformers(source.category, predicate, target.category))


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

