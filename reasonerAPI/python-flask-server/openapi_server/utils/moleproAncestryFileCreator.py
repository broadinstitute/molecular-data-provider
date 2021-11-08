
# imports
import json
import requests 
from contextlib import closing
import logging
import sys 

# constants
logging.basicConfig(level=logging.INFO, format=f'[%(asctime)s] - %(levelname)s - %(name)s : %(message)s')
handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)

# constants
url_node_normalizer = "https://bl-lookup-sri.renci.org/bl/{}/ancestors?version={}"
url_molepro_meta_knowledge_graph = "http://translator.broadinstitute.org/molepro/trapi/v1.2/meta_knowledge_graph"
url_molepro_meta_knowledge_graph = "http://localhost:9220/molepro/trapi/v1.2/meta_knowledge_graph"
file_molepro = 'biolinkAncestry.json'
VERSION = "2.1.0"

def get_biolink_ancestors(entity_name, api_version=VERSION, log=False):
    ''' retrieve the ancestors of a entity type '''
    ancestors = []

    # build the url
    query_url = url_node_normalizer.format(entity_name, api_version)

    # query the url
    if log:
        logger.info("finding ancestors for {}".format(entity_name))
    with closing(requests.get(query_url)) as response_obj:
        if response_obj is not None and response_obj.status_code != 404:
            ancestors = response_obj.json()

    if log:
        print("for {}: got ancestors: {}".format(entity_name, ancestors))

    # return list
    return ancestors

def get_entities_from_knowledge_graph(kg_url, log=False):
    ''' returns a list of objects defined in a meta knowledgre graph (entities, categories, predicates) '''
    entity_set = set()
    response = None

    # query the url
    with closing(requests.get(kg_url)) as response_obj:
        response = response_obj.json()

    if response is not None and response.get('edges') is not None:
        for item in response.get('edges'):
            entity_set.add(item.get('object'))
            entity_set.add(item.get('subject'))
            entity_set.add(item.get('predicate'))

    if log:
        for item in entity_set:
            logger.info("got mtg entity: {}".format(item))

    # rerturn
    return list(entity_set)

def build_ancestry_map(predicate_url, log=False):
    ''' build a map of biolink terms to predicate term list based on predicate url '''
    ancestry_map = {"all": []}

    # get the entities
    type_list = get_entities_from_knowledge_graph(predicate_url, log=log)

    # add all entities as child of 'all'
    for item in type_list:
        ancestry_map.get('all').append(item)

    # for each entity, get their ancestors
    for item in type_list:
        # add itself to the map
        if ancestry_map.get(item) is None:
            ancestry_map[item] = []
        ancestry_map.get(item).append(item)
        
        item_ancestry_list = get_biolink_ancestors(item, log=log)

        for ancestor in item_ancestry_list:
            # add them to each ancestors list
            if ancestry_map.get(ancestor) is None:
                ancestry_map[ancestor] = []
            ancestry_map.get(ancestor).append(item)

    # return
    return ancestry_map


if __name__ == "__main__":
    # get the map of ancestors for molepro
    logger.info("testing ancestor map from predicate")
    ancestor_map = build_ancestry_map(url_molepro_meta_knowledge_graph, log=False)
    # sort ancestor maps
    for key in list(ancestor_map.keys()):
        ancestor_map.get(key).sort()
        logger.info("for ancestor {} got list {}".format(key, ancestor_map.get(key)))

    # write out to file
    file_to_write = file_molepro
    with open(file_to_write, 'w') as json_file:
        json.dump(ancestor_map, json_file, indent=4, separators=(',', ': '), sort_keys=True)

    # log
    logger.info("got ancestry map: \n{}".format(json.dumps(ancestor_map, indent=2, separators=(',', ': '))))
    logger.info("wrote out dict to file {}".format(file_to_write))




