# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from molepro.openapi_server.classes.base_model_ import Model
from molepro.openapi_server import util


class KmAttribute(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, type=None, attribute_type_id=None, source=None, names=None):  # noqa: E501
        """KmAttribute - a model defined in OpenAPI

        :param type: The type of this KmAttribute.  # noqa: E501
        :type type: str
        :param attribute_type_id: The attribute_type_id of this KmAttribute.  # noqa: E501
        :type attribute_type_id: str
        :param source: The source of this KmAttribute.  # noqa: E501
        :type source: str
        :param names: The names of this KmAttribute.  # noqa: E501
        :type names: List[str]
        """
        self.openapi_types = {
            'type': str,
            'attribute_type_id': str,
            'source': str,
            'names': List[str]
        }

        self.attribute_map = {
            'type': 'type',
            'attribute_type_id': 'attribute_type_id',
            'source': 'source',
            'names': 'names'
        }

        self._type = type
        self._attribute_type_id = attribute_type_id
        self._source = source
        self._names = names

    @classmethod
    def from_dict(cls, dikt) -> 'KmAttribute':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The km_attribute of this KmAttribute.  # noqa: E501
        :rtype: KmAttribute
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self):
        """Gets the type of this KmAttribute.

        CURIE of the semantic type of the attribute, from the EDAM ontology if possible. If a suitable identifier does not exist, enter a descriptive phrase here and submit the new type for consideration by the appropriate authority.  # noqa: E501

        :return: The type of this KmAttribute.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this KmAttribute.

        CURIE of the semantic type of the attribute, from the EDAM ontology if possible. If a suitable identifier does not exist, enter a descriptive phrase here and submit the new type for consideration by the appropriate authority.  # noqa: E501

        :param type: The type of this KmAttribute.
        :type type: str
        """

        self._type = type

    @property
    def attribute_type_id(self):
        """Gets the attribute_type_id of this KmAttribute.

        CURIE of the semantic type of the attribute, from the EDAM ontology if possible. If a suitable identifier does not exist, enter a descriptive phrase here and submit the new type for consideration by the appropriate authority.  # noqa: E501

        :return: The attribute_type_id of this KmAttribute.
        :rtype: str
        """
        return self._attribute_type_id

    @attribute_type_id.setter
    def attribute_type_id(self, attribute_type_id):
        """Sets the attribute_type_id of this KmAttribute.

        CURIE of the semantic type of the attribute, from the EDAM ontology if possible. If a suitable identifier does not exist, enter a descriptive phrase here and submit the new type for consideration by the appropriate authority.  # noqa: E501

        :param attribute_type_id: The attribute_type_id of this KmAttribute.
        :type attribute_type_id: str
        """
        if attribute_type_id is None:
            raise ValueError("Invalid value for `attribute_type_id`, must not be `None`")  # noqa: E501

        self._attribute_type_id = attribute_type_id

    @property
    def source(self):
        """Gets the source of this KmAttribute.

        Source of the attribute, as a CURIE prefix.  # noqa: E501

        :return: The source of this KmAttribute.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this KmAttribute.

        Source of the attribute, as a CURIE prefix.  # noqa: E501

        :param source: The source of this KmAttribute.
        :type source: str
        """

        self._source = source

    @property
    def names(self):
        """Gets the names of this KmAttribute.

        Human-readable names or labels for the attribute for attributes of  given type.  # noqa: E501

        :return: The names of this KmAttribute.
        :rtype: List[str]
        """
        return self._names

    @names.setter
    def names(self, names):
        """Sets the names of this KmAttribute.

        Human-readable names or labels for the attribute for attributes of  given type.  # noqa: E501

        :param names: The names of this KmAttribute.
        :type names: List[str]
        """

        self._names = names
