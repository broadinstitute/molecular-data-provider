# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.operation_annotate import OperationAnnotate
from openapi_server.models.operation_annotate_edges import OperationAnnotateEdges
from openapi_server.models.operation_annotate_nodes import OperationAnnotateNodes
from openapi_server.models.operation_annotate_runner_parameters import OperationAnnotateRunnerParameters
from openapi_server.models.operation_bind import OperationBind
from openapi_server.models.operation_complete_results import OperationCompleteResults
from openapi_server.models.operation_enrich_results import OperationEnrichResults
from openapi_server.models.operation_fill import OperationFill
from openapi_server.models.operation_filter_kgraph import OperationFilterKgraph
from openapi_server.models.operation_filter_kgraph_continuous_kedge_attribute import OperationFilterKgraphContinuousKedgeAttribute
from openapi_server.models.operation_filter_kgraph_discrete_kedge_attribute import OperationFilterKgraphDiscreteKedgeAttribute
from openapi_server.models.operation_filter_kgraph_discrete_knode_attribute import OperationFilterKgraphDiscreteKnodeAttribute
from openapi_server.models.operation_filter_kgraph_orphans import OperationFilterKgraphOrphans
from openapi_server.models.operation_filter_kgraph_percentile import OperationFilterKgraphPercentile
from openapi_server.models.operation_filter_kgraph_std_dev import OperationFilterKgraphStdDev
from openapi_server.models.operation_filter_kgraph_top_n import OperationFilterKgraphTopN
from openapi_server.models.operation_filter_results import OperationFilterResults
from openapi_server.models.operation_filter_results_top_n import OperationFilterResultsTopN
from openapi_server.models.operation_lookup import OperationLookup
from openapi_server.models.operation_lookup_and_score import OperationLookupAndScore
from openapi_server.models.operation_overlay import OperationOverlay
from openapi_server.models.operation_overlay_compute_jaccard import OperationOverlayComputeJaccard
from openapi_server.models.operation_overlay_compute_ngd import OperationOverlayComputeNgd
from openapi_server.models.operation_overlay_connect_knodes import OperationOverlayConnectKnodes
from openapi_server.models.operation_overlay_fisher_exact_test import OperationOverlayFisherExactTest
from openapi_server.models.operation_restate import OperationRestate
from openapi_server.models.operation_score import OperationScore
from openapi_server.models.operation_sort_results import OperationSortResults
from openapi_server.models.operation_sort_results_edge_attribute import OperationSortResultsEdgeAttribute
from openapi_server.models.operation_sort_results_node_attribute import OperationSortResultsNodeAttribute
from openapi_server.models.operation_sort_results_score import OperationSortResultsScore
from openapi_server.models.operation_sort_results_score_parameters import OperationSortResultsScoreParameters
from openapi_server import util

from openapi_server.models.operation_annotate import OperationAnnotate  # noqa: E501
from openapi_server.models.operation_annotate_edges import OperationAnnotateEdges  # noqa: E501
from openapi_server.models.operation_annotate_nodes import OperationAnnotateNodes  # noqa: E501
from openapi_server.models.operation_annotate_runner_parameters import OperationAnnotateRunnerParameters  # noqa: E501
from openapi_server.models.operation_bind import OperationBind  # noqa: E501
from openapi_server.models.operation_complete_results import OperationCompleteResults  # noqa: E501
from openapi_server.models.operation_enrich_results import OperationEnrichResults  # noqa: E501
from openapi_server.models.operation_fill import OperationFill  # noqa: E501
from openapi_server.models.operation_filter_kgraph import OperationFilterKgraph  # noqa: E501
from openapi_server.models.operation_filter_kgraph_continuous_kedge_attribute import OperationFilterKgraphContinuousKedgeAttribute  # noqa: E501
from openapi_server.models.operation_filter_kgraph_discrete_kedge_attribute import OperationFilterKgraphDiscreteKedgeAttribute  # noqa: E501
from openapi_server.models.operation_filter_kgraph_discrete_knode_attribute import OperationFilterKgraphDiscreteKnodeAttribute  # noqa: E501
from openapi_server.models.operation_filter_kgraph_orphans import OperationFilterKgraphOrphans  # noqa: E501
from openapi_server.models.operation_filter_kgraph_percentile import OperationFilterKgraphPercentile  # noqa: E501
from openapi_server.models.operation_filter_kgraph_std_dev import OperationFilterKgraphStdDev  # noqa: E501
from openapi_server.models.operation_filter_kgraph_top_n import OperationFilterKgraphTopN  # noqa: E501
from openapi_server.models.operation_filter_results import OperationFilterResults  # noqa: E501
from openapi_server.models.operation_filter_results_top_n import OperationFilterResultsTopN  # noqa: E501
from openapi_server.models.operation_lookup import OperationLookup  # noqa: E501
from openapi_server.models.operation_lookup_and_score import OperationLookupAndScore  # noqa: E501
from openapi_server.models.operation_overlay import OperationOverlay  # noqa: E501
from openapi_server.models.operation_overlay_compute_jaccard import OperationOverlayComputeJaccard  # noqa: E501
from openapi_server.models.operation_overlay_compute_ngd import OperationOverlayComputeNgd  # noqa: E501
from openapi_server.models.operation_overlay_connect_knodes import OperationOverlayConnectKnodes  # noqa: E501
from openapi_server.models.operation_overlay_fisher_exact_test import OperationOverlayFisherExactTest  # noqa: E501
from openapi_server.models.operation_restate import OperationRestate  # noqa: E501
from openapi_server.models.operation_score import OperationScore  # noqa: E501
from openapi_server.models.operation_sort_results import OperationSortResults  # noqa: E501
from openapi_server.models.operation_sort_results_edge_attribute import OperationSortResultsEdgeAttribute  # noqa: E501
from openapi_server.models.operation_sort_results_node_attribute import OperationSortResultsNodeAttribute  # noqa: E501
from openapi_server.models.operation_sort_results_score import OperationSortResultsScore  # noqa: E501
from openapi_server.models.operation_sort_results_score_parameters import OperationSortResultsScoreParameters  # noqa: E501

class Schema1(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, parameters=None, runner_parameters=None):  # noqa: E501
        """Schema1 - a model defined in OpenAPI

        :param id: The id of this Schema1.  # noqa: E501
        :type id: str
        :param parameters: The parameters of this Schema1.  # noqa: E501
        :type parameters: OperationSortResultsScoreParameters
        :param runner_parameters: The runner_parameters of this Schema1.  # noqa: E501
        :type runner_parameters: OperationAnnotateRunnerParameters
        """
        self.openapi_types = {
            'id': str,
            'parameters': OperationSortResultsScoreParameters,
            'runner_parameters': OperationAnnotateRunnerParameters
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
    def from_dict(cls, dikt) -> 'Schema1':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The schema_1 of this Schema1.  # noqa: E501
        :rtype: Schema1
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this Schema1.


        :return: The id of this Schema1.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Schema1.


        :param id: The id of this Schema1.
        :type id: str
        """
        allowed_values = ["sort_results_score"]  # noqa: E501
        if id not in allowed_values:
            raise ValueError(
                "Invalid value for `id` ({0}), must be one of {1}"
                .format(id, allowed_values)
            )

        self._id = id

    @property
    def parameters(self):
        """Gets the parameters of this Schema1.


        :return: The parameters of this Schema1.
        :rtype: OperationSortResultsScoreParameters
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this Schema1.


        :param parameters: The parameters of this Schema1.
        :type parameters: OperationSortResultsScoreParameters
        """
        if parameters is None:
            raise ValueError("Invalid value for `parameters`, must not be `None`")  # noqa: E501

        self._parameters = parameters

    @property
    def runner_parameters(self):
        """Gets the runner_parameters of this Schema1.


        :return: The runner_parameters of this Schema1.
        :rtype: OperationAnnotateRunnerParameters
        """
        return self._runner_parameters

    @runner_parameters.setter
    def runner_parameters(self, runner_parameters):
        """Sets the runner_parameters of this Schema1.


        :param runner_parameters: The runner_parameters of this Schema1.
        :type runner_parameters: OperationAnnotateRunnerParameters
        """

        self._runner_parameters = runner_parameters
