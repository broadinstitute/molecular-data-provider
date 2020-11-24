import sqlite3

from transformers.transformer import Transformer
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.connection import Connection
from openapi_server.models.attribute import Attribute

SOURCE = 'ChEMBL'

# CURIE prefix
CHEMBL = 'ChEMBL:'
MESH = 'MESH:'

DOC_URL = 'https://www.ebi.ac.uk/chembl/document_report_card/'

#Biolink class
DISEASE = 'Disease'
ASSAY = 'Assay'
MOLECULAR_ENTITY = 'MolecularEntity'
CHEMICAL_SUBSTANCE = 'ChemicalSubstance'

class ChemblIndicationsExporter(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/indications_transformer_info.json')


    def export(self, collection, controls):
        indication_list = []
        indications = {}
        for element in collection:
            id = chembl_id(element.identifiers)
            if id is not None:
                for row in get_indications(id):
                    indication = self.get_or_create_indication(row, indications, indication_list)
                    self.add_identifiers_names(indication, row)
                    self.add_connection(id, indication, row)
        return indication_list


    def get_or_create_indication(self, row, indications, indication_list):
        mesh_id = MESH+row['mesh_id']
        efo_id = row['efo_id']
        if mesh_id is not None and mesh_id in indications:
            return indications[mesh_id]
        if efo_id is not None and efo_id in indications:
            return indications[efo_id]
        id = mesh_id if mesh_id is not None else efo_id
        names = Names(name = row['mesh_heading'],synonyms=[],source=SOURCE)
        indication = Element(id=id, biolink_class=DISEASE,connections=[])
        indication.identifiers={'efo':[]}
        indication.names_synonyms=[names]
        indication.source = self.info.name
        if mesh_id is not None:
            indications[mesh_id] = indication
            indication.identifiers['mesh'] = mesh_id
        if efo_id is not None:
            indications[efo_id] = indication
        indication_list.append(indication)
        return indication


    def add_identifiers_names(self, indication, row):
        mesh_id = MESH+row['mesh_id']
        efo_id = row['efo_id']
        efo_term = row['efo_term']
        if indication.id != mesh_id:
            print("WARNING: MESH ID mismatch {} != {} ({})".format(indication.id,mesh_id,row['drugind_id']))
        if efo_id not in indication.identifiers['efo']:
            indication.identifiers['efo'].append(efo_id)
        if efo_term not in indication.names_synonyms[0].synonyms:
            indication.names_synonyms[0].synonyms.append(efo_term)


    def add_connection(self, chembl_id, indication, row):
        curie = CHEMBL+chembl_id
        connection = None
        for c in indication.connections:
            if c.source_element_id == curie:
                connection = c
        if connection is None:
            connection = Connection(source_element_id=curie, attributes=[])
            connection.type = self.info.knowledge_map.predicates[0].predicate
            indication.connections.append(connection)
        max_phase = row['max_phase_for_ind']
        max_phase_attr = None
        for attr in connection.attributes:
            if attr.name == 'max phase for indication':
                max_phase_attr = attr
                break
        if max_phase_attr is None:
            max_phase_attr = Attribute(
                name='max phase for indication',
                value=max_phase,
                type='OPMI:0000367',# clinical trial phase
                source=SOURCE,
                url=None,
                provided_by=self.info.name
            )
            connection.attributes.append(max_phase_attr)
        elif max_phase > max_phase_attr.value:
            max_phase_attr.value = max_phase
        connection.attributes.append(Attribute(
            name=row['ref_type'],
            value=row['ref_id'],
            type='reference',
            source=SOURCE,
            url=row['ref_url'],
            provided_by=self.info.name
        ))



class ChemblAssayExporter(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/assays_transformer_info.json')


    def export(self, collection, controls):
        assay_list = []
        assays = {}
        for element in collection:
            id = chembl_id(element.identifiers)
            if id is not None:
                for row in get_activities(id):
                    assay = self.get_or_create_assay(row, assays, assay_list)
                    self.add_connection(id, assay, row)
        return assay_list


    def get_or_create_assay(self, row, assays, assay_list):
        assay_id = CHEMBL + row['assay_chembl_id']
        if assay_id in assays:
            return assays[assay_id]
        names = Names(
            name = row['assay_description'] if row['assay_description'] is not None else assay_id,
            synonyms = [],
            source = SOURCE
        )

        assay = Element(
            id=assay_id,
            biolink_class=ASSAY,
            identifiers = {'chembl':assay_id},
            names_synonyms=[names],
            connections=[],
            attributes=[]
        )
        add_attribute(self,assay,row,'BAO_label')
        add_attribute(self,assay,row,'assay_organism')
        add_attribute(self,assay,row,'target_chembl_id')
        add_attribute(self,assay,row,'target_name')
        add_attribute(self,assay,row,'target_organism')
        add_attribute(self,assay,row,'target_type')
        add_attribute(self,assay,row,'cell_chembl_id')
        add_attribute(self,assay,row,'assay_type')
        add_attribute(self,assay,row,'bao_format')
        add_attribute(self,assay,row,'assay_tissue_chembl_id')
        add_attribute(self,assay,row,'assay_tissue_name')
        add_attribute(self,assay,row,'assay_cell_type')
        add_attribute(self,assay,row,'assay_subcellular_fraction')
        assays[assay_id] = assay
        assay_list.append(assay)
        return assay


    def add_connection(self, id, assay, row):
        connection = Connection(
            source_element_id=CHEMBL+id,
            attributes=[],
            type=self.info.knowledge_map.predicates[0].predicate
        )
        add_attribute(self,connection,row,'standard_type')
        add_attribute(self,connection,row,'standard_relation')
        add_attribute(self,connection,row,'standard_value')
        add_attribute(self,connection,row,'standard_units')
        add_attribute(self,connection,row,'pchembl_value')
        add_attribute(self,connection,row,'activity_comment')
        reference=add_attribute(self,connection,row,'document_chembl_id')
        if reference is not None:
            reference.name = 'publication'
            reference.url = DOC_URL + reference.value
            reference.value = CHEMBL + reference.value
            reference.type = 'publication'
        add_attribute(self,connection,row,'source_description')
        add_attribute(self,connection,row,'data_validity_comment')
        add_attribute(self,connection,row,'uo_units')
        add_attribute(self,connection,row,'ligand_efficiency_BEI')
        add_attribute(self,connection,row,'ligand_efficiency_LE')
        add_attribute(self,connection,row,'ligand_efficiency_LLE')
        add_attribute(self,connection,row,'ligand_efficiency_SEI')
        add_attribute(self,connection,row,'journal')
        add_attribute(self,connection,row,'year')
        assay.connections.append(connection)



class ChemblMechanismExporter(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/mechanisms_transformer_info.json')

    def export(self, collection, controls):
        mechanism_list = []
        mechanisms = {}
        for element in collection:
            id = chembl_id(element.identifiers)
            if id is not None:
                for row in get_mechanisms(id):
                    mechanism = self.get_or_create_mechanism(row, mechanisms, mechanism_list)
                    self.add_connection(id, mechanism, row)
        return mechanism_list


    def get_or_create_mechanism(self, row, mechanisms, mechanism_list):
        name = row['target_chembl_id']
        id = CHEMBL+name
        if id in mechanisms:
            return mechanisms[id]
        names = Names(name=name, synonyms=[],source=SOURCE)
        mechanism = Element(
            id=id,
            biolink_class=MOLECULAR_ENTITY,
            identifiers = {'chembl':id},
            names_synonyms=[names],
            connections=[],
            attributes=[]
        )
        add_attribute(self,mechanism,row,'target_name')
        add_attribute(self,mechanism,row,'target_type')
        add_attribute(self,mechanism,row,'target_organism')
        mechanisms[id] = mechanism
        mechanism_list.append(mechanism)
        return mechanism


    def add_connection(self, id, mechanism, row):
        connection = Connection(
            source_element_id=CHEMBL+id,
            attributes=[],
            type=self.info.knowledge_map.predicates[0].predicate
        )
        add_attribute(self,connection,row,'action_type')
        add_attribute(self,connection,row,'mechanism_of_action')
        add_attribute(self,connection,row,'mechanism_comment')
        add_attribute(self,connection,row,'selectivity_comment')
        add_attribute(self,connection,row,'target_chembl_id')
        add_attribute(self,connection,row,'site_name')
        add_attribute(self,connection,row,'binding_site_comment')
        add_attribute(self,connection,row,'source_description')
        reference=add_attribute(self,connection,row,'document_chembl_id')
        if reference is not None:
            reference.name = 'publication'
            reference.url = DOC_URL + reference.value
            reference.value = CHEMBL + reference.value
            reference.type = 'publication'
        add_references(self, connection, 'mechanism_refs', 'mec_id', row['mec_id'])
        self.add_atc_classification(connection,row['molregno'])
        mechanism.connections.append(connection)


    def add_atc_classification(self, connection, molregno):
        for atc in get_atc_classification(molregno):
            value  = atc['level1']+'-'+atc['level1_description']+'|'
            value += atc['level2']+'-'+atc['level2_description']+'|'
            value += atc['level3']+'-'+atc['level3_description']+'|'
            value += atc['level4']+'-'+atc['level4_description']+'|'
            value += atc['level5']+'-'+atc['level5_description']
            connection.attributes.append(
                Attribute(
                    name='atc_classification',
                    value=value,
                    type='atc_classification',
                    source=SOURCE,
                    provided_by=self.info.name
                )
            )


class ChemblMetaboliteTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/metabolites_transformer_info.json')


    def map(self, collection, controls):
        metabolite_list = []
        metabolites = {}
        for element in collection:
            id = chembl_id(element.identifiers)
            if id is not None:
                for row in get_direct_metabolites(id):
                    metabolite = self.get_or_create_metabolite(row, metabolites, metabolite_list)
                    self.add_connection(id, metabolite, row)
        return metabolite_list


    def get_or_create_metabolite(self, row, metabolites, metabolite_list):
        chembl_id = row['metabolite_chembl_id']
        if chembl_id in metabolites:
            return metabolites[chembl_id]
        names = Names(name=row['metabolite_name'], synonyms=[],source=SOURCE)
        if row['metabolite_pref_name'] is not None and row['metabolite_pref_name'] != row['metabolite_name']:
            names.synonyms.append(row['metabolite_pref_name'])
        metabolite = Element(
            id=CHEMBL+chembl_id,
            biolink_class=CHEMICAL_SUBSTANCE,
            identifiers = {'chembl':CHEMBL+chembl_id},
            names_synonyms=[names],
            connections=[],
            attributes=[]
        )
        structure_source=None
        for struct in ['inchi', 'inchikey', 'smiles']:
            if row[struct] is not None:
                metabolite.identifiers[struct] = row[struct]
                structure_source=Attribute(name='structure source', value=SOURCE,source=self.info.name)
        if structure_source is not None:
            metabolite.attributes.append(structure_source)
        metabolites[chembl_id]=metabolite
        metabolite_list.append(metabolite)
        return metabolite


    def add_connection(self, id, metabolite, row):
        connection = Connection(
            source_element_id=CHEMBL+id,
            attributes=[],
            type=self.info.knowledge_map.predicates[0].predicate
        )
        add_attribute(self,connection,row,'enzyme_name')
        add_attribute(self,connection,row,'met_conversion')
        add_attribute(self,connection,row,'met_comment')
        add_attribute(self,connection,row,'organism')
        add_attribute(self,connection,row,'tax_id')
        add_attribute(self,connection,row,'enzyme_type')
        enzyme_chembl_id = add_attribute(self,connection,row,'enzyme_chembl_id')
        if enzyme_chembl_id is not None:
            enzyme_chembl_id.value = CHEMBL+row['enzyme_chembl_id']
        add_references(self, connection, 'metabolism_refs','met_id', row['met_id'])
        metabolite.connections.append(connection)


def chembl_id(identifiers):
    if 'chembl' in identifiers:
        curie = identifiers['chembl']
        if curie is not None:
            return curie[len(CHEMBL):] if curie.startswith(CHEMBL) else curie
    return None


def add_attribute(transformer, element, row, name):
    if row[name] is not None:
        attribute = Attribute(
                name=name,
                value=row[name],
                type=name,
                source=SOURCE,
                url=None,
                provided_by=transformer.info.name
            )
        element.attributes.append(attribute)
        return attribute
    return None


def add_references(transformer, connection, ref_table, id_column, ref_id):
    for reference in get_refs(ref_table, id_column, ref_id):
        connection.attributes.append(
            Attribute(
                name=reference['ref_type'],
                value=add_ref_prefix(reference['ref_type'], reference['ref_id']),
                type='publication',
                source=SOURCE,
                url=reference['ref_url'],
                provided_by=transformer.info.name
            )
        )


def add_ref_prefix(ref_type, ref_id):
    prefix_map = {'PMID':'PMID:', 'DOI':'DOI:', 'ISBN': 'ISBN:', 'PubMed':'PMID:'}
    if ref_type in prefix_map:
        return prefix_map[ref_type]+ref_id
    return ref_id


connection = sqlite3.connect("data/ChEMBL.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def get_indications(chembl_id):
    query = """
        SELECT drug_indication.drugind_id,
          drug_indication.mesh_id,
          drug_indication.mesh_heading,
          drug_indication.efo_id,
          drug_indication.efo_term,
          drug_indication.max_phase_for_ind,
          indication_refs.ref_type,
          indication_refs.ref_id,
          indication_refs.ref_url
        FROM drug_indication
        JOIN molecule_dictionary ON (molecule_dictionary.molregno = drug_indication.molregno)
        JOIN indication_refs ON (indication_refs.drugind_id = drug_indication.drugind_id)
        WHERE molecule_dictionary.chembl_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,))
    return cur.fetchall()


def get_activities(chembl_id):
    query = """
        SELECT
            activities.activity_id,
            activities.standard_type,
            activities.standard_relation,
            activities.standard_value,
            activities.standard_units,
            activities.pchembl_value,
            activities.activity_comment,
            assays.chembl_id AS assay_chembl_id,
            assays.description AS assay_description,
            bioassay_ontology.label AS BAO_label,
            assays.assay_organism,
            target_dictionary.chembl_id AS target_chembl_id,
            target_dictionary.pref_name AS target_name,
            target_dictionary.organism AS target_organism,
            target_dictionary.target_type,
            docs.chembl_id AS document_chembl_id,
            source.src_description AS source_description,
            cell_dictionary.chembl_id as cell_chembl_id,
            activities.data_validity_comment,
            activities.uo_units,
            ligand_eff.bei AS ligand_efficiency_BEI,
            ligand_eff.le AS ligand_efficiency_LE,
            ligand_eff.lle AS ligand_efficiency_LLE,
            ligand_eff.sei AS ligand_efficiency_SEI,
            assay_type.assay_desc AS assay_type,
            assays.bao_format,
            tissue_dictionary.chembl_id AS assay_tissue_chembl_id,
            tissue_dictionary.pref_name AS assay_tissue_name,
            assays.assay_cell_type,
            assays.assay_subcellular_fraction,
            docs.journal,
            docs.year
        FROM activities
        JOIN molecule_dictionary ON activities.molregno=molecule_dictionary.molregno
        JOIN assays ON activities.assay_id=assays.assay_id
        LEFT JOIN bioassay_ontology on bioassay_ontology.bao_id = assays.bao_format
        LEFT JOIN target_dictionary ON target_dictionary.tid=assays.tid
        LEFT JOIN cell_dictionary ON cell_dictionary.cell_id=assays.cell_id
        LEFT JOIN assay_type ON assay_type.assay_type=assays.assay_type
        LEFT JOIN tissue_dictionary ON tissue_dictionary.tissue_id=assays.tissue_id
        LEFT JOIN docs ON activities.doc_id=docs.doc_id
        LEFT JOIN source ON source.src_id = activities.src_id
        LEFT JOIN ligand_eff ON ligand_eff.activity_id=activities.activity_id
        WHERE molecule_dictionary.chembl_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,))
    return cur.fetchall()


def get_mechanisms(chembl_id):
    query = """
        SELECT
            drug_mechanism.mec_id,
            drug_mechanism.molregno,
            drug_mechanism.mechanism_of_action,
            drug_mechanism.action_type,
            drug_mechanism.mechanism_comment,
            drug_mechanism.selectivity_comment,
            target_dictionary.chembl_id AS target_chembl_id,
            target_dictionary.pref_name AS target_name,
            target_dictionary.target_type,
            target_dictionary.organism AS target_organism,
            binding_sites.site_name,
            drug_mechanism.binding_site_comment,
            source.src_description AS source_description,
            docs.chembl_id AS document_chembl_id
        FROM drug_mechanism
        JOIN molecule_dictionary ON molecule_dictionary.molregno=drug_mechanism.molregno
        LEFT JOIN target_dictionary ON target_dictionary.tid=drug_mechanism.tid
        LEFT JOIN binding_sites ON binding_sites.site_id=drug_mechanism.site_id
        LEFT JOIN compound_records ON compound_records.record_id=drug_mechanism.record_id
        LEFT JOIN docs ON (docs.doc_id=compound_records.doc_id AND compound_records.doc_id!=-1)
        LEFT JOIN source ON source.src_id=compound_records.src_id
        WHERE molecule_dictionary.chembl_id = ?;
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,))
    return cur.fetchall()


def get_mechanism_refs(mec_id):
    query = """
        SELECT ref_type, ref_id, ref_url
        FROM mechanism_refs
        WHERE mec_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(mec_id,))
    return cur.fetchall()


def get_atc_classification(molregno):
    query = """
        SELECT
            atc_classification.level1,
            atc_classification.level1_description,
            atc_classification.level2,
            atc_classification.level2_description,
            atc_classification.level3,
            atc_classification.level3_description,
            atc_classification.level4,
            atc_classification.level4_description,
            atc_classification.level5,
            atc_classification.who_name AS level5_description
        FROM molecule_atc_classification
        JOIN atc_classification ON atc_classification.level5=molecule_atc_classification.level5
        WHERE molecule_atc_classification.molregno = ?
    """
    cur = connection.cursor()
    cur.execute(query,(molregno,))
    return cur.fetchall()


def get_direct_metabolites(chembl_id):
    query = """
        SELECT
          metabolism.met_id,
          metabolism.enzyme_name,
          metabolism.met_conversion,
          metabolism.met_comment,
          metabolism.organism,
          metabolism.tax_id,
          metabolite_record.compound_name AS metabolite_name,
          metabolite.pref_name AS metabolite_pref_name,
          metabolite.chembl_id AS metabolite_chembl_id,
          target_dictionary.target_type AS enzyme_type,
          target_dictionary.chembl_id AS enzyme_chembl_id,
          compound_structures.standard_inchi AS inchi,
          compound_structures.standard_inchi_key AS inchikey,
          compound_structures.canonical_smiles AS smiles
        FROM molecule_dictionary
        JOIN compound_records ON compound_records.molregno = molecule_dictionary.molregno
        JOIN metabolism ON metabolism.substrate_record_id = compound_records.record_id
        JOIN compound_records AS metabolite_record ON metabolite_record.record_id = metabolism.metabolite_record_id
        JOIN molecule_dictionary AS metabolite on metabolite.molregno = metabolite_record.molregno
        LEFT JOIN target_dictionary ON (target_dictionary.tid = metabolism.enzyme_tid and target_type != 'UNCHECKED')
        LEFT JOIN compound_structures ON compound_structures.molregno = molecule_dictionary.molregno
        WHERE molecule_dictionary.chembl_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,))
    return cur.fetchall()


def get_refs(ref_table, id_column, ref_id):
    query = """
        SELECT ref_type, ref_id, ref_url
        FROM {}
        WHERE {} = ?
    """.format(ref_table, id_column)
    cur = connection.cursor()
    cur.execute(query,(ref_id,))
    return cur.fetchall()


