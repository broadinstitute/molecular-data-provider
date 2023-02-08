import connexion
import six

import sys
import json
import requests

from transformers.transformer import Transformer
from transformers.transformer import Producer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

species = "9606"


class StringTransformer(Transformer):

    variables = [
        'minimum combined score',
        'minimum neighborhood score',
        'minimum gene fusion score',
        'minimum cooccurence score',
        'minimum coexpression score',
        'minimum experimental score',
        'minimum database score',
        'minimum textmining score',
        'minimum best non-textmining component score',
        'maximum number of genes'
    ]

    def __init__(self):
        super().__init__(self.variables, definition_file='info/transformer_info.json')

    def expand(self, query_genes, controls):

        if len(query_genes) == 0:
            return []

        gene_list = []
        gene_id_map = {}  # Entrez to [original id(s)]
        genes = {}  # Entrez to [gene(s)]
        for gene in query_genes:
            entrez_id = self.entrez_gene_id(gene)
            if entrez_id is None and self.has_prefix('entrez', gene.id, 'Gene'):
                entrez_id = gene.id
            if entrez_id is not None:
                gene_list.append(gene)
                if entrez_id in gene_id_map.keys():  # multiple input nodes may have the same entrez identifier
                    gene_id_map[entrez_id].append(gene.id)
                    genes[entrez_id].append(gene)
                else:
                    gene_id_map[entrez_id] = [gene.id]
                    genes[entrez_id] = [gene]

        string_api_url = "https://string-db.org/api"
        output_format = "tsv-no-header"
        method = "interaction_partners"
        my_genes = [self.de_prefix('entrez', entrez_gene_id, "Gene") for entrez_gene_id in gene_id_map.keys()]

        limit = controls['maximum number of genes']
        required_score = controls['minimum combined score']
        my_app = "sharpener.ncats.io"

        ## Construct the request

        request_url = string_api_url + "/" + output_format + "/" + method + "?"
        request_url += "identifiers=%s" % "%0d".join(my_genes)
        request_url += "&" + "species=" + species
        request_url += "&" + "limit=" + str(limit)
        request_url += "&" + "required_score=" + str(float(required_score) * 1000)
        request_url += "&" + "caller_identity=" + my_app

        response = requests.get(request_url)
        if response.status_code != 200:
           msg = "Call to %s failed (%s)" % (string_api_url, response.status_code)
           return ({ "status": 500, "title": "Internal Server Error", "detail": msg, "type": "about:blank" }, 500 )

        symbol_to_id = {}

        lines = response.text.split('\n')

        for line in lines:
            l = line.strip().split("\t")
            if len(l) < 13:
                continue
            query_gene_symbol = l[2]
            partner_gene_symbol = l[3]
            combined_score = float(l[5])
            nscore = float(l[6])
            fscore = float(l[7])
            pscore = float(l[8])
            ascore = float(l[9])
            escore = float(l[10])
            dscore = float(l[11])
            tscore = float(l[12])

            if query_gene_symbol in symbol_to_id:
                query_gene_id = symbol_to_id[query_gene_symbol]
            else:
                query_gene_id = self.map_symbol_to_entrez_id(query_gene_symbol)
                symbol_to_id[query_gene_symbol] = query_gene_id

            if partner_gene_symbol in symbol_to_id:
                partner_gene_id = symbol_to_id[partner_gene_symbol]
            else:
                partner_gene_id = self.map_symbol_to_entrez_id(partner_gene_symbol)
                symbol_to_id[partner_gene_symbol] = partner_gene_id

            if combined_score >= float(controls['minimum combined score']) \
                    and nscore >= float(controls['minimum neighborhood score']) \
                    and fscore >= float(controls['minimum gene fusion score']) \
                    and pscore >= float(controls['minimum cooccurence score']) \
                    and ascore >= float(controls['minimum coexpression score']) \
                    and escore >= float(controls['minimum experimental score']) \
                    and dscore >= float(controls['minimum database score']) \
                    and tscore >= float(controls['minimum textmining score']) \
                    and max(nscore,fscore,pscore,ascore,escore,dscore) >= float(controls['minimum best non-textmining component score']):

                if partner_gene_id not in genes:
                    identifiers = {}
                    names = Names(partner_gene_symbol, synonyms=[], source=self.SOURCE, provided_by=self.PROVIDED_BY, name_type="")
                    genes[partner_gene_id] = [Element(
                        id=partner_gene_id,
                        biolink_class=self.biolink_class(self.OUTPUT_CLASS),
                        identifiers=identifiers,
                        names_synonyms=[names],
                        attributes=[],
                        connections=[],
                        source=self.SOURCE,
                        provided_by=self.PROVIDED_BY
                    )]

                    gene_list.append(genes[partner_gene_id][0])

                for original_gene_id in gene_id_map[query_gene_id]:
                    connection = Connection(
                        source_element_id=original_gene_id,
                        biolink_predicate=self.PREDICATE,
                        inverse_predicate=self.INVERSE_PREDICATE,
                        source=self.SOURCE,
                        provided_by=self.PROVIDED_BY,
                        attributes=[]
                    )

                    connection.attributes.append(Attribute(
                        attribute_type_id="biolink:primary_knowledge_source",
                        original_attribute_name="primary_knowledge_source",
                        value="infores:string",
                        attribute_source="infores:molepro",
                        provided_by=self.PROVIDED_BY
                    ))

                    conn_attribute_dict = {'combined score': combined_score,
                                           'neighborhood score': nscore,
                                           'gene fusion score': fscore,
                                           'cooccurence score': pscore,
                                           'coexpression score': ascore,
                                           'experimental score': escore,
                                           'database score': dscore,
                                           'textmining score': tscore}

                    for attribute in conn_attribute_dict.keys():
                        connection.attributes.append(Attribute(
                            attribute_type_id=attribute,
                            original_attribute_name=attribute,
                            value=conn_attribute_dict[attribute],
                            attribute_source=self.SOURCE,
                            provided_by=self.PROVIDED_BY
                        )
                        )
                    for partner_gene in genes[partner_gene_id]:
                        if partner_gene.connections is None:
                            partner_gene.connections = []
                        partner_gene.connections.append(connection)

        return gene_list

    def entrez_gene_id(self, gene):
        """
            Return value of the entrez_gene_id attribute
        """
        if gene.identifiers.get('entrez') is not None:
                return gene.identifiers.get('entrez')
        return None

    def map_symbol_to_entrez_id(self, gene_symbol):
        request_url = "https://mygene.info/v3/query?q=%s" % gene_symbol
        response = requests.get(request_url)
        if response.status_code != 200:
            return None
        response_object = eval(response.text)
        if 'hits' not in response_object:
            return None
        for hit in response_object['hits']:
            if 'taxid' in hit and str(hit['taxid']) == str(species):
                if 'entrezgene' in hit:
                    return self.add_prefix('entrez', str(hit['entrezgene']), 'Gene')
        return None
