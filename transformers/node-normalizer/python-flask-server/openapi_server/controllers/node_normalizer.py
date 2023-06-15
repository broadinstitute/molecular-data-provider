import requests
import json
from contextlib import closing
from collections import defaultdict

from transformers.transformer import Transformer


class NodeNormalizer(Transformer):

    variables = ['id', 'category']

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
        element_list = []
        elements = {}
        for curie in controls[self.variables[0]]:
            response = self.find(curie)
            if response is not None:
                id = response[curie]['id']['identifier']
                if id not in elements:
                    element = self.create_element(id, response[curie], controls)
                    if element is not None:
                        elements[id] = element
                        element_list.append(element)
                if id in elements:
                    elements[id].attributes.append(
                        self.Attribute(name='query name', value=curie, type='')
                )
        return element_list


    def find(self, curie):
        url = self.config['url']+self.config['query']+str(curie)
        with closing(requests.get(url)) as response_obj:
            response = response_obj.json()
            if curie in response and response[curie] is not None:
                return response
        return None


    def create_element(self, id, response, controls):
        element = None
        biolink_class = self.get_biolink_class(response, controls['category'])
        if biolink_class is not None:
            if biolink_class.startswith('biolink:'):
                biolink_class = biolink_class[8:]
            biolink_class = self.class_dict.get(biolink_class, biolink_class)
            identifiers = {}
            names = defaultdict(set)
            if 'label' in response['id'] and response['id']['label'] is not None:
                names[self.SOURCE].add(response['id']['label'])
            for alt_id in response.get('equivalent_identifiers',[]):
                field_name = self.source_map.get(biolink_class,{}).get(self.prefix(alt_id),self.prefix(alt_id).lower())
                self.add_identifier(identifiers, field_name, alt_id['identifier'], biolink_class)
                self.add_name(names, field_name, alt_id.get('label'))
            element = self.Element(id, biolink_class, identifiers, self.get_names(names))
        return element


    def get_biolink_class(self, response, categories):
        if categories is None:
            return response.get('type',['biolink:NamedThing'])[0]
        types = {tp[8:] if tp.startswith('biolink:') else tp for tp in response.get('type',['biolink:NamedThing'])}
        for category in categories:
            if category in types:
                return category
        return None


    def build_source_map(self):
        prefix_map = self.get_prefix_mapping()
        source_map = defaultdict(dict)
        for (biolink_class, mapping) in prefix_map.items():
            source_map[biolink_class]['node_normalizer'] = 'node_normalizer'
            for (field_name, prefixes) in mapping.items():
                if prefixes['biolink_prefix'] not in source_map[biolink_class]:
                    source_map[biolink_class][prefixes['biolink_prefix']] = field_name
                else:
                    print('  duplicate field_name')
        return source_map


    def prefix(self, alt_id):
        id = alt_id['identifier']
        if ':' in id:
            return id.split(':')[0]
        return 'node_normalizer'


    def add_identifier(self, identifiers, field_name, identifier, biolink_class):
        identifier = self.add_prefix(field_name, self.de_prefix(field_name, identifier, biolink_class), biolink_class)
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