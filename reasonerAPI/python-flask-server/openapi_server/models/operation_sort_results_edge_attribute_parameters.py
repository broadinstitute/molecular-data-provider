# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class OperationSortResultsEdgeAttributeParameters(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, edge_attribute=None, ascending_or_descending=None, qedge_keys=None):  # noqa: E501
        """OperationSortResultsEdgeAttributeParameters - a model defined in OpenAPI

        :param edge_attribute: The edge_attribute of this OperationSortResultsEdgeAttributeParameters.  # noqa: E501
        :type edge_attribute: str
        :param ascending_or_descending: The ascending_or_descending of this OperationSortResultsEdgeAttributeParameters.  # noqa: E501
        :type ascending_or_descending: str
        :param qedge_keys: The qedge_keys of this OperationSortResultsEdgeAttributeParameters.  # noqa: E501
        :type qedge_keys: List[str]
        """
        self.openapi_types = {
            'edge_attribute': str,
            'ascending_or_descending': str,
            'qedge_keys': List[str]
        }

        self.attribute_map = {
            'edge_attribute': 'edge_attribute',
            'ascending_or_descending': 'ascending_or_descending',
            'qedge_keys': 'qedge_keys'
        }

        self._edge_attribute = edge_attribute
        self._ascending_or_descending = ascending_or_descending
        self._qedge_keys = qedge_keys

    @classmethod
    def from_dict(cls, dikt) -> 'OperationSortResultsEdgeAttributeParameters':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The OperationSortResultsEdgeAttribute_parameters of this OperationSortResultsEdgeAttributeParameters.  # noqa: E501
        :rtype: OperationSortResultsEdgeAttributeParameters
        """
        return util.deserialize_model(dikt, cls)

    @property
    def edge_attribute(self):
        """Gets the edge_attribute of this OperationSortResultsEdgeAttributeParameters.

        The name of the edge attribute to order by.  # noqa: E501

        :return: The edge_attribute of this OperationSortResultsEdgeAttributeParameters.
        :rtype: str
        """
        return self._edge_attribute

    @edge_attribute.setter
    def edge_attribute(self, edge_attribute):
        """Sets the edge_attribute of this OperationSortResultsEdgeAttributeParameters.

        The name of the edge attribute to order by.  # noqa: E501

        :param edge_attribute: The edge_attribute of this OperationSortResultsEdgeAttributeParameters.
        :type edge_attribute: str
        """
        if edge_attribute is None:
            raise ValueError("Invalid value for `edge_attribute`, must not be `None`")  # noqa: E501

        self._edge_attribute = edge_attribute

    @property
    def ascending_or_descending(self):
        """Gets the ascending_or_descending of this OperationSortResultsEdgeAttributeParameters.

        Indicates whether results should be sorted in ascending or descending order.  # noqa: E501

        :return: The ascending_or_descending of this OperationSortResultsEdgeAttributeParameters.
        :rtype: str
        """
        return self._ascending_or_descending

    @ascending_or_descending.setter
    def ascending_or_descending(self, ascending_or_descending):
        """Sets the ascending_or_descending of this OperationSortResultsEdgeAttributeParameters.

        Indicates whether results should be sorted in ascending or descending order.  # noqa: E501

        :param ascending_or_descending: The ascending_or_descending of this OperationSortResultsEdgeAttributeParameters.
        :type ascending_or_descending: str
        """
        allowed_values = ["ascending", "descending"]  # noqa: E501
        if ascending_or_descending not in allowed_values:
            raise ValueError(
                "Invalid value for `ascending_or_descending` ({0}), must be one of {1}"
                .format(ascending_or_descending, allowed_values)
            )

        self._ascending_or_descending = ascending_or_descending

    @property
    def qedge_keys(self):
        """Gets the qedge_keys of this OperationSortResultsEdgeAttributeParameters.

        This indicates if you only want to consider edges with specific edge_keys. If not provided or empty, all edges will be looked at.  # noqa: E501

        :return: The qedge_keys of this OperationSortResultsEdgeAttributeParameters.
        :rtype: List[str]
        """
        return self._qedge_keys

    @qedge_keys.setter
    def qedge_keys(self, qedge_keys):
        """Sets the qedge_keys of this OperationSortResultsEdgeAttributeParameters.

        This indicates if you only want to consider edges with specific edge_keys. If not provided or empty, all edges will be looked at.  # noqa: E501

        :param qedge_keys: The qedge_keys of this OperationSortResultsEdgeAttributeParameters.
        :type qedge_keys: List[str]
        """

        self._qedge_keys = qedge_keys