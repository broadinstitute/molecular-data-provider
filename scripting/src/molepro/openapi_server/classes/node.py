# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from molepro.openapi_server.classes.base_model_ import Model
from molepro.openapi_server.classes.km_attribute import KmAttribute
from molepro.openapi_server import util


class Node(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id_prefixes=None, count=None, attributes=None):  # noqa: E501
        """Node - a model defined in OpenAPI

        :param id_prefixes: The id_prefixes of this Node.  # noqa: E501
        :type id_prefixes: List[str]
        :param count: The count of this Node.  # noqa: E501
        :type count: int
        :param attributes: The attributes of this Node.  # noqa: E501
        :type attributes: List[KmAttribute]
        """
        self.openapi_types = {
            'id_prefixes': List[str],
            'count': int,
            'attributes': List[KmAttribute]
        }

        self.attribute_map = {
            'id_prefixes': 'id_prefixes',
            'count': 'count',
            'attributes': 'attributes'
        }

        self._id_prefixes = id_prefixes
        self._count = count
        self._attributes = attributes

    @classmethod
    def from_dict(cls, dikt) -> 'Node':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The node of this Node.  # noqa: E501
        :rtype: Node
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id_prefixes(self):
        """Gets the id_prefixes of this Node.

        List of CURIE prefixes that this knowledge source understands and accepts on the input.  # noqa: E501

        :return: The id_prefixes of this Node.
        :rtype: List[str]
        """
        return self._id_prefixes

    @id_prefixes.setter
    def id_prefixes(self, id_prefixes):
        """Sets the id_prefixes of this Node.

        List of CURIE prefixes that this knowledge source understands and accepts on the input.  # noqa: E501

        :param id_prefixes: The id_prefixes of this Node.
        :type id_prefixes: List[str]
        """
        if id_prefixes is None:
            raise ValueError("Invalid value for `id_prefixes`, must not be `None`")  # noqa: E501

        self._id_prefixes = id_prefixes

    @property
    def count(self):
        """Gets the count of this Node.

        Number of node instances known to this knowledge source  # noqa: E501

        :return: The count of this Node.
        :rtype: int
        """
        return self._count

    @count.setter
    def count(self, count):
        """Sets the count of this Node.

        Number of node instances known to this knowledge source  # noqa: E501

        :param count: The count of this Node.
        :type count: int
        """

        self._count = count

    @property
    def attributes(self):
        """Gets the attributes of this Node.


        :return: The attributes of this Node.
        :rtype: List[KmAttribute]
        """
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        """Sets the attributes of this Node.


        :param attributes: The attributes of this Node.
        :type attributes: List[KmAttribute]
        """

        self._attributes = attributes
