# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.operation_overlay_compute_ngd_parameters import OperationOverlayComputeNgdParameters
from openapi_server.models.runner_parameters import RunnerParameters
from openapi_server import util

from openapi_server.models.operation_overlay_compute_ngd_parameters import OperationOverlayComputeNgdParameters  # noqa: E501
from openapi_server.models.runner_parameters import RunnerParameters  # noqa: E501

class OperationOverlayComputeNgd(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, parameters=None, runner_parameters=None):  # noqa: E501
        """OperationOverlayComputeNgd - a model defined in OpenAPI

        :param id: The id of this OperationOverlayComputeNgd.  # noqa: E501
        :type id: str
        :param parameters: The parameters of this OperationOverlayComputeNgd.  # noqa: E501
        :type parameters: OperationOverlayComputeNgdParameters
        :param runner_parameters: The runner_parameters of this OperationOverlayComputeNgd.  # noqa: E501
        :type runner_parameters: RunnerParameters
        """
        self.openapi_types = {
            'id': str,
            'parameters': OperationOverlayComputeNgdParameters,
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
    def from_dict(cls, dikt) -> 'OperationOverlayComputeNgd':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The OperationOverlayComputeNgd of this OperationOverlayComputeNgd.  # noqa: E501
        :rtype: OperationOverlayComputeNgd
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this OperationOverlayComputeNgd.


        :return: The id of this OperationOverlayComputeNgd.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this OperationOverlayComputeNgd.


        :param id: The id of this OperationOverlayComputeNgd.
        :type id: str
        """
        allowed_values = ["overlay_compute_ngd"]  # noqa: E501
        if id not in allowed_values:
            raise ValueError(
                "Invalid value for `id` ({0}), must be one of {1}"
                .format(id, allowed_values)
            )

        self._id = id

    @property
    def parameters(self):
        """Gets the parameters of this OperationOverlayComputeNgd.


        :return: The parameters of this OperationOverlayComputeNgd.
        :rtype: OperationOverlayComputeNgdParameters
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this OperationOverlayComputeNgd.


        :param parameters: The parameters of this OperationOverlayComputeNgd.
        :type parameters: OperationOverlayComputeNgdParameters
        """
        if parameters is None:
            raise ValueError("Invalid value for `parameters`, must not be `None`")  # noqa: E501

        self._parameters = parameters

    @property
    def runner_parameters(self):
        """Gets the runner_parameters of this OperationOverlayComputeNgd.


        :return: The runner_parameters of this OperationOverlayComputeNgd.
        :rtype: RunnerParameters
        """
        return self._runner_parameters

    @runner_parameters.setter
    def runner_parameters(self, runner_parameters):
        """Sets the runner_parameters of this OperationOverlayComputeNgd.


        :param runner_parameters: The runner_parameters of this OperationOverlayComputeNgd.
        :type runner_parameters: RunnerParameters
        """

        self._runner_parameters = runner_parameters
