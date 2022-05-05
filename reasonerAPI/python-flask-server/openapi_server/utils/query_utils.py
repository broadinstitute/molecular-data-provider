# imports
import copy
import json
from openapi_server.models.query_graph import QueryGraph
from openapi_server.models.knowledge_graph import KnowledgeGraph
from openapi_server.models.response import Response

# constants
MESSAGE = "message"
KNOWLEDGE_GRAPH = "knowledge_graph"
QUERY_GRAPH = "query_graph"
EDGES = "edges"
SUBJECT = "subject"
OBJECT = "object"
PREDICATES = "predicates"
NODES = "nodes"
IDS = "ids"
CATEGORIES = "categories"

# read the biolink predicate inverse file
map_predicate = {}
with open('conf/biolinkPredicateInverse.json') as json_file:
    # read the map
    map_inverse = json.load(json_file)
    for key, value in map_inverse.items():
        map_predicate[key] = value
        map_predicate[value] = key
    print("start with predicate {} inverses".format(len(map_predicate)))

# methods
def reverse_response(response: Response, query_graph: QueryGraph, debug=False):
    ''' will reverse the response data, flipping the subject/object and the predicates '''
    ''' also replace the query graph with the one provided '''
    # initialize
    flipped_response = copy.deepcopy(response)

    # get the data
    edges = response.message.knowledge_graph.edges

    # loop through the edges and replace the object/subjects and predicates
    for r_edge_id, r_edge_value in edges.items():
        flipped_response.message.knowledge_graph.edges.get(r_edge_id).object = response.message.knowledge_graph.edges.get(r_edge_id).subject
        flipped_response.message.knowledge_graph.edges.get(r_edge_id).subject = response.message.knowledge_graph.edges.get(r_edge_id).object

        # flip the predicate
        if map_predicate.get(response.message.knowledge_graph.edges.get(r_edge_id).predicate):
            flipped_response.message.knowledge_graph.edges.get(r_edge_id).predicate = map_predicate.get(response.message.knowledge_graph.edges.get(r_edge_id).predicate)

    # replace the query graph
    flipped_response.message.query_graph = query_graph

    # return
    return flipped_response


def reverse_query(query_graph: QueryGraph, debug=False):
    ''' will check to see if query has id on object id only, then flips it if applicable; do nothing if not '''
    ''' will return whether flip was necessary and the flipped query if applicable '''
    # initialize
    flipped_query = None
    is_flipped = False
    edge_id = None

    # get the data
    if len(query_graph.edges) == 1:
        if debug:
            print("got query: \n{}".format(query_graph))

        # get the edge and nodes
        for key, value in query_graph.edges.items():
            edge = value
            edge_id = key
        nodes = query_graph.nodes

        # log
        if debug:
            print("subject: {}, object: {} predicates: {}".format(edge.subject, edge.object, edge.predicates))

        # test if id on object only
        if edge.object and edge.subject:
            if debug:
                print("subject: {}".format(nodes.get(edge.subject)))
            if nodes.get(edge.object).ids and (not nodes.get(edge.subject).ids or (len(nodes.get(edge.subject).ids) < 1 and len(nodes.get(edge.object).ids) > 0)):
                # copy and flip
                is_flipped = True

                # functional programming: copy object, do not modify original
                flipped_query = copy.deepcopy(query_graph)

                # flip object/subject
                flipped_query.edges.get(edge_id).object = query_graph.edges.get(edge_id).subject
                flipped_query.edges.get(edge_id).subject = query_graph.edges.get(edge_id).object

                # log
                if debug:
                    print("flipped query graph result: \n{}".format(flipped_query))

                # flip predicates
                list_predicates_reverse = flip_predicates(edge.predicates, debug=debug)
                flipped_query.edges.get(edge_id).predicates = list_predicates_reverse
                                    
    # return orginal and result
    return is_flipped, flipped_query

def flip_predicates(list_predicates, debug=False):
    ''' will flip the predicates in the list '''
    # initialize
    list_predicates_reverse = []

    # FIX - https://github.com/broadinstitute/scb-kp-dev/issues/141
    # if null predicates 
    if not list_predicates or len(list_predicates) < 1:
        list_predicates_reverse = ['all']
    else:
        # loop therough the predicates
        for item in list_predicates:
            reversed_predicate = map_predicate.get(item)
            # if no reverse predicate found, then simply add in current predicate
            if not reversed_predicate:
                reversed_predicate = item
            list_predicates_reverse.append(reversed_predicate)

    # return 
    return list_predicates_reverse


def filter_by_object_id(response: Response, query_graph: QueryGraph, debug=False):
    ''' if the query contains both subject and object ids, will filter the response of the object ids that were not requested '''
    ''' this is to deal with the transformers being unable to accept specified object id, hence the post processing filtering '''
    # initialize
    result_response = response
    edge_id = None
    subject_nodes_id_to_keep = set()
    object_nodes_id_to_keep = set()

    # get the data
    if len(query_graph.edges) == 1:
        if debug:
            print("got query: \n{}".format(query_graph))

        # get the edge and nodes
        for key, value in query_graph.edges.items():
            edge = value
            edge_id = key
        nodes = query_graph.nodes

        # log
        if debug:
            print("subject: {}, object: {} predicates: {}".format(edge.subject, edge.object, edge.predicates))

        # test that edge has both subject and object
        if edge.object and edge.subject:
            # check if both subject and object specified
            if nodes.get(edge.object).ids and nodes.get(edge.subject).ids and len(nodes.get(edge.subject).ids) > 0 and len(nodes.get(edge.object).ids) > 0:
                if debug:
                    print("filtering response for object ids: {}".format(nodes.get(edge.object).ids))

                # collect node ids to keep
                subject_nodes_id_to_keep = set(nodes.get(edge.subject).ids)
                object_nodes_id_to_keep = set(nodes.get(edge.object).ids)

                # copy response
                result_response = copy.deepcopy(response)

                # loop through edges, keep only specified ones
                new_edges = {}
                for key, value in response.message.knowledge_graph.edges.items():
                    if value.subject in subject_nodes_id_to_keep and value.object in object_nodes_id_to_keep:
                        new_edges[key] = value
                result_response.message.knowledge_graph.edges = new_edges

                # loop through the nodes, keep only specified ones
                new_nodes = {}
                for key, value in response.message.knowledge_graph.nodes.items():
                    if key in subject_nodes_id_to_keep or key in object_nodes_id_to_keep:
                        new_nodes[key] = value
                result_response.message.knowledge_graph.nodes = new_nodes

                # loop through edge and node bindings
                new_results = []
                for res in response.message.results:
                    include_bindings = True
                    for key, value in res.edge_bindings.items():
                        for list_item in value:
                            if list_item.id not in new_edges:
                                include_bindings = False
                    
                    # only include result bindings if all nodes were in the result
                    if include_bindings:
                        new_results.append(res)
                    
                # assign new result bindings
                result_response.message.results = new_results

    # return
    return result_response