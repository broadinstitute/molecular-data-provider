import connexion
import six

from openapi_server.models.aggregation_query import AggregationQuery  # noqa: E501
from openapi_server.models.collection_info import CollectionInfo  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.mole_pro_query import MoleProQuery  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server import util


def aggregate_post(aggregation_query, cache=None):  # noqa: E501
    """Aggregate multiple collections

    Aggregates multiple collections into one collections. # noqa: E501

    :param aggregation_query: aggregation query
    :type aggregation_query: dict | bytes
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: CollectionInfo
    """
    if connexion.request.is_json:
        aggregation_query = AggregationQuery.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def transform_post(mole_pro_query, cache=None):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param mole_pro_query: transformer query
    :type mole_pro_query: dict | bytes
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: CollectionInfo
    """
    if connexion.request.is_json:
        mole_pro_query = MoleProQuery.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def transformers_get():  # noqa: E501
    """Retrieve a list of transformers

    Provides a list of transformers and their descriptions. # noqa: E501


    :rtype: List[TransformerInfo]
    """
    return 'do some magic!'
