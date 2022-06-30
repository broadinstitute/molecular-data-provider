from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute

from transformers.transformer import Transformer

import sqlite3
import scipy.stats
import numpy as np
from numpy import array, empty

#available at http://software.broadinstitute.org/gsea/downloads.jsp
msigdb_gmt_files=['dat/c2.all.current.0.entrez.gmt', 'dat/c5.all.current.0.entrez.gmt'] # WE MAY HAVE TO CHANGE THAT AND THE Exporter function


SOURCE = 'msigdb_v7.4'
# CURIE prefix
DOC_URL = 'https://software.broadinstitute.org/cancer/software/gsea/wiki/index.php/Main_Page'

class MSigDBEnrichment(Transformer): 
    # NEW version of the exporter -> to change controls    
    variables = ['maximum p-value', 'maximum q-value','correction method','total genes count','total pathways count']


    def __init__(self):
        super().__init__(self.variables,definition_file='info/enrichment_transformer_info.json')


    def export(self,gene_list, controls):
        # for each of the pathways:
        #       (1) get overlapping venn table T
        #       (2) calculate enrichment from Fisher exact test
        #       (3) correct for multiple testing
        #       (4) filter according parameters
        #       (5) fill biolink structure

        # set total number of unique NCBI Entrez gene IDs : this is not perfect due to sequencing of the gene 
        # sets being done at different time points so potentially slightly different total number of genes.  It does not change a lot the p-values anyway
        # To get the total number we went to https://www.genenames.org/download/statistics-and-files/ and got the total unique approved symbols 
        # We've chosen to hard code it to avoid un-necessary/computationnally expensive operations but this number may be revised from time to time when new builds are available.
        n_tot_genes = int(controls["total genes count"])
        n_total_pathways = int(controls["total pathways count"])

        # identify genesets
        genes = [self.de_prefix('entrez',gene.identifiers.get('entrez')) for gene in gene_list if gene.identifiers.get('entrez') is not None]
        pathway_list = set([pathw['STANDARD_NAME'] for gene in genes for pathw in get_pathways(gene)]) # get all unique pathways that have at least 1 overlapping gene id
        
        print('***************************************')

        
        # variable instantiation:
        odds_ratio_list = [None] * len(pathway_list)
        pvalue_list = [None] * len(pathway_list)
        overlap_list = [None] * len(pathway_list)
        idx = 0
        # compute Fisher exact test
        for pathways in pathway_list: 
            gene_set = [str(g['MEMBERS_3']) for g in get_genes(pathways)]
            T,overlap = gene_list_venn(genes,gene_set,n_tot_genes)
            odds_ratio, pvalue = scipy.stats.fisher_exact(T,alternative='greater')
            if overlap is not None:
                overlap_list[idx] = overlap
            if odds_ratio is not None:
                odds_ratio_list[idx] = odds_ratio
            if pvalue is not None:
                pvalue_list[idx] = pvalue
            idx = idx + 1
            if idx % 100 == 0:
                print(idx)

        #print(len(overlap_list)) 229
        # padding for non overlapping gene sets:
        n_pathway_list = int(len(pathway_list))
        n = n_total_pathways-n_pathway_list
        pvalue_list.extend([1] * n) # add 1 to remaining 0 overlap pathways to keep baseline comparable
        qvalue_list = correct_pvalues_for_multiple_testing(pvalue_list, correction_type=controls["correction method"])
        # filtering:
        pvalue_list = [p for i,p in enumerate(pvalue_list) if i<n_pathway_list]
        qvalue_list = [q for i,q in enumerate(qvalue_list) if i<n_pathway_list]
        qmax = float(controls["maximum q-value"])
        pmax = float(controls["maximum p-value"])
        mask = list(np.array([q<=qmax for q in qvalue_list]) & np.array([p<=pmax for p in pvalue_list]))
        print(qvalue_list)
        print(mask)
        #mask[[0,1]] = [True,True] ####### FOR TESTING PURPOSES

        # put values in Element:
        pathway_list = np.array(list(pathway_list))
        overlap_list = np.array(overlap_list)
        odds_ratio_list = np.array(odds_ratio_list)
        pvalue_list = np.array(pvalue_list)
        qvalue_list = np.array(qvalue_list)
        print(pathway_list[mask])
        p = fill_enriched_pathway_element(self,controls["correction method"],pathway_list[mask],overlap_list[mask],odds_ratio_list[mask],pvalue_list[mask],qvalue_list[mask])
        
        #print(p)
        print('***************************************')
        if len(p) != 0:
            pathways = p
        else:
            pathways = None
         

        return pathways



class MSigDbExporter_old(Transformer):

    variables = ['max p-value', 'max q-value']


    def __init__(self):
        super().__init__(self.variables,definition_file='info/enrichment_transformer_info.json')

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

# def entrez_gene_id(gene): # do we need this anymore?
#     """
#         Return value of the entrez_gene_id attribute
#     """
#     if (gene.identifiers is not None and gene.identifiers.entrez is not None):
#         if (gene.identifiers.entrez.startswith('NCBIGene:')):
#             return gene.identifiers.entrez[9:]
#         else:
#             return gene.identifiers.entrez
#     return None

# def correct_pvalues_for_multiple_testing(pvalues, correction_type = "Benjamini-Hochberg"):
#     """
#     consistent with R - print correct_pvalues_for_multiple_testing([0.0, 0.01, 0.029, 0.03, 0.031, 0.05, 0.069, 0.07, 0.071, 0.09, 0.1])
#     """
#     pvalues = array(pvalues)
#     n = int(pvalues.shape[0])
#     new_pvalues = empty(n)
#     if correction_type == "Bonferroni":
#         new_pvalues = n * pvalues
#     elif correction_type == "Bonferroni-Holm":
#         values = [ (pvalue, i) for i, pvalue in enumerate(pvalues) ]
#         values.sort()
#         for rank, vals in enumerate(values):
#             pvalue, i = vals
#             new_pvalues[i] = (n-rank) * pvalue
#     elif correction_type == "Benjamini-Hochberg":
#         values = [ (pvalue, i) for i, pvalue in enumerate(pvalues) ]
#         values.sort()
#         values.reverse()
#         new_values = []
#         for i, vals in enumerate(values):
#             rank = n - i
#             pvalue, index = vals
#             new_values.append((n/rank) * pvalue)
#         for i in range(0, int(n)-1):
#             if new_values[i] < new_values[i+1]:
#                 new_values[i+1] = new_values[i]
#         for i, vals in enumerate(values):
#             pvalue, index = vals
#             new_pvalues[index] = new_values[i]
#     return new_pvalues

def gene_list_venn(gene_list1,gene_list2,n_genes_baseline):
    # function that returns the overlap groups from 2 lists of gene ids. Returns a table (list of lists which columns are [in1in2],[in1out2],[out1in2],[out1out2])
    gene_set1 = set(gene_list1)
    gene_set2 = set(gene_list2)

    members_overlap = list(gene_set1.intersection(gene_set2))
    in1in2 = len(members_overlap)
    in1out2 = len(gene_set1.difference(gene_set2))
    out1in2 = len(gene_set2.difference(gene_set1))
    out1out2 = int(n_genes_baseline) - in1in2 - in1out2 - out1in2

    T_venn = [[in1in2,in1out2],[out1in2,out1out2]]
    
    return T_venn,members_overlap


def correct_pvalues_for_multiple_testing(pvalues, correction_type = "Benjamini-Hochberg"): # TO MAKE SIMPLER IF POSSIBLE WITH DIFFERENT CONTROLS FOR CORRECTION
    """
    consistent with R - print correct_pvalues_for_multiple_testing([0.0, 0.01, 0.029, 0.03, 0.031, 0.05, 0.069, 0.07, 0.071, 0.09, 0.1])
    """

    pvalues = np.array(pvalues,dtype=float, ndmin=1)
    n = int(pvalues.shape[0])
    new_pvalues = empty(n)
    if correction_type == "Bonferroni":
        new_pvalues = n * pvalues
    elif correction_type == "Bonferroni-Holm":
        values = [ (pvalue, i) for i, pvalue in enumerate(pvalues) ]
        values.sort(key=lambda x:x[0]) # added this argument in case of repeated number
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

def fill_enriched_pathway_element(Transformer,corr_type,pathway_list,overlap,OR,pvalues,qvalues):
    pathways_l = []
    genes_l = []
    idx_qvalues_sorted = np.argsort(qvalues)
    for i in idx_qvalues_sorted:
        pathway_name = pathway_list[i]

        # CREATE ELEMENT BY CALLING SELF.ELEMENT (LOOK AT NEWER TRANSFORMERS like https://github.com/broadinstitute/molecular-data-provider/blob/master/transformers/chebi/python-flask-server/openapi_server/controllers/chebi_transformer.py
        id = Transformer.add_prefix('msigdb', pathway_name)
        biolink_class = Transformer.biolink_class('pathway')
        identifiers = {'msigdb':id}
        names = []
        element = Transformer.Element(id, biolink_class, identifiers, names)

        # ADD ATTRIBUTES AND NAMES 
        if qvalues is not None:
            ## overlapping genes:
            gene_id_list = overlap[i]
            T = MSigDBGeneTransformer()
            biolink_class = T.biolink_class('gene')
            for g in gene_id_list:
                id = T.add_prefix('entrez', str(g))
                identifiers = {'entrez':id}
                names = []
                g_element = T.Element(id, biolink_class, identifiers, names)
                genes_l.append(g_element)

            attribute = Transformer.Attribute('overlap', genes_l)
            genes_l = []
            attribute.description = 'overlapping genes between your gene list and the pathway'
            element.attributes.append(attribute)
            attribute = Transformer.Attribute('odds-ratio', OR[i])
            attribute.description = 'overlap odds-ratio'
            element.attributes.append(attribute)
            attribute = Transformer.Attribute('p-value', pvalues[i])
            attribute.description = 'p-value associated with one-sided hypergeometric (Fisher exact) test'
            element.attributes.append(attribute)
            attribute = Transformer.Attribute('q-value', qvalues[i])
            attribute.description = 'p-value adjusted after multiple testing correction ('  + corr_type + ')'
            element.attributes.append(attribute)

            # ADD ELEMENT TO PATHWAY LIST
            pathways_l.append(element)
    print(pathways_l)
    return pathways_l

class MSigDBPathwayTransformer(Transformer):
    # gene to pathway

    variables = []


    def __init__(self):
        super().__init__(self.variables,definition_file='info/pathways_transformer_info.json')

    sub_categories = {
        'CP:KEGG': 'kegg',
        'CP:WIKIPATHWAYS':'wikipathways',
        'HPO': 'hpo',
        'GO:BP':'go',
        'GO:CC':'go',
        'GO:MF':'go',
        'CP:REACTOME': 'reactome',
        'CP:BIOCARTA': 'biocarta'
    }

    def identifier(self, field_name, value):
        biolink_class = 'pathway'
        if field_name == 'hpo':
            biolink_class = 'disease' 
        if field_name == 'go':
            biolink_class = 'BiologicalProcess' 
        return self.add_prefix(field_name, value, biolink_class)

    def export(self, gene_list, controls):
        pathway_list = []
        pathways = {}
        for gene in gene_list:
            gene_id = self.de_prefix('entrez',gene.identifiers.get('entrez'))
            for row in get_pathways(gene_id):
                pathway_name = row['STANDARD_NAME']
                if pathway_name not in pathways:
                    # CREATE ELEMENT BY CALLING SELF.ELEMENT (LOOK AT NEWER TRANSFORMERS like https://github.com/broadinstitute/scb-kp-dev/blob/master/transformers/chebi/python-flask-server/openapi_server/controllers/chebi_transformer.py
                    id = self.add_prefix('msigdb', pathway_name)
                    biolink_class = self.biolink_class('pathway')
                    identifiers = {'msigdb':id}
                    sub_category = row['SUB_CATEGORY_CODE']
                    if sub_category in self.sub_categories and row['EXACT_SOURCE'] is not None:
                        field_name = self.sub_categories[sub_category]
                        identifiers[field_name] = self.identifier(field_name, row['EXACT_SOURCE'])
                    names = []
                    element = self.Element(id, biolink_class, identifiers, names)

                    # ADD ELEMENT TO PATHWAY LIST
                    pathway_list.append(element) 
                    # ADD ELEMENT TO PATHWAY
                    pathways[pathway_name] = element

                element = pathways[pathway_name]
                
                # ADD CONNECTION TO PATHWAY 
                publication_attribute = None
                if row['PMID'] is not None:
                    publication_attribute = self.Attribute('PMID', 'PMID:'  + str(row['PMID']), type='biolink:publication', description=row['AUTHORS'])#description does not show in json from post request
                
                connection = self.Connection(gene.id, self.PREDICATE,self.INVERSE_PREDICATE)
                infores = self.sub_categories.get(row['SUB_CATEGORY_CODE'], 'infores:msigdb')
                infores_attr = self.Attribute('biolink:primary_knowledge_source', infores, value_type = 'biolink:InformationResource')
                connection.attributes.append(infores_attr)
                if sub_category in self.sub_categories:
                    sub_attr = self.Attribute('biolink:prev_knowledge_source', infores)
                    infores_attr = self.Attribute('biolink:aggregator_knowledge_source', 'infores:msigdb', value_type = 'biolink:InformationResource')
                    infores_attr.attributes=[sub_attr]
                    connection.attributes.append(infores_attr)
                if publication_attribute is not None:
                    element.attributes.append(publication_attribute)
                    connection.attributes.append(publication_attribute)
                element.connections.append(connection)

                # ADD ATTRIBUTES AND NAMES https://github.com/broadinstitute/scb-kp-dev/blob/master/util/python/transformers/transformer.py
                attribute_fields = ['ORGANISM','EXACT_SOURCE','GENESET_LISTING_URL', 'EXTERNAL_DETAILS_URL','CATEGORY_CODE','SUB_CATEGORY_CODE','CONTRIBUTOR','CONTRIBUTOR_ORG','DESCRIPTION_BRIEF','DESCRIPTION_FULL','REFINEMENT_DATASETS','VALIDATION_DATASETS','FILTERED_BY_SIMILARITY']
                for attr in attribute_fields:
                    if row[attr] is not None:
                        attribute = self.Attribute(attr, row[attr])
                        element.attributes.append(attribute)
                    
                element.names_synonyms = [self.Names(name=row['STANDARD_NAME'],synonyms=[row['SYSTEMATIC_NAME']])]


        return pathway_list
    
class MSigDBGeneTransformer(Transformer):
    # pathway to gene

    variables = []

    def __init__(self):
        super().__init__(self.variables,definition_file='info/genes_transformer_info.json')


    def produce(self,pathway, controls): # need to implement the case for 1 element only (not a collection)
        gene_list = []

    
    def export(self, pathway_list, controls):  
        gene_list = []
        genes = {}
        for pathway in pathway_list:
            pathway_id = self.de_prefix('msigdb',pathway.identifiers.get("msigdb"),"pathway")
            for row in get_genes(pathway_id):
                gene_id = row['MEMBERS_3']
                if gene_id not in genes and gene_id is not None:
                    id = self.add_prefix('entrez', str(gene_id))
                    biolink_class = self.biolink_class('gene')
                    identifiers = {'entrez':id}
                    names = [self.Names(name = row['MEMBERS_2'])]
                    element = self.Element(id, biolink_class, identifiers, names_synonyms = names)

                    # ADD ELEMENT TO GENE LIST
                    gene_list.append(element) 
                    # ADD ELEMENT TO GENE
                    genes[gene_id] = element

                
                element = genes[gene_id]

                connection = self.Connection(pathway.id, self.PREDICATE,self.INVERSE_PREDICATE)
                element.connections.append(connection)

        return gene_list


connection = sqlite3.connect("data/MSigDB.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

def get_pathway_count():
    query = """ 
    SELECT COUNT(DISTINCT STANDARD_NAME) FROM GENESET;
    """
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()

# get total number of pathways (when not overlap, p value will be automatically 1).
pathway_n_tot = get_pathway_count()
    
def get_pathways(gene_id):
    # do we need this :GENESET.GENESET_LISTING_URL
    query = """
    SELECT GENESET.STANDARD_NAME,
    GENESET.SYSTEMATIC_NAME,
    GENESET.ORGANISM,
    GENESET.PMID,
    GENESET.AUTHORS,
    GENESET.EXACT_SOURCE,
    GENESET.GENESET_LISTING_URL, 
    GENESET.EXTERNAL_DETAILS_URL,
    GENESET.CATEGORY_CODE,
    GENESET.SUB_CATEGORY_CODE,
    GENESET.CONTRIBUTOR,
    GENESET.CONTRIBUTOR_ORG,
    GENESET.DESCRIPTION_BRIEF,
    GENESET.DESCRIPTION_FULL,
    GENESET.REFINEMENT_DATASETS,
    GENESET.VALIDATION_DATASETS,
    GENESET.FILTERED_BY_SIMILARITY

    FROM MEMBER
    JOIN MEMBER_MAP ON (MEMBER_MAP.MEMBERS_1 = MEMBER.MEMBERS_1)
    JOIN GENESET ON (GENESET.STANDARD_NAME = MEMBER_MAP.STANDARD_NAME)
    WHERE CATEGORY_CODE != 'ARCHIVED'
    AND MEMBER.MEMBERS_3 = ?;
    """
    cur = connection.cursor()
    cur.execute(query,(gene_id,))
    return cur.fetchall()

def get_genes(pathway_id):

    query = """
    SELECT MEMBER.MEMBERS_1,
    MEMBER.MEMBERS_2,
    MEMBER.MEMBERS_3

    FROM MEMBER_MAP
    JOIN MEMBER ON (MEMBER.MEMBERS_1 = MEMBER_MAP.MEMBERS_1)
    WHERE MEMBER_MAP.STANDARD_NAME = ?;
    """
    cur = connection.cursor()
    cur.execute(query,(pathway_id,))
    return cur.fetchall()