# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.attribute import Attribute
from openapi_server.models.connection import Connection
from openapi_server.models.names import Names
from openapi_server import util

from openapi_server.models.attribute import Attribute  # noqa: E501
from openapi_server.models.connection import Connection  # noqa: E501
from openapi_server.models.names import Names  # noqa: E501

class Element(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, biolink_class=None, is_set=None, identifiers=None, alternative_identifiers=None, names_synonyms=None, attributes=None, connections=None, source=None, provided_by=None):  # noqa: E501
        """Element - a model defined in OpenAPI

        :param id: The id of this Element.  # noqa: E501
        :type id: str
        :param biolink_class: The biolink_class of this Element.  # noqa: E501
        :type biolink_class: str
        :param is_set: The is_set of this Element.  # noqa: E501
        :type is_set: bool
        :param identifiers: The identifiers of this Element.  # noqa: E501
        :type identifiers: Dict[str, object]
        :param alternative_identifiers: The alternative_identifiers of this Element.  # noqa: E501
        :type alternative_identifiers: List[Dict[str, object]]
        :param names_synonyms: The names_synonyms of this Element.  # noqa: E501
        :type names_synonyms: List[Names]
        :param attributes: The attributes of this Element.  # noqa: E501
        :type attributes: List[Attribute]
        :param connections: The connections of this Element.  # noqa: E501
        :type connections: List[Connection]
        :param source: The source of this Element.  # noqa: E501
        :type source: str
        :param provided_by: The provided_by of this Element.  # noqa: E501
        :type provided_by: str
        """
        self.openapi_types = {
            'id': str,
            'biolink_class': str,
            'is_set': bool,
            'identifiers': Dict[str, object],
            'alternative_identifiers': List[Dict[str, object]],
            'names_synonyms': List[Names],
            'attributes': List[Attribute],
            'connections': List[Connection],
            'source': str,
            'provided_by': str
        }

        self.attribute_map = {
            'id': 'id',
            'biolink_class': 'biolink_class',
            'is_set': 'is_set',
            'identifiers': 'identifiers',
            'alternative_identifiers': 'alternative_identifiers',
            'names_synonyms': 'names_synonyms',
            'attributes': 'attributes',
            'connections': 'connections',
            'source': 'source',
            'provided_by': 'provided_by'
        }

        self._id = id
        self._biolink_class = biolink_class
        self._is_set = is_set
        self._identifiers = identifiers
        self._alternative_identifiers = alternative_identifiers
        self._names_synonyms = names_synonyms
        self._attributes = attributes
        self._connections = connections
        self._source = source
        self._provided_by = provided_by

    @classmethod
    def from_dict(cls, dikt) -> 'Element':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The element of this Element.  # noqa: E501
        :rtype: Element
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this Element.

        Primary identifier of the element.  # noqa: E501

        :return: The id of this Element.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Element.

        Primary identifier of the element.  # noqa: E501

        :param id: The id of this Element.
        :type id: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def biolink_class(self):
        """Gets the biolink_class of this Element.

        BioLink class of the element.  # noqa: E501

        :return: The biolink_class of this Element.
        :rtype: str
        """
        return self._biolink_class

    @biolink_class.setter
    def biolink_class(self, biolink_class):
        """Sets the biolink_class of this Element.

        BioLink class of the element.  # noqa: E501

        :param biolink_class: The biolink_class of this Element.
        :type biolink_class: str
        """
        if biolink_class is None:
            raise ValueError("Invalid value for `biolink_class`, must not be `None`")  # noqa: E501

        self._biolink_class = biolink_class

    @property
    def is_set(self):
        """Gets the is_set of this Element.

        Indicates whether the element represents a set.  # noqa: E501

        :return: The is_set of this Element.
        :rtype: bool
        """
        return self._is_set

    @is_set.setter
    def is_set(self, is_set):
        """Sets the is_set of this Element.

        Indicates whether the element represents a set.  # noqa: E501

        :param is_set: The is_set of this Element.
        :type is_set: bool
        """

        self._is_set = is_set

    @property
    def identifiers(self):
        """Gets the identifiers of this Element.

        identifiers of the element.  # noqa: E501

        :return: The identifiers of this Element.
        :rtype: Dict[str, object]
        """
        return self._identifiers

    @identifiers.setter
    def identifiers(self, identifiers):
        """Sets the identifiers of this Element.

        identifiers of the element.  # noqa: E501

        :param identifiers: The identifiers of this Element.
        :type identifiers: Dict[str, object]
        """
        if identifiers is None:
            raise ValueError("Invalid value for `identifiers`, must not be `None`")  # noqa: E501

        self._identifiers = identifiers

    @property
    def alternative_identifiers(self):
        """Gets the alternative_identifiers of this Element.

        identifiers of additional chemical structures associated with chemical substance.  # noqa: E501

        :return: The alternative_identifiers of this Element.
        :rtype: List[Dict[str, object]]
        """
        return self._alternative_identifiers

    @alternative_identifiers.setter
    def alternative_identifiers(self, alternative_identifiers):
        """Sets the alternative_identifiers of this Element.

        identifiers of additional chemical structures associated with chemical substance.  # noqa: E501

        :param alternative_identifiers: The alternative_identifiers of this Element.
        :type alternative_identifiers: List[Dict[str, object]]
        """

        self._alternative_identifiers = alternative_identifiers

    @property
    def names_synonyms(self):
        """Gets the names_synonyms of this Element.

        Names and synonyms of the element.  # noqa: E501

        :return: The names_synonyms of this Element.
        :rtype: List[Names]
        """
        return self._names_synonyms

    @names_synonyms.setter
    def names_synonyms(self, names_synonyms):
        """Sets the names_synonyms of this Element.

        Names and synonyms of the element.  # noqa: E501

        :param names_synonyms: The names_synonyms of this Element.
        :type names_synonyms: List[Names]
        """

        self._names_synonyms = names_synonyms

    @property
    def attributes(self):
        """Gets the attributes of this Element.

        Additional information about the element and provenance about collection membership.  # noqa: E501

        :return: The attributes of this Element.
        :rtype: List[Attribute]
        """
        return self._attributes

    @attributes.setter
    def attributes(self, attributes):
        """Sets the attributes of this Element.

        Additional information about the element and provenance about collection membership.  # noqa: E501

        :param attributes: The attributes of this Element.
        :type attributes: List[Attribute]
        """

        self._attributes = attributes

    @property
    def connections(self):
        """Gets the connections of this Element.

        connections to elements of the input collection.  # noqa: E501

        :return: The connections of this Element.
        :rtype: List[Connection]
        """
        return self._connections

    @connections.setter
    def connections(self, connections):
        """Sets the connections of this Element.

        connections to elements of the input collection.  # noqa: E501

        :param connections: The connections of this Element.
        :type connections: List[Connection]
        """

        self._connections = connections

    @property
    def source(self):
        """Gets the source of this Element.

        Source of the element  # noqa: E501

        :return: The source of this Element.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this Element.

        Source of the element  # noqa: E501

        :param source: The source of this Element.
        :type source: str
        """
        if source is None:
            raise ValueError("Invalid value for `source`, must not be `None`")  # noqa: E501

        self._source = source

    @property
    def provided_by(self):
        """Gets the provided_by of this Element.

        Name of a transformer that added the element to the collection.  # noqa: E501

        :return: The provided_by of this Element.
        :rtype: str
        """
        return self._provided_by

    @provided_by.setter
    def provided_by(self, provided_by):
        """Sets the provided_by of this Element.

        Name of a transformer that added the element to the collection.  # noqa: E501

        :param provided_by: The provided_by of this Element.
        :type provided_by: str
        """
        if provided_by is None:
            raise ValueError("Invalid value for `provided_by`, must not be `None`")  # noqa: E501

        self._provided_by = provided_by
