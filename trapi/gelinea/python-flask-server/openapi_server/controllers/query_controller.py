import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.query import Query  # noqa: E501
from openapi_server.models.response import Response  # noqa: E501
from openapi_server import util


def query_post(request_body):  # noqa: E501
    """Initiate a query and wait to receive a Response

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: Dict[str, ]

    :rtype: Union[Response, Tuple[Response, int], Tuple[Response, int, Dict[str, str]]
    """
    return 'do some magic!'
