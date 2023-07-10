import connexion
import six

from openapi_server.models.collection import Collection  # noqa: E501
from openapi_server.models.collection_info import CollectionInfo  # noqa: E501
from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server import util


def compound_by_id_compound_id_get(compound_id, cache=None):  # noqa: E501
    """Retrieve a compound by an id

     # noqa: E501

    :param compound_id: Id of a compound (CURIE). Can be PubChem CID, DrugBank id, ChEMBL id, ChEBI id , or HMDB id.
    :type compound_id: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Element
    """
    return 'do some magic!'


def compound_by_id_post(request_body, cache=None):  # noqa: E501
    """Retrieve multiple compounds specified by ids

     # noqa: E501

    :param request_body: Ids (CURIEs) of the compound
    :type request_body: List[str]
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: CollectionInfo
    """
    return 'do some magic!'


def compound_by_name_name_get(name, cache=None):  # noqa: E501
    """Retrieve a compound by a name

     # noqa: E501

    :param name: Name of a compound.
    :type name: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Collection
    """
    return 'do some magic!'


def compound_by_name_post(request_body, cache=None):  # noqa: E501
    """Retrieve multiple compounds specified by names

     # noqa: E501

    :param request_body: Names of the compound
    :type request_body: List[str]
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: CollectionInfo
    """
    return 'do some magic!'


def compound_by_structure_post(body, cache=None):  # noqa: E501
    """Retrieve a compound by a structure

     # noqa: E501

    :param body: Structure of the compounds in SMILES, InChI, or InChI-key notation
    :type body: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Element
    """
    return 'do some magic!'
