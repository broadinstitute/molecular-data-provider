from openapi_server.models.gene_info import GeneInfo
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute

from transformers.transformer import Transformer

import scipy.stats
from numpy import array, empty

#available at http://software.broadinstitute.org/gsea/downloads.jsp
msigdb_gmt_files=['dat/c2.all.current.0.entrez.gmt', 'dat/c5.all.current.0.entrez.gmt']


class MSigDbExporter(Transformer):

    variables = ['max p-value', 'max q-value']


    def __init__(self):
        super().__init__(self.variables)


    def export(self, gene_list, controls):

        genes = dict([(entrez_gene_id(gene) if entrez_gene_id(gene) != None else gene.gene_id, None) for gene in gene_list])

        #Read in the gene sets
        gene_set_y_gene_list_y = {}
        gene_set_y_gene_list_n = {}
        gene_set_n_gene_list_y = {}
        gene_set_n_gene_list_n = {}
        gene_set_k = {}
        gene_set_N = {}
        gene_set_gene_ids = {}
        all_gene_set_gene_ids = set()
        for msigdb_gmt_file in msigdb_gmt_files:
            msigdb_gmt_fh = open(msigdb_gmt_file)
            for line in msigdb_gmt_fh:
                cols = line.strip().split('\t')
                if len(cols) < 3:
                    continue
                gene_set_id = cols[0]
                gene_ids = cols[2:len(cols)]
                overlap = len([x for x in gene_ids if x in genes])
                if overlap == 0:
                    continue
                gene_set_y_gene_list_y[gene_set_id] = overlap
                gene_set_gene_ids[gene_set_id] = gene_ids
                gene_set_N[gene_set_id] = len(gene_ids)

                gene_set_y_gene_list_n[gene_set_id] = gene_set_N[gene_set_id] - gene_set_y_gene_list_y[gene_set_id]
                gene_set_n_gene_list_y[gene_set_id] = len(genes) - gene_set_y_gene_list_y[gene_set_id]
                for x in gene_ids:
                    all_gene_set_gene_ids.add(x)
            msigdb_gmt_fh.close()
        M = len(all_gene_set_gene_ids)

        gene_set_pvalues = {}
        gene_set_qvalues = {}
        gene_set_odds_ratios = {}
        all_pvalues = []
        all_gene_set_ids = []

        for gene_set_id in gene_set_y_gene_list_y:
            gene_set_n_gene_list_n[gene_set_id] = M - gene_set_y_gene_list_y[gene_set_id] - gene_set_y_gene_list_n[gene_set_id] - gene_set_n_gene_list_y[gene_set_id]

            table = [[gene_set_y_gene_list_y[gene_set_id], gene_set_y_gene_list_n[gene_set_id]], [gene_set_n_gene_list_y[gene_set_id], gene_set_n_gene_list_n[gene_set_id]]]
            odds_ratio, pvalue = scipy.stats.fisher_exact(table)

            all_pvalues.append(pvalue)
            all_gene_set_ids.append(gene_set_id)

            if pvalue < controls['max p-value']:
                gene_set_pvalues[gene_set_id] = pvalue
                gene_set_odds_ratios[gene_set_id] = odds_ratio

        all_qvalues = correct_pvalues_for_multiple_testing(all_pvalues, correction_type="Benjamini-Hochberg")
        for i, gene_set_id in enumerate(all_gene_set_ids):
            if gene_set_id in gene_set_pvalues and all_qvalues[i] < controls['max q-value']:
                gene_set_qvalues[gene_set_id] = all_qvalues[i]

        pathways = []
        for gene_set_id in sorted(gene_set_qvalues.keys(), key=lambda x: gene_set_qvalues[x]):
            enriched_gene_set = Element(
                id = 'MSigDB:'+gene_set_id,
                biolink_class = 'Pathway',
                identifiers = {'MSigDB':'MSigDB:'+gene_set_id},
                names_synonyms = [Names(
                    name = gene_set_id,
                    synonyms = [],
                    source = 'MSigDB',
                    url = 'http://software.broadinstitute.org/gsea/msigdb/cards/{}.html'.format(gene_set_id)
                )],
                attributes = [
                    Attribute(
                        name = 'p-value',
                        value = str(gene_set_pvalues[gene_set_id]),
                        source = self.info.name
                    ),
                    Attribute(
                        name = 'q-value',
                        value = str(gene_set_qvalues[gene_set_id]),
                        source = self.info.name
                    ),
                    Attribute(
                        name = 'odds ratio',
                        value = str(gene_set_odds_ratios[gene_set_id]),
                        source = self.info.name
                    ),
                ],
                source = self.info.name
            )
            pathways.append(enriched_gene_set)
        return pathways

def entrez_gene_id(gene: GeneInfo):
    """
        Return value of the entrez_gene_id attribute
    """
    if (gene.identifiers is not None and gene.identifiers.entrez is not None):
        if (gene.identifiers.entrez.startswith('NCBIGene:')):
            return gene.identifiers.entrez[9:]
        else:
            return gene.identifiers.entrez
    return None

def correct_pvalues_for_multiple_testing(pvalues, correction_type = "Benjamini-Hochberg"):
    """
    consistent with R - print correct_pvalues_for_multiple_testing([0.0, 0.01, 0.029, 0.03, 0.031, 0.05, 0.069, 0.07, 0.071, 0.09, 0.1])
    """
    pvalues = array(pvalues)
    n = int(pvalues.shape[0])
    new_pvalues = empty(n)
    if correction_type == "Bonferroni":
        new_pvalues = n * pvalues
    elif correction_type == "Bonferroni-Holm":
        values = [ (pvalue, i) for i, pvalue in enumerate(pvalues) ]
        values.sort()
        for rank, vals in enumerate(values):
            pvalue, i = vals
            new_pvalues[i] = (n-rank) * pvalue
    elif correction_type == "Benjamini-Hochberg":
        values = [ (pvalue, i) for i, pvalue in enumerate(pvalues) ]
        values.sort()
        values.reverse()
        new_values = []
        for i, vals in enumerate(values):
            rank = n - i
            pvalue, index = vals
            new_values.append((n/rank) * pvalue)
        for i in range(0, int(n)-1):
            if new_values[i] < new_values[i+1]:
                new_values[i+1] = new_values[i]
        for i, vals in enumerate(values):
            pvalue, index = vals
            new_pvalues[index] = new_values[i]
    return new_pvalues
