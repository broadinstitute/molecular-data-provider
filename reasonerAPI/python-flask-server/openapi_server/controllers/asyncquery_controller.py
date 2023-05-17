import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.async_query import AsyncQuery  # noqa: E501
from openapi_server.models.async_query_response import AsyncQueryResponse  # noqa: E501
from openapi_server import util


def asyncquery_post(request_body):  # noqa: E501
    """Initiate a query with a callback to receive the response

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: Dict[str, ]

    :rtype: Union[AsyncQueryResponse, Tuple[AsyncQueryResponse, int], Tuple[AsyncQueryResponse, int, Dict[str, str]]
    """
    return 'do some magic!'
