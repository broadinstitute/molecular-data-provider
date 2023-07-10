import connexion
import six

from openapi_server.models.collection import Collection  # noqa: E501
from openapi_server.models.compound_list import CompoundList  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.gene_list import GeneList  # noqa: E501
from openapi_server import util


def collection_collection_id_get(collection_id, cache=None):  # noqa: E501
    """Retrieve a collection

    Retrieves a collection for a given collection id. # noqa: E501

    :param collection_id: collection id
    :type collection_id: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Collection
    """
    return 'do some magic!'


def compound_list_list_id_get(list_id, cache=None):  # noqa: E501
    """Retrieve a compound list

    Retrieves a compound list for a given compound-list id. # noqa: E501

    :param list_id: compound-list id
    :type list_id: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: CompoundList
    """
    return 'do some magic!'


def gene_list_list_id_get(list_id, cache=None):  # noqa: E501
    """Retrieve a gene list

    Retrieves a gene list for a given gene-list id. # noqa: E501

    :param list_id: gene-list id
    :type list_id: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: GeneList
    """
    return 'do some magic!'
