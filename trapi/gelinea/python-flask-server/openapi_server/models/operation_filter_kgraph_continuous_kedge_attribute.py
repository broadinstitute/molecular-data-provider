# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.operation_filter_kgraph_continuous_kedge_attribute_parameters import OperationFilterKgraphContinuousKedgeAttributeParameters
from openapi_server.models.runner_parameters import RunnerParameters
from openapi_server import util

from openapi_server.models.operation_filter_kgraph_continuous_kedge_attribute_parameters import OperationFilterKgraphContinuousKedgeAttributeParameters  # noqa: E501
from openapi_server.models.runner_parameters import RunnerParameters  # noqa: E501

class OperationFilterKgraphContinuousKedgeAttribute(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, parameters=None, runner_parameters=None):  # noqa: E501
        """OperationFilterKgraphContinuousKedgeAttribute - a model defined in OpenAPI

        :param id: The id of this OperationFilterKgraphContinuousKedgeAttribute.  # noqa: E501
        :type id: str
        :param parameters: The parameters of this OperationFilterKgraphContinuousKedgeAttribute.  # noqa: E501
        :type parameters: OperationFilterKgraphContinuousKedgeAttributeParameters
        :param runner_parameters: The runner_parameters of this OperationFilterKgraphContinuousKedgeAttribute.  # noqa: E501
        :type runner_parameters: RunnerParameters
        """
        self.openapi_types = {
            'id': str,
            'parameters': OperationFilterKgraphContinuousKedgeAttributeParameters,
            'runner_parameters': RunnerParameters
        }

        self.attribute_map = {
            'id': 'id',
            'parameters': 'parameters',
            'runner_parameters': 'runner_parameters'
        }

        self._id = id
        self._parameters = parameters
        self._runner_parameters = runner_parameters

    @classmethod
    def from_dict(cls, dikt) -> 'OperationFilterKgraphContinuousKedgeAttribute':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The OperationFilterKgraphContinuousKedgeAttribute of this OperationFilterKgraphContinuousKedgeAttribute.  # noqa: E501
        :rtype: OperationFilterKgraphContinuousKedgeAttribute
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this OperationFilterKgraphContinuousKedgeAttribute.


        :return: The id of this OperationFilterKgraphContinuousKedgeAttribute.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this OperationFilterKgraphContinuousKedgeAttribute.


        :param id: The id of this OperationFilterKgraphContinuousKedgeAttribute.
        :type id: str
        """
        allowed_values = ["filter_kgraph_continuous_kedge_attribute"]  # noqa: E501
        if id not in allowed_values:
            raise ValueError(
                "Invalid value for `id` ({0}), must be one of {1}"
                .format(id, allowed_values)
            )

        self._id = id

    @property
    def parameters(self):
        """Gets the parameters of this OperationFilterKgraphContinuousKedgeAttribute.


        :return: The parameters of this OperationFilterKgraphContinuousKedgeAttribute.
        :rtype: OperationFilterKgraphContinuousKedgeAttributeParameters
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this OperationFilterKgraphContinuousKedgeAttribute.


        :param parameters: The parameters of this OperationFilterKgraphContinuousKedgeAttribute.
        :type parameters: OperationFilterKgraphContinuousKedgeAttributeParameters
        """
        if parameters is None:
            raise ValueError("Invalid value for `parameters`, must not be `None`")  # noqa: E501

        self._parameters = parameters

    @property
    def runner_parameters(self):
        """Gets the runner_parameters of this OperationFilterKgraphContinuousKedgeAttribute.


        :return: The runner_parameters of this OperationFilterKgraphContinuousKedgeAttribute.
        :rtype: RunnerParameters
        """
        return self._runner_parameters

    @runner_parameters.setter
    def runner_parameters(self, runner_parameters):
        """Sets the runner_parameters of this OperationFilterKgraphContinuousKedgeAttribute.


        :param runner_parameters: The runner_parameters of this OperationFilterKgraphContinuousKedgeAttribute.
        :type runner_parameters: RunnerParameters
        """

        self._runner_parameters = runner_parameters