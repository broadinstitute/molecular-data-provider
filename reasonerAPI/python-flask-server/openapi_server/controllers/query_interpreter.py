from contextlib import closing
import time
import datetime
import copy
import os
import yaml

from openapi_server.models.query import Query
from openapi_server.models.message import Message
from openapi_server.models.attribute import Attribute
from openapi_server.models.log_entry import LogEntry
from openapi_server.models.log_level import LogLevel
from openapi_server.models.response import Response

from openapi_server.controllers.knowledge_map import knowledge_map
from openapi_server.controllers.molepro import MolePro
from openapi_server.controllers.molepro_edge import MoleproEdgeModel
from openapi_server.controllers.biolink_utils import BiolinkAncestrySingleton

from openapi_server.utils.query_utils import reverse_query, reverse_response, filter_by_object_id
from openapi_server.controllers.utils import translate_type
from openapi_server.controllers.utils import translate_curie
from openapi_server.controllers.utils import node_attributes, edge_attributes, hidden_attributes
from openapi_server.controllers.utils import get_logger
from openapi_server.utils.node_ancestry_utils import get_ancestry_map


# environment variables
MOLEPRO_QUERY_LIMIT = os.environ.get('MOLEPRO_QUERY_LIMIT')
limit_query_curie_size = 500
if MOLEPRO_QUERY_LIMIT:
    limit_query_curie_size = int(MOLEPRO_QUERY_LIMIT)
logger = get_logger("query_interpreter")
logger.info("Using query curie limit of: {}".format(limit_query_curie_size))

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

# print("biolink: {}".format(self.version_biolink))
# print("trapi: {}".format(self.version_trapi))

def execute_query(query: Query, debug = False):
    if query.workflow is None:
        if debug:
            print("No workflow")
        logger.info('Received no workflow query from {}'.format(query.submitter))
        return execute_lookup(query.message, query.submitter)
    if isinstance(query.workflow, list):
        # verify workflow
        supported_opperations = {'lookup', 'annotate_nodes'}
        for operation in query.workflow:
            operation_id = operation.get('id')
            if operation_id is None:
                return ({"status": 400, "title": "Bad Request", "detail": "No operation id", "type": "about:blank" }, 400)
            if operation_id not in supported_opperations:
                return ({"status": 400, "title": "Bad Request", "detail": "unsupported operation "+str(operation_id), "type": "about:blank" }, 400)

        # execute workflow
        message = query.message
        logs = []
        workflow = []
        for operation in query.workflow:
            operation_id = operation.get('id')
            if debug:
                print('Executing operation_id: ',operation_id)
            if operation_id == 'lookup':
                logger.info('Received lookup query from {}'.format(query.submitter))
                response = execute_lookup(message, query.submitter)
                message = response.message
                workflow.append(operation)
                if response.logs is not None:
                    logs.extend(response.logs)
            if operation_id == 'annotate_nodes':
                logger.info('Received annotate_nodes query from {}'.format(query.submitter))
                response = execute_annotate_nodes(operation, message, query.submitter)
                message = response.message
                workflow.append(operation)
                if response.logs is not None:
                    logs.extend(response.logs)
                
        return Response(message=message, logs=logs, workflow=workflow, schema_version=VERSION_TRAPI, biolink_version=VERSION_BIOLINK)
    else:
        return ({"status": 400, "title": "Bad Request", "detail": "Wrong workflow format", "type": "about:blank" }, 400)



def execute_lookup(message: Message, submitter, debug=False):
    start = time.time()
    query_graph = message.query_graph

    # check on the size limit
    query_nodes = query_graph.nodes
    id_count = -1
    if query_nodes:
        for key, node in query_nodes.items():
            if node.ids:
                id_count = max(id_count, len(node.ids))
                
    log_msg = "Got {} nodes with {} ids from {}".format(len(query_nodes), id_count, submitter)
    logger.info(log_msg)
    
    if id_count > limit_query_curie_size:
        return ({"status": 413, "title": "Query payload too large", "detail": "Query payload too large, exceeds the {} curie list size".format(limit_query_curie_size), "type": "about:blank" }, 413)
 

    if len(query_graph.edges) == 0:
        return ({"status": 400, "title": "Bad Request", "detail": "No edges", "type": "about:blank" }, 400)
    if len(query_graph.edges) > 1:
        return ({"status": 501, "title": "Not Implemented", "detail": "Multi-edges queries not yet implemented", "type": "about:blank" }, 501)

    # see if the query needs to be flipped
    original_query_graph = copy.deepcopy(query_graph)
    is_flipped, flipped_query_graph = reverse_query(query_graph)
    if is_flipped:
        query_graph = flipped_query_graph
        if debug:
            print("Flipped query graph")

    # expand the ancestry for the nodes
    query_graph, map_original_query_id = expand_ancestry_node_ids(query_graph, debug=debug)
    # print("got original query id map: {}".format(map_original_query_id))

    # call molepro
    molepro = MolePro(query_graph)
    molepro.logs.append(LogEntry(datetime.datetime.now(), LogLevel.INFO, LogLevel.INFO, log_msg))

    # returned edge is: {'id':edge_id, 'source':source, 'type':predicate, 'target':target}
    # edge, transformer_chain_list = knowledge_map.match_query_graph(query_graph)
    mole_edge_list = knowledge_map.match_query_graph(query_graph)

    if debug:
        print("egde: {}".format(mole_edge_list))

    # get results from MolePro DB
    query_molepro_db(molepro, query_graph, map_original_query_id)

    # for each predicate, run a query
    for mole_edge in mole_edge_list:
        for item in mole_edge.transformer_chain_list:
            molepro.execute_transformer_chain(mole_edge, item['transformer_chain'], map_original_query_id)

    # get the results
    response = molepro.get_results()
    # print("results of size: {}".format(response.message.knowledge_graph.edges))

    # if need to flip, then do so
    if is_flipped:
        response = reverse_response(response, original_query_graph)
    else:
        # run the response through the object filter
        response = filter_by_object_id(response, original_query_graph)

    # return
    log_msg = 'Returning {} edges to {} in {} s'.format(
        len(response.message.knowledge_graph.edges), submitter,  int(time.time() - start))
    logger.info(log_msg)
    response.logs.append(LogEntry(datetime.datetime.now(), LogLevel.INFO, LogLevel.INFO, log_msg))
    return response


def expand_ancestry_node_ids(query_graph, debug=False):
    ''' 
    expands the IDs given based on ancestry and return the modified query graph along with the ancestry origin
    '''
    # log
    if debug:
        logger.info("translating query graph: {}".format(query_graph))

    # keep track of reverse translation of ids
    map_query_id = {}

    # modify the queries
    query_nodes = query_graph.nodes
    if query_nodes:
        for key, node in query_nodes.items():
            if node.ids:

                # get the ancestry map
                map_ancestry = get_ancestry_map(node.ids, debug=debug)

                # concatenate all the results
                list_updated_ids = node.ids
                for key, list_item in map_ancestry.items():
                    list_updated_ids = list_updated_ids + list_item
                    for row in list_item:
                        map_query_id[row] = key
                
                # make sure list is unique
                list_updated_ids = list(set(list_updated_ids))

                # log
                if debug:
                    logger.info("translated IDs: {} to ancestry IDs: {}".format(node.ids, list_updated_ids))

                # update query graph
                node.ids = list_updated_ids

    # log
    if debug:
        logger.info("returning query graph: {}".format(query_graph))
        logger.info("returning map query id: {}".format(map_query_id))

    # return
    return query_graph, map_query_id

def query_molepro_db(molepro, query_graph, map_original_query_id, debug = False):

    biolink_object = BiolinkAncestrySingleton.getInstance({})
    ancestor_map = biolink_object.ancestry_map

    # get the edge and nodes
    for key, value in query_graph.edges.items():
        edge = value
        edge_id = key
    nodes = query_graph.nodes
    source = nodes[edge.subject]
    target = nodes[edge.object]
    source_type = source.categories[0] if source.categories is not None and len(source.categories) > 0 else 'biolink:NamedThing'
    qualifier_constraints = edge.qualifier_constraints

    subject_ids = source.ids
    if debug:
        print('subject_ids = ',subject_ids)
    if subject_ids is None:
        logger.warn('No source ids')
        return

    transformer_controls = []
    predicates = edge.predicates
    if debug:
        print('predicates = ', predicates)
    if predicates is not None:
        moleprodb_predicates = [edge['predicate'] for edge in knowledge_map.moleprodb_knowledge_map.get('edges',[])]
        if debug:
            print(str(len(moleprodb_predicates)) + ' moleprodb_predicates' )
        children = set(predicates)
        for predicate in predicates:
            if predicate in ancestor_map:
                children.update(ancestor_map.get(predicate))
        for predicate in moleprodb_predicates:
            if translate_type(predicate, False) in children:
                transformer_controls.append({'name':'predicate', 'value': predicate})
        if len(transformer_controls) == 0:
            for predicate in predicates:
                transformer_controls.append({'name':'predicate', 'value': predicate})

    object_classes = target.categories
    if debug:
        print('object_classes = ', object_classes)
    if object_classes is not None:
        moleprodb_classes = [node_id for node_id, node in knowledge_map.moleprodb_knowledge_map.get('nodes',{}).items()]
        if debug:
            print('moleprodb_classes = ', moleprodb_classes)
        children = set()
        for object_class in object_classes:
            if object_class in ancestor_map:
                children.update(ancestor_map.get(object_class))
        for object_class in moleprodb_classes:
            if translate_type(object_class, False) in children:
                transformer_controls.append({'name':'biolink_class', 'value': object_class})
        for object_class in target.categories:
            transformer_controls.append({'name':'biolink_class', 'value': object_class})

    object_ids = target.ids
    if debug:
        print('object_ids = ', object_ids)
    if object_ids is not None:
        for object_id in object_ids:
            transformer_controls.append({'name':'id', 'value': object_id})

    # restrict names and attributes 
    transformer_controls.append({'name':'name_source', 'value': 'MolePro'})
    for attribute in node_attributes():
        transformer_controls.append({'name':'element_attribute', 'value': attribute})
    for attribute in edge_attributes():
        transformer_controls.append({'name':'connection_attribute', 'value': attribute})
    for attribute in hidden_attributes():
        transformer_controls.append({'name':'connection_attribute', 'value': attribute})

    qualifier_control_sets = []
    if qualifier_constraints is None or len(qualifier_constraints) == 0:
        qualifier_control_sets.append([])
    else:
        for qualifier_set in qualifier_constraints:
            qualifier_control = []
            for qualifier_constraint in qualifier_set.qualifier_set:
                constraint = qualifier_constraint.qualifier_type_id + '==' + qualifier_constraint.qualifier_value
                qualifier_control.append({'name':'qualifier_constraint', 'value': constraint})
            qualifier_control_sets.append(qualifier_control)

    if debug:
        print(transformer_controls)
        print(qualifier_control_sets)
    
    for qualifier_control_set in qualifier_control_sets:
        controls = [{'name':'limit', 'value': '1000'}]
        controls.extend(transformer_controls)
        controls.extend(qualifier_control_set)
        producer = {'name': MoleProDB_node_producer, 'controls': [{'name': 'id', 'value': '#subject'}]}
        transformer = {'name': 'MoleProDB connections transformer', 'controls': controls}
        transformer_list = [producer, transformer]

        for subject_id in subject_ids:
            molepro_edge = MoleproEdgeModel(
                edge_key= edge_id, 
                source_key= source.node_id, 
                target_key= target.node_id, 
                source_id= subject_id,
                target_id= None, # target ids specified in transformer_controls
                edge_type= None, # edge type (predicate) specified in transformer_controls
                source_type= source_type, 
                target_type= None, # target type specified in transformer_controls
                target_constraints= target.constraints, 
                edge_constraints= edge.attribute_constraints, 
                transformer_chain_list= transformer_list)
            if debug:
                print(molepro_edge)
            molepro.execute_transformer_chain(molepro_edge, transformer_list, map_original_query_id)


MoleProDB_node_producer = 'MoleProDB node producer'


def execute_annotate_nodes(operation, message: Message, submitter, debug = False):
    if debug:
        print(operation)
    attribute_types = None
    if 'parameters' in operation:
        attribute_types = operation.get('parameters').get('attributes')
    knowledge_graph = message.knowledge_graph
    if knowledge_graph is None:
        ({"status": 400, "title": "Bad Request", "detail": "No knowledge graph to annotate", "type": "about:blank" }, 400)
    molepro = MolePro(message.query_graph)
    molepro.knowledge_graph = knowledge_graph
    molepro.results = message.results
    transformer_controls = []
    if knowledge_graph is None or knowledge_graph.nodes is None:
        if debug:
            print('WARN: No nodes in knowledge graph')
        return molepro.get_results()
    query_ids = {}
    for (node_id, node) in knowledge_graph.nodes.items():
        if debug:
            print(node_id)
        query_id = translate_curie(node_id, 'biolink:SmallMolecule')
        transformer_controls.append({'name':'id', 'value':query_id})
        query_ids[query_id] = node_id
    transformer= {'name':MoleProDB_node_producer, 'controls': transformer_controls}
    collection_info = molepro.execute_transformer(None,transformer,None)
    collection = molepro.getCollection(collection_info, cache='no')
    for element in collection['elements']:
        if debug:
            print(element['id'],'/',element['biolink_class'],'=>',len(element['attributes']), 'attributes')
        query_node_id = None
        for attribute in element['attributes']:
            if attribute['original_attribute_name'] == 'query name' and attribute['provided_by'] == MoleProDB_node_producer:
                if debug:
                    print(attribute)
                query_node_id = query_ids.get(attribute['value'])
        if query_node_id == None:
            logger.warn('WARNING: No query id received from MoleProDB node producer for '+element['id'])
        else:
            add_attributes(query_node_id, knowledge_graph.nodes.get(query_node_id), element, attribute_types)
    logger.info('Annotated {} nodes for {}'.format(len(knowledge_graph.nodes), submitter))
    return molepro.get_results()


def add_attributes(query_element_id, node, element, attribute_types):
    if node is None:
        logger.warn('WARNING: No node matches query id from MoleProDB node producer: '+query_element_id)
    node_attributes = {attr_key(attribute):attribute for attribute in node.attributes} if node.attributes else {}
    for attribute in element['attributes']:
        if attr_key(Attribute.from_dict(attribute)) not in node_attributes:
            if 'attribute_type_id' in attribute and attribute.get('attribute_type_id') is not None and attribute.get('attribute_type_id') != '':
                if attribute_types is None or attribute.get('attribute_type_id') in attribute_types:
                    if attribute.get('value') is not None and attribute.get('value') != '':
                        if node.attributes is None:
                            node.attributes = []
                        node.attributes.append(Attribute.from_dict(attribute))


def attr_key(attribute):
    return (attribute.attribute_source, attribute.attribute_type_id, str(attribute.value))
