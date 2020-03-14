import connexion
import six

from openapi_server.models.message import Message  # noqa: E501
from openapi_server import util

from openapi_server.models.query import Query
from openapi_server.controllers.query_interpreter import execute_query

def query(request_body):  # noqa: E501
    """Query reasoner via one of several inputs

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: dict | bytes

    :rtype: Message
    """
    #query = Query.from_dict(request_body)
    if connexion.request.is_json:
        query = Query.from_dict(connexion.request.get_json())
    return execute_query(query)
