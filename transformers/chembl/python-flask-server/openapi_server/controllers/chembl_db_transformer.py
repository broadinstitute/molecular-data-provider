import sqlite3
import json
import re
import csv
from collections import defaultdict
from collections import OrderedDict

from transformers.transformer import Transformer

SOURCE = 'ChEMBL'

# CURIE prefix
CHEMBL = 'ChEMBL:'
MESH = 'MESH:'

DOC_URL = 'https://www.ebi.ac.uk/chembl/document_report_card/'

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


class ChemblProducer(Transformer):

    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')
        with open('conf/chembl_producer_attr_map.json') as json_file:
            self.attribute_map = json.load(json_file)                          


    def produce(self, controls):
        compound_list = []
        names = controls['compound']
        for name in names:
            name = name.strip()
            for compound in self.find_compound(name):
                compound.attributes.append(self.Attribute(name='query name', value=name, type=None, value_type = None))
                compound_list.append(compound)
        return compound_list


    def find_compound(self, name):
        if name.upper().startswith('CHEMBL:'):
            return self.molecules(get_compound_by_id(name[7:]))
        elif name.upper().startswith('CHEMBL'):
            return self.molecules(get_compound_by_id(name))
        elif inchikey_regex.match(name) is not None:
            return self.molecules(get_compound_by_inchikey(name))
        else:
            molecules = self.molecules(get_compound_by_pref_name(name.upper()))
            if len(molecules) != 0:
                return molecules
            molecules = self.molecules(get_compound_by_pref_name(name))
            if len(molecules) != 0:
                return molecules
            return self.molecules(get_compound_by_synonym(name))


    def molecules(self, results):
        compounds = []
        for row in results:
            compounds.append(self.row_to_element(row))
        return compounds


    def row_to_element(self, row):
        id = self.add_prefix('chembl', row['chembl_id'])
        identifiers = {
            'chembl': id,
            'smiles':  row['canonical_smiles'],
            'inchi': row['standard_inchi'],
            'inchikey': row['standard_inchi_key'],
        }

        biolink = None
        if row['molecule_type'] is not None:
            biolink = row['molecule_type']
        else:
            biolink = 'SmallMolecule' if row['standard_inchi_key'] is not None else 'ChemicalEntity'

        element = self.Element(
            id=id,
            biolink_class=self.biolink_class(biolink),
            identifiers=identifiers,
            names_synonyms=self.get_names_synonyms(row[ 'chembl_id'],row['pref_name'],row['molregno']),
            attributes = []
        )
        self.add_attributes(element, row)
        return element


    def get_names_synonyms(self, id, pref_name, molregno):
        """
            Build names and synonyms list
        """
        synonyms = defaultdict(list)
        for molecule_synonym in get_molecule_synonyms(molregno):
            if molecule_synonym['syn_type'] is None:
                synonyms['ChEMBL'].append(molecule_synonym['synonyms'])
            else:
                synonyms[molecule_synonym['syn_type']].append(molecule_synonym['synonyms'])
        names_synonyms = []
        names_synonyms.append(
            self.Names(
                name =pref_name,
                synonyms = synonyms['ChEMBL']
            ) 
        ),
        for syn_type, syn_list in synonyms.items():
            if syn_type != 'ChEMBL':
                names_synonyms.append(
                    self.Names(
                        name = syn_list[0] if len(syn_list) == 1 else  None,
                        synonyms = syn_list if len(syn_list) > 1 else  None,
                        type = syn_type
                    )
                )
        return names_synonyms


    def add_attributes(self, element, row):
        str_attr = [
            'max_phase','molecule_type','first_approval','usan_year',
            'usan_stem','usan_substem','usan_stem_definition','indication_class']
        flag_attr = [
            'therapeutic_flag','dosed_ingredient','black_box_warning',
            'natural_product','first_in_class','prodrug','inorganic_flag','polymer_flag','withdrawn_flag']
        for attr_name in str_attr:
            # (self, transformer, element, row, name)
            add_attribute(self, None, element, row, attr_name)
        for attr_name in flag_attr:
            if row[attr_name] is not None and row[attr_name] > 0:
                attr = add_attribute(self, None, element, row, attr_name)
                attr.value = 'yes'
        for attr in self.attribute_map:
            attr_name = attr['original_attribute_name']
            attr_type = attr['attribute_type_id']
            attr_value_type = attr.get('value_type_id')
            attr_value = attr['value_map'].get(str(row[attr_name]))
            if attr_value is not None:
                element.attributes.append(self.Attribute(
                    name = attr_name,
                    value = attr_value,
                    type = attr_type,
                    value_type = attr_value_type
                ))
        self.add_atc_classification(element, row["molregno"])
        self.add_drug_warning(element, row["molregno"])
        

    def add_atc_classification(self, element, molregno):
        atc_classifications = OrderedDict()
        for atc in get_atc_classification(molregno):
            value  = atc['level1']+'-'+atc['level1_description']+'|'
            value += atc['level2']+'-'+atc['level2_description']+'|'
            value += atc['level3']+'-'+atc['level3_description']+'|'
            value += atc['level4']+'-'+atc['level4_description']+'|'
            value += atc['level5']+'-'+atc['level5_description']
            element.attributes.append(
                self.Attribute(
                    name='atc_classification',
                    value=value,
                    type='atc_classification'
                )
            )
            atc_classifications['ATC:'+atc['level1']] = atc['level1']
            atc_classifications['ATC:'+atc['level2']] = atc['level2']
            atc_classifications['ATC:'+atc['level3']] = atc['level3']
            atc_classifications['ATC:'+atc['level4']] = atc['level4']
            atc_classifications['ATC:'+atc['level5']] = atc['level5']
        element.attributes.append(
            self.Attribute(
                name='atc_classifications',
                value=[atc for atc in atc_classifications],
                type='atc_classifications'
            )
        )


    def add_drug_warning(self, element, molregno):
        for warning in get_drug_warning(molregno):
            sub_attributes = []
       
            if warning['withdrawn_flag'] is not None:
                sub_attributes.append(self.Attribute(
                    name='withdrawn_flag', 
                    value=warning["withdrawn_flag"],
                    type='withdrawn_flag', url=None)
                )
            if warning["warning_type"] is not None:
                sub_attributes.append(self.Attribute(
                    name='warning_type',
                    value=warning["warning_type"],
                    type='warning_type', url=None)
                )
            if warning['warning_class'] is not None:
                sub_attributes.append(self.Attribute(
                    name='warning_class',
                    value=warning["warning_class"],
                    type='warning_class', url=None)
                )
            if warning['warning_description'] is not None:
                sub_attributes.append(self.Attribute(
                    name='drug_warning_description',
                    value=warning["warning_description"],
                    type='drug_warning_description', url=None)
                )
            if warning['warning_country'] is not None:
                sub_attributes.append(self.Attribute(
                    name='warning_country',
                    value=warning["warning_country"],
                    type='warning_country', url=None)
                )
            if warning['warning_year'] is not None:
                sub_attributes.append(self.Attribute(
                    name='warning_year',
                    value=warning["warning_year"],
                    type='warning_year', url=None)
                )
            if warning['warning_type'] is not None:
                drug_warning_attribute = self.Attribute(
                    name='drug_warning',
                    value=warning["warning_type"],
                    type='drug_warning', url=None,
                    attributes=sub_attributes
                )

            self.add_warning_references(sub_attributes, warning["warning_id"])

            element.attributes.append(
                    drug_warning_attribute
            )

    def add_warning_references(self, sub_attributes, warning_id):
                for reference in get_warning_references(warning_id):
                    sub_attributes.append(self.Attribute(
                        name='warning_reference',
                        value=reference["ref_id"],
                        type=reference["ref_type"], url=reference["ref_url"])
                    )



class ChemblIndicationsTransformer(Transformer):

    variables = []

    research_phase_map = {
        0.5: 'pre_clinical_research_phase',
        1: 'clinical_trial_phase_1',
        2: 'clinical_trial_phase_2',
        3: 'clinical_trial_phase_3',
        4: 'clinical_trial_phase_4',
        }

    def __init__(self):
        super().__init__(self.variables, definition_file='info/indications_transformer_info.json')
        self.TREAT_PREDICATE = self.PREDICATE
        self.TREAT_INV_PREDICATE = self.INVERSE_PREDICATE
        if len(self.info.knowledge_map.edges) >= 2:
            self.TREAT_PREDICATE = self.info.knowledge_map.edges[1].predicate
            self.TREAT_INV_PREDICATE = self.info.knowledge_map.edges[1].inverse_predicate

    def map(self, collection, controls):
        indication_list = []
        indications = {}
        for element in collection:
            identifiers = element.identifiers
            ids = []
            if 'chembl' in identifiers and identifiers['chembl'] is not None:
                ids = self.get_identifiers(element, 'chembl', de_prefix=True)
            elif 'inchikey' in identifiers and identifiers['inchikey'] is not None:
                ids = [compound['chembl_id'] for compound in get_compound_by_inchikey(identifiers['inchikey'])]
            for id in ids:
                for row in get_indications(id):
                    indication = self.get_or_create_indication(row, indications, indication_list)
                    self.add_identifiers_names(indication, row)
                    self.add_connection(element.id, id, indication, row)
        return indication_list

    #########################################################
    #
    # This method either retrieves an existing indication or
    # produces a whole new indication
    #
    #########################################################
    def get_or_create_indication(self, row, indications, indication_list):  
        mesh_id = MESH+row['mesh_id']
        efo_id = row['efo_id']
        if mesh_id is not None and mesh_id in indications:
           return indications[mesh_id]        # retrieved an existing indication
        if efo_id is not None and efo_id in indications:
           return indications[efo_id]         # retrieved an existing indication
        id = mesh_id if mesh_id is not None else efo_id
        names = self.Names(name = row['mesh_heading'],synonyms=[])
    
        indication = self.Element(            # create a whole new indication
                id=id,
                biolink_class= 'DiseaseOrPhenotypicFeature',
                identifiers={'efo':[]},
                attributes=[]
            )

        indication.identifiers={'efo':[]}
        indication.names_synonyms=[names]
        indication.source = self.info.label
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

    def add_connection(self, source_element_id, chembl_id, indication, row):
        connection = None
        for c in indication.connections:
            if c.source_element_id == source_element_id:
                connection = c
        if connection is None:
            infores = self.Attribute('biolink:primary_knowledge_source','infores:chembl')
            infores.attribute_source = 'infores:molepro'
            level = self.Attribute('biolink:knowledge_level',self.KNOWLEDGE_LEVEL)
            level.attribute_source = 'infores:molepro'
            agent = self.Attribute('biolink:agent_type',self.AGENT_TYPE)
            agent.attribute_source = 'infores:molepro'
            connection = self.Connection(
                source_element_id=source_element_id, 
                predicate=self.PREDICATE,
                inv_predicate=self.INVERSE_PREDICATE,
                attributes=[infores, level, agent]
            )
            indication.connections.append(connection)
        # clinical trial phase
        max_phase = row['max_phase_for_ind']
        max_phase_attr = None
        research_phase_attr = None
        approval_attr = None
        for attr in connection.attributes:
            if attr.original_attribute_name	 == 'max_phase_for_ind':
                max_phase_attr = attr
            if attr.original_attribute_name	 == 'max_research_phase':
                research_phase_attr = attr
            if attr.original_attribute_name	 == 'clinical_approval_status':
                approval_attr = attr
        if max_phase_attr is None:
            max_phase_attr = self.Attribute(
                name='max_phase_for_ind',
                value=max_phase,
                type='max phase for indication',  
                url=None
            )
            connection.attributes.append(max_phase_attr)
        if research_phase_attr is None and max_phase > 0:
            research_phase_attr = self.Attribute(
                name='max_research_phase',
                value=self.research_phase_map.get(max_phase,'not_provided'),
                type='biolink:max_research_phase', 
                url=None
            )
            connection.attributes.append(research_phase_attr)
        elif max_phase > max_phase_attr.value:
            max_phase_attr.value = max_phase
        if max_phase == 4:
            connection.biolink_predicate = self.TREAT_PREDICATE
            connection.inverse_predicate = self.TREAT_INV_PREDICATE
            if approval_attr is None:
                approval_attr = self.Attribute(
                    name='clinical_approval_status',
                    value='approved_for_condition',
                    type='biolink:clinical_approval_status', 
                    url=None
                )
                connection.attributes.append(approval_attr)
        # reference
        attr_value = row['ref_id']
        if row['ref_type'] == 'DailyMed' or row['ref_type'] == 'FDA':
            attr_value = row['ref_url']
        if row['ref_type'] == 'ClinicalTrials':
            attr_value = ['clinicaltrials:'+nct for nct in attr_value.split(',') if nct.startswith('NCT')]
        if row['ref_type'] != 'ATC':
            connection.attributes.append(self.Attribute(
                name=row['ref_type'],
                value=attr_value,
                type='biolink:publications' if isinstance(attr_value, list) else 'biolink:Publication',
                url=row['ref_url']
            ))


##############################################################################
## This was formerly class ChemblAssayExporter 
##
## The query provides to transformer a compound that is used in an assay to 
## assess the activity on a target
##
##
class ChemblActivitiesTransformer(Transformer):
    target_class_dict = None   # Dictionary of ChEMBL target type to MolePro class
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/activities_transformer_info.json')
        self.target_class_dict = self.get_target_class_dict()
        with open('conf/chembl_qualifiers.json') as json_file:
            self.qualifier_map = json.load(json_file)


    ##########################################################################
    # This function reads & converts into a dictionary where the columns are:
    # target_type	|	molepro_semantic_type
    def get_target_class_dict(self):
            classDict = {}
            tsv_file = open("conf/chembl_molepro_map.txt")
            for line in csv.DictReader(tsv_file, delimiter="\t"):
                classDict[line['target_type']] = line['molepro_semantic_type']
            return classDict

    def map(self, collection, controls):
        target_list = []
        targets = {}
        for element in collection:
            identifiers = element.identifiers
            ids = []
            if 'chembl' in identifiers and identifiers['chembl'] is not None:
                ids = self.get_identifiers(element, 'chembl', de_prefix=True)
            elif 'inchikey' in identifiers and identifiers['inchikey'] is not None:
                ids = [compound['chembl_id'] for compound in get_compound_by_inchikey(identifiers['inchikey'])]

            for id in ids:
                for row in get_activities(id):
                    if row['target_type'] not in ('UNCHECKED', 'NON-MOLECULAR','NO TARGET'):
                        target = self.get_or_create_target(row, targets, target_list)
                        self.add_connection(element.id, self.add_prefix('chembl', id), target, row)
                       
        return target_list

    def get_or_create_target(self, row, targets, assay_list):
        target_id = self.add_prefix('chembl', row['target_chembl_id'])
        if target_id in targets:
            return targets[target_id]
        biolink_class = self.target_class_dict.get(row['target_type'], row['target_type'])
        names = self.Names(
            name = row['cell_name'] if biolink_class == 'CellLine' else row['target_name'],
            synonyms = []
        )
        identifier_dict = {'chembl':target_id}
        if row['clo_id'] is not None and biolink_class in ['Cell','CellLine']:
            identifier_dict["clo"] = self.add_prefix('clo', row['clo_id'], 'Cell')
        if row['efo_id'] is not None and biolink_class in ['Cell','CellLine']:
            identifier_dict["efo"] = self.add_prefix('efo', row['efo_id'], 'Cell')
        if row['cellosaurus_id'] is not None and biolink_class in ['Cell','CellLine']:
            identifier_dict["cellosaurus"] = self.add_prefix('cellosaurus', row['cellosaurus_id'], 'Cell')
        if row['cl_lincs_id'] is not None and biolink_class in ['Cell','CellLine']: 
            identifier_dict["lincs"] = self.add_prefix('lincs', row['cl_lincs_id'], 'Cell')
        if row['cell_ontology_id'] is not None and biolink_class in ['Cell','CellLine']: 
            identifier_dict["cell_ontology"] = self.add_prefix('cell_ontology', row['cell_ontology_id'], 'Cell')
        if row['assay_tax_id'] is not None and biolink_class in ['Organism']:
            identifier_dict["ncbi_taxon"] = self.add_prefix('ncbi_taxon', row['assay_tax_id'],'OrganismEntity')
        target = self.Element(            # create a whole new target
                id=target_id,
                biolink_class=self.target_class_dict.get(row['target_type'], row['target_type']),
                identifiers= identifier_dict,
                attributes=[]
            )
        if biolink_class in ['Protein'] and row['component_type'] == 'PROTEIN' and row['accession'] is not None:
            target.identifiers['uniprot'] = self.add_prefix('uniprot', row['accession'], 'protein')       # add uniprot id
        
        target.names_synonyms=[names]
        target_organism_attribute = add_attribute(self,None,target,row,'target_organism')
        if target_organism_attribute is not None:
            target_organism_attribute.description = row['cell_source_organism']            
        add_attribute(self,None,target,row,'cell_description')
        add_attribute(self,None,target,row,'cell_source_tissue')
        cell_source_attribute = add_attribute(self,None,target,row,'cell_source_tax_id')
        add_attribute(self,None,target,row,'target_mapping')
        add_attribute(self,None,target,row,'assay_tissue_name')
        add_attribute(self,None,target,row,'assay_subcellular_fraction')
        targets[target_id] = target
        assay_list.append(target)
        return target

    def add_connection(self,source_element_id, id, target, row):
        connection = None
        source_element_id = source_element_id
        assay_tax_id = ''
        qualifiers = []
        if row['assay_tax_id'] is not None:
            assay_tax_id = self.add_prefix('ncbi_taxon', row['assay_tax_id'],'OrganismEntity')
            qualifiers.append(self.Qualifier('species_context_qualifier',assay_tax_id))
        
        if row['action_type'] is None or row['action_type'] not in self.qualifier_map:
            for c in target.connections:
                if c.source_element_id == source_element_id:
                    qualifier_tax_id = ''
                    for qualifier in c.qualifiers:
                        if qualifier.qualifier_type_id == 'species_context_qualifier':
                            qualifier_tax_id = qualifier.qualifier_value
                    if assay_tax_id == qualifier_tax_id:
                        return  # do not add to connections the same source_element_id

        if connection is None:
            infores = self.Attribute('biolink:primary_knowledge_source','infores:chembl')
            infores.attribute_source = 'infores:molepro'
            level = self.Attribute('biolink:knowledge_level',self.KNOWLEDGE_LEVEL)
            level.attribute_source = 'infores:molepro'
            agent = self.Attribute('biolink:agent_type',self.AGENT_TYPE)
            agent.attribute_source = 'infores:molepro'
            if row['curated_by'] in {'Expert','Intermediate'}:
                agent = self.Attribute('biolink:agent_type','manual_validation_of_experimental_agent')
                agent.attribute_source = 'infores:molepro'
            if row['action_type'] in self.qualifier_map:
                agent = self.Attribute('biolink:agent_type','manual_agent')
                agent.attribute_source = 'infores:molepro'
                for qualifier in self.qualifier_map[row['action_type']].get('qualifiers', []):
                    qualifiers.append(self.Qualifier(qualifier['qualifier_type_id'],qualifier['qualifier_value']))

            connection = self.Connection(
                source_element_id = source_element_id,
                predicate = self.PREDICATE,
                inv_predicate = self.INVERSE_PREDICATE,
                qualifiers = qualifiers,
                attributes = [infores, level, agent]
            )

        add_attribute(self,None,connection,row,'action_type')
        add_attribute(self,None,connection,row,'data_validity_comment')
        potential_duplicate_attribute = add_attribute(self,None,connection,row,'potential_duplicate')
        assay_attribute = add_attribute(self,None,connection,row,'assay_chembl_id')
        if assay_attribute is not None and row['assay_chembl_id'] is not None:
            subattributes=[]
            assay_attribute.description = row['assay_description']
            assay_attribute.attributes = subattributes
            if row["assay_category"] is not None:
                subattributes.append(self.Attribute(
                    name='assay_category',
                    value=row["assay_category"],
                    type='assay_category', url=None) 
                )
            subattributes.append(self.Attribute(
                name='BAO_label',
                value=row["BAO_label"],
                type='BAO_label', url=None) ) 
            subattributes.append(self.Attribute(
                name='bao_format',
                value=row["bao_format"],
                type='bao_format', url=None) ) 
            subattributes.append(self.Attribute(
                name='assay_type',
                value=row["assay_type"],
                type='assay_type', url=None) ) 
            if row["assay_cell_type"] is not None:
                subattributes.append(self.Attribute(
                    name='assay_cell_type',
                    value=row["assay_cell_type"],
                    type='assay_cell_type', url=None) 
                )
            subattributes.append(self.Attribute(
                name='assay_source_id',
                value=row["assay_source_id"],
                type='assay_source_id', url=None) )     
            if row["assay_tissue"] is not None:
                subattributes.append(self.Attribute(
                    name='assay_tissue',
                    value=row["assay_tissue"],
                    type='assay_tissue', url=None) 
                )
            subattributes.append(self.Attribute(
                name='relationship_type',
                value=row["relationship_type"],
                type='relationship_type', url=None) )
            subattributes.append(self.Attribute(
                name='confidence_score',
                value=row["confidence_score"],
                type='confidence_score', url=None) )   
            subattributes.append(self.Attribute(
                name='curated_by',
                value=row["curated_by"],
                type='curated_by', url=None) )                      
        tissue_attribute = add_attribute(self,None,connection,row,'assay_tissue_chembl_id')
        if tissue_attribute is not None:
            subattributes=[]
            tissue_attribute.description = row["assay_tissue_name"]
        assay_organism_attribute = add_attribute(self,None,connection,row,'assay_tax_id')
        if assay_organism_attribute is not None:
            assay_organism_attribute.description = row["assay_organism"] 

        activity_attribute = add_attribute(self,None,connection,row,'standard_value')
        
        if activity_attribute is not None:
            subattributes=[]
            activity_attribute.attributes = subattributes     
            if row["standard_type"] is not None:
                subattributes.append(self.Attribute(
                    name='standard_type',
                    value=row["standard_type"],
                    type='standard_type', url=None) 
                )
            if row["standard_relation"] is not None:
                subattributes.append(self.Attribute(
                    name='standard_relation',
                    value=row["standard_relation"],
                    type='standard_relation', url=None) 
                )
            if row["standard_units"] is not None:        
                subattributes.append(self.Attribute(
                    name='standard_units',
                    value=row["standard_units"],
                    type='standard_units', url=None) 
                )
            if row["activity_comment"] is not None: 
                subattributes.append(self.Attribute(
                    name='activity_comment',
                    value=row["activity_comment"],
                    type='activity_comment', url=None) 
                )
            if row["standard_text_value"] is not None: 
                subattributes.append(self.Attribute(
                    name='standard_text_value',
                    value=row["standard_text_value"],
                    type='standard_text_value', url=None) 
                )
            if row["standard_upper_value"] is not None: 
                if row["standard_upper_value"] is not None:
                    subattributes.append(self.Attribute(
                        name='standard_upper_value',
                        value=row["standard_upper_value"],
                        type='standard_upper_value', url=None) 
                    ) 
            if row["uo_units"] is not None: 
                if row["uo_units"] is not None:
                    subattributes.append(self.Attribute(
                        name='uo_units',
                        value=row["uo_units"],
                        type='uo_units', url=None) 
                    ) 

        ligand_efficiency_attribute = add_attribute(self,None,connection,row,'ligand_efficiency_BEI')
        if ligand_efficiency_attribute is not None:
            subattributes = []
            ligand_efficiency_attribute.attributes = subattributes
            ligand_efficiency_attribute.attribute_type_id = 'Binding_Efficiency_Index'
            if row["ligand_efficiency_LE"] is not None:
                subattributes.append(self.Attribute(
                    name='ligand_efficiency',
                    value=row["ligand_efficiency_LE"],
                    type='ligand_efficiency_LE', url=None) 
                ) 
            if row["ligand_efficiency_LLE"] is not None:
                subattributes.append(self.Attribute(
                    name='ligand_efficiency',
                    value=row["ligand_efficiency_LLE"],
                    type='ligand_efficiency_LLE', url=None) 
                ) 
            if row["ligand_efficiency_SEI"] is not None:
                subattributes.append(self.Attribute(
                    name='ligand_efficiency',
                    value=row["ligand_efficiency_SEI"],
                    type='ligand_efficiency_SEI', url=None) 
                ) 
        reference = None
        if row["pubmed_id"] is not None:
            reference = add_attribute(self,None,connection,row,'pubmed_id')
            reference.value = get_ref_value('PubMed', reference.value, None)
        elif row["doi"] is not None:
            reference = add_attribute(self,None,connection,row,'doi')
            reference.value = get_ref_value('DOI', reference.value, None)
        elif row["document_chembl_id"] is not None:
            reference = add_attribute(self,None,connection,row,'document_chembl_id')
            reference.value = DOC_URL + row['document_chembl_id']
        if reference is not None:
            subattributes=[]
            reference.type = 'biolink:Publication'
            reference.value_url = DOC_URL + row['document_chembl_id']
            reference.attribute_type_id = 'biolink:Publication'
            reference.attributes = subattributes
            description = ''
            if row["source_description"] is not None:
                subattributes.append(self.Attribute(
                    name='source_description',
                    value=row["source_description"],
                    type='source_description', url=None) 
                )             
            if row["authors"] is not None:
                description = description + row["authors"] + ': ' 
            if row["title"] is not None:
                description = description + row["title"]
            if row["journal"] is not None:
                description = description + row["journal"] + ' '
            if row["year"] is not None:
                description = description + str(row["year"])
            reference.description = description.strip()
        target.connections.append(connection)



###############################################################
# This is the parent class of ChemblGeneTargetTransformer
# 
###############################################################
class ChemblMechanismTransformer(Transformer):
    variables = []
    target_class_dict = None   # Dictionary of ChEMBL target type to MolePro class

    def __init__(self, definition_file=None):
        if definition_file is not None:
            super().__init__(self.variables, definition_file=definition_file)
        else:
            definition_file='info/mechanisms_transformer_info.json'
            super().__init__(self.variables, definition_file)

        self.target_class_dict = self.get_target_class_dict()
        with open('conf/chembl_qualifiers.json') as json_file:
            self.qualifier_map = json.load(json_file)


    ##########################################################################
    # This function reads & converts into a dictionary where the columns are:
    # target_type	|	molepro_semantic_type
    def get_target_class_dict(self):
            classDict = {}
            tsv_file = open("conf/chembl_molepro_map.txt")
            for line in csv.DictReader(tsv_file, delimiter="\t"):
                classDict[line['target_type']] = line['molepro_semantic_type']
            return classDict

    def map(self, collection, controls):
        mechanism_list = []     # List of all the elements to be returned
        mechanisms = {}         # Dictionary of all the elements
        for element in collection:
            identifiers = element.identifiers
            ids = []
            if 'chembl' in identifiers and identifiers['chembl'] is not None:
                ids = self.get_identifiers(element, 'chembl', de_prefix=True)
            elif 'inchikey' in identifiers and identifiers['inchikey'] is not None:
                ids = [compound['chembl_id'] for compound in get_compound_by_inchikey(identifiers['inchikey'])]

            for id in ids:
                mech_ids = set()
                for row in get_mechanisms(id):
                    if row['mec_id'] not in mech_ids:
                        mechanism = self.get_or_create_mechanism(row, mechanisms, mechanism_list)
                        if mechanism is not None:
                            self.add_connection(element.id, mechanism, row)
                            mech_ids.add(row['mec_id'])
        return mechanism_list


    ###############################################################
    # This function creates a new element if it does not exist
    #
    def get_or_create_mechanism(self, row, mechanisms, mechanism_list):
        name = row['target_chembl_id']
        id = self.add_prefix('chembl', name, 'target')
        if id in mechanisms:
            return mechanisms[id]
        mechanism = self.Element(
                        id=id,
                        biolink_class=self.target_class_dict.get(row['target_type'], row['target_type']),
                        identifiers = {'chembl':id},
                        names_synonyms=self.get_names_synonyms(row['target_chembl_id'],row['target_name'],row['molregno']),
                        attributes=[]
                    )
        #name = get_uniprot_xrefs(row['target_chembl_id'])        # add uniprot id
        if mechanism.biolink_class == 'Protein' and row['component_type'] == 'PROTEIN' and row['accession'] is not None:
            uniprot_id = self.add_prefix('uniprot', row['accession'], 'protein')
            mechanism.identifiers['uniprot'] = uniprot_id

    #   add_attribute(self, None, mechanism,row,'target_name') # is an identifier, not an attribute
        add_attribute(self, None, mechanism,row,'target_type')
        add_attribute(self, None, mechanism,row,'target_organism')
        add_attribute(self, None, mechanism,row,'component_type')
        add_attribute(self, None, mechanism,row,'description', 'biolink:description')
        tax_id = add_attribute(self, None, mechanism,row,'tax_id', 'biolink:in_taxon')
        if tax_id is not None:
            tax_id.value = self.add_prefix('ncbi_taxon', tax_id.value, 'OrganismEntity')
        add_attribute(self, None, mechanism,row,'organism')        
        add_attribute(self, None, mechanism,row,'mutation')
        if row['mutation_accession'] != row['accession']:  # mutation accession is not same as protein accession
            add_attribute(self, None, mechanism,row,'mutation_accession')

        mechanisms[id] = mechanism
        mechanism_list.append(mechanism)
        return mechanism


    def get_names_synonyms(self, id, pref_name, molregno):
        """
            Build names and synonyms list
        """
        synonyms = defaultdict(list)
        for target_synonym in get_target_synonyms(id):
            if target_synonym['syn_type'] is None:
                synonyms['ChEMBL'].append(target_synonym['component_synonym'])
            else:
                synonyms[target_synonym['syn_type']].append(target_synonym['component_synonym'])
        names_synonyms = []
        names_synonyms.append(
            self.Names(
                name =pref_name,
                synonyms = synonyms['ChEMBL']
            ) 
        ),
        for syn_type, syn_list in synonyms.items():
            if syn_type != 'ChEMBL':
                names_synonyms.append(
                    self.Names(
                        name = syn_list[0] if len(syn_list) == 1 else  None,
                        synonyms = syn_list if len(syn_list) > 1 else  None,
                        type = syn_type
                    )
                )
        return names_synonyms

    def add_connection(self, source_element_id, mechanism, row):
        infores = self.Attribute('biolink:primary_knowledge_source','infores:chembl')
        infores.attribute_source = 'infores:molepro'
        level = self.Attribute('biolink:knowledge_level',self.KNOWLEDGE_LEVEL)
        level.attribute_source = 'infores:molepro'
        agent = self.Attribute('biolink:agent_type',self.AGENT_TYPE)
        agent.attribute_source = 'infores:molepro'
        predicate=self.PREDICATE
        inv_predicate=self.INVERSE_PREDICATE
        qualifiers = []
        if row['action_type'] in self.qualifier_map:
            predicate = self.qualifier_map[row['action_type']].get('predicate', predicate)
            inv_predicate = self.qualifier_map[row['action_type']].get('inv_predicate', inv_predicate)
            for qualifier in self.qualifier_map[row['action_type']].get('qualifiers', []):
                qualifiers.append(qualifier)
        if row['tax_id'] is not None and row['tax_id'] != '':
            tax_id = self.add_prefix('ncbi_taxon', row['tax_id'], 'OrganismEntity')
            species_qualifier = self.Qualifier('species_context_qualifier',tax_id)
            qualifiers.append(species_qualifier)
        connection = self.Connection(
            source_element_id=source_element_id,
            predicate=predicate,
            inv_predicate=inv_predicate,
            attributes=[infores, level, agent],
            qualifiers=qualifiers
        )
        add_attribute(self,None,connection,row,'action_type')
        add_attribute(self,None,connection,row,'direct_interaction')
        add_attribute(self,None,connection,row,'selectivity_comment')

        mechanism_of_action = add_attribute(self,None,connection,row,'mechanism_of_action')
        if mechanism_of_action is not None and row["mechanism_comment"] is not None:
        #   sub-attribute mechanism_comment
            subattributes = []
            mechanism_of_action.attributes = subattributes
            subattributes.append(self.Attribute(
                        name='mechanism_comment',
                        value=row["mechanism_comment"],
                        type='mechanism_comment', url=None) )

        site_name = add_attribute(self,None,connection,row,'site_name')
        if site_name is not None and row["binding_site_comment"] is not None:
        #   sub-attribute binding_site_comment
            subattributes = []
            site_name.attributes = subattributes
            subattributes.append(self.Attribute(
                        name='binding_site_comment',
                        value=row["binding_site_comment"],
                        type='binding_site_comment', url=None))            
        if row['document_chembl_id'] is not None:
            reference=add_attribute(self, None, connection,row,'document_chembl_id')
            if reference is not None and reference.value is not None:
                reference.name = 'document_chembl_id'
                reference.url = DOC_URL + reference.value
                reference.type = 'biolink:Publication'
                reference.value = self.add_prefix('chembl', reference.value, reference.type)
            #   sub-attribute source_description
                subattributes = []
                reference.attributes = subattributes
                subattributes.append(self.Attribute(
                            name='source_description',
                            value=row["source_description"],
                            type='source_description', url=None))
        add_references(self, connection, 'mechanism_refs', 'mec_id', row['mec_id'])
        mechanism.connections.append(connection)


###############################################################
# This child class of ChemblMechanismTransformer is for reporting
# any targets of the following types:
# SINGLE PROTEIN
# PROTEIN FAMILY
# PROTEIN COMPLEX GROUP
# PROTEIN COMPLEX
# CHIMERIC PROTEIN
# SELECTIVITY GROUP
# PROTEIN NUCLEIC-ACID COMPLEX
# NUCLEIC-ACID
# PROTEIN-PROTEIN INTERACTION
#
###############################################################
class ChemblGeneTargetTransformer(ChemblMechanismTransformer):

    variables = []

    def __init__(self):
        super().__init__(definition_file='info/gene_targets_transformer_info.json')
        self.target_class_dict = self.get_target_class_dict()

    ###############################################################
    #  As a child class of ChemblMechanismTransformer, this method is 
    #  called by default but returns gene targets.
    ###############################################################
    def map(self, collection, controls):
        gene_list = []     # List of all the elements to be returned
        genes = {}         # Dictionary of all the elements
        for element in collection:
            identifiers = element.identifiers
            ids = []
            if 'chembl' in identifiers and identifiers['chembl'] is not None:
                ids = self.get_identifiers(element, 'chembl', de_prefix=True)
            elif 'inchikey' in identifiers and identifiers['inchikey'] is not None:
                ids = [compound['chembl_id'] for compound in get_compound_by_inchikey(identifiers['inchikey'])]
            for id in ids:
                for target in get_mechanisms(id):
                    for gene_id in target_xref(target['accession']):
                        gene_target = self.get_or_create_gene_target(target, gene_id, genes, gene_list)
                        if gene_target is not None:
                            self.add_connection(element.id, gene_target, target)
        return gene_list


    def get_or_create_gene_target(self, row, gene_id, gene_targets, gene_target_list):
        gene_target_array = ["SINGLE PROTEIN",
                                "PROTEIN FAMILY",
                                "PROTEIN COMPLEX GROUP",
                                "PROTEIN COMPLEX",
                                "CHIMERIC PROTEIN",
                                "SELECTIVITY GROUP",
                                "PROTEIN NUCLEIC-ACID COMPLEX",
                                "NUCLEIC-ACID",
                                "PROTEIN-PROTEIN INTERACTION"]
        if row['target_type'] in gene_target_array:
            id = self.add_prefix('ensembl', gene_id, 'Gene')
            if id in gene_targets:
                return gene_targets[id]
            gene_target = self.Element(
                            id=id,
                            biolink_class='Gene',
                            identifiers = {'ensembl':id},
                            names_synonyms =self.get_names_synonyms(row['component_id'], row['description'],row['molregno']),
                            attributes=[]
                        )
            add_attribute(self, None, gene_target,row,'target_organism')
            add_attribute(self, None, gene_target,row,'description', 'biolink:description')
            tax_id = add_attribute(self, None, gene_target,row,'tax_id', 'biolink:in_taxon')
            if tax_id is not None:
                tax_id.value = self.add_prefix('ncbi_taxon', tax_id.value, 'OrganismEntity')
            add_attribute(self, None, gene_target,row,'organism')
            add_attribute(self, None, gene_target,row,'mutation')
            if row['mutation_accession'] != row['accession']:  # mutation accession is not same as protein accession
                add_attribute(self, None, gene_target,row,'mutation_accession')
            gene_targets[id] = gene_target
            gene_target_list.append(gene_target)
            return gene_target

    def get_names_synonyms(self, id, pref_name, molregno):
        """
            Build names and synonyms list
        """
        synonyms = defaultdict(list)
        for target_synonym in get_gene_target_synonyms(id):
            if target_synonym['syn_type'] is None:
                synonyms['ChEMBL'].append(target_synonym['component_synonym'])
            else:
                synonyms[target_synonym['syn_type']].append(target_synonym['component_synonym'])
        names_synonyms = []
        names_synonyms.append(
            self.Names(
                name =pref_name,
                synonyms = synonyms['ChEMBL']
            ) 
        ),
        for syn_type, syn_list in synonyms.items():
            if syn_type != 'ChEMBL':
                names_synonyms.append(
                    self.Names(
                        name = syn_list[0] if len(syn_list) == 1 else  None,
                        synonyms = syn_list if len(syn_list) > 1 else  None,
                        type = syn_type
                    )
                )
        return names_synonyms


class ChemblMetaboliteTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/metabolites_transformer_info.json')


    def map(self, collection, controls):
        metabolite_list = []
        metabolites = {}
        for element in collection:
            identifiers = element.identifiers
            ids = []
            if 'chembl' in identifiers and identifiers['chembl'] is not None:
                ids = self.get_identifiers(element, 'chembl', de_prefix=True)
            elif 'inchikey' in identifiers and identifiers['inchikey'] is not None:
                ids = [compound['chembl_id'] for compound in get_compound_by_inchikey(identifiers['inchikey'])]
            for id in ids:
                for row in get_direct_metabolites(id):
                    metabolite = self.get_or_create_metabolite(row, metabolites, metabolite_list)
                    self.add_connection(element.id, id, metabolite, row)
        return metabolite_list

    def get_or_create_metabolite(self, row, metabolites, metabolite_list):
        chembl_id = row['metabolite_chembl_id']
        if chembl_id in metabolites:
            return metabolites[chembl_id]
        names = self.Names(name = row['metabolite_name'], synonyms=[])    
        if row['metabolite_pref_name'] is not None and row['metabolite_pref_name'] != row['metabolite_name']:
            names.synonyms.append(row['metabolite_pref_name'])

        metabolite = self.Element(
            id=CHEMBL+chembl_id,
            biolink_class= 'SmallMolecule',
            identifiers = {'chembl':CHEMBL+chembl_id},
            names_synonyms=[names],
            attributes=[]
        )
                                  
        for struct in ['inchi', 'inchikey', 'smiles']:
            if row[struct] is not None:
                metabolite.identifiers[struct] = row[struct]
        metabolites[chembl_id]=metabolite
        metabolite_list.append(metabolite)
        return metabolite


    def add_connection(self, source_element_id, id, metabolite, row):
        infores = self.Attribute('biolink:primary_knowledge_source','infores:chembl')
        infores.attribute_source = 'infores:molepro'
        level = self.Attribute('biolink:knowledge_level',self.KNOWLEDGE_LEVEL)
        level.attribute_source = 'infores:molepro'
        agent = self.Attribute('biolink:agent_type',self.AGENT_TYPE)
        agent.attribute_source = 'infores:molepro'
        connection = self.Connection(
            source_element_id=source_element_id,
            predicate=self.PREDICATE,
            inv_predicate=self.INVERSE_PREDICATE,
            attributes=[infores, level, agent]
        )

        add_attribute(self,None,connection,row,'enzyme_name')
        add_attribute(self,None,connection,row,'met_conversion')
        add_attribute(self,None,connection,row,'met_comment')
        add_attribute(self,None,connection,row,'organism')
        add_attribute(self,None,connection,row,'tax_id')
        add_attribute(self,None,connection,row,'enzyme_type')
        enzyme_chembl_id = add_attribute(self,None,connection,row,'enzyme_chembl_id')
        if enzyme_chembl_id is not None:
            enzyme_chembl_id.value = CHEMBL+row['enzyme_chembl_id']
        add_references(self, connection, 'metabolism_refs','met_id', row['met_id'])
        metabolite.connections.append(connection)



################################ Common functions ###################################################

def add_attribute(self, transformer, element, row, name, type = None):
    if row[name] is not None and row[name] != '':
        attribute = self.Attribute(
                name=name,
                value=str(row[name]),
                type= type if type is not None else name ,
                url=None
            )
        element.attributes.append(attribute)
        return attribute
    return None

###########################################################
#  obtain ref_type, ref_id, ref_url from a reference table
#
def add_references(self, connection, ref_table, id_column, ref_id):
    for reference in get_refs(ref_table, id_column, ref_id):
        if reference['ref_id'] is not None:
            connection.attributes.append(
                self.Attribute(
                    name=reference['ref_type'],
                    value=get_ref_value(reference['ref_type'], reference['ref_id'], reference['ref_url']),
                    type='biolink:Publication',
                    url=reference['ref_url']
                )
            )


def get_ref_value(ref_type, ref_id, ref_url):
    prefix_map = {'PMID':'PMID:', 'DOI':'doi:', 'ISBN': 'ISBN:', 'PubMed':'PMID:'}
    if ref_type in prefix_map:
        return prefix_map[ref_type]+ref_id
    if ref_url is not None:
        return ref_url
    return ref_id


connection = sqlite3.connect("data/ChEMBL.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def get_compound_by_pref_name(name):
    where = 'WHERE molecule_dictionary.pref_name = ?'
    join = 'LEFT JOIN compound_structures ON (compound_structures.molregno = molecule_dictionary.molregno)'
    return get_compound(join, where, name)


def get_compound_by_id(chembl_id):
    where = 'WHERE molecule_dictionary.chembl_id = ? '
    join = 'LEFT JOIN compound_structures ON (compound_structures.molregno = molecule_dictionary.molregno)'
    return get_compound(join, where, chembl_id)


def get_compound_by_inchikey(inchikey):
    where = 'WHERE compound_structures.standard_inchi_key = ?'
    join = 'JOIN compound_structures ON (compound_structures.molregno = molecule_dictionary.molregno)'
    return get_compound(join, where, inchikey)


def get_compound_by_synonym(synonym):
    join = """
    JOIN (
        SELECT DISTINCT molregno
        FROM molecule_synonyms
        WHERE synonyms = ? COLLATE NOCASE
    ) AS syn
    ON (syn.molregno=molecule_dictionary.molregno)
    LEFT JOIN compound_structures ON (compound_structures.molregno = molecule_dictionary.molregno)
    """
    return get_compound(join, '', synonym)


def get_compound(join, where, name):
    query = """
        SELECT
            molecule_dictionary.molregno,
            molecule_dictionary.pref_name,
            molecule_dictionary.chembl_id,
            molecule_dictionary.max_phase,
            molecule_dictionary.therapeutic_flag,
            molecule_dictionary.dosed_ingredient,
            molecule_dictionary.chebi_par_id,
            lower(molecule_dictionary.molecule_type) AS molecule_type,
            molecule_dictionary.first_approval,
            molecule_dictionary.oral,
            molecule_dictionary.parenteral,
            molecule_dictionary.topical,
            molecule_dictionary.black_box_warning,
            molecule_dictionary.natural_product,
            molecule_dictionary.first_in_class,
            molecule_dictionary.chirality,
            molecule_dictionary.prodrug,
            molecule_dictionary.inorganic_flag,
            molecule_dictionary.usan_year,
            molecule_dictionary.availability_type,
            molecule_dictionary.usan_stem,
            molecule_dictionary.polymer_flag,
            molecule_dictionary.usan_substem,
            molecule_dictionary.usan_stem_definition,
            molecule_dictionary.indication_class,
            molecule_dictionary.withdrawn_flag,
            compound_structures.standard_inchi,
            compound_structures.standard_inchi_key,
            compound_structures.canonical_smiles
        FROM molecule_dictionary
        {}
        {}
    """.format(join, where)
    cur = connection.cursor()
    cur.execute(query,(name,))
    return cur.fetchall()


def get_molecule_synonyms(molregno):
    query = """
        SELECT syn_type, synonyms
        FROM molecule_synonyms
        WHERE molregno = ?
    """
    cur = connection.cursor()
    cur.execute(query,(molregno,))
    return cur.fetchall()


def get_target_synonyms(target_chembl_id):
    query = """
        SELECT target_components.tid, syn_type, target_type, component_synonym
        FROM target_dictionary
        JOIN target_components ON target_dictionary.tid = target_components.tid
        JOIN component_synonyms ON target_components.component_id = component_synonyms.component_id
        WHERE chembl_id = ?;
    """
    cur = connection.cursor()
    cur.execute(query, (target_chembl_id,))
    return cur.fetchall()

def get_gene_target_synonyms(component_id):
    query = """
        SELECT DISTINCT component_synonym, syn_type
        FROM component_synonyms
        JOIN target_components ON target_components.component_id = component_synonyms.component_id
        WHERE target_components.component_id =  ?;
    """
    cur = connection.cursor()
    cur.execute(query, (component_id,))
    return cur.fetchall()

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
        LEFT JOIN indication_refs ON (indication_refs.drugind_id = drug_indication.drugind_id)
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
            activities.data_validity_comment,
            activities.standard_text_value,
            activities.standard_upper_value,
            activities.uo_units,
            activities.potential_duplicate,
            activities.action_type,
            assays.chembl_id AS assay_chembl_id,
            assays.description AS assay_description,
            assays.assay_organism,
            assays.assay_cell_type,
            assays.assay_subcellular_fraction,
            assays.bao_format,
            assays.assay_category,
            assays.assay_tax_id,
            assays.assay_tissue,
            assays.assay_cell_type,
            assays.relationship_type,
            assays.confidence_score,
            assays.curated_by,
            assays.src_id AS assay_source_id,
            assay_type.assay_desc AS assay_type,
            bioassay_ontology.label AS BAO_label,
            target_dictionary.chembl_id AS target_chembl_id,
            target_dictionary.pref_name AS target_name,
            target_dictionary.organism AS target_organism,
            target_dictionary.target_type,
            component_sequences.component_type,
            component_sequences.accession,
            source.src_description AS source_description,
            cell_dictionary.chembl_id as cell_chembl_id,
            cell_dictionary.cell_name,
            cell_dictionary.cell_description,
            cell_dictionary.cell_source_tissue,
            cell_dictionary.cell_source_organism,
            cell_dictionary.cell_source_tax_id,
            cell_dictionary.clo_id,
            cell_dictionary.efo_id,
            cell_dictionary.cellosaurus_id,
            cell_dictionary.cl_lincs_id,
            cell_dictionary.cell_ontology_id,
            ligand_eff.bei AS ligand_efficiency_BEI,
            ligand_eff.le AS ligand_efficiency_LE,
            ligand_eff.lle AS ligand_efficiency_LLE,
            ligand_eff.sei AS ligand_efficiency_SEI,
            tissue_dictionary.chembl_id AS assay_tissue_chembl_id,
            tissue_dictionary.pref_name AS assay_tissue_name,
            docs.chembl_id AS document_chembl_id,
            docs.journal,
            docs.title,
            docs.year,
            docs.authors,
            docs.pubmed_id,
            docs.doi,
            relationship_type.relationship_desc AS relationship_description,
            confidence_score_lookup.description AS confidence_score_description,
            confidence_score_lookup.target_mapping,
            curation_lookup.description AS curation_description
        FROM activities
        JOIN molecule_dictionary ON activities.molregno=molecule_dictionary.molregno
        JOIN assays ON activities.assay_id=assays.assay_id
        LEFT JOIN bioassay_ontology on bioassay_ontology.bao_id = assays.bao_format
        LEFT JOIN target_dictionary ON target_dictionary.tid=assays.tid
        LEFT JOIN target_components ON (
            target_components.tid = target_dictionary.tid AND target_dictionary.target_type IN ('SINGLE PROTEIN'))
        LEFT JOIN component_sequences ON component_sequences.component_id = target_components.component_id
        LEFT JOIN cell_dictionary ON cell_dictionary.cell_id=assays.cell_id
        LEFT JOIN assay_type ON assay_type.assay_type=assays.assay_type
        LEFT JOIN tissue_dictionary ON tissue_dictionary.tissue_id=assays.tissue_id
        LEFT JOIN docs ON activities.doc_id=docs.doc_id
        LEFT JOIN source ON source.src_id = activities.src_id
        LEFT JOIN ligand_eff ON ligand_eff.activity_id=activities.activity_id
        LEFT JOIN relationship_type ON relationship_type.relationship_type = assays.relationship_type
        LEFT JOIN confidence_score_lookup ON confidence_score_lookup.confidence_score = assays.confidence_score
        LEFT JOIN curation_lookup ON curation_lookup.curated_by = assays.curated_by
        WHERE molecule_dictionary.chembl_id =  ?
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,))
    return cur.fetchall()

#####################################################################################
# This query revision allows us to add mutation information to mechanisms transformer 
# (even though this means only 29 rows with mutations).
# We should add mutation attribute if it is not null 
# and mutation_accession attribute if it is different from 
# protein accession. 
#
def get_mechanisms(chembl_id):
    query = """
        SELECT
            drug_mechanism.mec_id,
            drug_mechanism.molregno,
            drug_mechanism.mechanism_of_action,
            drug_mechanism.action_type,
            drug_mechanism.direct_interaction,
            drug_mechanism.mechanism_comment,
            drug_mechanism.selectivity_comment,
            target_dictionary.chembl_id AS target_chembl_id,
            target_dictionary.pref_name AS target_name,
            target_dictionary.target_type,
            target_dictionary.organism AS target_organism,
            binding_sites.site_name,
            target_components.component_id,
            drug_mechanism.binding_site_comment,
            source.src_description AS source_description,
            docs.chembl_id AS document_chembl_id,
            component_sequences.component_type,
            component_sequences.accession,
            component_sequences.description,
            component_sequences.tax_id,
            component_sequences.organism,
            variant_sequences.mutation,
            variant_sequences.accession AS mutation_accession
        FROM drug_mechanism
        JOIN molecule_dictionary ON molecule_dictionary.molregno=drug_mechanism.molregno
        JOIN target_dictionary ON target_dictionary.tid=drug_mechanism.tid
        LEFT JOIN binding_sites ON binding_sites.site_id=drug_mechanism.site_id
        LEFT JOIN compound_records ON compound_records.record_id=drug_mechanism.record_id
        LEFT JOIN docs ON (docs.doc_id=compound_records.doc_id AND compound_records.doc_id!=-1)
        LEFT JOIN source ON source.src_id=compound_records.src_id
        LEFT JOIN target_components ON (
            target_components.tid = target_dictionary.tid)
        LEFT JOIN component_sequences ON component_sequences.component_id = target_components.component_id
        LEFT JOIN variant_sequences ON variant_sequences.variant_id = drug_mechanism.variant_id and drug_mechanism.variant_id != -1
        WHERE molecule_dictionary.chembl_id = ?;
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,))
    return cur.fetchall()


def get_targets(chembl_id):
    query = """
        SELECT 
            drug_mechanism.mec_id,
            drug_mechanism.mechanism_of_action,
            drug_mechanism.action_type,
            target_dictionary.chembl_id AS target_chembl_id,
            target_components.component_id
        FROM drug_mechanism
        JOIN molecule_dictionary ON molecule_dictionary.molregno = drug_mechanism.molregno
        JOIN target_dictionary ON target_dictionary.tid=drug_mechanism.tid
        JOIN target_components ON target_components.tid = drug_mechanism.tid
        WHERE (target_dictionary.target_type = 'SINGLE PROTEIN' OR target_dictionary.target_type = 'PROTEIN FAMILY')
        AND molecule_dictionary.chembl_id = ?;
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,))
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


def get_drug_warning(molregno):
    query = """
        SELECT DISTINCT
            molecule_dictionary.molregno, 
            warning_id, 
            pref_name, 
            withdrawn_flag,
            warning_type, 
            warning_class, 
            warning_description, 
            warning_country, 
            warning_year
        FROM molecule_dictionary
        JOIN drug_warning ON molecule_dictionary.molregno = drug_warning.molregno
        WHERE molecule_dictionary.molregno = ?
    """
    cur = connection.cursor()
    cur.execute(query,(molregno,))
    return cur.fetchall()


def get_warning_references(warning_id):
    query = """
        SELECT DISTINCT ref_type, ref_id, ref_url
        FROM warning_refs 
        WHERE warning_id = ?
    """
    cur = connection.cursor()
    cur.execute(query,(warning_id,))
    return cur.fetchall()


def get_direct_metabolites(chembl_id):
    query = """
        SELECT
            met_id,
            enzyme_name,
            met_conversion,
            met_comment,
            metabolism_organism as organism,
            metabolism_tax_id as tax_id,
            metabolite_record.compound_name AS metabolite_name,
            metabolite.pref_name AS metabolite_pref_name,
            metabolite.chembl_id AS metabolite_chembl_id,
            target_dictionary.target_type AS enzyme_type,
            target_dictionary.chembl_id AS enzyme_chembl_id,
            compound_structures.standard_inchi AS inchi,
            compound_structures.standard_inchi_key AS inchikey,
            compound_structures.canonical_smiles AS smiles
        FROM(
            SELECT met_id, enzyme_name, met_conversion, met_comment, organism as metabolism_organism, tax_id as metabolism_tax_id, metabolite_record_id, enzyme_tid
            FROM molecule_dictionary
            JOIN compound_records ON compound_records.molregno = molecule_dictionary.molregno
            JOIN metabolism ON (metabolism.drug_record_id = compound_records.record_id)
            WHERE molecule_dictionary.chembl_id = ?
            UNION
            SELECT met_id, enzyme_name, met_conversion, met_comment, organism as metabolism_organism, tax_id as metabolism_tax_id, metabolite_record_id, enzyme_tid
            FROM molecule_dictionary
            JOIN compound_records ON compound_records.molregno = molecule_dictionary.molregno
            JOIN metabolism ON (metabolism.substrate_record_id = compound_records.record_id)
            WHERE molecule_dictionary.chembl_id = ?
        )
        JOIN compound_records AS metabolite_record ON metabolite_record.record_id = metabolite_record_id
        JOIN molecule_dictionary AS metabolite on metabolite.molregno = metabolite_record.molregno
        LEFT JOIN target_dictionary ON (target_dictionary.tid = enzyme_tid and target_type != 'UNCHECKED')
        LEFT JOIN compound_structures ON compound_structures.molregno = metabolite.molregno
    """
    cur = connection.cursor()
    cur.execute(query,(chembl_id,chembl_id))
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


target_xref_con = sqlite3.connect("data/UniProt.sqlite", check_same_thread=False)
target_xref_con.row_factory = sqlite3.Row

target_xrefs = {}


def target_xref(accession):
    if accession not in target_xrefs:
        target_xrefs[accession] = get_target_xrefs(accession)
    return target_xrefs[accession]


def get_target_xrefs(accession):
    query = """
        SELECT XREF
        FROM XREF
        WHERE XREF_TYPE = 'Ensembl'
        AND UNIPROT_AC = ?
    """
    xrefs = []
    cur = target_xref_con.cursor()
    cur.execute(query,(accession,))
    for xref in cur.fetchall():
        xrefs.append(xref['XREF'])
    return xrefs
