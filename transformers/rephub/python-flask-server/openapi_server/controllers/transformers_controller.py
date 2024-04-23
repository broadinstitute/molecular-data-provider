import connexion
import six

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server import util

from openapi_server.controllers.repurposing_hub import RepurposingHubProducer, FeaturesTransformer, TargetsTransformer, IndicationsTransformer

transformer = {'compounds':RepurposingHubProducer(), 'targets':TargetsTransformer(), 'indications':IndicationsTransformer()}

def service_transform_post(service, body):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param service: ChemBank service
    :type service: str
    :param transformer_query: transformer query
    :type transformer_query: dict | bytes

    :rtype: List[Element]
    """
    if connexion.request.is_json:
        transformer_query = TransformerQuery.from_dict(connexion.request.get_json())  # noqa: E501
    return transformer[service].transform(transformer_query)


def service_transformer_info_get(service):  # noqa: E501
    """Retrieve transformer info

    Provides information about the transformer. # noqa: E501

    :param service: ChemBank service
    :type service: str

    :rtype: TransformerInfo
    """
    return transformer[service].info
