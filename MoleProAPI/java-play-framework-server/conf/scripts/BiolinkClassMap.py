from collections import defaultdict
from collections import OrderedDict
from contextlib import closing
import requests
import json

biolink_map_file = 'BiolinkClassMap.txt'

biolink_url = 'https://bl-lookup-sri.renci.org/bl/{}?version=latest'
ancestors_url = 'https://bl-lookup-sri.renci.org/bl/{}/ancestors?version=latest'

classes = {}


def get_biolink(concept):
    global classes
    if concept in classes:
        return classes[concept]
    url = biolink_url.format(concept)
    print(url)
    with closing(requests.get(url)) as response_obj:
        if response_obj is not None and response_obj.status_code == 200:
            biolink_class_json = response_obj.json()
            classes[concept] = biolink_class_json
            if 'ia_a' in biolink_class_json:
                classes[biolink_class_json['ia_a']] = biolink_class_json
            return biolink_class_json
    return {}


def get_ancestors(concept):
    url = ancestors_url.format(concept)
    print(url)
    with closing(requests.get(url)) as response_obj:
        if response_obj is not None and response_obj.status_code == 200:
            return response_obj.json()
    return []


def read_file(file_path):
    data_dict = defaultdict(list)
    with open(file_path, 'r') as file:
        file.readline()
        for line in file:
            columns = line.strip().split('\t')
            if len(columns) >= 2:
                value = columns[0]
                key = columns[1]
                data_dict[key].append(value)
    return data_dict


def read_prefixes():
    with open('prefixMap.json', 'r') as json_file:
        return json.load(json_file)


def find_prefix(prefix, molepro_prefixes):
    for key, value in molepro_prefixes.items():
        if value.get('biolink_prefix') == prefix:
            print('  found in MolePro:', key, prefix)
            return {
                'biolink_prefix': prefix,
                'field_name': key,
                'infores': value.get('infores'),
                'molepro_prefix': value.get('molepro_prefix', prefix + ':')
            }


def get_parent(biolink_class):
    parent = biolink_class.get('is_a')
    if parent is not None:
        if parent in classes:
            return classes[parent]
        for ancestor in get_ancestors(biolink_class['name']):
            ancestor_class = get_biolink(ancestor)
            print('    ancestor check:', parent, ancestor_class.get('name', '?'))
            if ancestor_class is not None and 'name' in ancestor_class and ancestor_class['name'] == parent:
                print('    ancestor match:', parent, ancestor_class['name'])
                return ancestor_class
    return None


def get_prefixes(biolink_class, molepro_prefixes):
    prefixes = OrderedDict()
    biolink_prefixes = biolink_class.get('id_prefixes', [])
    for prefix in biolink_prefixes:
        molepro_prefix = find_prefix(prefix, molepro_prefixes)
        if molepro_prefix is not None:
            field_name = molepro_prefix['field_name']
            prefixes[field_name] = molepro_prefix
        else:
            print('  not found in MolePro:', prefix)
            prefixes[prefix.lower()] = {
                'field_name': prefix.lower(),
                'biolink_prefix': prefix,
                'molepro_prefix': prefix + ':'
            }
    for field_name, entry in molepro_prefixes.items():
        prefix = entry.get('biolink_prefix')
        if field_name not in prefixes:
            prefixes[field_name] = entry
            prefixes[field_name]['field_name'] = field_name
            print('  addind prefix:', field_name, prefix)
    return [prefixes[key] for key in prefixes]


def main():
    molepro_prefixes = read_prefixes()
    biolink_class_map = defaultdict(dict)
    parents = set()
    for key, value in read_file(biolink_map_file).items():
        print(key)
        biolink_class = get_biolink(key)
        biolink_class_map[key]['id_prefixes'] = get_prefixes(biolink_class, molepro_prefixes.get(key, {}))
        biolink_class_map[key]['alias'] = value
        parent = get_parent(biolink_class)
        if parent is not None:
            parent_class = parent.get('class_uri')[8:]
            biolink_class_map[key]['parent'] = parent_class
            parents.add(parent_class)
    while len(parents) > 0:
        parent = parents.pop()
        biolink_class = get_biolink(parent)
        if parent not in biolink_class_map:
            print('+'+parent)
            biolink_class_map[parent]['id_prefixes'] = get_prefixes(biolink_class, molepro_prefixes.get(parent, {}))
            biolink_class_map[parent]['alias'] = []
            parent_parent = get_parent(biolink_class)
            if parent_parent is not None:
                parent_class = parent_parent.get('class_uri')[8:]
                biolink_class_map[parent]['parent'] = parent_class
                parents.add(parent_class)
    json.dump(biolink_class_map, open('biolink_class_map.json', 'w'), indent=4, separators=(',', ': '), sort_keys=True, )


if __name__ == '__main__':
    main()
