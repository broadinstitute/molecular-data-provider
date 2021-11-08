import connexion
import six

from openapi_server.models.response import Response  # noqa: E501
from openapi_server import util


def query_post(request_body):  # noqa: E501
    """Initiate a query and wait to receive a Response

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: Dict[str, ]

    :rtype: Response
    """
    return 'do some magic!'
