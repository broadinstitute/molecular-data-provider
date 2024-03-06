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


def input_class_output_class_transform_post(input_class, output_class, transformer_query, cache=None):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param input_class: input class for the transformer
    :type input_class: str
    :param output_class: output class for the transformer
    :type output_class: str
    :param transformer_query: transformer query
    :type transformer_query: dict | bytes
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Union[List[Element], Tuple[List[Element], int], Tuple[List[Element], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        transformer_query = TransformerQuery.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def input_class_output_class_transformer_info_get(input_class, output_class, cache=None):  # noqa: E501
    """Retrieve transformer info

    Provides information about the transformer. # noqa: E501

    :param input_class: input class for the transformer
    :type input_class: str
    :param output_class: output class for the transformer
    :type output_class: str
    :param cache: Directive for handling caching, can be &#39;yes&#39; (default), &#39;no&#39;, &#39;bypass&#39; or &#39;remove&#39;
    :type cache: str

    :rtype: Union[TransformerInfo, Tuple[TransformerInfo, int], Tuple[TransformerInfo, int, Dict[str, str]]
    """
    return 'do some magic!'
