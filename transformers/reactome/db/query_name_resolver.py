# 1. Collect all the cell component names in the reactome database
# 2. Query the Name Resolver for the CURIE and synonyms
#    e.g., https://name-lookup.transltr.io/lookup?string=peroxisome
# 3. In case there are no GO term found, the use 

import sqlite3
import requests
import json
import time

db_connection = sqlite3.connect("data/reactome.sqlite", check_same_thread=False)
db_connection.row_factory = sqlite3.Row
cell_component_set = set()
json_file = 'data/config/compartments.json'


###############################################################
# This class gets all the cell components into a python set.
###############################################################
class Cell_Components_Collector():
    def collect():
        #Cell_Components_Collector.collect_interaction_map()
        Cell_Components_Collector.collect_physical_entity()
        Cell_Components_Collector.collect_complex()
        return cell_component_set


    def collect_physical_entity():
        cursor = db_connection.cursor()
        cursor.execute('''SELECT DISTINCT compartment
                      FROM PHYSICAL_ENTITY''')
        for row in cursor.fetchall():
            cell_component_set.add(row['compartment'])

    def collect_complex():
        cursor = db_connection.cursor()
        cursor.execute('''SELECT DISTINCT compartment
                            FROM COMPLEX''')
        for row in cursor.fetchall():
            cell_component_set.add(row['compartment'])

###############################################################
# This class calls the Name Resolver to get JSON with name data.
###############################################################
class Name_Resolver_Caller():
    request_headers = {}
    def request_names(components_list):
        compartment_dict = {}
        request_headers = "application/json"
        print('********************************************')
        for component in components_list:
            if component is not None:
                api_url = "https://name-lookup.transltr.io/lookup?string=" + component
                response = requests.get(api_url, request_headers)
                try:
                    json_obj = json.loads(response.content.decode('utf-8')) #raise JSONDecodeError("Expecting value", s, err.value) from None
                    print(component, json_obj[0]['curie'] )
                except Exception as E:
                    print('#################')
                    print(response.content.decode('utf-8'))
                    while '403 Forbidden' in response.content.decode('utf-8') or '502 Bad Gateway' in response.content.decode('utf-8') or '504 Gateway Time-out' in response.content.decode('utf-8'):
                        time.sleep(30)
                        print('Waited 30 seconds', time.clock_gettime)
                        response = requests.get(api_url, request_headers)   #Try again in case of glitch in API
                json_obj = json.loads(response.content.decode('utf-8')) #raise JSONDecodeError("Expecting value", s, err.value) from None
                curie = None
                for compartment_detail in json_obj:
                    if 'GO:' in compartment_detail.get('curie'):
                        curie = compartment_detail.get('curie')
                        compartment_dict[component] = curie
                if curie == None:
                    compartment_dict[component] = search_ols4(component)

        #       Save as a JSON file
                with open(json_file, 'w') as outfile:
                    json.dump(compartment_dict, outfile, indent=4, sort_keys=True)             



#############################################################################
# If component's GO: term is not found in Name Lookup, the search in OLS 4
#############################################################################
def search_ols4(component):
    doc_list = None
    print('search')
    # "My name is {}, I'm {}".format("John",36)
    api_url = "https://www.ebi.ac.uk/ols4/api/search?q={}&obsoletes=false&local=false&rows=10&start=0&format=json&lang=en".format(component)
    request_headers = "application/json"
    response = requests.get(api_url, request_headers)
    try:
        json_obj = json.loads(response.content.decode('utf-8')) #raise JSONDecodeError("Expecting value", s, err.value) from None
        doc_list = json_obj['response']['docs']
    except Exception as E:
        print('#################')
        print(response.content.decode('utf-8'))
        while '403 Forbidden' in response.content.decode('utf-8') or '502 Bad Gateway' in response.content.decode('utf-8') or '504 Gateway Time-out' in response.content.decode('utf-8'):
            time.sleep(30)
            print('Waited 30 seconds', time.clock_gettime)
            response = requests.get(api_url, request_headers)   #Try again in case of glitch in API
        json_obj = json.loads(response.content.decode('utf-8')) #raise JSONDecodeError("Expecting value", s, err.value) from None
        doc_list = json_obj['response']['docs']

    for doc in doc_list:
        if 'GO:' in doc['obo_id']:
            print('OLS4', component, doc['obo_id'])
            return doc['obo_id']  # Found the GO: CURIE



###############################################################
# This class filters out all the dictionaries in the JSON file
# that have labels not matching the "compartment" name used to
# query the Name Resolver.
# e.g., cytosol vs. ""label": "Cytosol of endoplasm""
############################################################### 
class JSON_Filter():
    def interact_through_JSON():
        with open(json_file) as file:
            data = json.load(file)
        dict_of_keys = {}
        for key in data:
            key_list = list()
            if len(key) > 0:
                for element in data[key]:
                    if key.casefold() == element['label'].casefold():
                        key_list.append(element)
                dict_of_keys[key] = key_list      
#       Save as a JSON file
        with open('data/config/interaction_terms.json', 'w') as outfile:
            json.dump(dict_of_keys, outfile, indent=4, sort_keys=True)  


  


def main():
    components_set = Cell_Components_Collector.collect()
    Name_Resolver_Caller.request_names(list(components_set))
    #JSON_Filter.interact_through_JSON()

if __name__ == "__main__":
    main()
