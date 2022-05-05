
# imports
import os
import requests
from openapi_server.controllers.utils import get_logger

# logger
logger = get_logger("node_ancestry_utils")

# environment variables
MOLEPRO_BASE_URL = os.environ.get('MOLEPRO_BASE_URL')

BASE_URL = 'https://translator.broadinstitute.org/molecular_data_provider'
if MOLEPRO_BASE_URL:
    BASE_URL = MOLEPRO_BASE_URL
logger.info("using molepro base URL: {}".format(BASE_URL))

# constants
MOLEPRO_URL_NODE_ANCESTRY = "{}/transform".format(BASE_URL)
ANCESTRY_PREFIX = ['MONDO', 'EFO', 'NCIT']

# MAIN METHOD
def get_ancestry_map(list_ids, debug=False):
    '''
    get the ancestry map from molepro given an input list
    key is an item in the list
    value is the list of ancestors/translated IDs
    '''
    # get the ancestry map
    ancestry_map = get_ancestry_map_with_url(MOLEPRO_URL_NODE_ANCESTRY ,list_ids, debug)

    # return
    return ancestry_map



# CHILDREN METHODS
def get_ancestry_map_with_url(query_url, list_ids, debug=False):
    '''
    get the ancestry map from molepro given an input list
    key is an item in the list
    value is the list of ancestors/translated IDs
    '''
    # make sure IDs are unique
    list_ids = list(set(list_ids))

    # split based on prefix of ID
    list_temp = []
    map_skipped = {}
    map_ancestry = {}
    for item in list_ids:
        if item.split(":")[0] in ANCESTRY_PREFIX:
            list_temp.append(item)
        else:
            map_skipped[item] = [item]

    # log
    if debug:
        print("got skipped map: {}".format(map_skipped))

    if len(list_temp) > 0:
        # get the collection id
        collection_id = get_node_producer_collection_id(query_url, list_temp, debug)

        # get the query get url
        get_url = get_node_ancestry_url(query_url, collection_id, debug)

        # get the ancestry map
        map_ancestry = get_node_ancestry_from_url(get_url, debug)

    # log
    if debug:
        print("got skipped map: {}".format(map_skipped))
        print("got searched map: {}".format(map_ancestry))

    # combine the skipped items with the searched items
    if len(map_skipped) > 0:
        if debug:
            print("merging maps")
        map_ancestry = dict(map_ancestry, **map_skipped)
        
    # log
    if debug:
        print("got result map: {}".format(map_ancestry))

    # return
    return map_ancestry


def make_node_producer_payload(list_ids, debug=False):
    '''
    method to make a payload for the node producer translator post call
    '''
    # build the control list
    list_control = []
    for id in list_ids:
        list_control.append({'name': 'id', 'value': id})

    # build the map
    result = {'name': 'MoleProDB node producer', 'controls': list_control}

    # log
    if debug:
        print("got payload: {}".format(result))

    # return
    return result

def get_node_producer_collection_id(query_url, list_ids, debug=False):
    '''
    method tto call the node producer transformer with the proper payload
    '''
    # create the payload
    query_map = make_node_producer_payload(list_ids, debug)

    # call the REST POST call and get the response
    response = requests.post(query_url, json=query_map).json()

    # log
    if debug:
        print("got node producer results: \n{}".format(response))

    # parse the results
    result_id = response.get('id')

    # return
    return result_id

def get_node_ancestry_url(query_url, collection_id, debug=False):
    '''
    method to call the molepro hierarchy with the given collection id
    '''
    # make the payload
    controls_list = [{'name': 'name_source', 'value': 'MolePro'}, {'name': 'element_attribute', 'value': 'biolink:publication'}]
    query_map = {'name': 'MoleProDB hierarchy transformer', 'collection_id': collection_id, 'controls': controls_list}

    # call the REST POST
    response = requests.post(query_url, json=query_map).json()

    # get the result
    result_url = response.get('url')

    # log
    if debug:
        print("got hierarchy url: {}".format(result_url))

    # return
    return result_url

def get_node_ancestry_from_url(query_url, debug=False):
    '''
    method to call the collection specific url and pull out the ancestry nodes
    '''
    # initialize
    result_map = {}

    # call the REST GET endpoint
    response = requests.get(query_url).json()

    # loop and pull out results
    elements_list = response.get('elements')
    if elements_list:
        for element in elements_list:
            # get the child id
            child_id = element.get('id')

            # loop through the connections
            connections = element.get('connections')
            if connections:
                for connection in connections:
                    parent_id = connection.get('source_element_id')

                    # add to the result map
                    if not result_map.get(parent_id):
                        result_map[parent_id] = []
                    result_map.get(parent_id).append(child_id)
                    

    # log
    if debug:
        print("got ancestry result map: {}".format(result_map))

    #return
    return result_map

