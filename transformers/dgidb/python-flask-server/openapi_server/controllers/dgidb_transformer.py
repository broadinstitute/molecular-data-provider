from flask import g
from collections import OrderedDict
from transformers.transformer import Producer 
from transformers.transformer import Transformer
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection
import sqlite3
import re
import json
import copy

SOURCE = 'DGIdb'
database_connection = sqlite3.connect("data/DGIdb.sqlite", check_same_thread=False)
database_connection.row_factory = sqlite3.Row

log = False

field_name_list = [
    'pubchem',
    'chembl',
    'drugbank',
    'gtopdb',
    'pharmgkb',
    'pubchem-sid',
    'nci_thesaurus',
    'ttd',
]

###############################################################
# This class provides all the DGIdb information about the drugs 
# in the request query to the DGIdb Transformer REST API
###############################################################
class DGIdbProducer(Producer):

    variables = ['compound']
    dgidb_prefix_map = {}
    field_name_list = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')
        self.dgidb_prefix_map = load_dgidb_prefix_mapping()  
        self.field_name_list = field_name_list

    ###########################################################################
    # Called by Producer Base Class' produce() method
    # 'name' comes from the query graph
    #
    def find_names(self, name):
        if log:
            print('query name', name)
        if name.startswith('DGIdb.UUID:'):
            id = name[11:] # remove the prefix
            return find_drug_by_id(id)
        ids = find_compound_by_primary_name(name)  # find compound by primary name
        if len(ids) == 0:
            # handle MolePro prefixes
            if name.startswith('GTOPDB:'): 
                name = name.replace('GTOPDB','iuphar.ligand')
            if name.startswith('CID:'): 
                name = name.replace('CID','PUBCHEM.COMPOUND')
            ids = find_compound_by_alias(name)
        return ids    # Returned to Producer.produce(), which then calls create_element()


    def create_element(self, identifier):
        return create_element(self, identifier)


###############################################################
# This class transforms a collection of compounds in the 
# request query to the DGIdb Transformer REST API into 
# information about the corresponding target genes 
###############################################################
class DGIdbTargetTransformer(Transformer):
    variables = []
    dgidb_prefix_map = {}
    dgidb_qualifiers_map = {}
    specific_action_map = {}
    field_names = set()

    def __init__(self):
        super().__init__(self.variables, definition_file='info/targets_transformer_info.json')
        self.dgidb_qualifiers_map = load_dgidb_qualifiers_mapping()
        self.specific_action_map = load_dgidb_specific_action_mapping()
        self.field_names = get_field_names()
        for dgidb_prefix, molepro_prefix in load_dgidb_prefix_mapping().items():
            self.dgidb_prefix_map[molepro_prefix['field_name']] = {molepro_prefix['molepro_prefix'][:-1]: dgidb_prefix+':'}
        if log:
            print(json.dumps(self.dgidb_prefix_map, indent=2))


    def map(self, collection, controls):
        """
            Find targets by compound names
        """
        gene_list = []
        genes = {}
    #   find connection data for each compound that were submitted
        for element in collection:
            ids_set = set()
            for field_name in self.field_names:
                if field_name in element.identifiers:
                    for identifier in self.get_identifiers(element, field_name, de_prefix=False):
                        mapped_identifier = self.map_prefix(self.dgidb_prefix_map[field_name], identifier)
                        if log:
                            print(identifier, '  => ', mapped_identifier)
                        ids_set.add(mapped_identifier)
            for row in find_genes(ids_set):
                gene_id = row['gene_id']
                if log:
                    print('**gene_id:', gene_id)
                if gene_id not in genes:
                    gene = self.create_element(row)
                    if gene is not None:
                        gene_list.append(gene)
                        genes[gene_id] = gene
                gene = genes.get(gene_id)
                if gene is not None:
                    self.add_connection(gene, row, element.id)
    #   send back to the REST client the entire list of targets (genes that interact with the drugs)
        return gene_list


    def map_prefix(self, prefix_map, identifier):
        old_prefix = identifier.split(':')[0]
        if old_prefix in prefix_map:
            return identifier.replace(old_prefix+':', prefix_map[old_prefix])
        return identifier


    def create_element(self, row):
        dgidb_gene_id   = row['gene_id']
        gene = self.Element(
            id = None,
            biolink_class = "Gene",
            identifiers = {},
            names_synonyms = [],
        )
        #   Start adding the gene name & symbol from the genes table
        synonyms_list = [row['symbol']]
        gene.names_synonyms.append(
            Names(
                name = row['name'],
                synonyms = synonyms_list,
                source = self.info.name,
            )
        )
        #   Add identifiers from concept_id
        self.add_id_from_concept_id(row['gene_concept_id'], gene)
        #   Add identifiers & synonyms from the gene_aliases table
        get_gene_names_synonyms(self, dgidb_gene_id, synonyms_list, gene)
        self.set_id(gene)
        if gene.id is None:
            return None
        #   Append to gene additional attributes collected from DGIdb gene_attributes table
        get_gene_attributes(self, gene, self.info.name, dgidb_gene_id)
        return gene


    def add_connection(self, gene, row, source_element_id):
        interaction_id  = row['interaction_id']
        attributes, specific_action_of_ligand, dirrect_interaction = get_interaction_attributes(self, interaction_id)
        predicate = self.PREDICATE
        inv_predicate = self.INVERSE_PREDICATE
        qualifiers = []
        if specific_action_of_ligand in self.dgidb_qualifiers_map:
            qualifiers.extend(self.dgidb_qualifiers_map[specific_action_of_ligand]['qualifiers'])
            if 'qualified_predicate' in self.dgidb_qualifiers_map[specific_action_of_ligand]:
                qualifiers.append({
                    'qualifier_type_id': 'qualified_predicate',
                    'qualifier_value': self.dgidb_qualifiers_map[specific_action_of_ligand]['qualified_predicate']
                })
            predicate = self.dgidb_qualifiers_map[specific_action_of_ligand]['predicate']
            inv_predicate = self.dgidb_qualifiers_map[specific_action_of_ligand]['inv_predicate']
            if log:
                print('  predicate:', predicate, 'inv_predicate:', inv_predicate)
        elif dirrect_interaction:
            predicate = 'biolink:directly_physically_interacts_with'
            inv_predicate = 'biolink:directly_physically_interacts_with'
        drug_gene_interaction  = self.Connection(
                            source_element_id = source_element_id,
                            attributes = attributes,
                            predicate = predicate,
                            inv_predicate = inv_predicate,
                            qualifiers = qualifiers
                        )
        gene.connections.append(drug_gene_interaction)


    def add_id_from_concept_id(self, concept_id, gene):
        if ':' in concept_id:
            (field_name, id) = concept_id.split(':', 1)
            if field_name == 'ncbigene':
                field_name = 'entrez'
            id = self.add_prefix(field_name, id)
            gene.identifiers[field_name] = id
            if log:
                print('concept_id:', concept_id, 'field_name:', field_name, 'id:', id)


    def set_id(self, gene):
        if 'entrez' in gene.identifiers:
            gene.id = gene.identifiers['entrez']
        if gene.id is None and 'hgnc' in gene.identifiers:
            gene.id = gene.identifiers['hgnc']


###############################################################
# This class transforms a collection of genes in the 
# request query to the DGIdb Transformer REST API into 
# information about the corresponding drugs (compounds)
###############################################################
class DGIdbInhibitorTransformer(Transformer):
    variables = []
    dgidb_prefix_map = {}
    field_name_list = []
    dgidb_qualifiers_map = {}
    specific_action_map = {}
    gene_prefix_map = {
        'entrez': 'NCBIGENE:',
        'ensembl': 'ENSEMBL:',
        'hgnc': 'HGNC:',
    }
    gene_concept_prefix_map = {
        'entrez': 'ncbigene:',
        'ensembl': 'ensembl:',
        'hgnc': 'hgnc:',
    }

    def __init__(self):
        super().__init__(self.variables, definition_file='info/inhibitors_transformer_info.json')
        self.dgidb_prefix_map = load_dgidb_prefix_mapping() 
        self.dgidb_qualifiers_map = load_dgidb_qualifiers_mapping()
        self.specific_action_map = load_dgidb_specific_action_mapping()
        self.field_name_list = field_name_list


    def map(self, collection, controls):
        drug_list = OrderedDict()

    #   find connection (gene-inhibitor interaction) data for each gene that were submitted
        for gene in collection:
            for gene_id in self.get_gene_ids(gene):
                if log:
                    print('gene_id:', gene_id)
                for interaction in find_drugs_by_gene(gene_id):
                    if log:
                        print('  interaction:', interaction['interaction_id'])
                    grug_id = interaction['drug_id']
                    if grug_id not in drug_list:
                        drug = create_element(self, grug_id)
                        if drug is not None:
                            drug_list[grug_id] = drug
                    drug = drug_list.get(grug_id)
                    if drug is not None:
                        self.add_connection(drug, interaction, gene.id)

    #   send back to the REST client the entire list of targets (genes that interact with the drugs)
        return [drug for drug in drug_list.values()]


    def get_gene_ids(self, gene):
        gene_ids = set()
        for field_name in ['entrez', 'ensembl', 'hgnc']:
            for gene_id in self.get_identifiers(gene, field_name, de_prefix=True):
                gene_id = self.gene_concept_prefix_map[field_name] + gene_id
                gene_ids.add(gene_id)
        dgidg_gene_id = find_gene_by_concept_id(gene_ids)
        if len(dgidg_gene_id) > 0:
            return dgidg_gene_id

        gene_ids = set()
        for field_name in ['entrez', 'ensembl', 'hgnc']:
            for gene_id in self.get_identifiers(gene, field_name, de_prefix=True):
                gene_id = self.gene_prefix_map[field_name] + gene_id
                gene_ids.add(gene_id)
        return find_gene_by_id(gene_ids)


    def add_connection(self, drug, row, source_element_id):
        interaction_id  = row['interaction_id']
        attributes, specific_action_of_ligand, dirrect_interaction = get_interaction_attributes(self, interaction_id)
        predicate = self.PREDICATE
        inv_predicate = self.INVERSE_PREDICATE
        qualifiers = []
        if specific_action_of_ligand in self.dgidb_qualifiers_map:
            qualifiers.extend(self.invert(self.dgidb_qualifiers_map[specific_action_of_ligand]['qualifiers']))
            if 'inv_qualified_predicate' in self.dgidb_qualifiers_map[specific_action_of_ligand]:
                qualifiers.append({
                    'qualifier_type_id': 'qualified_predicate',
                    'qualifier_value': self.dgidb_qualifiers_map[specific_action_of_ligand]['inv_qualified_predicate']
                })
            predicate = self.dgidb_qualifiers_map[specific_action_of_ligand]['inv_predicate']
            inv_predicate = self.dgidb_qualifiers_map[specific_action_of_ligand]['predicate']
            if log:
                print('  predicate:', predicate, 'inv_predicate:', inv_predicate)
        elif dirrect_interaction:
            predicate = 'biolink:directly_physically_interacts_with'
            inv_predicate = 'biolink:directly_physically_interacts_with'
        connection  = self.Connection(
                            source_element_id = source_element_id,
                            attributes = attributes,
                            predicate = predicate,
                            inv_predicate = inv_predicate,
                            qualifiers = qualifiers
                        )
        drug.connections.append(connection)


    def invert(self, qualifiers):
        inv_qualifiers = []
        for qualifier in qualifiers:
            if qualifier['qualifier_type_id'].startswith('subject_'):
                qualifier['qualifier_type_id'] = qualifier['qualifier_type_id'].replace('subject_', 'object_')
            elif qualifier['qualifier_type_id'].startswith('object_'):
                qualifier['qualifier_type_id'] = qualifier['qualifier_type_id'].replace('object_', 'subject_')
            inv_qualifiers.append(qualifier)
        return qualifiers


############################################################################################################
# Common code for retrieving genes and drugs 
# based on the request query to the DGIdb Transformer REST API 
############################################################################################################


###############################################################
# Obtain the list of field names from the drugs_aliases table
def get_field_names():
    query = "SELECT DISTINCT field_name FROM drug_aliases;"
    cur = database_connection.execute(query)
    field_name_list = set()
    for row in cur.fetchall():
        field_name_list.add(row['field_name'])
    return field_name_list


###############################################################
# Obtain identifier's field prefix from the dgidb prefix map
#
def map_prefix(dgidb_prefix_map, identifier):
    old_prefix = identifier.split(':')[0]
    if old_prefix in dgidb_prefix_map:
        return identifier.replace(old_prefix+':', dgidb_prefix_map[old_prefix]['molepro_prefix'])
    return identifier

###########################################################
# Read JSON file (config/DGIdb_prefixes.json) that contains 
# mapping of DGIdb identifiers 
def load_dgidb_prefix_mapping():
    with open("config/DGIdb_prefixes.json") as json_file:
        return json.load(json_file)


###########################################################
# Read JSON file (config/DGIdb_qualifiers.json) that contains 
# mapping of DGIdb qualifiers 
def load_dgidb_qualifiers_mapping():
    with open("config/DGIdb_qualifiers.json") as json_file:
        return json.load(json_file)


###########################################################
# Read JSON file (config/DGIdb_moa_map.json) that contains
# mapping of DGIdb Mechanism of Action to specific action
def load_dgidb_specific_action_mapping():
    with open("config/DGIdb_moa_map.json") as json_file:
        return json.load(json_file)


###########################################################
# Pick the top identifier in accordance to Biolink order of
# precedence of prefixes: 
# PUBCHEM.COMPOUND, CHEMBL, DRUGBANK, IUPHAR.LIGAND, PHARMGKB.DRUG, PUBCHEM.SUBSTANCE
# followed by NCIT, TTD.DRUG, rxcui (not on Biolink's list)
def pick_identifier(field_name_list, identifiers):
    element_id = None
    for field_name in field_name_list:
        if field_name in identifiers:
            return identifiers[field_name]
    return element_id  # return even None to keep the default element ID


#######################################################
# Find drug by its ID
#
def find_drug_by_id(id):
    """
    Find a drug by its ID.

    This function queries the database to find a drug with the specified ID.
    It returns a list of IDs that match the given ID.

    """
    if log:
        print('query 11: drugs')
    query11 = """
        SELECT DISTINCT id
        FROM drugs
        WHERE drugs.id = ?;
    """
    ids = []
    cur = database_connection.execute(query11, (id,))
    for row in cur.fetchall():
        ids.append(row['id'])
    return ids


#   Get the compound's id from its name
def find_compound_by_primary_name(name):
    if log:
        print('query 0: drugs')
    query0 = """
        SELECT DISTINCT id
        FROM drugs
        WHERE name = ?
        COLLATE NOCASE;
    """
    ids = []
    cur = database_connection.execute(query0, (name,))
    for row in cur.fetchall():
        ids.append(row['id'])
    return ids


#   Get the compound's synonyms (aliases) and from its name
def find_compound_by_alias(name):
        if log:
            print('query 1: drug_aliases......')
        """
            Find compound by a name
        """
        query1 = """
            SELECT DISTINCT 
                drugs.id 
            FROM drugs
            JOIN drug_aliases ON drugs.id = drug_aliases.drug_id
            WHERE drug_aliases.alias = ?
            COLLATE NOCASE;
        """
        ids = []
        cur = database_connection.execute(query1,(name,))
        # for each hit (i.e., of the same drug name, an unlikely but possible occurrence)
        for row in cur.fetchall():
            ids.append(row['id'])
        return ids


# Called by Producer Base Class' produce() method, which was invoked by 
# Transformer.transform(query) method because "function":"producer" is 
# specified in the openapi.yaml file
#
def create_element(self, identifier):
    id = None
    if log:
        print('  identifier', identifier)
        print('  self.OUTPUT_CLASS',self.OUTPUT_CLASS)
    biolink_class = self.biolink_class(self.OUTPUT_CLASS)       # set default
    identifiers = {'dgidb': 'DGIdb.UUID:'+identifier}       # dict of various identifiers 
    names_synonyms = None              # dict that has list of various synonyms 
    compound = self.Element(id, 
                                biolink_class, 
                                identifiers, 
                                names_synonyms)
    # Append synonyms
    get_names_synonyms(self, identifier, compound)
    cursor = get_compound_by_identifier(identifier)
    compound_id = None
    for row in cursor.fetchall():
        compound_id = row['drug_id']
    # Append additional attributes collected from DGIdb drugs table
        if (row['approved'] == 't'):
            compound.attributes.append(
                    self.Attribute(
                        name='FDA approval', 
                        value="approved",
                        type='FDA approval'
                    )
            ) 
        if (row['immunotherapy'] == 't'):
            compound.attributes.append(
                    self.Attribute(
                        name="Drug Class" ,
                        value="immunotherapy",
                        type="Drug Class"
                    )
            )            
        if (row['anti_neoplastic'] == 't'):
            compound.attributes.append(
                    self.Attribute(
                        name="Drug Class" ,
                        value="anti_neoplastic",
                        type="Drug Class"
                    )
            )
                
    # Append additional attributes from drug attributes table    
    get_drug_attributes(self, compound_id, compound)
    if compound.id is None or len(identifiers) == 0:
        return None
    return compound


#######################################################
#   Get the genes that are targets of the compound
#
def find_genes(id_set):
    if log:
        print('query 2: genes, interactions, drugs')
    ids = ["'"+id+"'" for id in id_set]
    query2 = """
        SELECT DISTINCT
            drugs.id AS drug_id,
            genes.concept_id AS gene_concept_id,
            genes.name AS symbol,
            genes.long_name AS name,
            genes.id AS gene_id,
            interactions.id AS interaction_id
        FROM drug_aliases
        JOIN drugs ON drugs.id = drug_aliases.drug_id
        JOIN interactions ON interactions.drug_id = drugs.id
        JOIN genes ON genes.id = interactions.gene_id
        WHERE alias in ({})
        AND field_name is not null;
    """.format(','.join(ids))
    cur = database_connection.execute(query2)
    return cur.fetchall()


######################################################
#
def get_gene_attributes(self, gene, info_name, dgidb_gene_id):
    if log:
        print('query 3: gene_attributes, gene_attributes_sources, sources', dgidb_gene_id)
    query3 = """ 
            SELECT 
                gene_attributes.name AS attribute_name,
                gene_attributes.value AS attribute_value,
                sources.source_db_name
            FROM gene_attributes
            LEFT JOIN gene_attributes_sources ON gene_attributes_sources.gene_attribute_id = gene_attributes.id
            LEFT JOIN sources ON sources.id = gene_attributes_sources.source_id
            WHERE gene_attributes.gene_id =?;
            """       
    cur3 = database_connection.execute(query3,(dgidb_gene_id,))        
    for row in cur3.fetchall():
        gene.attributes.append(
                self.Attribute(
                    name = row['attribute_name'],
                    value = row['attribute_value'],
                    type = row['attribute_name'],
                )
        )


def find_gene_by_concept_id(gene_ids):
    if log:
        print('query 4c: genes')
    gene_ids = ["'"+id+"'" for id in gene_ids]
    query4 = """
        SELECT DISTINCT id
        FROM genes
        WHERE concept_id in ({});
    """.format(','.join(gene_ids))
    cur = database_connection.execute(query4)
    ids = []
    for row in cur.fetchall():
        ids.append(row['id'])
    return ids


def find_gene_by_id(gene_ids):
    if log:
        print('query 4a: genes')
    gene_ids = ["'"+id+"'" for id in gene_ids]
    query4a = """
        SELECT DISTINCT genes.id
        FROM genes
        JOIN gene_aliases ON genes.id = gene_aliases.gene_id
        WHERE gene_aliases.alias in ({});
    """.format(','.join(gene_ids))
    cur = database_connection.execute(query4a)
    ids = []
    for row in cur.fetchall():
        ids.append(row['id'])
    return ids


#########################################################
#
def find_drugs_by_gene(dgidb_gene_id): 
        """
        Collect all the drugs that inhibit the gene
        """
#       Inhibitors SQL query.
        if log:
            print('query 4: genes, interactions, drugs', dgidb_gene_id)
        query4 = """ 
                SELECT
                    drugs.id AS drug_id,
                    drugs.concept_id AS drug_concept_id,
                    drugs.name AS name,
                    drugs.immunotherapy,
                    drugs.anti_neoplastic,
                    drugs.approved,
                    genes.long_name AS name,
                    interactions.id AS interaction_id
                FROM genes
                JOIN interactions on interactions.gene_id = genes.id
                JOIN drugs ON drugs.id = interactions.drug_id
                WHERE genes.id = ?;
                """     
        cur4 = database_connection.execute(query4,(dgidb_gene_id,))
        return cur4.fetchall()


########################################################################
# Based this function on one in chembl transformer code
# Get the drug's aliases and use them as identifiers or synonyms
def get_names_synonyms(self, identifier, compound):  
    """
        Build names and synonyms list
    """
#   Query for data to fill the Names class.
    if log:
        print('query 5: drug_aliases, drugs', identifier)
    query5 = """ 
        SELECT name, drug_aliases.alias, field_name
            FROM drugs
            JOIN drug_aliases ON drugs.id = drug_aliases.drug_id
        WHERE drugs.id = ?;
    """
#   List to collect synonyms (aliases) 
    synonyms = []
    cur5 = database_connection.execute(query5,(identifier,))

    primary_name = None
    for row in cur5.fetchall():
        primary_name = row['name']
        # sort out the identifiers from the aliases (synonyms)
        field_name = row['field_name']
        if field_name is not None and field_name != '':  # if identifier and not a name
            compound.identifiers[field_name] =  map_prefix(self.dgidb_prefix_map, row['alias'])
        else:                       # else it must be a synonym
            if row['alias'] != primary_name:
                synonyms.append(row['alias'])

    # Pick the best element ID from the identifers_list
    element_id = pick_identifier(self.field_name_list, compound.identifiers)
    if not element_id is None:
        field_name = element_id.split(':')[0].lower()
        compound.id = self.add_prefix(field_name, self.de_prefix(field_name, element_id, self.OUTPUT_CLASS), self.OUTPUT_CLASS)
    
    names =  self.Names(
            name = primary_name,
            type = None,
            synonyms = synonyms
        )
    compound.names_synonyms.append(names)

##################################################################
#
#
def get_drug_attributes(self, id, compound): 
#   query to fill the attributes array.
    if log:
        print('query 6: drug_attributes, drug_attributes_sources, sources', id)
    query6 = """ 
        SELECT DISTINCT
            drug_attributes.name,
            lower(drug_attributes.value) AS value,
            sources.source_db_name AS attribute_source
        FROM drug_attributes
        JOIN drug_attributes_sources ON drug_attributes.id = drug_attributes_sources.drug_attribute_id
        JOIN sources ON drug_attributes_sources.source_id = sources.id
        WHERE drug_attributes.drug_id = ?;
    """
    cur6 = database_connection.execute(query6,(id,))
    # Because of unhashable type: 'Attribute' we need to use a dictionary
    # instead to filter out duplicate attributes.
    attribute_dict = {}
    for row in cur6.fetchall(): 
        attribute_dict[row['name']+row['value']] = self.Attribute(
                    name = row['name'],
                    value = row['value'],
                    type = row['name']
                )
    for an_attribute_key in attribute_dict:
        compound.attributes.append(attribute_dict[an_attribute_key])


#############################################################
# Get the interaction attributes and publication information 
# 
def get_interaction_attributes(self, interaction_id):
    attributes, specific_action_of_ligand, dirrect_interaction = find_interaction_attributes(self, interaction_id)
    #  add primary knowledge source attribute
    attributes.append(
                    self.Attribute(
                        name= 'biolink:primary_knowledge_source',
                        value= self.info.infores,
                        value_type= 'biolink:InformationResource',
                        type= 'biolink:primary_knowledge_source',
                        url = 'https://www.dgidb.org/interactions/' + interaction_id)
                )
    #  add KL/AT
    attributes.append(self.Attribute(
                        name = 'biolink:knowledge_level',
                        value = self.KNOWLEDGE_LEVEL,
                        type = 'biolink:knowledge_level',
                        value_type = 'String')
                        )
    attributes.append(self.Attribute(
                        name = 'biolink:agent_type',
                        value = self.AGENT_TYPE,
                        type = 'biolink:agent_type',
                        value_type = 'String')
                        )
    attributes.extend(find_publication_attributes(self, interaction_id))
    return (attributes, specific_action_of_ligand, dirrect_interaction)


############################################################################################################
# 
# Get the interaction attributes from the interaction_attributes table
#
def find_interaction_attributes(self, interaction_id):
    if log:
        print('query 7: interaction_attributes, interaction_attributes_sources, sources', interaction_id)
    query7 = """ 
            SELECT DISTINCT
                interaction_attributes.name,
                interaction_attributes.value,
                sources.source_db_name
            FROM interaction_attributes
            LEFT JOIN interaction_attributes_sources ON interaction_attributes_sources.interaction_attribute_id = interaction_attributes.id
            LEFT JOIN sources ON sources.id = interaction_attributes_sources.source_id
            WHERE interaction_attributes.interaction_id = ?;
            """
    cur7 = database_connection.execute(query7,(interaction_id,))
    attributes = []
    specific_action_of_ligand = None
    dirrect_interaction = False
    for row in cur7.fetchall():
        attributes.append(
            self.Attribute(
                name=row['name'],
                value=row['value'],
                type=row['name']
            )
        )
        if row['name'] == 'Mechanism of Action' and not row['value'] == 'None': 
            specific_action_of_ligand = self.specific_action_map.get(row['value'])
            if log:
                print('  Mechanism of Action:', row['value'], ' specific_action_of_ligand:', specific_action_of_ligand)
            if specific_action_of_ligand is not None:
                attributes.append(
                    self.Attribute(
                        name = 'specific action of ligand',
                        value = specific_action_of_ligand,
                        type = 'specific action of ligand'
                    )
                )
        if row['name'] == 'Direct Interaction' and row['value'] == 'true':
            dirrect_interaction = True
            if log:
                print('  Direct Interaction:', row['value'])
    return (attributes, specific_action_of_ligand, dirrect_interaction)


############################################################################################
#   Based on the interaction_id, add publication information
def find_publication_attributes(self, interaction_id):
    if log:
        print('query 8: interactions, interactions_publications, publications', interaction_id)
    query8 = """ 
            SELECT 
                publications.pmid,
                publications.citation
            FROM interactions_publications
            JOIN publications ON publications.id = interactions_publications.publication_id
            WHERE interactions_publications.interaction_id = ?;
            """
    cur8 = database_connection.execute(query8,(interaction_id,))  
    attributes = []
    for row in cur8.fetchall():                     # loop for each PubMed citation
        attributes.append(
                        self.Attribute(
                            name = "publication",
                            value = "PMID:"+str(row['pmid']),
                            type = "biolink:Publication", 
                            url = "https://pubmed.ncbi.nlm.nih.gov/" + str(row['pmid']))        
        )
    return attributes


############################################################################################
#   Use the concept id to find the drug's names and other details
#        
def get_compound_by_identifier(identifier):
        """
            Find compound by a chembl_id
        """
        if log:
            print('query 9: drugs')
        query9 = """
                SELECT DISTINCT 
                    drugs.id AS drug_id,
                    drugs.name AS drug_name, 
                    drugs.approved, 
                    drugs.immunotherapy, 
                    drugs.anti_neoplastic, 
                    drugs.concept_id
                FROM drugs
                WHERE id = ?;
        """  
        cur = database_connection.execute(query9,(identifier,))    
        return cur


#######################################################################
#   Based this function on one in chembl transformer code
#   Get the gene's aliases and use them as identifiers or synonyms
#    "ensembl":"ENSEMBL:"
#    "entrez":"NCBIGene:"
#    "hgnc":""HGNC:"
def get_gene_names_synonyms(self, identifier, aliases_list, gene):  
    """
        Build names and synonyms list
    """
#   Query for data to fill the Names class.
    if log:
        print('query 10: genes, gene_aliases', identifier)
    query10 = """ 
        SELECT gene_aliases.alias
        FROM gene_aliases
        WHERE gene_id = ?;
    """
    cur10 = database_connection.execute(query10,(identifier,))

    ensembl_list = []  # there may be multiple ensembl numbers
    for row in cur10.fetchall():
        # sort out the identifiers from the non-identifiers (synonyms)
        if 'NCBIGENE:' in row['alias']:
            id = self.add_prefix('entrez', self.de_prefix('entrez', row['alias'], 'Gene'), 'Gene')
            gene.identifiers['entrez'] = id
        elif 'ENSEMBL:' in row['alias']:
            ensembl_list = []
            if 'ensembl' in gene.identifiers.keys():
                if type(gene.identifiers['ensembl']) == list:
                    gene.identifiers['ensembl'].append(row['alias'])
                else:
                    ensembl_list.append(gene.identifiers['ensembl'])
                    ensembl_list.append(row['alias'])
                    gene.identifiers['ensembl'] = ensembl_list
            else:
                gene.identifiers['ensembl'] = row['alias']
                gene.id = row['alias']
        elif 'HGNC:' in row['alias']:
            gene.identifiers['hgnc'] = row['alias']
        elif not ':' in row['alias'] :
            aliases_list.append(row['alias'])


