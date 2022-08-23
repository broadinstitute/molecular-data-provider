import requests
from molepro.openapi_server.classes.collection_info import CollectionInfo
from molepro.openapi_server.classes.collection import Collection


def transform(transformer, collection_id, controls):
    query = {
        "name": transformer,
        "collection_id": collection_id,
        "controls": controls
    }
    url = 'https://translator.broadinstitute.org/molecular_data_provider/transform'
    response = requests.post(url, json = query) 
    collection_info =  CollectionInfo.from_dict(response.json())
    print("[MolePro] "+transformer+": "+str(collection_info.size))
    return collection_info


def aggregate(operation, collection_ids):
    collection_ids = [id for id in collection_ids if id is not None]
    query = {
        "operation": operation,
        "collection_ids": collection_ids,
        "controls": []
    }
    url = 'https://translator.broadinstitute.org/molecular_data_provider/aggregate'
    response = requests.post(url, json = query) 
    collection_info =  CollectionInfo.from_dict(response.json())
    print("[MolePro] "+operation+": "+str(collection_info.size))
    return collection_info


def elements(collection_info):
    collection_id = collection_info.id
    url = 'https://translator.broadinstitute.org/molecular_data_provider/collection/'+collection_id
    response = requests.get(url)
    collection = Collection.from_dict(response.json())
    return collection.elements
