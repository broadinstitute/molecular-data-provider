import requests
import json
from contextlib import closing

from openapi_server.models.query_graph import QueryGraph

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


    def match_query_graph(self, query_graph: QueryGraph):
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

