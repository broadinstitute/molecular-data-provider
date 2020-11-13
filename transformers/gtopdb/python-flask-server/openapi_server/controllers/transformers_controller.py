import connexion
import six

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server import util

#from transformers.transformer import Transformer

from openapi_server.controllers.gtopdb_transformer import GtoPdbProducer
from openapi_server.controllers.gtopdb_transformer import GtoPdbTargetsTransformer
from openapi_server.controllers.gtopdb_transformer import GtoPdbInhibitorsTransformer

transformer = {
    'molecules': GtoPdbProducer(),
    'targets': GtoPdbTargetsTransformer(),
    'inhibitors': GtoPdbInhibitorsTransformer()
}

def service_transform_post(service, body):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param service: DrugBank service
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

    :param service: DrugBank service
    :type service: str

    :rtype: TransformerInfo
    """
    return transformer[service].info
