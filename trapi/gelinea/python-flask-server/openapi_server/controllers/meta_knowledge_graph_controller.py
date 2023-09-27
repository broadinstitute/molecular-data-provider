import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.meta_knowledge_graph import MetaKnowledgeGraph  # noqa: E501
from openapi_server import util


def meta_knowledge_graph_get():  # noqa: E501
    """Meta knowledge graph representation of this TRAPI web service.

     # noqa: E501


    :rtype: Union[MetaKnowledgeGraph, Tuple[MetaKnowledgeGraph, int], Tuple[MetaKnowledgeGraph, int, Dict[str, str]]
    """
    return 'do some magic!'
