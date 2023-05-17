import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.async_query_status_response import AsyncQueryStatusResponse  # noqa: E501
from openapi_server import util


def asyncquery_status(job_id):  # noqa: E501
    """Retrieve the current status of a previously submitted asyncquery given its job_id

     # noqa: E501

    :param job_id: Identifier of the job for status request
    :type job_id: str

    :rtype: Union[AsyncQueryStatusResponse, Tuple[AsyncQueryStatusResponse, int], Tuple[AsyncQueryStatusResponse, int, Dict[str, str]]
    """
    return 'do some magic!'
