# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from molepro.openapi_server.classes.base_model_ import Model
from molepro.openapi_server import util


class Names(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, name=None, synonyms=None, name_type=None, source=None, provided_by=None, language=None):  # noqa: E501
        """Names - a model defined in OpenAPI

        :param name: The name of this Names.  # noqa: E501
        :type name: str
        :param synonyms: The synonyms of this Names.  # noqa: E501
        :type synonyms: List[str]
        :param name_type: The name_type of this Names.  # noqa: E501
        :type name_type: str
        :param source: The source of this Names.  # noqa: E501
        :type source: str
        :param provided_by: The provided_by of this Names.  # noqa: E501
        :type provided_by: str
        :param language: The language of this Names.  # noqa: E501
        :type language: str
        """
        self.openapi_types = {
            'name': str,
            'synonyms': List[str],
            'name_type': str,
            'source': str,
            'provided_by': str,
            'language': str
        }

        self.attribute_map = {
            'name': 'name',
            'synonyms': 'synonyms',
            'name_type': 'name_type',
            'source': 'source',
            'provided_by': 'provided_by',
            'language': 'language'
        }

        self._name = name
        self._synonyms = synonyms
        self._name_type = name_type
        self._source = source
        self._provided_by = provided_by
        self._language = language

    @classmethod
    def from_dict(cls, dikt) -> 'Names':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The names of this Names.  # noqa: E501
        :rtype: Names
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self):
        """Gets the name of this Names.

        Name of the compound.  # noqa: E501

        :return: The name of this Names.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Names.

        Name of the compound.  # noqa: E501

        :param name: The name of this Names.
        :type name: str
        """

        self._name = name

    @property
    def synonyms(self):
        """Gets the synonyms of this Names.

        Name of the compound.  # noqa: E501

        :return: The synonyms of this Names.
        :rtype: List[str]
        """
        return self._synonyms

    @synonyms.setter
    def synonyms(self, synonyms):
        """Sets the synonyms of this Names.

        Name of the compound.  # noqa: E501

        :param synonyms: The synonyms of this Names.
        :type synonyms: List[str]
        """

        self._synonyms = synonyms

    @property
    def name_type(self):
        """Gets the name_type of this Names.

        Type of names and synonyms, e.g. inn, trademarked name.  # noqa: E501

        :return: The name_type of this Names.
        :rtype: str
        """
        return self._name_type

    @name_type.setter
    def name_type(self, name_type):
        """Sets the name_type of this Names.

        Type of names and synonyms, e.g. inn, trademarked name.  # noqa: E501

        :param name_type: The name_type of this Names.
        :type name_type: str
        """
        ##if name_type is None:
        ##    raise ValueError("Invalid value for `name_type`, must not be `None`")  # noqa: E501

        self._name_type = name_type

    @property
    def source(self):
        """Gets the source of this Names.

        Primary source of names and synonyms.  # noqa: E501

        :return: The source of this Names.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """Sets the source of this Names.

        Primary source of names and synonyms.  # noqa: E501

        :param source: The source of this Names.
        :type source: str
        """
        if source is None:
            raise ValueError("Invalid value for `source`, must not be `None`")  # noqa: E501

        self._source = source

    @property
    def provided_by(self):
        """Gets the provided_by of this Names.

        Transformer that produced the names and synonyms.  # noqa: E501

        :return: The provided_by of this Names.
        :rtype: str
        """
        return self._provided_by

    @provided_by.setter
    def provided_by(self, provided_by):
        """Sets the provided_by of this Names.

        Transformer that produced the names and synonyms.  # noqa: E501

        :param provided_by: The provided_by of this Names.
        :type provided_by: str
        """
        if provided_by is None:
            raise ValueError("Invalid value for `provided_by`, must not be `None`")  # noqa: E501

        self._provided_by = provided_by

    @property
    def language(self):
        """Gets the language of this Names.

        Language of names and synonyms.  # noqa: E501

        :return: The language of this Names.
        :rtype: str
        """
        return self._language

    @language.setter
    def language(self, language):
        """Sets the language of this Names.

        Language of names and synonyms.  # noqa: E501

        :param language: The language of this Names.
        :type language: str
        """

        self._language = language