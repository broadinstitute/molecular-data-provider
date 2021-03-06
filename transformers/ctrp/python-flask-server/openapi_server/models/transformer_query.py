# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.element import Element
from openapi_server.models.model_property import ModelProperty
from openapi_server import util

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.model_property import ModelProperty  # noqa: E501

class TransformerQuery(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, collection=None, controls=None):  # noqa: E501
        """TransformerQuery - a model defined in OpenAPI

        :param collection: The collection of this TransformerQuery.  # noqa: E501
        :type collection: List[Element]
        :param controls: The controls of this TransformerQuery.  # noqa: E501
        :type controls: List[ModelProperty]
        """
        self.openapi_types = {
            'collection': List[Element],
            'controls': List[ModelProperty]
        }

        self.attribute_map = {
            'collection': 'collection',
            'controls': 'controls'
        }

        self._collection = collection
        self._controls = controls

    @classmethod
    def from_dict(cls, dikt) -> 'TransformerQuery':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The transformer_query of this TransformerQuery.  # noqa: E501
        :rtype: TransformerQuery
        """
        return util.deserialize_model(dikt, cls)

    @property
    def collection(self):
        """Gets the collection of this TransformerQuery.

        List of elements that will be transformed. Required for all transformers except producers.  # noqa: E501

        :return: The collection of this TransformerQuery.
        :rtype: List[Element]
        """
        return self._collection

    @collection.setter
    def collection(self, collection):
        """Sets the collection of this TransformerQuery.

        List of elements that will be transformed. Required for all transformers except producers.  # noqa: E501

        :param collection: The collection of this TransformerQuery.
        :type collection: List[Element]
        """

        self._collection = collection

    @property
    def controls(self):
        """Gets the controls of this TransformerQuery.

        Values that control the behavior of the transformer. Names of the controls must match the names specified in the transformer's definition and values must match types (and possibly  allowed_values) specified in the transformer's definition.  # noqa: E501

        :return: The controls of this TransformerQuery.
        :rtype: List[ModelProperty]
        """
        return self._controls

    @controls.setter
    def controls(self, controls):
        """Sets the controls of this TransformerQuery.

        Values that control the behavior of the transformer. Names of the controls must match the names specified in the transformer's definition and values must match types (and possibly  allowed_values) specified in the transformer's definition.  # noqa: E501

        :param controls: The controls of this TransformerQuery.
        :type controls: List[ModelProperty]
        """
        if controls is None:
            raise ValueError("Invalid value for `controls`, must not be `None`")  # noqa: E501

        self._controls = controls
