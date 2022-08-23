from molepro.server import transform
from molepro.server import aggregate
from molepro.utils import get_controls


def pubchem_compound_list_producer(compound):
    transformer = 'Pubchem compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def chembl_compound_list_producer(compounds):
    transformer = 'ChEMBL compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def drugbank_compound_list_producer(compounds):
    transformer = 'DrugBank compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def chembank_compound_list_producer(compounds):
    transformer = 'ChemBank compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def chebi_compound_list_producer(compounds):
    transformer = 'ChEBI compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def repurposing_hub_compound_list_producer(compounds):
    transformer = 'Repurposing Hub compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def dgidb_compound_list_producer(compounds):
    transformer = 'DGIdb compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def gtopdb_compound_list_producer(compounds):
    transformer = 'GtoPdb compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def hmdb_metabolite_producer(compound):
    transformer = 'HMDB metabolite producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def drugcentral_compounds_producer(compound):
    transformer = 'DrugCentral compounds producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def inxightdrugs_substance_list_producer(substances):
    transformer = 'Inxight:Drugs substance-list producer'
    collection_id = None
    controls = get_controls(substances=substances)
    return transform(transformer, collection_id, controls)


def stitch_compound_list_producer(compounds):
    transformer = 'STITCH compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def rxnorm_compound_list_producer(compound):
    transformer = 'RxNorm compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def bigg_compound_list_producer(compounds):
    transformer = 'BiGG compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def ctd_compound_list_producer(compound):
    transformer = 'CTD compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def probeminer_compound_list_producer(compound):
    transformer = 'ProbeMiner compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def inxightdrugs_drug_producer(drugs):
    transformer = 'Inxight:Drugs drug producer'
    collection_id = None
    controls = get_controls(drugs=drugs)
    return transform(transformer, collection_id, controls)


def inxightdrugs_relationship_transformer(collection):
    transformer = 'Inxight:Drugs relationship transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def inxightdrugs_active_ingredients_transformer(collection, substances):
    transformer = 'Inxight:Drugs active ingredients transformer'
    collection_id = collection.id
    controls = get_controls(substances=substances)
    return transform(transformer, collection_id, controls)


def rxnorm_drug_list_producer(drug):
    transformer = 'RxNorm drug-list producer'
    collection_id = None
    controls = get_controls(drug=drug)
    return transform(transformer, collection_id, controls)


def unii_ingredient_list_producer(ingredient):
    transformer = 'UNII ingredient-list producer'
    collection_id = None
    controls = get_controls(ingredient=ingredient)
    return transform(transformer, collection_id, controls)


def drugbank_molecule_list_producer(compounds):
    transformer = 'DrugBank molecule-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def hgnc_gene_list_producer(genes):
    transformer = 'HGNC gene-list producer'
    collection_id = None
    controls = get_controls(genes=genes)
    return transform(transformer, collection_id, controls)


def uniprot_protein_list_producer(proteins):
    transformer = 'UniProt protein-list producer'
    collection_id = None
    controls = get_controls(proteins=proteins)
    return transform(transformer, collection_id, controls)


def drugcentral_disease_producer(disease):
    transformer = 'DrugCentral disease producer'
    collection_id = None
    controls = get_controls(disease=disease)
    return transform(transformer, collection_id, controls)


def rxnorm_drug_relation_info(collection):
    transformer = 'RxNorm drug relation info'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def rxnorm_active_ingredient_transformer(collection):
    transformer = 'RxNorm active ingredient transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def rxnorm_components_transformer(collection):
    transformer = 'RxNorm components transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugcentral_indications_transformer(disease):
    transformer = 'DrugCentral indications transformer'
    collection_id = None
    controls = get_controls(disease=disease)
    return transform(transformer, collection_id, controls)


def hmdb_disorders_transformer(collection):
    transformer = 'HMDB disorders transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def ctd_disease_associations_transformer(collection):
    transformer = 'CTD disease associations transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_indication_transformer(collection):
    transformer = 'ChEMBL indication transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def repurposing_hub_indication_transformer(collection):
    transformer = 'Repurposing Hub indication transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_target_genes_transformer(collection):
    transformer = 'DrugBank target genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_enzyme_genes_transformer(collection):
    transformer = 'DrugBank enzyme genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_transporter_genes_transformer(collection):
    transformer = 'DrugBank transporter genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_carrier_genes_transformer(collection):
    transformer = 'DrugBank carrier genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def pharos_target_genes_transformer(collection):
    transformer = 'Pharos target genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_target_transformer(collection):
    transformer = 'ChEMBL target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def hmdb_target_genes_transformer(collection):
    transformer = 'HMDB target genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def repurposing_hub_target_transformer(collection):
    transformer = 'Repurposing Hub target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def dgidb_target_transformer(collection):
    transformer = 'DGIdb target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gtopdb_target_transformer(collection):
    transformer = 'GtoPdb target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def ctd_gene_interactions_transformer(collection):
    transformer = 'CTD gene interactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def probeminer_chemical_interactions_transformer(collection):
    transformer = 'ProbeMiner chemical interactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_inhibitors_transformer(collection):
    transformer = 'DrugBank inhibitors transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_substrates_transformer(collection):
    transformer = 'DrugBank substrates transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_transporter_substrates_transformer(collection):
    transformer = 'DrugBank transporter substrates transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_carrier_substrates_transformer(collection):
    transformer = 'DrugBank carrier substrates transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def dgidb_inhibitor_transformer(collection):
    transformer = 'DGIdb inhibitor transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gtopdb_inhibitors_transformer(collection):
    transformer = 'GtoPdb inhibitors transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def stitch_link_transformer(collection, score_threshold, limit):
    transformer = 'STITCH link transformer'
    collection_id = collection.id
    controls = get_controls(score_threshold=score_threshold, limit=limit)
    return transform(transformer, collection_id, controls)


def drugbank_target_proteins_transformer(collection):
    transformer = 'DrugBank target proteins transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_enzyme_proteins_transformer(collection):
    transformer = 'DrugBank enzyme proteins transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_transporter_proteins_transformer(collection):
    transformer = 'DrugBank transporter proteins transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugbank_carrier_proteins_transformer(collection):
    transformer = 'DrugBank carrier proteins transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def hmdb_target_proteins_transformer(collection):
    transformer = 'HMDB target proteins transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def probeminer_protein_interactions_transformer(collection, limit):
    transformer = 'ProbeMiner protein interactions transformer'
    collection_id = collection.id
    controls = get_controls(limit=limit)
    return transform(transformer, collection_id, controls)


def chembl_metabolite_transformer(collection):
    transformer = 'ChEMBL metabolite transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def pubchem_chemical_similarity_transformer(collection):
    transformer = 'PubChem chemical similarity transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gwas_disease_to_gene_transformer(collection):
    transformer = 'GWAS disease to gene transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gwas_gene_to_disease_transformer(collection):
    transformer = 'GWAS gene to disease transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def cmap_compound_to_compound_expander(collection, score_threshold, maximum_number):
    transformer = 'CMAP compound-to-compound expander'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def ctrp_compound_list_expander(collection, maximum_fdr, disease_context, maximum_number):
    transformer = 'CTRP compound-list expander'
    collection_id = collection.id
    controls = get_controls(maximum__fdr=maximum_fdr, disease__context=disease_context, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def cmap_compound_to_gene_transformer(collection, score_threshold, maximum_number):
    transformer = 'CMAP compound-to-gene transformer'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def cmap_gene_to_compound_transformer(collection, score_threshold, maximum_number):
    transformer = 'CMAP gene-to-compound transformer'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def cmap_gene_to_gene_expander(collection, score_threshold, maximum_number):
    transformer = 'CMAP gene-to-gene expander'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def depmap_co_fitness_correlation(collection, correlation_threshold, correlation_direction, maximum_number=0):
    transformer = 'DepMap co-fitness correlation'
    collection_id = collection.id
    controls = get_controls(correlation__threshold=correlation_threshold, correlation__direction=correlation_direction, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def bigg_reactions_transformer(collection):
    transformer = 'BiGG reactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def bigg_genes_transformer(collection):
    transformer = 'BiGG genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def bigg_gene_reaction_transformer(collection):
    transformer = 'BiGG gene_reaction transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def ctd_go_associations_transformer(collection, limit=0):
    transformer = 'CTD go associations transformer'
    collection_id = collection.id
    controls = get_controls(limit=limit)
    return transform(transformer, collection_id, controls)


def ctd_pathway_associations_transformer(collection, limit=0):
    transformer = 'CTD pathway associations transformer'
    collection_id = collection.id
    controls = get_controls(limit=limit)
    return transform(transformer, collection_id, controls)


def ctd_phenotype_interactions_transformer(collection):
    transformer = 'CTD phenotype interactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def hmdb_pathways_transformer(collection):
    transformer = 'HMDB pathways transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def hmdb_locations_transformer(collection):
    transformer = 'HMDB locations transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_assay_transformer(collection):
    transformer = 'ChEMBL assay transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_mechanism_transformer(collection):
    transformer = 'ChEMBL mechanism transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def msigdb_hypergeometric_enrichment_exporter(collection, maximum_p_value, maximum_q_value):
    transformer = 'MSigDB hypergeometric enrichment exporter'
    collection_id = collection.id
    controls = get_controls(maximum__p___value=maximum_p_value, maximum__q___value=maximum_q_value)
    return transform(transformer, collection_id, controls)


def gene_list_network_enrichment_analysis(collection, maximum_p_value, network, gene_set_collection):
    transformer = 'Gene-list network enrichment analysis'
    collection_id = collection.id
    controls = get_controls(maximum__p___value=maximum_p_value, network=network, gene___set__collection=gene_set_collection)
    return transform(transformer, collection_id, controls)


def union(*args):
    transformer = 'union'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def intersection(*args):
    transformer = 'intersection'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def difference(*args):
    transformer = 'difference'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def symmetric_difference_xor(*args):
    transformer = 'symmetric difference (XOR)'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def string_protein_protein_interaction(collection, minimum_combined_score, minimum_neighborhood_score, minimum_gene_fusion_score, minimum_cooccurence_score, minimum_coexpression_score, minimum_experimental_score, minimum_database_score, minimum_textmining_score, minimum_best_non_textmining_component_score, maximum_number_of_genes):
    transformer = 'STRING protein-protein interaction'
    collection_id = collection.id
    controls = get_controls(minimum__combined__score=minimum_combined_score, minimum__neighborhood__score=minimum_neighborhood_score, minimum__gene__fusion__score=minimum_gene_fusion_score, minimum__cooccurence__score=minimum_cooccurence_score, minimum__coexpression__score=minimum_coexpression_score, minimum__experimental__score=minimum_experimental_score, minimum__database__score=minimum_database_score, minimum__textmining__score=minimum_textmining_score, minimum__best__non___textmining__component__score=minimum_best_non_textmining_component_score, maximum__number__of__genes=maximum_number_of_genes)
    return transform(transformer, collection_id, controls)


def sri_node_normalizer_producer(id):
    transformer = 'SRI node normalizer producer'
    collection_id = None
    controls = get_controls(id=id)
    return transform(transformer, collection_id, controls)


def moleprodb_node_producer(id):
    transformer = 'MoleProDB node producer'
    collection_id = None
    controls = get_controls(id=id)
    return transform(transformer, collection_id, controls)


def moleprodb_name_producer(name):
    transformer = 'MoleProDB name producer'
    collection_id = None
    controls = get_controls(name=name)
    return transform(transformer, collection_id, controls)


def moleprodb_connections_transformer(collection, predicate=None, biolink_class=None, id=None, name_source=None, element_attribute=None, connection_attribute=None):
    transformer = 'MoleProDB connections transformer'
    collection_id = collection.id
    controls = get_controls(predicate=predicate, biolink_class=biolink_class, id=id, name_source=name_source, element_attribute=element_attribute, connection_attribute=connection_attribute)
    return transform(transformer, collection_id, controls)


def moleprodb_hierarchy_transformer(collection, name_source=None, element_attribute=None):
    transformer = 'MoleProDB hierarchy transformer'
    collection_id = collection.id
    controls = get_controls(name_source=name_source, element_attribute=element_attribute)
    return transform(transformer, collection_id, controls)


def element_attribute_filter(collection, id, name, operator, value, _not=None, unit_id=None, unit_name=None):
    transformer = 'Element attribute filter'
    collection_id = collection.id
    controls = get_controls(id=id, name=name, _not=_not, operator=operator, value=value, unit_id=unit_id, unit_name=unit_name)
    return transform(transformer, collection_id, controls)


def connection_attribute_filter(collection, id, name, operator, value, _not=None, unit_id=None, unit_name=None):
    transformer = 'Connection attribute filter'
    collection_id = collection.id
    controls = get_controls(id=id, name=name, _not=_not, operator=operator, value=value, unit_id=unit_id, unit_name=unit_name)
    return transform(transformer, collection_id, controls)


def compound_producer(elements):
    x0 = pubchem_compound_list_producer(elements)
    x1 = chembl_compound_list_producer(elements)
    x2 = drugbank_compound_list_producer(elements)
    x3 = chembank_compound_list_producer(elements)
    x4 = chebi_compound_list_producer(elements)
    x5 = repurposing_hub_compound_list_producer(elements)
    x6 = dgidb_compound_list_producer(elements)
    x7 = gtopdb_compound_list_producer(elements)
    x8 = hmdb_metabolite_producer(elements)
    x9 = drugcentral_compounds_producer(elements)
    x10 = stitch_compound_list_producer(elements)
    x11 = rxnorm_compound_list_producer(elements)
    x12 = bigg_compound_list_producer(elements)
    x13 = ctd_compound_list_producer(elements)
    x14 = probeminer_compound_list_producer(elements)
    return union(x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14)


def transform_compound_to_disease(collection):
    x0 = hmdb_disorders_transformer(collection)
    x1 = ctd_disease_associations_transformer(collection)
    x2 = chembl_indication_transformer(collection)
    return union(x0,x1,x2)


def transform_compound_to_gene(collection, score_threshold, maximum_number):
    x0 = drugbank_target_genes_transformer(collection)
    x1 = drugbank_enzyme_genes_transformer(collection)
    x2 = drugbank_transporter_genes_transformer(collection)
    x3 = drugbank_carrier_genes_transformer(collection)
    x4 = pharos_target_genes_transformer(collection)
    x5 = chembl_target_transformer(collection)
    x6 = hmdb_target_genes_transformer(collection)
    x7 = repurposing_hub_target_transformer(collection)
    x8 = dgidb_target_transformer(collection)
    x9 = gtopdb_target_transformer(collection)
    x10 = ctd_gene_interactions_transformer(collection)
    x11 = cmap_compound_to_gene_transformer(collection, score_threshold, maximum_number)
    x12 = bigg_genes_transformer(collection)
    return union(x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12)


def transform_compound_to_protein(collection, score_threshold, limit):
    x0 = probeminer_chemical_interactions_transformer(collection)
    x1 = stitch_link_transformer(collection, score_threshold, limit)
    x2 = drugbank_target_proteins_transformer(collection)
    x3 = drugbank_enzyme_proteins_transformer(collection)
    x4 = drugbank_transporter_proteins_transformer(collection)
    x5 = drugbank_carrier_proteins_transformer(collection)
    x6 = hmdb_target_proteins_transformer(collection)
    return union(x0,x1,x2,x3,x4,x5,x6)


def transform_gene_to_compound(collection, score_threshold, maximum_number):
    x0 = drugbank_inhibitors_transformer(collection)
    x1 = drugbank_substrates_transformer(collection)
    x2 = drugbank_transporter_substrates_transformer(collection)
    x3 = drugbank_carrier_substrates_transformer(collection)
    x4 = dgidb_inhibitor_transformer(collection)
    x5 = gtopdb_inhibitors_transformer(collection)
    x6 = cmap_gene_to_compound_transformer(collection, score_threshold, maximum_number)
    return union(x0,x1,x2,x3,x4,x5,x6)


def transform_compound_to_compound(collection, score_threshold, maximum_number, maximum_fdr, disease_context):
    x0 = chembl_metabolite_transformer(collection)
    x1 = pubchem_chemical_similarity_transformer(collection)
    x2 = cmap_compound_to_compound_expander(collection, score_threshold, maximum_number)
    x3 = ctrp_compound_list_expander(collection, maximum_fdr, disease_context, maximum_number)
    return union(x0,x1,x2,x3)


