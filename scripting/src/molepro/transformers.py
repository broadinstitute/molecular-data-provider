from molepro.server import transform
from molepro.server import aggregate
from molepro.utils import get_controls


def pubchem_compound_list_producer(compound):
    transformer = 'Pubchem compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def chembl_compound_list_producer(compound):
    transformer = 'ChEMBL compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def chembank_compound_list_producer(compound):
    transformer = 'ChemBank compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def chebi_compound_list_producer(compound):
    transformer = 'ChEBI compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def drug_repurposing_hub_compound_list_producer(compound):
    transformer = 'Drug Repurposing Hub compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def dgidb_compound_list_producer(compounds):
    transformer = 'DGIdb compound-list producer'
    collection_id = None
    controls = get_controls(compounds=compounds)
    return transform(transformer, collection_id, controls)


def gtopdb_compound_list_producer(compound):
    transformer = 'GtoPdb compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
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


def inxightdrugs_substance_list_producer(substance):
    transformer = 'Inxight:Drugs substance-list producer'
    collection_id = None
    controls = get_controls(substance=substance)
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


def bindingbd_ligand_producer(ligand):
    transformer = 'BindingBD ligand producer'
    collection_id = None
    controls = get_controls(ligand=ligand)
    return transform(transformer, collection_id, controls)


def pharmgkb_compound_list_producer(compound):
    transformer = 'PharmGKB compound-list producer'
    collection_id = None
    controls = get_controls(compound=compound)
    return transform(transformer, collection_id, controls)


def kinomescan_small_molecule_list_producer(small_molecule):
    transformer = 'KINOMEscan small-molecule-list producer'
    collection_id = None
    controls = get_controls(small__molecule=small_molecule)
    return transform(transformer, collection_id, controls)


def inxightdrugs_drug_producer(drugs):
    transformer = 'Inxight:Drugs drug producer'
    collection_id = None
    controls = get_controls(drugs=drugs)
    return transform(transformer, collection_id, controls)


def inxightdrugs_relationship_transformer(collection,cache='yes'):
    transformer = 'Inxight:Drugs relationship transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def inxightdrugs_active_ingredients_transformer(collection, association_level='associated',cache='yes'):
    transformer = 'Inxight:Drugs active ingredients transformer'
    collection_id = collection.id
    controls = get_controls(association__level=association_level)
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


def sider_drug_producer(drug):
    transformer = 'SIDER drug producer'
    collection_id = None
    controls = get_controls(drug=drug)
    return transform(transformer, collection_id, controls)


def hgnc_gene_list_producer(gene):
    transformer = 'HGNC gene-list producer'
    collection_id = None
    controls = get_controls(gene=gene)
    return transform(transformer, collection_id, controls)


def uniprot_protein_list_producer(protein):
    transformer = 'UniProt protein-list producer'
    collection_id = None
    controls = get_controls(protein=protein)
    return transform(transformer, collection_id, controls)


def drugcentral_disease_producer(disease):
    transformer = 'DrugCentral disease producer'
    collection_id = None
    controls = get_controls(disease=disease)
    return transform(transformer, collection_id, controls)


def rxnorm_drug_relation_info(collection,cache='yes'):
    transformer = 'RxNorm drug relation info'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def rxnorm_active_ingredient_transformer(collection,cache='yes'):
    transformer = 'RxNorm active ingredient transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def rxnorm_components_transformer(collection,cache='yes'):
    transformer = 'RxNorm components transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drugcentral_indications_transformer(disease):
    transformer = 'DrugCentral indications transformer'
    collection_id = None
    controls = get_controls(disease=disease)
    return transform(transformer, collection_id, controls)


def hmdb_disorders_transformer(collection,cache='yes'):
    transformer = 'HMDB disorders transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def ctd_disease_associations_transformer(collection,cache='yes'):
    transformer = 'CTD disease associations transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_indication_transformer(collection,cache='yes'):
    transformer = 'ChEMBL indication transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drug_repurposing_hub_indication_transformer(collection,cache='yes'):
    transformer = 'Drug Repurposing Hub indication transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def sider_indication_transformer(collection,cache='yes'):
    transformer = 'SIDER indication transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def sider_side_effect_transformer(collection,cache='yes'):
    transformer = 'SIDER side effect transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def pharos_target_genes_transformer(collection,cache='yes'):
    transformer = 'Pharos target genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_gene_target_transformer(collection,cache='yes'):
    transformer = 'ChEMBL gene target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def hmdb_target_genes_transformer(collection,cache='yes'):
    transformer = 'HMDB target genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def drug_repurposing_hub_target_transformer(collection,cache='yes'):
    transformer = 'Drug Repurposing Hub target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def dgidb_target_transformer(collection,cache='yes'):
    transformer = 'DGIdb target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gtopdb_target_transformer(collection,cache='yes'):
    transformer = 'GtoPdb target transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def ctd_gene_interactions_transformer(collection,cache='yes'):
    transformer = 'CTD gene interactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def probeminer_chemical_interactions_transformer(collection,cache='yes'):
    transformer = 'ProbeMiner chemical interactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def pharmgkb_relations_transformer(collection, association_level='associated',cache='yes'):
    transformer = 'PharmGKB relations transformer'
    collection_id = collection.id
    controls = get_controls(association__level=association_level)
    return transform(transformer, collection_id, controls)


def pharmgkb_automated_annotations_transformer(collection,cache='yes'):
    transformer = 'PharmGKB automated annotations transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def dgidb_inhibitor_transformer(collection,cache='yes'):
    transformer = 'DGIdb inhibitor transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gtopdb_inhibitors_transformer(collection,cache='yes'):
    transformer = 'GtoPdb inhibitors transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def stitch_link_transformer(collection, score_threshold, limit,cache='yes'):
    transformer = 'STITCH link transformer'
    collection_id = collection.id
    controls = get_controls(score_threshold=score_threshold, limit=limit)
    return transform(transformer, collection_id, controls)


def hmdb_target_proteins_transformer(collection,cache='yes'):
    transformer = 'HMDB target proteins transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def probeminer_protein_interactions_transformer(collection, limit,cache='yes'):
    transformer = 'ProbeMiner protein interactions transformer'
    collection_id = collection.id
    controls = get_controls(limit=limit)
    return transform(transformer, collection_id, controls)


def bindingbd_binding_transformer(collection, threshold_nm='10000',cache='yes'):
    transformer = 'BindingBD binding transformer'
    collection_id = collection.id
    controls = get_controls(threshold_nm=threshold_nm)
    return transform(transformer, collection_id, controls)


def kinomescan_activity_transformer(collection, Kd_nMol_threshold, percent_control_threshold,cache='yes'):
    transformer = 'KINOMEscan activity transformer'
    collection_id = collection.id
    controls = get_controls(Kd__nMol__threshold=Kd_nMol_threshold, percent__control__threshold=percent_control_threshold)
    return transform(transformer, collection_id, controls)


def kinomescan_screening_transformer(collection, Kd_nMol_threshold, percent_control_threshold,cache='yes'):
    transformer = 'KINOMEscan screening transformer'
    collection_id = collection.id
    controls = get_controls(Kd__nMol__threshold=Kd_nMol_threshold, percent__control__threshold=percent_control_threshold)
    return transform(transformer, collection_id, controls)


def chembl_metabolite_transformer(collection,cache='yes'):
    transformer = 'ChEMBL metabolite transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def pubchem_chemical_similarity_transformer(collection,cache='yes'):
    transformer = 'PubChem chemical similarity transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chebi_relations_transformer(collection, direction='both',cache='yes'):
    transformer = 'ChEBI relations transformer'
    collection_id = collection.id
    controls = get_controls(direction=direction)
    return transform(transformer, collection_id, controls)


def uniprot_protein_to_gene_transformer(collection,cache='yes'):
    transformer = 'UniProt protein to gene transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def uniprot_gene_to_protein_transformer(collection,cache='yes'):
    transformer = 'UniProt gene to protein transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gwas_disease_to_gene_transformer(collection,cache='yes'):
    transformer = 'GWAS disease to gene transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gwas_gene_to_disease_transformer(collection,cache='yes'):
    transformer = 'GWAS gene to disease transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def cmap_compound_to_compound_expander(collection, score_threshold='95', maximum_number='0',cache='yes'):
    transformer = 'CMAP compound-to-compound expander'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def ctrp_compound_list_expander(collection, maximum_FDR, disease_context, maximum_number,cache='yes'):
    transformer = 'CTRP compound-list expander'
    collection_id = collection.id
    controls = get_controls(maximum__FDR=maximum_FDR, disease__context=disease_context, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def cmap_compound_to_gene_transformer(collection, score_threshold='95', maximum_number='0',cache='yes'):
    transformer = 'CMAP compound-to-gene transformer'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def cmap_gene_to_compound_transformer(collection, score_threshold='95', maximum_number='0',cache='yes'):
    transformer = 'CMAP gene-to-compound transformer'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def cmap_gene_to_gene_expander(collection, score_threshold='95', maximum_number='0',cache='yes'):
    transformer = 'CMAP gene-to-gene expander'
    collection_id = collection.id
    controls = get_controls(score__threshold=score_threshold, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def depmap_co_fitness_correlation(collection, correlation_threshold, correlation_direction, maximum_number='0',cache='yes'):
    transformer = 'DepMap co-fitness correlation'
    collection_id = collection.id
    controls = get_controls(correlation__threshold=correlation_threshold, correlation__direction=correlation_direction, maximum__number=maximum_number)
    return transform(transformer, collection_id, controls)


def bigg_reactions_transformer(collection,cache='yes'):
    transformer = 'BiGG reactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def bigg_genes_transformer(collection,cache='yes'):
    transformer = 'BiGG genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def bigg_gene_reaction_transformer(collection,cache='yes'):
    transformer = 'BiGG gene_reaction transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def ctd_go_associations_transformer(collection, limit='0',cache='yes'):
    transformer = 'CTD go associations transformer'
    collection_id = collection.id
    controls = get_controls(limit=limit)
    return transform(transformer, collection_id, controls)


def ctd_pathway_associations_transformer(collection, limit='0',cache='yes'):
    transformer = 'CTD pathway associations transformer'
    collection_id = collection.id
    controls = get_controls(limit=limit)
    return transform(transformer, collection_id, controls)


def ctd_phenotype_interactions_transformer(collection,cache='yes'):
    transformer = 'CTD phenotype interactions transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def hmdb_pathways_transformer(collection,cache='yes'):
    transformer = 'HMDB pathways transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def msigdb_genes_transformer(collection,cache='yes'):
    transformer = 'MSigDB genes transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def msigdb_pathways_transformer(collection,cache='yes'):
    transformer = 'MSigDB pathways transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def hmdb_locations_transformer(collection,cache='yes'):
    transformer = 'HMDB locations transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_activities_transformer(collection,cache='yes'):
    transformer = 'ChEMBL activities transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def chembl_mechanism_transformer(collection,cache='yes'):
    transformer = 'ChEMBL mechanism transformer'
    collection_id = collection.id
    controls = []
    return transform(transformer, collection_id, controls)


def gene_list_network_enrichment_analysis(collection, maximum_p_value='1e-05', network='STRING-human-700', gene_set_collection='H - hallmark gene sets',cache='yes'):
    transformer = 'Gene-list network enrichment analysis'
    collection_id = collection.id
    controls = get_controls(maximum__p___value=maximum_p_value, network=network, gene___set__collection=gene_set_collection)
    return transform(transformer, collection_id, controls)


def union(*args,cache='yes'):
    transformer = 'union'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def intersection(*args,cache='yes'):
    transformer = 'intersection'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def difference(*args,cache='yes'):
    transformer = 'difference'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def symmetric_difference_xor(*args,cache='yes'):
    transformer = 'symmetric difference (XOR)'
    collection_ids = [collection.id for collection in args]
    controls = []
    return aggregate(transformer, collection_ids)


def string_protein_protein_links_transformer(collection, minimum_combined_score='0.7', maximum_number_of_genes='0',cache='yes'):
    transformer = 'STRING protein-protein links transformer'
    collection_id = collection.id
    controls = get_controls(minimum__combined__score=minimum_combined_score, maximum__number__of__genes=maximum_number_of_genes)
    return transform(transformer, collection_id, controls)


def sri_node_normalizer_producer(id, category=None):
    transformer = 'SRI node normalizer producer'
    collection_id = None
    controls = get_controls(id=id, category=category)
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


def moleprodb_connections_transformer(collection, predicate=None, qualifier_constraint=None, biolink_class=None, id=None, name_source=None, element_attribute=None, connection_attribute=None, limit='0',cache='yes'):
    transformer = 'MoleProDB connections transformer'
    collection_id = collection.id
    controls = get_controls(predicate=predicate, qualifier_constraint=qualifier_constraint, biolink_class=biolink_class, id=id, name_source=name_source, element_attribute=element_attribute, connection_attribute=connection_attribute, limit=limit)
    return transform(transformer, collection_id, controls)


def moleprodb_hierarchy_transformer(collection, name_source=None, element_attribute=None, hierarchy_type=None,cache='yes'):
    transformer = 'MoleProDB hierarchy transformer'
    collection_id = collection.id
    controls = get_controls(name_source=name_source, element_attribute=element_attribute, hierarchy_type=hierarchy_type)
    return transform(transformer, collection_id, controls)


def element_attribute_filter(collection, id, name, operator, value, _not=None, unit_id=None, unit_name=None,cache='yes'):
    transformer = 'Element attribute filter'
    collection_id = collection.id
    controls = get_controls(id=id, name=name, _not=_not, operator=operator, value=value, unit_id=unit_id, unit_name=unit_name)
    return transform(transformer, collection_id, controls)


def connection_attribute_filter(collection, id, name, operator, value, _not=None, unit_id=None, unit_name=None,cache='yes'):
    transformer = 'Connection attribute filter'
    collection_id = collection.id
    controls = get_controls(id=id, name=name, _not=_not, operator=operator, value=value, unit_id=unit_id, unit_name=unit_name)
    return transform(transformer, collection_id, controls)


def compound_producer(elements):
    x0 = pubchem_compound_list_producer(elements)
    x1 = chembl_compound_list_producer(elements)
    x2 = chembank_compound_list_producer(elements)
    x3 = chebi_compound_list_producer(elements)
    x4 = drug_repurposing_hub_compound_list_producer(elements)
    x5 = dgidb_compound_list_producer(elements)
    x6 = hmdb_metabolite_producer(elements)
    x7 = drugcentral_compounds_producer(elements)
    x8 = stitch_compound_list_producer(elements)
    x9 = rxnorm_compound_list_producer(elements)
    x10 = bigg_compound_list_producer(elements)
    x11 = ctd_compound_list_producer(elements)
    x12 = probeminer_compound_list_producer(elements)
    x13 = bindingbd_ligand_producer(elements)
    x14 = pharmgkb_compound_list_producer(elements)
    x15 = sider_drug_producer(elements)
    return union(x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,cache='no')


def gene_producer(elements):
    x0 = hgnc_gene_list_producer(elements)
    return union(x0,cache='no')


def protein_producer(elements):
    x0 = uniprot_protein_list_producer(elements)
    return union(x0,cache='no')


def disease_producer(elements):
    x0 = drugcentral_disease_producer(elements)
    return union(x0,cache='no')


def transform_compound_to_disease(collection):
    x0 = hmdb_disorders_transformer(collection)
    x1 = ctd_disease_associations_transformer(collection)
    x2 = chembl_indication_transformer(collection)
    return union(x0,x1,x2,cache='no')


def transform_compound_to_DiseaseOrPhenotypicFeature(collection):
    x0 = drug_repurposing_hub_indication_transformer(collection)
    x1 = sider_indication_transformer(collection)
    x2 = sider_side_effect_transformer(collection)
    return union(x0,x1,x2,cache='no')


def transform_compound_to_gene(collection, association_level, score_threshold, maximum_number):
    x0 = pharos_target_genes_transformer(collection)
    x1 = chembl_gene_target_transformer(collection)
    x2 = hmdb_target_genes_transformer(collection)
    x3 = drug_repurposing_hub_target_transformer(collection)
    x4 = dgidb_target_transformer(collection)
    x5 = gtopdb_target_transformer(collection)
    x6 = ctd_gene_interactions_transformer(collection)
    x7 = pharmgkb_relations_transformer(collection, association_level='associated')
    x8 = pharmgkb_automated_annotations_transformer(collection)
    x9 = gtopdb_inhibitors_transformer(collection)
    x10 = cmap_compound_to_gene_transformer(collection, score_threshold='95', maximum_number='0')
    x11 = bigg_genes_transformer(collection)
    return union(x0,x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,cache='no')


def transform_compound_to_protein(collection, score_threshold, limit):
    x0 = probeminer_chemical_interactions_transformer(collection)
    x1 = stitch_link_transformer(collection, score_threshold, limit)
    x2 = hmdb_target_proteins_transformer(collection)
    return union(x0,x1,x2,cache='no')


def transform_compound_to_target(collection, threshold_nm):
    x0 = bindingbd_binding_transformer(collection, threshold_nm='10000')
    x1 = chembl_activities_transformer(collection)
    x2 = chembl_mechanism_transformer(collection)
    return union(x0,x1,x2,cache='no')


def transform_compound_to_compound(collection, direction, score_threshold, maximum_number, maximum_FDR, disease_context):
    x0 = chembl_metabolite_transformer(collection)
    x1 = pubchem_chemical_similarity_transformer(collection)
    x2 = chebi_relations_transformer(collection, direction='both')
    x3 = cmap_compound_to_compound_expander(collection, score_threshold='95', maximum_number='0')
    x4 = ctrp_compound_list_expander(collection, maximum_FDR, disease_context, maximum_number)
    return union(x0,x1,x2,x3,x4,cache='no')


def transform_disease_to_gene(collection):
    x0 = gwas_disease_to_gene_transformer(collection)
    return union(x0,cache='no')


