import connexion
import six

from openapi_server import util

from openapi_server.controllers.knowledge_map import knowledge_map

def predicates_get():  # noqa: E501
    """Get supported relationships by source and target

     # noqa: E501


    :rtype: Dict[str, Dict[str, List[str]]]
    """
    return knowledge_map.predicates()
