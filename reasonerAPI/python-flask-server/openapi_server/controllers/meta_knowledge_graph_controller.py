import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.meta_knowledge_graph import MetaKnowledgeGraph  # noqa: E501
from openapi_server.models.meta_edge import MetaEdge  # noqa: E501
from openapi_server.models.meta_node import MetaNode  # noqa: E501
from openapi_server import util
from openapi_server.controllers.knowledge_map import knowledge_map


def meta_knowledge_graph_get():  # noqa: E501
    """Meta knowledge graph representation of this TRAPI web service.

     # noqa: E501


    :rtype: Union[MetaKnowledgeGraph, Tuple[MetaKnowledgeGraph, int], Tuple[MetaKnowledgeGraph, int, Dict[str, str]]
    """
    # initialize
    meta_edges = []

    # get the data
    nodes, edges, map_edge_attributes = knowledge_map.meta_knowledge_graph()

    # convert
    for subject, target, predicate in edges:
        list_attributes = []
        if map_edge_attributes.get((subject, target, predicate)):
            list_attributes = map_edge_attributes.get((subject, target, predicate))

        meta_edges.append(MetaEdge(subject=subject, object=target, predicate=predicate, attributes=list_attributes, knowledge_types=['lookup'], qualifiers=[]))

    # for key, values in nodes.items():
    #     meta_nodes[key] = MetaNode(id_prefixes=values)

    return MetaKnowledgeGraph(nodes=nodes, edges=meta_edges)