# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.classes.base_model_ import Model
from openapi_server import util


class KmQualifier(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, qualifier_type_id=None, qualifier_values=None):  # noqa: E501
        """KmQualifier - a model defined in OpenAPI

        :param qualifier_type_id: The qualifier_type_id of this KmQualifier.  # noqa: E501
        :type qualifier_type_id: str
        :param qualifier_values: The qualifier_values of this KmQualifier.  # noqa: E501
        :type qualifier_values: List[str]
        """
        self.openapi_types = {
            'qualifier_type_id': str,
            'qualifier_values': List[str]
        }

        self.attribute_map = {
            'qualifier_type_id': 'qualifier_type_id',
            'qualifier_values': 'qualifier_values'
        }

        self._qualifier_type_id = qualifier_type_id
        self._qualifier_values = qualifier_values

    @classmethod
    def from_dict(cls, dikt) -> 'KmQualifier':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The km_qualifier of this KmQualifier.  # noqa: E501
        :rtype: KmQualifier
        """
        return util.deserialize_model(dikt, cls)

    @property
    def qualifier_type_id(self):
        """Gets the qualifier_type_id of this KmQualifier.

        The category of the qualifier, drawn from a hierarchy of qualifier slots in the Biolink model (e.g. subject_aspect, subject_direction, object_aspect, object_direction, etc).  # noqa: E501

        :return: The qualifier_type_id of this KmQualifier.
        :rtype: str
        """
        return self._qualifier_type_id

    @qualifier_type_id.setter
    def qualifier_type_id(self, qualifier_type_id):
        """Sets the qualifier_type_id of this KmQualifier.

        The category of the qualifier, drawn from a hierarchy of qualifier slots in the Biolink model (e.g. subject_aspect, subject_direction, object_aspect, object_direction, etc).  # noqa: E501

        :param qualifier_type_id: The qualifier_type_id of this KmQualifier.
        :type qualifier_type_id: str
        """
        if qualifier_type_id is None:
            raise ValueError("Invalid value for `qualifier_type_id`, must not be `None`")  # noqa: E501

        self._qualifier_type_id = qualifier_type_id

    @property
    def qualifier_values(self):
        """Gets the qualifier_values of this KmQualifier.

        Values associated with the type of the qualifier, drawn from a set of controlled values by the type as specified in the Biolink model (e.g. 'expression' or 'abundance' for the qualifier type 'subject_aspect', etc).  # noqa: E501

        :return: The qualifier_values of this KmQualifier.
        :rtype: List[str]
        """
        return self._qualifier_values

    @qualifier_values.setter
    def qualifier_values(self, qualifier_values):
        """Sets the qualifier_values of this KmQualifier.

        Values associated with the type of the qualifier, drawn from a set of controlled values by the type as specified in the Biolink model (e.g. 'expression' or 'abundance' for the qualifier type 'subject_aspect', etc).  # noqa: E501

        :param qualifier_values: The qualifier_values of this KmQualifier.
        :type qualifier_values: List[str]
        """
        if qualifier_values is None:
            raise ValueError("Invalid value for `qualifier_values`, must not be `None`")  # noqa: E501

        self._qualifier_values = qualifier_values
