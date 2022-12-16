import sqlite3
import re
import json

from openapi_server.models.names import Names
from transformers.transformer import Producer # noqa: E501
from transformers.transformer import Transformer
from collections import defaultdict

db_connection = sqlite3.connect("data/chebi.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
db_connection.row_factory = sqlite3.Row

with open('info/chebi_source.json') as json_file:
    df_source = json.load(json_file)
with open('info/chebi_relations.json') as json_file:
    df_relations = json.load(json_file)


class ChebiCompoundProducer(Producer):
    variables = ['compounds']
    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compounds_transformer_info.json')


    ###########################################################################
    # Called by Producer Base Class' produce() method
    # name
    #
    #
    def find_names(self, name):
        ids = []
        self.find_compound(name, ids)
        return ids


    ###########################################################################
    # Called by Producer Base Class' produce() method
    #
    #    select id, name, source, parent_id, chebi_accession,
    #    status, definition, star, modified_on, created_by
    def create_element(self, compound_id):
        identifiers = {}
        compound_name = None
        for row in get_compound(compound_id):
            compound_name = row['name']
        names = get_names(compound_id, compound_name, self.SOURCE, self.PROVIDED_BY)
        structures = get_structure(compound_id)
        id = self.add_prefix('chebi',str(compound_id))
        identifiers['chebi'] = id
        molepro_class = 'ChemicalEntity'
        if structures.get('SMILES') is not None:
            identifiers['smiles'] = structures.get('SMILES')
            molepro_class = self.OUTPUT_CLASS
        if structures.get('InChI') is not None:
            identifiers['inchi'] = structures.get('InChI')
            molepro_class = self.OUTPUT_CLASS
        if structures.get('InChIKey') is not None:
            identifiers['inchikey'] = structures.get('InChIKey')
            molepro_class = self.OUTPUT_CLASS
        biolink_class = self.biolink_class(molepro_class)
        element = self.Element(id, biolink_class, identifiers, names)
        self.get_attributes(compound_id, element)
        return element


    def find_compound(self, name, ids):
        if name.startswith('InChI='):
            find_compound_by_structure(name, ids)
            return
        if name.startswith('CHEBI:'):
            find_compound_by_id(name, ids)
            return
        if self.inchikey_regex.match(name) is not None:
            find_compound_by_structure(name, ids)
            return
        find_compound_by_name(name, ids)
        if len(ids) == 0:
            find_compound_by_synonym(name, ids)


    ########################################################
    # Find attributes of the compound from
    # compound_origins, comments, database_accession tables
    def get_attributes(self, chebi_id, element):
        get_compound_origins(self, chebi_id, element)
        get_comments(self, chebi_id, element)
        get_accessions(self, chebi_id, element)
        get_chemical_data(self, chebi_id, element)
        get_compound_attributes(self, chebi_id, element) 




###################################################################
# This child class of Transformer is for gathering all the 
# superclass and subclass compounds of a chemical entity.
# For example, some chemical  entities related to CHEBI:190358 are:
# 
###################################################################
class ChebiRelationsTransformer(Transformer):
    variables = ['direction']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/relations_transformer_info.json')

    def map(self, collection, controls):
        relations_list = []    # List of all the elements to be in the knowledge graph
        relations_dict = {}    # Dictionary of all the elements
        for element in collection:
            identifiers = element.identifiers
            id = None
            if 'chebi' in identifiers and identifiers['chebi'] is not None:
                curie = identifiers['chebi']
                if curie is not None:
                   id = self.de_prefix('chebi', identifiers['chebi'])

            ############ RECURSIVE APPROACH #####################
            if id is not None:
                if controls['direction'] in ['up','both']:
                    get_all_relations_up(self, element, id, relations_dict, relations_list, set())    # recursive approach
                if controls['direction'] in ['down','both']:
                    get_all_relations_down(self, element, id, relations_dict, relations_list)  # recursive approach
        return relations_list


    def get_or_create_relation(self, row, chebi_id, relations, relations_list):
        identifiers = {}
        id = self.add_prefix('chebi', str(chebi_id))
        if id in relations:
            return relations[id]

        structures = get_structure(chebi_id)  
        identifiers['chebi'] = id
        if structures.get('SMILES') is not None:
            identifiers['smiles'] = structures.get('SMILES')
        if structures.get('InChI') is not None:
            identifiers['inchi'] = structures.get('InChI')
        if structures.get('InChIKey') is not None:
            identifiers['inchikey'] = structures.get('InChIKey')
            # Retrieve identifiers from the reference table
            # BindingDB
            # ChEMBL
            # PubChem      
        self.get_reference_identifiers(identifiers, chebi_id)

        relation = self.Element(
                        id=id,
                        biolink_class = 'ChemicalEntity',
                        identifiers = identifiers,
                        names_synonyms = get_names(chebi_id, row['name'], self.SOURCE, self.PROVIDED_BY),
                        attributes=[]
                    )
        relation.source = 'infores:chebi'
        self.get_attributes(chebi_id, relation)
        relations[id] = relation
        relations_list.append(relation)
        return relation


    ########################################################
    # Find attributes of the compound from
    # compound_origins, comments, database_accession tables
    def get_attributes(self, chebi_id, relation):
        get_compound_origins(self, chebi_id, relation)
        get_comments(self, chebi_id, relation)
        get_accessions(self, chebi_id, relation)
        get_chemical_data(self, chebi_id, relation)
        get_compound_attributes(self, chebi_id, relation)


    ################################################################################
    #The status we refer to has the following definitions
    #   'C' - Checked by one of our curators and released to the public domain.
    #   'E' - Exists but not been checked by one of our curators.
    #   'S' - Sumbitted.

    def add_connection(self, source_element_id, id, relation, row):
        connection = None

        for c in relation.connections:
            if c.source_element_id == source_element_id:
                return  # do not add to connections the same source_element_id

        if connection is None:
            infores = self.Attribute('biolink:primary_knowledge_source','infores:chebi')
            infores.attribute_source = 'infores:molepro'        

        connection = self.Connection(
            source_element_id=source_element_id,
            predicate=df_relations[row['type']]['biolink_predicate'],
            inv_predicate=df_relations[row['type']]['inverse_predicate'],
            relation=row['type'],
            attributes=[infores]
        )
        if row['relation_status'] == 'C':
            status = 'Checked by one of our curators and released to the public domain.'
        elif row['relation_status'] == 'E':
            status = 'Exists but not been checked by one of our curators.'
        elif row['relation_status'] == 'S':
            status = 'Sumbitted'
        if status is not None:
            attribute = self.Attribute(
                name = 'relation.status',
                value = status,
                url = None
            ) 
            connection.attributes.append(attribute)     
        relation.connections.append(connection)


    ######################################################
    #     "id": "CHEBI:64341",
    #       "identifiers": {
    #       "bindingdb": [
    #       "67445"
    #       ], 
    #
    def get_reference_identifiers(self, identifiers, chebi_id):
        identifiers_dict = defaultdict(list)
        molepro_fieldname = ''
        databases = ['BindingDB', 'ChEMBL', 'PubChem']
        for row in get_references(chebi_id):
            if (row['reference_db_name'] in databases):
            # -- add prefix & molepro field name here
                molepro_fieldname = str(row['reference_db_name']).lower()
                if row['reference_id'].find('SID:') > -1:    # an exception for pubchem SID:
                        molepro_fieldname = 'pubchem-sid'
                key = row['reference_db_name'] + '&' + molepro_fieldname + '&' + 'en'
                if row['reference_db_name'] == 'PubChem':
                    identifiers_dict[key].append(str(row['reference_id']).replace(' ','')) # because ChEBI database includes prefix for PubChem
                else:
                    identifiers_dict[key].append( self.add_prefix(molepro_fieldname, row['reference_id']))

        for key, identifiers_list in identifiers_dict.items():
            key_parts = key.split('&')
            db_name = key_parts[0]
            molepro_field = key_parts[1]
            language = key_parts[2]
            # -- must handle single and array of identifiers
            if len(identifiers_list) == 1:   # only one identifier
                identifiers[molepro_field] = identifiers_list[0]
            else:                            # multiple identifiers
                identifiers[molepro_field] = identifiers_list



########################## Common functions ################################

def get_names(id, primary_name, source, transformer_name):
    name_map = {
        'en@@ChEBI': Names(
            name=primary_name,
            synonyms=[],
            name_type= None,
            source=source,
            provided_by= transformer_name,
            language= 'en'
        )
    }
    names_list = [name_map['en@@ChEBI']]
    synonyms = get_synonyms(id)
    for row in synonyms:
        name = row['name']
        type = row['type']
        source = row['source']
        language = row['language']
        name_type = '' if type=='NAME' or type=='SYNONYM' else type
        key = language+'@'+name_type+'@'+source
        if key not in name_map.keys():
            name_map[key] = Names(
                name = None,
                synonyms =[],
                name_type = name_type if name_type != '' else None,
                source = df_source.get(source,'infores:chebi'),
                provided_by = transformer_name,
                language = language  
            )
            names_list.append(name_map[key])
        names = name_map[key]
        if type=='SYNONYM' or names.name is not None:
            names.synonyms.append(name)
        else:
            names.name = name
    return names_list




def find_compound_by_name(name, ids):
    query = """
        SELECT DISTINCT id FROM compounds
        WHERE name = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(name,))
    for row in cur.fetchall():
        ids.append(row['id'])


def find_compound_by_id(chebi_id, ids):
    query = """
        SELECT DISTINCT id FROM compounds
        WHERE chebi_accession = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))
    for row in cur.fetchall():
        ids.append(row['id'])


def find_compound_by_synonym(synonym, ids):
    query = """
        SELECT DISTINCT compound_id FROM names
        WHERE name = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(synonym,))
    for row in cur.fetchall():
        ids.append(row['compound_id'])


def find_compound_by_structure(structure, ids):
    query = """
        SELECT DISTINCT compound_id FROM structures
        WHERE structure = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(structure,))
    for row in cur.fetchall():
        ids.append(row['compound_id'])


def get_compound(id):
    query = """
        SELECT id, name, chebi_accession FROM compounds
        WHERE id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_synonyms(id):
    query = """
        SELECT name, type, source, language 
        FROM names
        WHERE compound_id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_references(id):
    query = """
        SELECT reference_id, reference_db_name, location_in_ref, reference_name, definition
        FROM reference
        JOIN compounds ON reference.compound_id = compounds.id
        WHERE compound_id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def get_structure(id):
    query = """
        SELECT structure, type 
        FROM structures
        WHERE compound_id = ?
    """
    structures = {}
    cur = db_connection.cursor()
    cur.execute(query,(id,))
    for (structure, type) in cur.fetchall():
        if type != 'mol':
            structures[type] = structure
    return structures


#####################################################################################
# This query allows us to gather all relations information to relations transformer 
# RECURSIVE APPROACH
#
def get_all_relations_up(this, element, chebi_id, relations_dict, relations_list, processed):
    query = """
        SELECT
            relation.id,
            type,
            init_id,
            final_id,
            relation.status AS relation_status,
            name,
            source,
            chebi_accession,
            compounds.status AS compounds_status,
            definition,
            star
        FROM relation
        JOIN compounds ON init_id = compounds.id
        WHERE final_id = ?
        AND relation.status IN ("C", "E", "S");
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))
    for row in cur.fetchall():
    #   ADD new element to the element list if it is not already in the element list
        relation = this.get_or_create_relation(row, row['init_id'], relations_dict, relations_list)
        if relation is not None:
            this.add_connection(element.id, id, relation, row)
        #   Carry on with hierarchy traversal if the new relation is of type "is_a"
        if row['init_id'] not in processed:
            if row['type'] == 'is_a':
                get_all_relations_up(this, element, row['init_id'], relations_dict, relations_list, processed)
            processed.add(row['init_id'])
            

#####################################################################################
# This query allows us to gather all relations information to relations transformer 
# RECURSIVE APPROACH
#
def get_all_relations_down(this, element, chebi_id, relations, relations_list):
    query = """
        SELECT
            relation.id,
            type,
            init_id,
            final_id,
            relation.status AS relation_status,
            name,
            source,
            chebi_accession,
            compounds.status AS compounds_status,
            definition,
            star
        FROM relation
        JOIN compounds ON final_id = compounds.id 
        WHERE init_id = ?
        AND relation.status IN ("C", "E", "S");      
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))
    for row in cur.fetchall():
    #   ADD new element to the element list
        relation = this.get_or_create_relation(row, row['final_id'], relations, relations_list)
        if relation is not None:
            this.add_connection(element.id, id, relation, row)

    #   Carry on with hierarchy traversal if the new relation is of type "is_a"
        if row['type'] == 'is_a':
            get_all_relations_down(this, element, row['final_id'], relations, relations_list)


################################################################
#  Data from chemical_data
#
#
def get_chemical_data(this, chebi_id, element):
    query = """
            SELECT compound_id, 
                chemical_data,
                source,
                type
            FROM chemical_data
            WHERE compound_id = ?;
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))
    for row in cur.fetchall():
        chemical_attribute = None 
        chemical_attribute = this.Attribute(
            name = row['type'],
            value = row['chemical_data'],
            type = row['type']   )
        chemical_attribute.attribute_source = df_source.get(row['source'],'infores:chebi')
        element.attributes.append(chemical_attribute)


################################################################
# Obtain identities and publications from this one table
# e.g., PMCID: PMC3368685  PubMed Central citation
# url https://europepmc.org/article/MED/ for source: Europe PMC 
#
def get_accessions(this, chebi_id, element):
    query = """
        SELECT accession_number, type, database_accession.source, definition 
        FROM database_accession
        JOIN compounds ON database_accession.compound_id = compounds.id
        WHERE compound_id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))

    for row in cur.fetchall():
        subattributes=[]
        url = None
        publication_attribute = None
        if str(row['type']).find('citation') > -1:   # getting publications from database_accession table
            if row['source'] == 'Europe PMC':
                url = 'https://europepmc.org/article/MED/' + row['accession_number'] 
            elif row['type'] == 'PubMed citation':
                url = 'https://pubmed.ncbi.nlm.nih.gov/' + row['accession_number'] 
            publication_attribute = this.Attribute(
                name = 'database_accession.accession_number',
                value = add_ref_prefix(row['type'], row['accession_number']),
                type = 'biolink:publication',
                description = row['type'],
                url = url
            )
            element.attributes.append(publication_attribute)
        else:                                        # getting identifiers from database_accession table
            if(row['type'] == 'CAS Registry Number'):
                element.identifiers['cas'] = this.add_prefix('cas', row['accession_number'])
            elif(row['type'] == 'DrugBank accession'):
                element.identifiers['drugbank'] = this.add_prefix('drugbank', row['accession_number'])
            elif(row['type'] == 'Drug Central accession'):
                element.identifiers['drugcentral'] = this.add_prefix('drugcentral', row['accession_number'])
            elif(row['type'] == 'KEGG COMPOUND accession'):
                element.identifiers['kegg'] = this.add_prefix('kegg', row['accession_number'])
            elif(row['type'] == 'LINCS accession'):
                element.identifiers['lincs'] = this.add_prefix('lincs', row['accession_number'])
  

#####################################################################################
# This query allows us get the species/strain source information of a compound
# 
#
def get_compound_origins(this, chebi_id, element):
    query = """
        select 
            compound_id,
            species_text,
            species_accession,
            component_text,
            component_accession,
            strain_text,
            source_type,
            source_accession,
            comments
        from compound_origins
            where compound_id = ?;
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))

    for row in cur.fetchall():
        subattributes=[]
        url = None
        attribute = this.Attribute(
                name = 'compound_origins.species_accession',
                value = row['species_accession'],
                type = 'biolink:organism_taxon',
                description = row['species_text'],
                url = None
            )

#   build subattributes of species attribute
        if row['strain_text'] is not None and len(str(row['strain_text']).strip()) > 0:
            strain_attribute = this.Attribute(
                    name = 'compound_origins.strain_text',
                    value = row['strain_text'],
                    type = 'strain',
                    url = None
                )
            subattributes.append(strain_attribute)

        if row['component_accession'] is not None and len(str(row['component_accession']).strip()) > 0:
            component_attribute = this.Attribute(
                    name = 'compound_origins.component_accession',
                    value = row['component_accession'],
                    type = 'biolink:part_of',
                    description = row['component_text'],
                    url = None
                )
            subattributes.append(component_attribute)

        url = None
        if str(row['source_type']) ==  'MetaboLights':
            url = 'https://www.ebi.ac.uk/metabolights/' +  row['source_accession']  
        publication_attribute = this.Attribute(
                name = 'compound_origins.source_accession',
                value = add_ref_prefix(row['source_type'], row['source_accession']),
                type = 'biolink:publication',
                url = url
            )
        subattributes.append(publication_attribute)
        attribute.attributes = subattributes
        element.attributes.append(attribute)


#################################################################
#
#
#
def get_comments(this, chebi_id, element):
    query = """
            SELECT * 
            FROM comments
            WHERE compound_id = ?;
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))

    for row in cur.fetchall():
        subattributes=[]
        attribute = this.Attribute(
                name = 'comments.text',
                value = row['text'],
                type = 'biolink:comment'
            )

#   build subattribute of comment attribute
        subattribute = this.Attribute(
                name = 'comments.created_on',
                value = row['created_on'],
                type = 'biolink:creation_date'
            )
        subattributes.append(subattribute)

        subattribute = this.Attribute(
                name= 'comments.datatype',
                value = row['datatype'],
                type = 'comments.datatype'
            )
        subattributes.append(subattribute)

        attribute.attributes = subattributes
        element.attributes.append(attribute)


#################################################################
# To create compound attribute & subattributes
# C  Checked
# D  Deleted
# E  OK (2-star) status
# O  OK
# S  SUBMITTED
# F
# 
# C for checked, D for deleted, S for submitted but not yet checked by a ChEBI curator, or E  for OK (2-star) status] 
# The status of the structures (REDUNDANT, PENDING, SUBMITTED, OK, DELETED, CHECKED OR OBSOLETE) 
# The status of the entry is indicated as OK, CHECKED, DELETED, SUBMITTED, REDUNDANT, or INTERNAL.
# status confirming whether it is OK, CHECKED, DELETED, SUBMITTED, INTERNAL, or REDUNDANT
#

def get_compound_attributes(this, chebi_id, element):
    query = """
        select id, name, source, parent_id, chebi_accession,
        status, definition, star, modified_on, created_by
        from compounds where id = ?
    """
    cur = db_connection.cursor()
    cur.execute(query,(chebi_id,))

    for row in cur.fetchall():
        subattributes=[]
        status = row['status']
        if status == 'C':
            status = 'Checked by one of our curators and released to the public domain.'
        elif status == 'D':
            status = 'Deleted.'
        elif status == 'E':
            status = 'OK (2-star) status.'
        elif status == 'O':
            status = 'OK.'
        elif status == 'S':
            status = 'SUBMITTED.'

        attribute = this.Attribute(
                name = 'compounds.status',
                value = status,
                type = 'compounds.status'
            )
        element.attributes.append(attribute)

        if row['definition'] is not None and len(row['definition']) != 0:
            attribute = this.Attribute(
                    name = 'compounds.definition',
                    value = row['definition'],
                    type = 'biolink:description'
                )
            element.attributes.append(attribute)

        if row['star'] is not None and len(str(row['star'])) != 0:
            attribute = this.Attribute(
                    name = 'compounds.star',
                    value = str(row['star']),
                    type = 'compounds.star'
                )
            element.attributes.append(attribute)

        if row['modified_on'] is not None and len(row['modified_on']) != 0:
            attribute = this.Attribute(
                    name = 'compounds.modified_on',
                    value = row['modified_on'],
                    type = 'biolink:update_date'
                )
            element.attributes.append(attribute)

        if row['created_by'] is not None and len(row['created_by']) != 0:
            attribute = this.Attribute(
                    name = 'compounds.created_by',
                    value = row['created_by'],
                    type = 'biolink:author'
                )
            element.attributes.append(attribute)              


def add_ref_prefix(ref_type, ref_id):
    prefix_map = {'PMID':'PMID:', 'DOI':'DOI:', 'ISBN': 'ISBN:', 'PubMed Id':'PMID:','PubMed citation':'PMID:', 
    'Article':'', 'CiteXplore Id':'citexplore:', 'MetaboLights':'metabolights:'}
    if ref_type in prefix_map:
        return prefix_map[ref_type]+ref_id
    return ref_id
