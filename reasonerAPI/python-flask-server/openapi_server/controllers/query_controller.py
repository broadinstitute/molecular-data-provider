import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.query import Query  # noqa: E501
from openapi_server.models.response import Response  # noqa: E501
from openapi_server import util
from openapi_server.controllers.biolink_utils import get_trapi_version, get_biolink_version

from openapi_server.models.query import Query
from openapi_server.models.message import Message
from openapi_server.models.query_graph import QueryGraph

from openapi_server.controllers.query_interpreter import execute_query

def query_post(request_body):  # noqa: E501
    """Initiate a query and wait to receive a Response

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: Dict[str, ]

    :rtype: Union[Response, Tuple[Response, int], Tuple[Response, int, Dict[str, str]]
    """
    #query = Query.from_dict(request_body)
    if connexion.request.is_json:
        query_json = connexion.request.get_json()
        workflow = query_json.pop('workflow') if 'workflow' in query_json else None
        query = Query.from_dict(query_json)
        query.workflow = workflow

        # check for worklow

        # check for number of edges

        # check for set properties
        is_good_set, log_message = is_acceptable_node_sets(query=query)
        if not is_good_set:
            # return empty respponse
            return Response(message=query.message, logs=[log_message], workflow=workflow, schema_version=get_trapi_version(), biolink_version=get_biolink_version())

    return execute_query(query)


def is_acceptable_node_sets(query: Query, log=False):
    '''
    will evaluate the query nodes to make sure the set interpretation
    - only accept null or batch set_interpretation
    '''
    is_acceptable = True
    log_message = None

    # check all node set interpretation
    if query:
        message: Message = query.message
        message.results = []
        if message.query_graph:
            query_graph: QueryGraph = message.query_graph
            if query_graph.nodes and len(query_graph.nodes) > 0:
                for node in query_graph.nodes.values():
                    set_interpretation = node.set_interpretation
                    if set_interpretation and set_interpretation != 'BATCH':
                        is_acceptable = False
                        log_message = "The MolePro service only has BATCH node answers"

    # return
    return is_acceptable, log_message


    
