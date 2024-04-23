# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from molepro.openapi_server.classes.base_model_ import Model
from molepro.openapi_server.classes.attribute import Attribute
from molepro.openapi_server import util


class Connection(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, source_element_id=None, biolink_predicate=None, inverse_predicate=None, relation=None, inverse_relation=None, source=None, provided_by=None, attributes=None):  # noqa: E501
        """Connection - a model defined in OpenAPI

        :param source_element_id: The source_element_id of this Connection.  # noqa: E501
        :type source_element_id: str
        :param biolink_predicate: The biolink_predicate of this Connection.  # noqa: E501
        :type biolink_predicate: str
        :param inverse_predicate: The inverse_predicate of this Connection.  # noqa: E501
        :type inverse_predicate: str
        :param relation: The relation of this Connection.  # noqa: E501
        :type relation: str
        :param inverse_relation: The inverse_relation of this Connection.  # noqa: E501
        :type inverse_relation: str
        :param source: The source of this Connection.  # noqa: E501
        :type source: str
        :param provided_by: The provided_by of this Connection.  # noqa: E501
        :type provided_by: str
        :param attributes: The attributes of this Connection.  # noqa: E501
        :type attributes: List[Attribute]
        """
        self.openapi_types = {
            'source_element_id': str,
            'biolink_predicate': str,
            'inverse_predicate': str,
            'relation': str,
            'inverse_relation': str,
            'source': str,
            'provided_by': str,
            'attributes': List[Attribute]
        }

        self.attribute_map = {
            'source_element_id': 'source_element_id',
            'biolink_predicate': 'biolink_predicate',
            'inverse_predicate': 'inverse_predicate',
            'relation': 'relation',
            'inverse_relation': 'inverse_relation',
            'source': 'source',
            'provided_by': 'provided_by',
            'attributes': 'attributes'
        }

        self._source_element_id = source_element_id
        self._biolink_predicate = biolink_predicate
        self._inverse_predicate = inverse_predicate
        self._relation = relation
        self._inverse_relation = inverse_relation
        self._source = source
        self._provided_by = provided_by
        self._attributes = attributes

    @classmethod
    def from_dict(cls, dikt) -> 'Connection':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The connection of this Connection.  # noqa: E501
        :rtype: Connection
        """
        return util.deserialize_model(dikt, cls)

    @property
    def source_element_id(self):
        """Gets the source_element_id of this Connection.

        Id (CURIE) of the connected query node.  # noqa: E501

        :return: The source_element_id of this Connection.
        :rtype: str
        """
        return self._source_element_id

    @source_element_id.setter
    def source_element_id(self, source_element_id):
        """Sets the source_element_id of this Connection.

        Id (CURIE) of the connected query node.  # noqa: E501

        :param source_element_id: The source_element_id of this Connection.
        :type source_element_id: str
        """
        if source_element_id is None:
            raise ValueError("Invalid value for `source_element_id`, must not be `None`")  # noqa: E501

        self._source_element_id = source_element_id

    @property
    def biolink_predicate(self):
        """Gets the biolink_predicate of this Connection.

        Biolink predicate.  # noqa: E501

        :return: The biolink_predicate of this Connection.
        :rtype: str
        """
        return self._biolink_predicate

    @biolink_predicate.setter
    def biolink_predicate(self, biolink_predicate):
        """Sets the biolink_predicate of this Connection.

        Biolink predicate.  # noqa: E501

        :param biolink_predicate: The biolink_predicate of this Connection.
        :type biolink_predicate: str
        """
        if biolink_predicate is None:
            raise ValueError("Invalid value for `biolink_predicate`, must not be `None`")  # noqa: E501

        self._biolink_predicate = biolink_predicate

    @property
    def inverse_predicate(self):
        """Gets the inverse_predicate of this Connection.

        Inverse Biolink predicate.  # noqa: E501

        :return: The inverse_predicate of this Connection.
        :rtype: str
        """
        return self._inverse_predicate

    @inverse_predicate.setter
    def inverse_predicate(self, inverse_predicate):
        """Sets the inverse_predicate of this Connection.

        Inverse Biolink predicate.  # noqa: E501

        :param inverse_predicate: The inverse_predicate of this Connection.
        :type inverse_predicate: str
        """
        if inverse_predicate is None:
            raise ValueError("Invalid value for `inverse_predicate`, must not be `None`")  # noqa: E501

        self._inverse_predicate = inverse_predicate

    @property
    def relation(self):
        """Gets the relation of this Connection.

        Lower-level relationship type of this connection.  # noqa: E501

        :return: The relation of this Connection.
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation):
        """Sets the relation of this Connection.

        Lower-level relationship type of this connection.  # noqa: E501

        :param relation: The relation of this Connection.
        :type relation: str
        """

        self._relation = relation

    @property
    def inverse_relation(self):
        """Gets the inverse_relation of this Connection.

        Inverse lower-level relationship type of this connection.  # noqa: E501

        :return: The inverse_relation of this Connection.
        :rtype: str
        """
        return self._inverse_relation

    @inverse_relation.setter
    def inverse_relation(self, inverse_relation):
        """Sets the inverse_relation of this Connection.

        Inverse lower-level relationship type of this connection.  # noqa: E501

        :param inverse_relation: The inverse_relation of this Connection.
        :type inverse_relation: str
        """

        self._inverse_relation = inverse_relation

    @property
    def source(self):
        """Gets the source of this Connection.

        Source of the connection, as a CURIE prefix.  # noqa: E501

        :return: The source of this Connection.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this Connection.

        Source of the connection, as a CURIE prefix.  # noqa: E501

        :param source: The source of this Connection.
        :type source: str
        """
        if source is None:
            raise ValueError("Invalid value for `source`, must not be `None`")  # noqa: E501

        self._source = source

    @property
    def provided_by(self):
        """Gets the provided_by of this Connection.

        Transformer that produced the connection.  # noqa: E501

        :return: The provided_by of this Connection.
        :rtype: str
        """
        return self._provided_by

    @provided_by.setter
    def provided_by(self, provided_by):
        """Sets the provided_by of this Connection.

        Transformer that produced the connection.  # noqa: E501

        :param provided_by: The provided_by of this Connection.
        :type provided_by: str
        """
        if provided_by is None:
            raise ValueError("Invalid value for `provided_by`, must not be `None`")  # noqa: E501

        self._provided_by = provided_by

    @property
    def attributes(self):
        """Gets the attributes of this Connection.

        Additional information and provenance about the connection.  # noqa: E501

        :return: The attributes of this Connection.
        :rtype: List[Attribute]
        """
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        """Sets the attributes of this Connection.

        Additional information and provenance about the connection.  # noqa: E501

        :param attributes: The attributes of this Connection.
        :type attributes: List[Attribute]
        """

        self._attributes = attributes
