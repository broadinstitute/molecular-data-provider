import connexion
import six
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server import util

from openapi_server.controllers.inxight_drugs_transformer import Inxight_SubstancesProducer
from openapi_server.controllers.inxight_drugs_transformer import Inxight_DrugsRelationshipTransformer
from openapi_server.controllers.inxight_drugs_transformer import Inxight_DrugsTransformer
from openapi_server.controllers.inxight_drugs_transformer import Inxight_DrugsActiveIngredientsTransformer

transformer = { 
    'substances':Inxight_SubstancesProducer(),
    'relationships':Inxight_DrugsRelationshipTransformer(),
    'drugs':Inxight_DrugsTransformer(),
    'active_ingredients':Inxight_DrugsActiveIngredientsTransformer()
}

def service_transform_post(service, body, cache=None):  # noqa: E501
    """Transform a list of drugs or substances

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
    return transformer[service].transform(transformer_query) 


def service_transformer_info_get(service, cache=None):  # noqa: E501
    """Retrieve transformer info

    Provides information about the transformer. # noqa: E501

    :param service: Service provided by this transformer.
    :type service: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Union[TransformerInfo, Tuple[TransformerInfo, int], Tuple[TransformerInfo, int, Dict[str, str]]
    """
    return transformer[service].transformer_info(cache)
