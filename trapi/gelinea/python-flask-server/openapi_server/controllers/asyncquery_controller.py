import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.async_query import AsyncQuery  # noqa: E501
from openapi_server.models.async_query_response import AsyncQueryResponse  # noqa: E501
from openapi_server import util

import asyncio
import uuid
from openapi_server.controllers.gelinea_controler import async_run_workflow

def asyncquery_post(request_body):  # noqa: E501
    """Initiate a query with a callback to receive the response

     # noqa: E501

    :param request_body: Query information to be submitted
    :type request_body: Dict[str, ]

    :rtype: Union[AsyncQueryResponse, Tuple[AsyncQueryResponse, int], Tuple[AsyncQueryResponse, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        query = AsyncQuery.from_dict(connexion.request.get_json())
    job_id = str(uuid.uuid4())
    description = 'Query commenced. Will send result to {}'.format(query.callback)
    response = AsyncQueryResponse(status='Accepted', description=description, job_id=job_id)
    with open('jobs/{}'.format(job_id), 'w') as status_file:
        print('0', file=status_file)
    coro = async_run_workflow(query, job_id, query.callback)
    asyncio.run(coro)
    return response
