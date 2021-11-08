import connexion
import six

from openapi_server.models.response import Response  # noqa: E501
from openapi_server import util

from openapi_server.models.query import Query
from openapi_server.controllers.query_interpreter import execute_query

def query_post(request_body):  # noqa: E501
    """Initiate a query and wait to receive a Response

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: Dict[str, ]

    :rtype: Response
    """
    #query = Query.from_dict(request_body)
    if connexion.request.is_json:
        query = Query.from_dict(connexion.request.get_json())
    return execute_query(query)
