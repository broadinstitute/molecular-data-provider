# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.edge import Edge
from openapi_server.models.knowledge_graph import KnowledgeGraph
from openapi_server.models.node import Node
from openapi_server import util

from openapi_server.models.edge import Edge  # noqa: E501
from openapi_server.models.knowledge_graph import KnowledgeGraph  # noqa: E501
from openapi_server.models.node import Node  # noqa: E501

class MessageKnowledgeGraph(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, nodes=None, edges=None):  # noqa: E501
        """MessageKnowledgeGraph - a model defined in OpenAPI

        :param nodes: The nodes of this MessageKnowledgeGraph.  # noqa: E501
        :type nodes: Dict[str, Node]
        :param edges: The edges of this MessageKnowledgeGraph.  # noqa: E501
        :type edges: Dict[str, Edge]
        """
        self.openapi_types = {
            'nodes': Dict[str, Node],
            'edges': Dict[str, Edge]
        }

        self.attribute_map = {
            'nodes': 'nodes',
            'edges': 'edges'
        }

        self._nodes = nodes
        self._edges = edges

    @classmethod
    def from_dict(cls, dikt) -> 'MessageKnowledgeGraph':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Message_knowledge_graph of this MessageKnowledgeGraph.  # noqa: E501
        :rtype: MessageKnowledgeGraph
        """
        return util.deserialize_model(dikt, cls)

    @property
    def nodes(self):
        """Gets the nodes of this MessageKnowledgeGraph.

        Dictionary of Node instances used in the KnowledgeGraph, referenced elsewhere in the TRAPI output by the dictionary key.  # noqa: E501

        :return: The nodes of this MessageKnowledgeGraph.
        :rtype: Dict[str, Node]
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """Sets the nodes of this MessageKnowledgeGraph.

        Dictionary of Node instances used in the KnowledgeGraph, referenced elsewhere in the TRAPI output by the dictionary key.  # noqa: E501

        :param nodes: The nodes of this MessageKnowledgeGraph.
        :type nodes: Dict[str, Node]
        """
        if nodes is None:
            raise ValueError("Invalid value for `nodes`, must not be `None`")  # noqa: E501

        self._nodes = nodes

    @property
    def edges(self):
        """Gets the edges of this MessageKnowledgeGraph.

        Dictionary of Edge instances used in the KnowledgeGraph, referenced elsewhere in the TRAPI output by the dictionary key.  # noqa: E501

        :return: The edges of this MessageKnowledgeGraph.
        :rtype: Dict[str, Edge]
        """
        return self._edges

    @edges.setter
    def edges(self, edges):
        """Sets the edges of this MessageKnowledgeGraph.

        Dictionary of Edge instances used in the KnowledgeGraph, referenced elsewhere in the TRAPI output by the dictionary key.  # noqa: E501

        :param edges: The edges of this MessageKnowledgeGraph.
        :type edges: Dict[str, Edge]
        """
        if edges is None:
            raise ValueError("Invalid value for `edges`, must not be `None`")  # noqa: E501

        self._edges = edges
