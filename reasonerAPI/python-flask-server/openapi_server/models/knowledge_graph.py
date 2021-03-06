# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.edge import Edge
from openapi_server.models.node import Node
from openapi_server import util


class KnowledgeGraph(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, nodes=None, edges=None):  # noqa: E501
        """KnowledgeGraph - a model defined in OpenAPI

        :param nodes: The nodes of this KnowledgeGraph.  # noqa: E501
        :type nodes: List[Node]
        :param edges: The edges of this KnowledgeGraph.  # noqa: E501
        :type edges: List[Edge]
        """
        self.openapi_types = {
            'nodes': List[Node],
            'edges': List[Edge]
        }

        self.attribute_map = {
            'nodes': 'nodes',
            'edges': 'edges'
        }

        self._nodes = nodes
        self._edges = edges

    @classmethod
    def from_dict(cls, dikt) -> 'KnowledgeGraph':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The KnowledgeGraph of this KnowledgeGraph.  # noqa: E501
        :rtype: KnowledgeGraph
        """
        return util.deserialize_model(dikt, cls)

    @property
    def nodes(self):
        """Gets the nodes of this KnowledgeGraph.

        List of nodes in the KnowledgeGraph  # noqa: E501

        :return: The nodes of this KnowledgeGraph.
        :rtype: List[Node]
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """Sets the nodes of this KnowledgeGraph.

        List of nodes in the KnowledgeGraph  # noqa: E501

        :param nodes: The nodes of this KnowledgeGraph.
        :type nodes: List[Node]
        """
        if nodes is None:
            raise ValueError("Invalid value for `nodes`, must not be `None`")  # noqa: E501

        self._nodes = nodes

    @property
    def edges(self):
        """Gets the edges of this KnowledgeGraph.

        List of edges in the KnowledgeGraph  # noqa: E501

        :return: The edges of this KnowledgeGraph.
        :rtype: List[Edge]
        """
        return self._edges

    @edges.setter
    def edges(self, edges):
        """Sets the edges of this KnowledgeGraph.

        List of edges in the KnowledgeGraph  # noqa: E501

        :param edges: The edges of this KnowledgeGraph.
        :type edges: List[Edge]
        """
        if edges is None:
            raise ValueError("Invalid value for `edges`, must not be `None`")  # noqa: E501

        self._edges = edges
