import requests
import json
from contextlib import closing

from openapi_server.models.query import Query
from openapi_server.controllers.knowledge_map import knowledge_map
from openapi_server.controllers.molepro import MolePro

BASE_URL = 'http://localhost:9200/molecular_data_provider'

def execute_query(query: Query):
    query_graph = query.message.query_graph
    if len(query_graph.edges) == 0:
        return ({"status": 400, "title": "Bad Request", "detail": "No edges", "type": "about:blank" }, 400)
    if len(query_graph.edges) > 1:
        return ({"status": 501, "title": "Not Implemented", "detail": "Multi-edges queries not yet implemented", "type": "about:blank" }, 501)

    molepro = MolePro(query_graph)
    edge, predicates = knowledge_map.match_query_graph(query_graph)
    if edge['source'].curie is None:
        return ({"status": 501, "title": "Not Implemented", "detail": "Variable-source queries not yet implemented", "type": "about:blank" }, 501)
    for predicate in predicates:
        molepro.execute_transformer_chain(edge, predicate['transformer_chain'])
    return molepro.get_results()
