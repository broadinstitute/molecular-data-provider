import connexion
import six

from openapi_server.models.element import Element  # noqa: E501
from openapi_server.models.error_msg import ErrorMsg  # noqa: E501
from openapi_server.models.transformer_info import TransformerInfo  # noqa: E501
from openapi_server.models.transformer_query import TransformerQuery  # noqa: E501
from openapi_server import util


from openapi_server.controllers.drugbank_transformer import DrugBankMolecularProducer, DrugBankDrugProducer, DrugBankCompoundProducer, DrugBankInhibitorsTransformer, DrugBankGeneInteractionsTransformer, DrugBankProteinInteractionsTransformer

transformer = {'compounds':DrugBankCompoundProducer(), 
               'molecules':DrugBankMolecularProducer(),
              #'drugs':DrugBankDrugProducer(), 
              'inhibitors':DrugBankInhibitorsTransformer('target', 'inhibitors'),
              'substrates':DrugBankInhibitorsTransformer('enzyme','substrates'),
              'transporter_substrates':DrugBankInhibitorsTransformer('transporter','transporter substrates'),
              'carrier_substrates':DrugBankInhibitorsTransformer('carrier','carrier substrates'),
              'gene_targets':DrugBankGeneInteractionsTransformer('target'),
              'gene_enzymes':DrugBankGeneInteractionsTransformer('enzyme'),
              'gene_transporters':DrugBankGeneInteractionsTransformer('transporter'),
              'gene_carriers':DrugBankGeneInteractionsTransformer('carrier'),
              'protein_targets':DrugBankProteinInteractionsTransformer('target'),
              'protein_enzymes':DrugBankProteinInteractionsTransformer('enzyme'),
              'protein_transporters':DrugBankProteinInteractionsTransformer('transporter'),
              'protein_carriers':DrugBankProteinInteractionsTransformer('carrier')
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

    :rtype: List[Element]
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

    :rtype: TransformerInfo
    """
    return transformer[service].transformer_info(cache)
