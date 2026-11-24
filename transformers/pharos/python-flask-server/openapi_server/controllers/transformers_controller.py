import connexion
import json
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server import encoder
from openapi_server import util

from openapi_server.controllers.pharos_transformer import PharosGeneInteractionsTransformer
from openapi_server.controllers.pharos_transformer import PharosCompoundProducer

transformer = { 'gene_targets': PharosGeneInteractionsTransformer(),
                'compounds': PharosCompoundProducer()
}

def service_transform_post(service, body, cache=None):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param service: Service provided by this transformer.
    :type service: str
    :param transformer_query: transformer query
    :type transformer_query: dict | bytes
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Union[List[Element], Tuple[List[Element], int], Tuple[List[Element], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        transformer_query = TransformerQuery.from_dict(connexion.request.get_json())  # noqa: E501
    result = transformer[service].transform(transformer_query)
    return json.loads(json.dumps(result, cls=encoder.JSONEncoder))


def service_transformer_info_get(service, cache=None):  # noqa: E501
    """Retrieve transformer info

    Provides information about the transformer. # noqa: E501

    :param service: Service provided by this transformer.
    :type service: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Union[TransformerInfo, Tuple[TransformerInfo, int], Tuple[TransformerInfo, int, Dict[str, str]]
    """
    result = transformer[service].transformer_info(cache)
    return json.loads(json.dumps(result, cls=encoder.JSONEncoder))
