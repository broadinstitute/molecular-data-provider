import sqlite3
import json
from copy import copy
from collections import defaultdict

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.connection import Connection
from openapi_server.models.node import Node
from openapi_server.models.predicate import Predicate
from openapi_server.models.km_attribute import KmAttribute
from openapi_server.models.transformer_info import TransformerInfo
from openapi_server.encoder import JSONEncoder

from transformers.transformer import Transformer, Producer


connection = sqlite3.connect("data/MoleProDB.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

identifier_priority = []

class MoleProDB(Transformer):

    def __init__(self, variables, definition_file):
        super().__init__(variables, definition_file)


    def update_transformer_info(self, transformer_info):
        load_identifier_priority()


    def find_element(self, element_identifiers):
        for field in identifier_priority:
            if field in element_identifiers:
                identifiers = element_identifiers[field]
                if isinstance(identifiers, str):
                    identifiers = [identifiers]
                for identifier in identifiers:
                    for list_element_id in find_element(identifier):
                        return list_element_id
        return None


    def create_element(self, list_element_id, name_sources=None, element_attributes=None):
        element = None
        for row in get_element(list_element_id):
            identifiers = self.get_identifiers([list_element_id])[list_element_id]
            id = self.primary_id(identifiers)
            if id is None:
                return None
            names = self.get_names([list_element_id], copy(name_sources))
            names = self.create_names(row['primary_name'], names[list_element_id], copy(name_sources))
            attributes = self.get_attributes([list_element_id], 'List_Element_Attribute', 'list_element_id', element_attributes)
            element = self.Element(id, row['biolink_class'], identifiers, names, attributes[list_element_id])
        return element


    def get_identifiers(self, list_element_ids):
        identifiers = defaultdict(dict)
        for row in get_identifiers(list_element_ids):
            list_element_id = row['list_element_id']
            field_name = row['field_name']
            if field_name not in identifiers[list_element_id]:
                prefix = row['mole_pro_prefix']
                curie = prefix + ':' + row['xref'] if len(prefix) > 0 else row['xref']
                identifiers[list_element_id][field_name] = curie
        return identifiers


    def primary_id(self, identifiers):
        for field in identifier_priority:
            if field in identifiers:
                return identifiers[field]
        for (field, value) in identifiers.items():
            return value
        return None


    def get_names(self, list_element_ids, name_sources):
        names = defaultdict(list)
        if name_sources is None or len(name_sources) > 0:
            for row in get_names(list_element_ids, name_sources):
                list_element_id = row['list_element_id']
                names[list_element_id].append(row_to_dict(row, NAME_COLUMNS))
        return names


    def create_names(self, primary_name, rows, name_sources):
        name_list = []
        names = {}
        if name_sources is None or 'MolePro' in name_sources:
            name = Names(primary_name,[],'','MolePro',self.PROVIDED_BY,None)
            name_list.append(name)
            names[self.key(name.source, name.provided_by, name.name_type, name.language)] = name
            if name_sources is not None:
                name_sources.discard('MolePro')
       
        if name_sources is None or len(name_sources) > 0:
            for row in rows:
                name_source = row['name_source']
                if name_sources is None or name_source in name_sources:
                    name = row['name']
                    is_synonym = False
                    name_type = row['name_type']
                    if name_type.endswith(' synonym'):
                        name_type = name_type[:-8]
                        is_synonym = True
                    if name_type == 'synonym':
                        name_type = ''
                        is_synonym = True
                    if name_type == 'primary name':
                        name_type = ''
                    provided_by = row['transformer']
                    language = row['language'] 
                    key = self.key(name_source,provided_by,name_type,language)
                    if key not in names:
                        names[key] = Names(None,[],name_type,name_source,provided_by,language)
                        name_list.append(names[key])
                    if is_synonym or names[key].name is not None:
                        names[key].synonyms.append(name)
                    else:
                        names[key].name = name
        return name_list


    def get_attributes(self, parent_ids, attr_table, parent_id_name, types):
        if len(parent_ids) == 0:
            return {}
        attributes = defaultdict(list)
        attribute_ids = []
        for row in get_attributes(parent_ids, attr_table, parent_id_name, types):
            attribute_type = row['attribute_type']
            attribute_name = row['attribute_name']
            attribute_value = row['attribute_value']
            value_type = row['value_type']
            url = row['url']
            description = row['description']
            source_name = row['source_name']
            transformer = row['transformer']
            attribute = Attribute(
                attribute_type_id = attribute_type,
                original_attribute_name = attribute_name,
                value = attribute_value,
                value_type_id = value_type,
                attribute_source = source_name,
                value_url = url,
                description = description,
                attributes = [], 
                provided_by = transformer)
            parent_id = row[parent_id_name]
            attributes[parent_id].append(attribute)
            attribute_id = row['attribute_id']
            attribute.attribute_id = attribute_id
            attribute_ids.append(str(attribute_id))
        sub_attributes = self.get_attributes(attribute_ids, 'Parent_Attribute', 'parent_attribute_id', None)
        for attr_list in attributes.values():
            for attr in attr_list:
                attr.attributes = sub_attributes.get(attr.attribute_id)
        return attributes


    def key(self, source, provided_by, name_type, language):
        language = language if language is not None else ''
        return source+'|'+provided_by+'|'+name_type+'|'+language



class MoleProDBProducer(Producer, MoleProDB):

    variables = ['id']

    def __init__(self):
        super().__init__(self.variables, definition_file='data/moleprodb_producer_info.json')


    def find_names(self, query_id):
        return find_element(query_id)



class MoleProDBNameProducer(Producer, MoleProDB):

    variables = ['name']

    def __init__(self):
        super().__init__(self.variables, definition_file='data/moleprodb_name_producer_info.json')


    def find_names(self, name):
        ids = find_element_by_primary_name(name)
        if len(ids) > 0:
            return ids
        return find_element_by_name(name)



##############################################
#  MoleProDB connections transformer
#
#
class MoleProDBTransformer(MoleProDB):

    variables = ['predicate', 'biolink_class', 'id', 'name_source', 'element_attribute', 'connection_attribute', 'limit']


    def __init__(self):
        super().__init__(self.variables, definition_file='data/moleprodb_transformer_info.json')

    def update_transformer_info(self, transformer_info):
        load_identifier_priority()


    def map(self, input_list, controls):
        name_sources = set(controls.get('name_source')) if controls.get('name_source') is not None else None
        control_element_attributes = set(controls.get('element_attribute')) if controls.get('element_attribute') is not None else None
        control_connection_attributes = set(controls.get('connection_attribute')) if controls.get('connection_attribute') is not None else None
        limit = int(controls.get('limit', 0))

        connections = self.get_connections(input_list, controls, limit)
        element_ids = self.get_element_ids(connections)
        identifiers = self.get_identifiers(element_ids)
        names = self.get_names(element_ids, name_sources)
        element_attributes = self.get_attributes(element_ids, 'List_Element_Attribute', 'list_element_id', control_element_attributes)
        element_list = []
        elements = {}
        for row in get_elements(element_ids):
            element_id = row['list_element_id']
            element = self.create_element(row, identifiers.get(element_id), names.get(element_id,[]), element_attributes.get(element_id,[]), name_sources) 
            if element is not None:
                element_list.append(element)
                elements[element_id] = element
        connection_ids = [connection['connection_id'] for connection in connections]
        connection_attributes = self.get_attributes(connection_ids, 'Connection_Attribute', 'connection_id', control_connection_attributes)
        for connection_row in connections:
            connection_id = connection_row['connection_id']
            element_id = connection_row['object_id']
            connection = self.create_connection(connection_row, connection_attributes.get(connection_id,[]))
            if element_id in elements:
                elements[element_id].connections.append(connection)
        return element_list


    def get_connections(self, input_list, controls, limit):
        connections = []
        for query_element in input_list:
            counts = {}
            query_element_id = self.find_element(query_element.identifiers)
            for row in find_connections(query_element_id, controls):
                connection = row_to_dict(row, CONNECTION_COLUMNS)
                connection['source_element_id'] = query_element.id
                transformer = connection['transformer']
                counts[transformer] = counts.get(transformer, 0) + 1
                if limit <= 0 or counts[transformer] <= limit:
                    connections.append(connection)
        return connections


    def get_element_ids(self, connections):
        element_ids = []
        elements = set()
        for connection in connections:
            object_id = connection['object_id']
            if object_id not in elements:
                element_ids.append(object_id)
                elements.add(object_id)
        return element_ids
            

    def create_element(self, row, identifiers, names, element_attributes, name_sources):
        id = self.primary_id(identifiers)
        if id is None:
            return None
        names = self.create_names(row['primary_name'], names, name_sources)
        return self.Element(id, row['biolink_class'], identifiers, names, element_attributes)


    def create_connection(self, row, connection_attributes):
        source_element_id = row['source_element_id']
        uuid = row['uuid']
        biolink_predicate = row['biolink_predicate']
        inverse_predicate = row['inverse_predicate']
        relation = row['relation']
        inverse_relation = row['inverse_relation']
        source_name = row['source_name']
        transformer = row['transformer']
        attributes = connection_attributes
        attributes.append(self.Attribute('connection_id', str(uuid), type=''))
        connection = Connection(
            source_element_id = source_element_id,
            biolink_predicate = biolink_predicate,
            inverse_predicate = inverse_predicate,
            relation = relation,
            inverse_relation = inverse_relation,
            source = source_name,
            provided_by = transformer,
            attributes = attributes
        )
        return connection



##############################################################
#  MoleProDB hierarchy transformer
#
# Support for entity subclass operations issue #189
#  https://github.com/broadinstitute/scb-kp-dev/issues/189
#  
# self.find_element(query_element.identifiers) obtains parent element 
# ids before the query
#
# self.create_element(object_id, name_sources, element_attributes) 
# query the elements after the query. 
#
#
class MoleProDBhierarchyTransformer(MoleProDB):

    variables = ['name_source', 'element_attribute', 'hierarchy_type']

    inverse = {
        'biolink:subclass_of': 'biolink:superclass_of',
        'biolink:superclass_of': 'biolink:subclass_of'
    }

    def __init__(self):
        super().__init__(self.variables, definition_file='data/moleprodb_hierarchy_transformer_info.json')

    def update_transformer_info(self, transformer_info):
        load_identifier_priority()

    def map(self, input_list, controls):
        ### Use name_source (e.g., BiGG, BiGG Model, CBN, COMe, CTD, ChEBI, ChEMBL, ChemBank)
        name_sources = set(controls.get('name_source')) if controls.get('name_source') is not None else None
        ### Use element_attribute
        element_attributes = set(controls.get('element_attribute')) if controls.get('element_attribute') is not None else None
        element_list = []
        elements = {}
        
        for query_element in input_list:
            query_element_id = self.find_element(query_element.identifiers)
            #### query to get hierarchy information
            for row in find_hierarchy(query_element_id, controls.get('hierarchy_type')):
                element_id = row['list_element_id']
                if element_id not in elements:
                    #query elements after the query. 
                    element = self.create_element(element_id, name_sources, element_attributes)
                    element_list.append(element)
                    elements[element_id] = element
                connection = self.create_connection(query_element.id, row['hierarchy_type'])
                elements[element_id].connections.append(connection)
        return element_list


    def create_connection(self, source_element_id, hierarchy_type):
        return Connection(
            source_element_id = source_element_id,
            biolink_predicate = hierarchy_type,
            inverse_predicate = self.inverse.get(hierarchy_type),
            relation = hierarchy_type,
            inverse_relation = self.inverse.get(hierarchy_type),
            source = self.SOURCE,
            provided_by = self.PROVIDED_BY,
            attributes = []
        )


def row_to_dict(row, columns):
    return {key: row[key] for key in columns}


def find_elements_by_id1(prefix, xref):
    query = """
        SELECT DISTINCT list_element_id
        FROM List_Element_Identifier
        JOIN Curie_Prefix ON Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
        JOIN Source ON Source.source_id = List_Element_Identifier.source_id
        WHERE (mole_pro_prefix = ? OR biolink_prefix = ? COLLATE NOCASE) COLLATE NOCASE AND xref = ?
        AND Source.infores_id = Curie_Prefix.infores_id
    """
    cur = connection.cursor()
    cur.execute(query,(prefix,prefix,xref))
    return cur.fetchall()


def find_elements_by_id2(prefix, xref):
    query = """
        SELECT DISTINCT list_element_id
        FROM List_Element_Identifier
        JOIN Curie_Prefix ON Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
        JOIN Source ON Source.source_id = List_Element_Identifier.source_id
        WHERE (mole_pro_prefix = ? OR biolink_prefix = ? COLLATE NOCASE) COLLATE NOCASE AND xref = ?
        AND Source.transformer = 'SRI node normalizer producer'
    """
    cur = connection.cursor()
    cur.execute(query,(prefix,prefix,xref))
    return cur.fetchall()


def find_elements_by_id3(prefix, xref):
    query = """
        SELECT DISTINCT list_element_id
        FROM List_Element_Identifier
        JOIN Curie_Prefix ON Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
        WHERE (mole_pro_prefix = ? OR biolink_prefix = ? COLLATE NOCASE) COLLATE NOCASE AND xref = ?
    """
    cur = connection.cursor()
    cur.execute(query,(prefix,prefix,xref))
    return cur.fetchall()


def get_element(list_element_id):
    query = """
        SELECT list_element_id, primary_name, biolink_class
        FROM List_Element
        JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id
        WHERE list_element_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(list_element_id,))
    return cur.fetchall()


def get_elements(list_element_ids):
    query = """
        SELECT list_element_id, primary_name, biolink_class
        FROM List_Element
        JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id
        WHERE list_element_id in ({})
    """.format(','.join([str(id) for id in list_element_ids]))
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()


def get_ids(list_element_id):
    query = """
        SELECT DISTINCT field_name, mole_pro_prefix, xref
        FROM List_Element_Identifier
        JOIN Curie_Prefix ON Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
        WHERE list_element_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(list_element_id,))
    return cur.fetchall()


def get_identifiers(list_element_ids):
    query = """
        SELECT DISTINCT list_element_id, field_name, mole_pro_prefix, xref
        FROM List_Element_Identifier
        JOIN Curie_Prefix ON Curie_Prefix.prefix_id = List_Element_Identifier.prefix_id
        WHERE list_element_id in ({})
    """.format(','.join([str(id) for id in list_element_ids]))
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()


def get_single_names(list_element_id, name_sources):
    query = """
        SELECT name, name_type, name_source, transformer, language
        FROM List_Element_Name
        JOIN Name ON Name.name_id = List_Element_Name.name_id
        JOIN Name_Type ON Name_Type.name_type_id = List_Element_Name.name_type_id
        JOIN Name_Source ON Name_Source.name_source_id = List_Element_Name.name_source_id
        JOIN Source ON Source.source_id = List_Element_Name.source_id
        WHERE list_element_id = ?
    """
    if name_sources is not None:
        query = query + "AND name_source IN ('" + "','".join(name_sources) + "')"
    cur = connection.cursor()
    cur.execute(query,(list_element_id,))
    return cur.fetchall()


NAME_COLUMNS = ['name', 'name_type', 'name_source', 'transformer', 'language']

def get_names(list_element_ids, name_sources):
    query = """
        SELECT list_element_id, name, name_type, name_source, transformer, language
        FROM List_Element_Name
        JOIN Name ON Name.name_id = List_Element_Name.name_id
        JOIN Name_Type ON Name_Type.name_type_id = List_Element_Name.name_type_id
        JOIN Name_Source ON Name_Source.name_source_id = List_Element_Name.name_source_id
        JOIN Source ON Source.source_id = List_Element_Name.source_id
        WHERE list_element_id in ({})
    """.format(','.join([str(id) for id in list_element_ids]))
    if name_sources is not None:
        query = query + "AND name_source IN ('" + "','".join(name_sources) + "')"
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()


def get_attributes_single(parent_id, attr_table, parent_id_name, types):
    query = """
        SELECT Attribute.attribute_id, attribute_type, attribute_name, attribute_value, value_type, url, description, source_name, transformer
        FROM {}
        JOIN Attribute ON Attribute.attribute_id = {}.attribute_id
        JOIN Attribute_Type ON Attribute_Type.attribute_type_id = Attribute.attribute_type_id
        JOIN Source ON Source.source_id = {}.source_id
        WHERE {} = ?
    """.format(attr_table,attr_table,attr_table,parent_id_name)
    if types is not None:
        query = query + "AND attribute_type IN ('" + "','".join(types) + "')"
    cur = connection.cursor()
    cur.execute(query,(parent_id,))
    return cur.fetchall()


def get_attributes(parent_ids, attr_table, parent_id_name, types):
    query = """
        SELECT {}, Attribute.attribute_id, attribute_type, attribute_name, attribute_value, value_type, url, description, source_name, transformer
        FROM {}
        JOIN Attribute ON Attribute.attribute_id = {}.attribute_id
        JOIN Attribute_Type ON Attribute_Type.attribute_type_id = Attribute.attribute_type_id
        JOIN Source ON Source.source_id = {}.source_id
        WHERE {} in ({})
    """.format(parent_id_name, attr_table, attr_table, attr_table, parent_id_name, ','.join([str(id) for id in parent_ids]))
    if types is not None:
        query = query + "AND attribute_type IN ('" + "','".join(types) + "')"
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()


CONNECTION_COLUMNS = [
    'subject_id',
    'connection_id',
    'uuid',
    'object_id',
    'biolink_predicate',
    'inverse_predicate',
    'relation',
    'inverse_relation',
    'source_name',
    'transformer'
]


def find_connections(query_element_id, controls):
    if query_element_id is None:
        return []

    predicate_clause = ''
    inv_predicate_clause = ''
    if controls.get('predicate') is not None:
        predicates = [
            predicate if predicate.startswith('biolink:') else 'biolink:'+predicate
            for predicate in controls.get('predicate')
        ]
        predicates = ["'" + predicate + "'" for predicate in predicates]
        predicate_clause = 'biolink_predicate in (' + ','.join(predicates) + ') AND '
        inv_predicate_clause = 'inverse_predicate in (' + ','.join(predicates) + ') AND '

    biolink_class_join = ''
    biolink_class_clause = ''
    inv_biolink_class_join = ''
    if controls.get('biolink_class') is not None:
        biolink_class_join = 'JOIN List_Element ON List_Element.list_element_id = Connection.object_id\n'
        biolink_class_join += '        JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id'
        inv_biolink_class_join = 'JOIN List_Element ON List_Element.list_element_id = Connection.subject_id\n'
        inv_biolink_class_join += '        JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id'
        classes = [
            biolink_class[8:] if biolink_class.startswith('biolink:') else biolink_class
            for biolink_class in controls.get('biolink_class')
        ]
        classes = ["'" + biolink_class + "'" for biolink_class in classes]
        biolink_class_clause = 'biolink_class in (' + ','.join(classes) + ') AND'

    object_clause = ''
    subject_clause = ''
    if controls.get('id') is not None:
        ids = []
        for id in controls.get('id'):
            ids.extend(find_element(id))
        if len(ids) == 0:
            return []
        object_clause = 'object_id in (' + ','.join(str(id) for id in ids) + ') AND'
        subject_clause = 'subject_id in (' + ','.join(str(id) for id in ids) + ') AND'

    query = """
        SELECT DISTINCT
            subject_id,
            connection_id,
            uuid,
            object_id,
            biolink_predicate,
            inverse_predicate,
            relation,
            inverse_relation,
            source_name,
            transformer
        FROM Connection
        JOIN Source ON Source.source_id = Connection.source_id
        JOIN Predicate ON Predicate.predicate_id = Connection.predicate_id
        {}
        WHERE subject_id = ? AND {} {} {} Connection.source_id > 0
        
        UNION

        SELECT DISTINCT
            object_id AS subject_id,
            connection_id,
            uuid,
            subject_id AS object_id,
            inverse_predicate AS biolink_predicate,
            biolink_predicate AS inverse_predicate,
            inverse_relation AS relation,
            relation AS inverse_relation,
            source_name,
            transformer
        FROM Connection
        JOIN Source ON Source.source_id = Connection.source_id
        JOIN Predicate ON Predicate.predicate_id = Connection.predicate_id
        {}
        WHERE object_id = ? AND {} {} {} Connection.source_id > 0;
    """.format(biolink_class_join, predicate_clause, biolink_class_clause, object_clause,
        inv_biolink_class_join, inv_predicate_clause, biolink_class_clause, subject_clause
    )
    cur = connection.cursor()
    cur.execute(query,(query_element_id,query_element_id))
    return cur.fetchall()


####################################################################################################
#
# Given the Parent class, find child classes (e.g., For "Type II Diabetes" the child classes include
# diabetic ketoacidosis, glucose metabolism disease, diabetes mellitus, noninsulin-dependent, 5)
# 
#
#
def find_hierarchy(query_element_id, hierarchy_types):
    in_hierarchy_types = ' AND hierarchy_type IN (' + ','.join(["'"+hierarchy_type+"'" for hierarchy_type in hierarchy_types]) + ')' if hierarchy_types is not None else ''
    if query_element_id is None:
        return []
    query = """
        SELECT list_element_id, hierarchy_type
        FROM Element_Hierarchy
        WHERE parent_element_id = ? {};
        """.format(in_hierarchy_types)
    cur = connection.cursor()
    cur.execute(query, (query_element_id,))
    return cur.fetchall()


def find_element(query_id):
    ids = []
    prefix = ''
    xref = query_id
    if ':' in query_id:
        curie = query_id.split(':')
        prefix = curie[0]
        xref = curie[1]
    for row in find_elements_by_id1(prefix, xref):
        ids.append(row['list_element_id'])
    if len(ids) == 0:
        for row in find_elements_by_id2(prefix, xref):
            ids.append(row['list_element_id'])
    if len(ids) == 0:
        for row in find_elements_by_id3(prefix, xref):
            ids.append(row['list_element_id'])            
    return ids


def find_element_by_primary_name(name):
    query = """
        SELECT list_element_id
        FROM List_Element
        WHERE primary_name = ? COLLATE NOCASE
    """
    cur = connection.cursor()
    cur.execute(query,(name,))
    return [row['list_element_id'] for row in cur.fetchall()]


def find_element_by_name(name):
    query = """
        SELECT DISTINCT list_element_id
        FROM Name
        JOIN List_Element_Name ON List_Element_Name.name_id = Name.name_id
        WHERE name = ? COLLATE NOCASE
    """
    cur = connection.cursor()
    cur.execute(query,(name,))
    return [row['list_element_id'] for row in cur.fetchall()]


def load_identifier_priority():
    global identifier_priority
    with open('data/transformerConfig.json') as json_file:
        config = json.load(json_file)
        identifier_priority = config['identifier priority']


def get_node_counts():
    query = """
    SELECT count(*) as count, biolink_class
        FROM List_Element
        JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id
        GROUP BY biolink_class;
    """
    cur = connection.cursor()
    cur.execute(query)
    nodes = {}
    for row in cur.fetchall():
        biolink_class = row['biolink_class']
        count = row['count']
        nodes[biolink_class] = Node(id_prefixes=[],count=count,attributes=[])
    return nodes


def get_node_attributes():
    query = """
        SELECT source_name, biolink_class, attribute_type, attribute_name
        FROM List_Element_Attribute
        JOIN Attribute ON Attribute.attribute_id = List_Element_Attribute.attribute_id
        JOIN Attribute_Type ON Attribute_Type.attribute_type_id = Attribute.attribute_type_id
        JOIN Source ON Source.source_id = List_Element_Attribute.source_id
        JOIN List_Element ON List_Element.list_element_id = List_Element_Attribute.list_element_id
        JOIN Biolink_Class ON Biolink_Class.biolink_class_id = List_Element.biolink_class_id
    """
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()


def get_edge_counts():
    query = """
        SELECT Subject_Class.biolink_class AS subject_class, biolink_predicate, inverse_predicate, 
          Object_Class.biolink_class object_class, count(*) as count
        FROM Connection
        JOIN List_Element AS Object_Element ON Object_Element.list_element_id = Connection.object_id
        JOIN Biolink_Class AS Object_Class ON Object_Class.biolink_class_id = Object_Element.biolink_class_id
        JOIN List_Element AS Subject_Element ON Subject_Element.list_element_id = Connection.subject_id
        JOIN Biolink_Class AS Subject_Class ON Subject_Class.biolink_class_id = Subject_Element.biolink_class_id
        JOIN Predicate ON Predicate.predicate_id = Connection.predicate_id
        GROUP BY subject_class, biolink_predicate, inverse_predicate, object_class
    """
    cur = connection.cursor()
    cur.execute(query)
    edges = {}
    for row in cur.fetchall():
        subject_class = row['subject_class']
        biolink_predicate = row['biolink_predicate']
        inverse_predicate = row['inverse_predicate']
        object_class = row['object_class']
        count = row['count']
        
        inv_pred = Predicate(object_class, inverse_predicate, biolink_predicate, subject_class, count=count,attributes=[])
        if (subject_class, biolink_predicate, object_class) in edges:
            edges[(subject_class, biolink_predicate, object_class)].count += count
        else:
            pred = Predicate(subject_class, biolink_predicate, inverse_predicate, object_class, count=count,attributes=[])
            edges[(subject_class, biolink_predicate, object_class)] = pred
        if (object_class, inverse_predicate, subject_class) in edges:
            edges[(object_class, inverse_predicate, subject_class)].count += count
        else:
            edges[(object_class, inverse_predicate, subject_class)] = inv_pred
    return edges


def get_edge_attributes():
    query = """
        SELECT Subject_Class.biolink_class AS subject_class, biolink_predicate, inverse_predicate, 
          Object_Class.biolink_class object_class, source_name, attribute_type, attribute_name
        FROM Connection_Attribute
        JOIN Attribute ON Attribute.attribute_id = Connection_Attribute.attribute_id
        JOIN Attribute_Type ON Attribute_Type.attribute_type_id = Attribute.attribute_type_id
        JOIN Source ON Source.source_id = Connection_Attribute.source_id
        JOIN Connection ON Connection.connection_id = Connection_Attribute.connection_id
        JOIN List_Element AS Object_Element ON Object_Element.list_element_id = Connection.object_id
        JOIN Biolink_Class AS Object_Class ON Object_Class.biolink_class_id = Object_Element.biolink_class_id
        JOIN List_Element AS Subject_Element ON Subject_Element.list_element_id = Connection.subject_id
        JOIN Biolink_Class AS Subject_Class ON Subject_Class.biolink_class_id = Subject_Element.biolink_class_id
        JOIN Predicate ON Predicate.predicate_id = Connection.predicate_id
    """
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()


def get_prefixes():
    query = """
        SELECT DISTINCT biolink_class, field_name, mole_pro_prefix
        FROM Curie_Prefix
        JOIN Biolink_Class ON Biolink_Class.biolink_class_id = Curie_Prefix.biolink_class_id
    """
    cur = connection.cursor()
    cur.execute(query)
    nodes = {}
    for row in cur.fetchall():
        biolink_class = row['biolink_class']
        prefix = row['mole_pro_prefix']
        field_name = row['field_name']
        prefix = field_name if prefix == '' else prefix
        if biolink_class not in nodes:
            nodes[biolink_class] = set()
        nodes[biolink_class].add(prefix)
    return nodes


def meta_node_attributes():
    i = 0
    nodes = {}
    for row in get_node_attributes():
        source_name = row['source_name']
        biolink_class = row['biolink_class']
        attribute_type = row['attribute_type']
        attribute_name = row['attribute_name']
        if attribute_type != '':
            if biolink_class not in nodes:
                nodes[biolink_class] = {}
            if (source_name,attribute_type) not in nodes[biolink_class]:
                attribute = KmAttribute(type=attribute_type, attribute_type_id = attribute_type, source=source_name, names = [])
                nodes[biolink_class][(source_name,attribute_type)] = attribute
            if attribute_name not in nodes[biolink_class][(source_name,attribute_type)].names:
                nodes[biolink_class][(source_name,attribute_type)].names.append(attribute_name)
    return nodes


def meta_edge_attributes():
    i = 0
    edges = {}
    for row in get_edge_attributes():
        subject_class = row['subject_class']
        biolink_predicate = row['biolink_predicate']
        inverse_predicate = row['inverse_predicate']
        object_class = row['object_class']
        source_name = row['source_name']
        attribute_type = row['attribute_type']
        attribute_name = row['attribute_name']
        if attribute_type != '':
            if (subject_class, biolink_predicate, object_class)  not in edges:
                edges[(subject_class, biolink_predicate, object_class)] = {}
            if (source_name,attribute_type) not in edges[(subject_class, biolink_predicate, object_class)]:
                attribute = KmAttribute(type=attribute_type, attribute_type_id = attribute_type, source=source_name, names = [])
                edges[(subject_class, biolink_predicate, object_class)][(source_name,attribute_type)] = attribute
            if attribute_name not in edges[(subject_class, biolink_predicate, object_class)][(source_name,attribute_type)].names:
                edges[(subject_class, biolink_predicate, object_class)][(source_name,attribute_type)].names.append(attribute_name)
    return edges


def nodes():
    print('loading node counts')
    nodes = get_node_counts()
    print('loading node prefixes')
    for (biolink_class, prefixes) in get_prefixes().items():
        if biolink_class in nodes:
            nodes[biolink_class].id_prefixes=list(prefixes)
    print('loading node attributes')
    for (biolink_class, attributes) in meta_node_attributes().items():
        if biolink_class in nodes:
            nodes[biolink_class].attributes=list(attributes.values())
    return nodes


def edges():
    print('loading edge counts')
    edges = get_edge_counts()
    print('loading edge attributes')
    for (predicate, attributes) in meta_edge_attributes().items():
        if predicate in edges:
            edges[predicate].attributes=list(attributes.values())
    return  [edges[key] for key in sorted(edges.keys())] 


def read_info_template(definition_file):
    with open(definition_file,'r') as f:
        return TransformerInfo.from_dict(json.loads(f.read()))


def main():
    # extract knowledge map from the database and upate transformer_info files
    node_info = nodes()
    info = read_info_template('info/moleprodb_producer_info.json')
    info.knowledge_map.nodes = node_info
    with open('data/moleprodb_producer_info.json', 'w') as json_file:
        json.dump(info, json_file, cls=JSONEncoder, indent=4, separators=(',', ': '))

    info = read_info_template('info/moleprodb_name_producer_info.json')
    info.knowledge_map.nodes = node_info
    with open('data/moleprodb_name_producer_info.json', 'w') as json_file:
        json.dump(info, json_file, cls=JSONEncoder, indent=4, separators=(',', ': '))

    info = read_info_template('info/moleprodb_transformer_info.json')
    info.knowledge_map.nodes = node_info
    info.knowledge_map.edges = edges()
    with open('data/moleprodb_transformer_info.json', 'w') as json_file:
        json.dump(info, json_file, cls=JSONEncoder, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
