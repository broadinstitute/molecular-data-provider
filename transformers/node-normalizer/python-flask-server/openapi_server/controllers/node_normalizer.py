import requests
import json
from contextlib import closing
from collections import defaultdict

from transformers.transformer import Producer


class NodeNormalizer(Producer):

    variables = ['id']

    config = {}

    def __init__(self):
        super().__init__(self.variables, definition_file='info/node_normalizer_transformer_info.json')


    def update_transformer_info(self, transformer_info):
        with open('info/node_normalizer_config.json','r') as f:
            self.config = json.loads(f.read())
        print(self.config)
        transformer_info.properties.source_version = self.config['version']
        self.source_map = self.build_source_map()


    def produce(self, controls):
        self.map = {}
        return super().produce(controls)


    def find_names(self, query_id):
        url = self.config['url']+self.config['query']+str(query_id)
        with closing(requests.get(url)) as response_obj:
            response = response_obj.json()
            if query_id in response and response[query_id] is not None:
                id = response[query_id]['id']['identifier']
                self.map[id] = response[query_id]
                return [id]
        return []


    def create_element(self, id):
        element = None
        if id in self.map:
            response = self.map.pop(id)
            biolink_class = response.get('type',['biolink:NamedThing'])[0]
            if biolink_class.startswith('biolink:'):
                biolink_class = biolink_class[8:]
            biolink_class = self.class_dict.get(biolink_class, biolink_class)
            identifiers = {}
            names = defaultdict(set)
            if 'label' in response['id'] and response['id']['label'] is not None:
                names[self.SOURCE].add(response['id']['label'])
            for alt_id in response.get('equivalent_identifiers',[]):
                field_name = self.source_map.get(biolink_class,{}).get(self.prefix(alt_id),self.prefix(alt_id).lower())
                self.add_identifier(identifiers, field_name, alt_id['identifier'])
                self.add_name(names, field_name, alt_id.get('label'))
            element = self.Element(id, biolink_class, identifiers, self.get_names(names))
        return element


    def build_source_map(self):
        prefix_map = self.get_prefix_mapping()
        source_map = defaultdict(dict)
        for (biolink_class, mapping) in prefix_map.items():
            source_map[biolink_class]['node_normalizer'] = 'node_normalizer'
            for (field_name, prefixes) in mapping.items():
                print(biolink_class, prefixes['biolink_prefix'], field_name)
                source_map[biolink_class][prefixes['biolink_prefix']] = field_name
        print(source_map)
        return source_map


    def prefix(self, alt_id):
        id = alt_id['identifier']
        if ':' in id:
            return id.split(':')[0]
        return 'node_normalizer'


    def add_identifier(self, identifiers, field_name, identifier):
        if field_name in identifiers:
            if isinstance(identifiers[field_name], str):
                identifiers[field_name] = [identifiers[field_name]]
            if isinstance(identifiers[field_name], list):
                identifiers[field_name].append(identifier)
        else:
            identifiers[field_name] = identifier
    

    def add_name(self, names, source_name, name):
        if name is not None: 
            names[source_name].add(name)


    def get_names(self, names):
        names_list = []
        for (source_name, name_set) in names.items():
            name = None
            synonyms = list(name_set)
            if len(synonyms) == 1:
                name = synonyms[0]
                synonyms = []
            name_obj = self.Names(name, synonyms)
            name_obj.source = source_name
            names_list.append(name_obj)
        return names_list