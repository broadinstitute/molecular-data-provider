from reasoner_validator import validate_Message, ValidationError
import requests
from contextlib import closing

TRAPI_QUERY = {
    "message": {
        "query_graph": {
            "edges": {
                "e00": {
                    "subject": "n00",
                    "object": "n01",
                    "predicate": "biolink:affected_by"
                }
            },
            "nodes": {
                "n00": {
                    "id": "NCBIGene:1803",
                    "category": "biolink:Gene"
                },
                "n01": {
                    "category": "biolink:ChemicalSubstance"
                }
            }
        }
    }
}

def main():
    url = 'http://localhost:8090/trapi/v1.0/query'
    response_obj = requests.post(url, json=TRAPI_QUERY)
    response = response_obj.json()

    message = response['message']
    try:
        validate_Message(message)
        print("OK")
    except ValidationError:
        raise ValueError('Bad Reasoner component!')


if __name__ == '__main__':
    main()