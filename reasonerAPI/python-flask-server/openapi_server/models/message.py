# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.message_knowledge_graph import MessageKnowledgeGraph
from openapi_server.models.message_query_graph import MessageQueryGraph
from openapi_server.models.result import Result
from openapi_server import util

from openapi_server.models.message_knowledge_graph import MessageKnowledgeGraph  # noqa: E501
from openapi_server.models.message_query_graph import MessageQueryGraph  # noqa: E501
from openapi_server.models.result import Result  # noqa: E501

class Message(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, results=None, query_graph=None, knowledge_graph=None, auxiliary_graphs=None):  # noqa: E501
        """Message - a model defined in OpenAPI

        :param results: The results of this Message.  # noqa: E501
        :type results: List[Result]
        :param query_graph: The query_graph of this Message.  # noqa: E501
        :type query_graph: MessageQueryGraph
        :param knowledge_graph: The knowledge_graph of this Message.  # noqa: E501
        :type knowledge_graph: MessageKnowledgeGraph
        :param auxiliary_graphs: The auxiliary_graphs of this Message.  # noqa: E501
        :type auxiliary_graphs: Dict[str, object]
        """
        self.openapi_types = {
            'results': List[Result],
            'query_graph': MessageQueryGraph,
            'knowledge_graph': MessageKnowledgeGraph,
            'auxiliary_graphs': Dict[str, object]
        }

        self.attribute_map = {
            'results': 'results',
            'query_graph': 'query_graph',
            'knowledge_graph': 'knowledge_graph',
            'auxiliary_graphs': 'auxiliary_graphs'
        }

        self._results = results
        self._query_graph = query_graph
        self._knowledge_graph = knowledge_graph
        self._auxiliary_graphs = auxiliary_graphs

    @classmethod
    def from_dict(cls, dikt) -> 'Message':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Message of this Message.  # noqa: E501
        :rtype: Message
        """
        return util.deserialize_model(dikt, cls)

    @property
    def results(self):
        """Gets the results of this Message.

        List of all returned Result objects for the query posed. The list SHOULD NOT be assumed to be ordered. The 'score' property,  if present, MAY be used to infer result rankings.  # noqa: E501

        :return: The results of this Message.
        :rtype: List[Result]
        """
        return self._results

    @results.setter
    def results(self, results):
        """Sets the results of this Message.

        List of all returned Result objects for the query posed. The list SHOULD NOT be assumed to be ordered. The 'score' property,  if present, MAY be used to infer result rankings.  # noqa: E501

        :param results: The results of this Message.
        :type results: List[Result]
        """

        self._results = results

    @property
    def query_graph(self):
        """Gets the query_graph of this Message.


        :return: The query_graph of this Message.
        :rtype: MessageQueryGraph
        """
        return self._query_graph

    @query_graph.setter
    def query_graph(self, query_graph):
        """Sets the query_graph of this Message.


        :param query_graph: The query_graph of this Message.
        :type query_graph: MessageQueryGraph
        """

        self._query_graph = query_graph

    @property
    def knowledge_graph(self):
        """Gets the knowledge_graph of this Message.


        :return: The knowledge_graph of this Message.
        :rtype: MessageKnowledgeGraph
        """
        return self._knowledge_graph

    @knowledge_graph.setter
    def knowledge_graph(self, knowledge_graph):
        """Sets the knowledge_graph of this Message.


        :param knowledge_graph: The knowledge_graph of this Message.
        :type knowledge_graph: MessageKnowledgeGraph
        """

        self._knowledge_graph = knowledge_graph

    @property
    def auxiliary_graphs(self):
        """Gets the auxiliary_graphs of this Message.

        Dictionary of AuxiliaryGraph instances that are used by Knowledge Graph Edges and Result Analyses. These are referenced elsewhere by the dictionary key.  # noqa: E501

        :return: The auxiliary_graphs of this Message.
        :rtype: Dict[str, object]
        """
        return self._auxiliary_graphs

    @auxiliary_graphs.setter
    def auxiliary_graphs(self, auxiliary_graphs):
        """Sets the auxiliary_graphs of this Message.

        Dictionary of AuxiliaryGraph instances that are used by Knowledge Graph Edges and Result Analyses. These are referenced elsewhere by the dictionary key.  # noqa: E501

        :param auxiliary_graphs: The auxiliary_graphs of this Message.
        :type auxiliary_graphs: Dict[str, object]
        """

        self._auxiliary_graphs = auxiliary_graphs
