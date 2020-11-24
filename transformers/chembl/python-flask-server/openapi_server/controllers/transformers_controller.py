import connexion
import six

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server import util

from openapi_server.controllers.chembl_db_transformer import ChemblProducer
from openapi_server.controllers.chembl_transformer import ChemblTargetTransformer
from openapi_server.controllers.chembl_db_transformer import ChemblIndicationsExporter
from openapi_server.controllers.chembl_db_transformer import ChemblAssayExporter
from openapi_server.controllers.chembl_db_transformer import ChemblMechanismExporter
from openapi_server.controllers.chembl_db_transformer import ChemblMetaboliteTransformer

transformer = {
    'molecules':ChemblProducer(),
    'targets': ChemblTargetTransformer(),
    'indications': ChemblIndicationsExporter(),
    'assays': ChemblAssayExporter(),
    'mechanisms': ChemblMechanismExporter(),
    'metabolites': ChemblMetaboliteTransformer()
}

def service_transform_post(service, body):  # noqa: E501
    """Transform a list of genes or compounds

    Depending on the function of a transformer, creates, expands, or filters a list. # noqa: E501

    :param service: ChEMBL service
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

    :param service: ChEMBL service
    :type service: str

    :rtype: TransformerInfo
    """
    return transformer[service].info
