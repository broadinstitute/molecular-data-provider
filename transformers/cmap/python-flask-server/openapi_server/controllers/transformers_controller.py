import connexion
import six

from openapi_server.models.compound_info import CompoundInfo  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.gene_info import GeneInfo  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server import util


from openapi_server.controllers.cmap_expander import CmapExpander

transformers = {
    'gene': {
        'gene': CmapExpander('gene', 'gene'),
        'compound':  CmapExpander('gene', 'compound')
        },
    'compound': {
        'gene': CmapExpander('compound', 'gene'),
        'compound':  CmapExpander('compound', 'compound')
        }
    }

classes = {'compound', 'gene'}


def input_class_compound_transform_post(input_class, body):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param input_class: input class for the transformer
    :type input_class: str
    :param transformer_query: transformer query
    :type transformer_query: dict | bytes

    :rtype: List[CompoundInfo]
    """
    if connexion.request.is_json:
        transformer_query = TransformerQuery.from_dict(connexion.request.get_json())  # noqa: E501
    if input_class in classes:
        return transformers[input_class]['compound'].transform(transformer_query)


def input_class_gene_transform_post(input_class, body):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param input_class: input class for the transformer
    :type input_class: str
    :param transformer_query: transformer query
    :type transformer_query: dict | bytes

    :rtype: List[GeneInfo]
    """
    if connexion.request.is_json:
        transformer_query = TransformerQuery.from_dict(connexion.request.get_json())  # noqa: E501
    if input_class in classes:
        return transformers[input_class]['gene'].transform(transformer_query)


def input_class_output_class_transformer_info_get(input_class, output_class):  # noqa: E501
    """Retrieve transformer info

    Provides information about the transformer. # noqa: E501

    :param input_class: input class for the transformer
    :type input_class: str
    :param output_class: output class for the transformer
    :type output_class: str

    :rtype: TransformerInfo
    """
    if input_class in classes and output_class in classes:
        return transformers[input_class][output_class].info
    else:
        msg = "invalid input or output class: '"+input_class+"/"+output_class+"'"
        return ({ "status": 400, "title": "Bad Request", "detail": msg, "type": "about:blank" }, 400 )
