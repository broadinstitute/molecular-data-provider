
# imports
import json
import requests 
from contextlib import closing
import os
import yaml

from openapi_server.controllers.utils import get_logger

# environment variables
MOLEPRO_URL_BIOLINK = os.environ.get('MOLEPRO_URL_BIOLINK')

# constants
file_prepend = "/Users/mduby"
file_prepend = "/home/javaprog"
file_molepro = file_prepend + '/Data/Broad/Translator/Molepro/biolinkAncestry.json'
file_genepro = file_prepend + '/Data/Broad/Translator/Genepro/biolinkAncestry.json'
file_query = file_prepend + '/Data/Broad/Translator/Client/afibGeneRelated.json'
file_chem_query = file_prepend + '/Data/Broad/Translator/Client/chemGeneRelated.json'
file_blank_query = file_prepend + '/Data/Broad/Translator/Client/blankGeneRelated.json'

# url constants
url_node_normalizer = "https://bl-lookup-sri.renci.org/bl/{}/ancestors?version={}"
if MOLEPRO_URL_BIOLINK:
    url_node_normalizer = MOLEPRO_URL_BIOLINK + "/bl/{}/ancestors?version={}"
# url_molepro_predicates = 'https://translator.broadinstitute.org/molepro/trapi/v1.0/predicates'


# read trapi and biolink versions
logger = get_logger("biolink_utils")
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

def get_biolink_version():
    return VERSION_BIOLINK

def get_trapi_version():
    return VERSION_TRAPI

# singleton class to keep translations in memory, avoid repeated file reading
# see https://www.geeksforgeeks.org/singleton-method-python-design-patterns/
class BiolinkAncestrySingleton:
  
    __shared_instance = 'biolink_ancestry'
  
    @staticmethod
    def getInstance(predicate_map):
        """Static Access Method"""
        if BiolinkAncestrySingleton.__shared_instance == 'biolink_ancestry':
            BiolinkAncestrySingleton(predicate_map)
        return BiolinkAncestrySingleton.__shared_instance
  
    def __init__(self, predicate_map):
        """virtual private constructor"""
        if BiolinkAncestrySingleton.__shared_instance != 'biolink_ancestry':
            raise Exception ("This BiolinkAncestrySingleton class is a singleton class !")
        else:
            print("reading BiolinkAncestrySingleton data")
            # read the biolink translations file
            with open('conf/biolinkAncestry.json') as json_file:
                # read the map
                self.ancestry_map = json.load(json_file)
            self.predicate_map = predicate_map

            # set the object
            BiolinkAncestrySingleton.__shared_instance = self


def get_biolink_ancestors(entity_name, api_version='latest'):
    ''' retrieve the ancestors of a entity type '''
    ancestors = []

    # build the url
    query_url = url_node_normalizer.format(entity_name, api_version)

    # query the url
    print("finding ancestors for {}".format(entity_name))
    with closing(requests.get(query_url)) as response_obj:
        if response_obj is not None and response_obj.status_code != 404:
            ancestors = response_obj.json()

    # return list
    return ancestors

def get_entities_from_predicates(predicate_url):
    ''' returns a list of objects defined in a predicate (entities, categories, predicates) '''
    entity_set = set()
    response = None

    # query the url
    with closing(requests.get(predicate_url)) as response_obj:
        response = response_obj.json()

    if response is not None:
        # get all the types
        key_list = list(response.keys())
        entity_set.update(key_list)

        # get all the categories
        for item in key_list:
            category_list = list(response.get(item).keys())
            entity_set.update(category_list)

            # get all the predicates
            for category in category_list:
                entity_set.update(response.get(item).get(category))

    # rerturn
    return list(entity_set)

def build_ancestry_map(predicate_url):
    ''' build a map of biolink terms to predicate term list based on predicate url '''
    ancestry_map = {"all": []}

    # get the entities
    type_list = get_entities_from_predicates(predicate_url)

    # add all entities as child of 'all'
    for item in type_list:
        ancestry_map.get('all').append(item)

    # for each entity, get their ancestors
    for item in type_list:
        # add itself to the map
        if ancestry_map.get(item) is None:
            ancestry_map[item] = []
        ancestry_map.get(item).append(item)
        
        item_ancestry_list = get_biolink_ancestors(item)

        for ancestor in item_ancestry_list:
            # add them to each ancestors list
            if ancestry_map.get(ancestor) is None:
                ancestry_map[ancestor] = []
            ancestry_map.get(ancestor).append(item)

    # return
    return ancestry_map

def create_query_string(subject_type=None, object_type=None, predicate=None):
    ''' creates representative string from query objects '''
    query = ""

    for item in [subject_type, predicate, object_type]:
        # print("adding {}".format(item))
        if item is None:
            query += "all "
        else:
            query += item + " "

    # return
    return query    

def create_predicate_query_list(predicate_json):
    ''' create a list query strings of all accepted queries for the given predicate '''
    query_list = []

    # go through json and build all possible queries
    if predicate_json is not None:
        # get all the subject categories
        subject_category_list = list(predicate_json.keys())

        # get all the object categories
        for subject_category in subject_category_list:
            object_category_list = list(predicate_json.get(subject_category).keys())

            # get all the predicates
            for object_category in object_category_list:
                for predicate in predicate_json.get(subject_category).get(object_category):
                    query_list.append(create_query_string(subject_category, object_category, predicate))

    # return
    return query_list

def build_query_descendant_list(descendant_map, subject_type, object_type, predicate):
    ''' returns all the possible descendant queries in string format '''
    query_list = []

    # check the inputs
    if subject_type is None or len(subject_type) < 1:
        subject_type = ['all']
    if object_type is None or len(object_type) < 1:
        object_type = ['all']
    if predicate is None or len(predicate) < 1:
        predicate = ['all']
    
    # make arrays
    subject_type = make_into_array(subject_type)
    object_type = make_into_array(object_type)
    predicate = make_into_array(predicate)

    # loop
    for sub in subject_type:
        if descendant_map.get(sub):
            for dsub in descendant_map.get(sub):
                for pred in predicate:
                    if descendant_map.get(pred):
                        for dpred in descendant_map.get(pred):
                            for obj in object_type:
                                if descendant_map.get(obj):
                                    for dobj in descendant_map.get(obj):
                                        query_list.append(create_query_string(dsub, dobj, dpred))

    # return
    return query_list

def get_query_parts(query_json):
    ''' returns subject/object/predicate of the json query '''
    sub = ['all']
    obj = ['all']
    pred = ['all']
    subject_key = None
    object_key = None

    # get the objects
    qg = query_json.get('message').get('query_graph')
    # print("got {}".format(qg))
    if len(qg.get('edges').keys()) > 0:
        for key in list(qg.get('edges').keys()):
            if qg.get('edges').get(key).get('predicate'):
                pred = qg.get('edges').get(key).get('predicate')
                subject_key = qg.get('edges').get(key).get('subject')
                object_key = qg.get('edges').get(key).get('object')
    if subject_key:
        if qg.get('nodes').get(subject_key).get('category'):
            sub = qg.get('nodes').get(subject_key).get('category')
    if object_key:
        if qg.get('nodes').get(object_key).get('category'):
            obj = qg.get('nodes').get(object_key).get('category')

    # return
    return sub, obj, pred 

def get_all_overlap_queries(ancestor_map, predicate_json, query_json):
    ''' returns the intersection of the predicates and expanded query list '''
    # get the parts of the query
    sub, obj, pred = get_query_parts(query_json)

    # get the intersection
    result = get_all_overap_queries_for_parts(ancestor_map, predicate_json, sub, obj, pred)

    # return
    return result

def get_overlap_queries_for_parts(subject_type, object_type, predicate, debug=False):
    ''' returns the intersection of the predicates and expanded query list '''
    query_list = []

    # get the ancestor map
    biolink_object = BiolinkAncestrySingleton.getInstance()
    ancestor_map = biolink_object.ancestry_map
    predicate_map = biolink_object.predicate_map

    # get the query list
    query_list = get_all_overap_queries_for_parts(ancestor_map, predicate_map, subject_type, object_type, predicate, debug)

    # return
    return query_list

def get_overlap_queries_for_parts_list(subject_type_list, object_type_list, predicate_list, predicates_map=None, debug=False):
    ''' returns the intersection of the predicates and biolink expanded query list '''
    query_list = []

    # get the ancestor map
    biolink_object = BiolinkAncestrySingleton.getInstance(predicates_map)
    ancestor_map = biolink_object.ancestry_map
    predicate_map = biolink_object.predicate_map

    # get the query list
    for subject_type in subject_type_list:
        for object_type in object_type_list:
            for predicate in predicate_list:
                query_list += get_all_overap_queries_for_parts(ancestor_map, predicate_map, subject_type, object_type, predicate, debug)

    # make a set to remove duplicates
    if debug:
        print("got list {}".format(query_list))
    query_set = set(query_list)

    # return
    return list(query_set)

def get_all_overap_queries_for_parts(ancestor_map, predicate_json, subject_type, object_type, predicate, debug=False):
    ''' returns the intersection of the predicates and expanded parts from query '''
    predicate_list =  create_predicate_query_list(predicate_json)
    # print("predicate {}".format(len(predicate_list)))
    query_list = build_query_descendant_list(ancestor_map, subject_type, object_type, predicate)

    # log
    if debug:
        print("predicate list:")
        for item in predicate_list:
            print("=== {}".format(item))
        print("ancestor list:")
        for item in query_list:
            print("=== {}".format(item))

    # get the intersection
    result = list(set(predicate_list) & set(query_list))
    if debug:
        print("overlap list:")
        for item in result:
            print("=== {}".format(item))

    # return
    return result

def make_into_array(temp):
    ''' turns input into array if not already '''
    result = temp

    # checks
    if temp is None:
        result = []
    if type(temp) != type([]):
         result = [temp]

    # return
    return result

if __name__ == "__main__":
    # get the gene ancestors
    gene_list = get_biolink_ancestors('Gene')
    for item in gene_list:
        print("got ancestor {}".format(item))



