import requests
from molepro.openapi_server.classes.collection_info import CollectionInfo
from molepro.openapi_server.classes.collection import Collection
from molepro.openapi_server.classes.error_msg import ErrorMsg

base_url = 'https://molepro.broadinstitute.org/molecular_data_provider'


def set_base_url(url):
    global base_url
    base_url = url
    print("[MolePro] using base_url = "+str(base_url))


def transform(transformer, collection_id, controls, cache='yes'):
    query = {
        "name": transformer,
        "collection_id": collection_id,
        "controls": controls
    }
    url = base_url + '/transform'
    if cache == 'no':
        url = url + '?cache=no'
    response = requests.post(url, json = query) 
    collection_info =  CollectionInfo.from_dict(response.json())
    if response.status_code == 200:
        print("[MolePro] "+transformer+": "+str(collection_info.size))
    else:
        message = ErrorMsg().from_dict(response.json())
        print("[ERROR] "+transformer+": "+str(response.status_code)+" "+str(message.title))
        print("  "+str(message.detail))
        print("  query = "+str(query))
    return collection_info


def aggregate(operation, collection_ids, cache='yes'):
    collection_ids = [id for id in collection_ids if id is not None]
    query = {
        "operation": operation,
        "collection_ids": collection_ids,
        "controls": []
    }
    url = base_url + '/aggregate'
    if cache == 'no':
        url = url + '?cache=no'
    response = requests.post(url, json = query) 
    collection_info =  CollectionInfo.from_dict(response.json())
    if response.status_code == 200:
        print("[MolePro] "+operation+": "+str(collection_info.size))
    else:
        message = ErrorMsg().from_dict(response.json())
        print("[ERROR] "+operation+": "+str(response.status_code)+" "+str(message.title))
        print("  "+str(message.detail))
        print("  query = "+str(query))
    return collection_info


def elements(collection_info, cache='yes'):
    collection_id = collection_info.id
    url = base_url + '/collection/'+collection_id
    if cache == 'no':
        url = url + '?cache=no'
    response = requests.get(url)
    if response.status_code == 200:
        collection = Collection.from_dict(response.json())
    else:
        message = ErrorMsg().from_dict(response.json())
        print("[ERROR] elements: "+str(response.status_code)+" "+str(message.title))
        print("  "+str(message.detail))
        print("  collection_id = "+str(collection_id))
    return collection.elements
