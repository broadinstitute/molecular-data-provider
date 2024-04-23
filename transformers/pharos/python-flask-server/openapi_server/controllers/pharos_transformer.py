import sqlite3
import json

from transformers.transformer import Transformer
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.connection import Connection



###################################################################################
#
#        WARNING: THIS CLASS IS ONLY FOR TESTING PURPOSES
#
#  INPUT FROM REST REQUEST: Name 
#       -- acetylcholine
#       -- adenosine
#       -- bicalutamide
#       -- bortezomib
#   
class PharosCompoundProducer(Transformer):
    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/producer_transformer_info.json')

    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            find_drug(self, name, compound_list)
        return compound_list


class PharosGeneInteractionsTransformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/gene_targets_transformer_info.json')

    #################################################
    # Request Query Body:
    #   {
    #    'alternative_identifiers': None,
    #    'attributes': None,
    #    'biolink_class': 'ChemicalSubstance',
    #    'connections': None,
    #    'id': 'aspirin',
    #    'identifiers': {'chembl': 'CHEMBL25'},
    #    'names_synonyms': None,
    #    'provided_by': 'pharos',
    #    'source': 'pharos'

    def map(self, compound_list, controls):
        target_list = []    # list of all targets collected by this transformer
        targetDict = {}     # a geneid-element dictionary of collected targets and their elements
        target_id  = ''
    #   find connection data for each compound that was submitted in the query
        for compound in compound_list:
            self.get_targets(compound, target_list, targetDict)         
    #   send back to the REST client the entire list of targets (genes that interact with the drugs)
        return target_list


    #####################################################
    #  
    #  Generate a list of targets for drugs and compounds
    #
    def get_targets(self, element_compound: Element, target_list, targetDict):
        for fieldname in element_compound.identifiers:
            if fieldname in {'pubchem', 'chembl'}:
                if self.has_prefix(fieldname, element_compound.identifiers.get(fieldname), self.INPUT_CLASS):
                    compound_id = self.de_prefix(fieldname, element_compound.identifiers.get(fieldname), element_compound.biolink_class)
                    if fieldname == 'chembl':
                        get_targets_of_drug(self, element_compound.id, compound_id, target_list, targetDict)
                        get_targets_of_compound(self, element_compound.id, compound_id, target_list, targetDict, True)
                    if fieldname == 'pubchem':
                        get_targets_of_compound(self, element_compound.id, compound_id, target_list, targetDict)
        return None




#########################################################################################################################
db_connection = sqlite3.connect("data/Pharos.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) 
db_connection.row_factory = sqlite3.Row

def get_db():
    return db_connection

def close_db(self, e=None):
    pass

#############################################################################
#
#-- ********** Pharos gene target transformer
#-- => biolink_class = "Gene"
#-- => id = ENSEMBL + : + protein.stringid
#-- => drug (drug_activity.drug, drug_activity.source, drug_activity.reference )
#-- => connection (drug_activity.action_type -> relation)
#-- => connection attributes (drug_activity.act_type, drug_activity.act_value )
#-- => protein attributes(protein.description, protein.geneid, target_development_level)
#-- => protein names(protein.name)
#-- => protein identifiers(protein.sym, protein.uniprot, ENSEMBL + : + protein.stringid )
def get_targets_of_drug(this, id, identifier, target_list, targetDict):
    source_element_id = id
    query = """
        SELECT
        drug_activity.drug,
        drug_activity.act_type,
        drug_activity.act_value,
        drug_activity.action_type,
        drug_activity.source,
        drug_activity.reference,
        target.tdl as target_development_level,
        protein.description,
        protein.geneid,
        protein.sym,
        protein.uniprot,
        protein.stringid,
        protein.name
        FROM drug_activity
        join target on target.id = drug_activity.target_id
        JOIN protein on protein.id = drug_activity.target_id
        WHERE cmpd_chemblid = ?
    """
    params = (identifier,)
    dbConnection = get_db()   
    cur = dbConnection.cursor()
    cur.execute(query, params)

#   map for translating Pharo's Tclin, Tchem, Tbio, Tdark into meaningful text
    tdl_map = get_tdl_mapping()

    for row in cur.fetchall():
        gene_connection = None
        element = targetDict.get(row['geneid'])  # look for pre-existing gene target

        if element is None:  # Add a new target to target_list
            element = get_element(source_element_id, this.biolink_class(this.OUTPUT_CLASS), this.SOURCE, this.PROVIDED_BY)
            element.attributes.append(get_attribute(this, 'target_development_level', tdl_map[row['target_development_level']]) )
            element.attributes.append(get_attribute(this, 'symbol', row['sym']) )
            targetDict[row['geneid']] = element
            target_list.append(element)

        gene_connection = get_element_connection(this, source_element_id)
        if row['act_value'] is not None:
            gene_connection.attributes.append(get_attribute(this, row['act_type'], str(row['act_value'])) )
        if row['action_type'] is not None:
            gene_connection.attributes.append(get_attribute(this, "action_type", row['action_type'] ) )
        if  row['reference'] is not None:
            if row['source'] in ['SCIENTIFIC LITERATURE', 'DRUG LABEL']:
                pub_attribute = get_attribute(this, "publication", "publication", row['reference'] ) 
                pub_attribute.attribute_type_id = 'biolink:publication'
            else:
                pub_attribute = get_attribute(this, "reference", row['reference'], row['reference'] ) 
                pub_attribute.attribute_type_id = 'reference'            
            pub_attribute.value_type_id = row['source']
            gene_connection.attributes.append(pub_attribute)
        element.connections.append(gene_connection)
        element.names_synonyms = Names(name=row['description'],
                                        synonyms=[row['sym']],
                                        provided_by = this.PROVIDED_BY,
                                        source=this.SOURCE,), # add names & synonyms from the database

        element.id = this.add_prefix('entrez', str(row['geneid']))
        element.identifiers['entrez'] = element.id

        
    #   category attribute    
        cat_attribute = get_attribute(this, 'biolink:primary_knowledge_source', 'TCRD' ) 
        cat_attribute.attribute_type_id = 'biolink:primary_knowledge_source'
        cat_attribute.value_type_id = "biolink:InformationResource"
        cat_attribute.attribute_source = 'infores:molepro-kp'
        gene_connection.attributes.append(cat_attribute)


#########################################################################
#
#   
#
def get_element_connection(this, source_element_id):
    geneConnection = Connection(
                        source_element_id = source_element_id, 
                        biolink_predicate = this.PREDICATE,
                        inverse_predicate = this.INVERSE_PREDICATE,
                        source = this.SOURCE,
                        provided_by = this.PROVIDED_BY,
                        attributes = [],
                    )    
    return geneConnection


#########################################################################
#
#   
#
def get_attribute(this, original_attribute_name, attribute_value, url=None):
    attribute = Attribute(
                    attribute_type_id= original_attribute_name,
                    attribute_source= this.SOURCE,    
                    provided_by= this.PROVIDED_BY,
                    original_attribute_name= original_attribute_name,
                    value= attribute_value,
                    value_url = url,
                    )
    return attribute


#########################################################################
#
# # Create an object of type openapi_server.models.element  (version 2.3)
#
def get_element(id, biolink_class, source, provided_by):
    element = Element(
            id = '',
            biolink_class = biolink_class,
            identifiers = {},
            names_synonyms = [],
            attributes = [],
            connections = [],
            source = source,
            provided_by = provided_by
    )
    return element



#######################################################################################################
# 
# Read JSON file (data/TargetDevelopmentLeveljson) that contains mapping of the four Pharos TDLs
#
def get_tdl_mapping():      
    with open('data/TargetDevelopmentLevel.json') as json_file:
        tdl_map = json.load(json_file)                           
    return tdl_map


#############################################################################
#
# This method either creates a new target for the target list or it adds
# additional connection attributes to an existing target already in the target list
#
#-- ********** Used by Pharos gene target transformer
#
#-- => compound (cmpd_activity.cmpd_name_in_src, cmpd_activity.catype, cmpd_activity.reference )
#-- => connection (drug_activity.action_type -> relation)
#-- => connection attributes (cmpd_activity.act_type, cmpd_activity.act_value)
#-- => protein attributes(protein.description, protein.geneid, target_development_level)
#-- => protein names(protein.name)
#-- => protein identifiers(protein.sym, protein.uniprot, protein.stringid, )
#------------------------------------------------------------------------------------
# Vlado Dancik (Molecular Data Provider)  7:21 PM 6/8/2021
# On today's operations call there was a discussion about ARAs merging results from KPs 
# and they will need to rely on biolink:primary_knowledge_source attribute to achieve that. 
# To prevent messing them up, we can have only one such attribute per connection. It also 
# means that for connections that are coming from both ChEMBL and GtoPdb, we need to create 
# separate conections.
# 
# 
def get_targets_of_compound(this, id, cid, target_list, targetDict, is_chembl = None):
    source_element_id = id
    query = """
            SELECT
            cmpd_activity.cmpd_name_in_src,
            cmpd_activity.catype,
            cmpd_activity.act_type,
            cmpd_activity.act_value,
            cmpd_activity.reference,
            cmpd_activity.pubmed_ids,
            target.tdl as target_development_level,
            protein.description,
            protein.geneid,
            protein.sym,
            protein.uniprot,
            protein.stringid,
            protein.name
            FROM cmpd_activity
            join target on target.id = cmpd_activity.target_id
            JOIN protein on protein.id = cmpd_activity.target_id
    """

    if is_chembl:
        query =  query + ' where cmpd_activity.cmpd_id_in_src = ?;'
    else:
        query =  query + ' WHERE cmpd_pubchem_cid = ?;'

    params = (cid,)
    dbConnection = get_db()   
    cur = dbConnection.cursor()
    cur.execute(query, params)

#   a map for translating Pharo's Tclin, Tchem, Tbio, Tdark into meaningful text
    tdl_map = get_tdl_mapping()

    for row in cur.fetchall():
        gene_connection = None
        element = targetDict.get(row['geneid'])  # look for pre-existing gene target
        if element is None:  # Add a new target to target_list
            element = get_element(source_element_id, this.biolink_class(this.OUTPUT_CLASS), this.SOURCE, this.PROVIDED_BY)
            element.attributes.append(get_attribute(this, 'target_development_level', tdl_map[row['target_development_level']]) )
            element.attributes.append(get_attribute(this, 'symbol', row['sym']) )
            
            gene_connection = get_element_connection(this, source_element_id)
            element.connections.append(gene_connection)

            element.names_synonyms = Names(name=row['description'],
                                            synonyms=[row['sym']],
                                            provided_by = this.PROVIDED_BY,
                                            source=this.SOURCE,), # add names & synonyms from the database
            element.id = this.add_prefix('entrez', str(row['geneid']))
            element.identifiers['entrez'] = element.id

        #   category attribute    
            cat_attribute = get_attribute(this, 'biolink:primary_knowledge_source', row['catype'] ) 
            cat_attribute.attribute_type_id = 'biolink:primary_knowledge_source'
            cat_attribute.value_type_id = "biolink:InformationResource"
            cat_attribute.description = this.info.name
            gene_connection.attributes.append(cat_attribute)

            targetDict[row['geneid']] = element
            target_list.append(element)
              # 7:21 PM 6/8/2021 requirement for one 'biolink:primary_knowledge_source' per connection
        else: # Either augment existing target connection with new attributes or create a new target connection
            found_primary_knowledge_source = False
            # same_primary_knowledge_source = False
            last = len(element.connections) - 1
            for attributes in element.connections[last].attributes:
                if attributes.attribute_type_id.find('biolink:primary_knowledge_source') == 0:  # 
                    found_primary_knowledge_source = True
                    # if attributes.value.find(row['catype']) == 0:
                    #     same_primary_knowledge_source = True

            if found_primary_knowledge_source: # and not same_primary_knowledge_source:
                    gene_connection = get_element_connection(this, source_element_id) # create the element's new connection
                    element.connections.append(gene_connection)
                #   category attribute    
                    cat_attribute = get_attribute(this, 'biolink:primary_knowledge_source', row['catype'] ) 
                    cat_attribute.attribute_type_id = 'biolink:primary_knowledge_source'
                    cat_attribute.value_type_id = "biolink:InformationResource"
                    cat_attribute.description = this.info.name
                    gene_connection.attributes.append(cat_attribute)
            else:          
                gene_connection = element.connections[last]                           # use the element's last connection

    #   Check when sometimes there is just a null, zero-length string or '-' for act_type
        if row['act_type'] is None or (len(str(row['act_type'])) == 0 or str(row['act_type']) == '-'):
            if row['pubmed_ids'] is not None:
                gene_connection.attributes.append(get_attribute(this, 'activity', str(row['act_value'])) )
        else:
            gene_connection.attributes.append(get_attribute(this, row['act_type'], str(row['act_value'])) )

        if row['pubmed_ids'] is not None:
            pubmeds = str(row['pubmed_ids']).split('|') # There are cases with concatenated multiple PMIDs
            for pubmed in pubmeds:
                already_cited = False
                pubmed_citation = 'PMID:' + pubmed
                for attr in gene_connection.attributes:  # eliminate duplicate citation in JSON output
                    if attr.value == pubmed_citation:
                        already_cited = True
                if not already_cited:
                    pub_attribute = get_attribute(this, "publication", pubmed_citation ) 
                    pub_attribute.attribute_type_id = 'biolink:publication'
                    pub_attribute._value_type_id = 'biolink:uriorcurie'
                    gene_connection.attributes.append(pub_attribute)




#############################################################################
#
# 
#-- ********** Used by TEST Pharos producer transformer
#
#
def find_drug(this, name, compound_list):
    query = """
            SELECT DISTINCT drug,
                drug_activity.act_type,
                drug_activity.act_value,
                drug_activity.has_moa,
                drug_activity.nlm_drug_info,
                drug_activity.reference,
                drug_activity.smiles,
                target.name AS target,
                description, 
                target.comment, 
                target.tdl, 
                target.idg, 
                target.fam, 
                target.famext, 
                has_moa, 
                source, 
                cmpd_chemblid, 
                cmpd_id_in_src, 
                nlm_drug_info, 
                cmpd_activity.cmpd_pubchem_cid, 
                dcid
            FROM drug_activity
            LEFT JOIN target ON drug_activity.target_id = target.id
            LEFT JOIN cmpd_activity ON drug_activity.cmpd_chemblid = cmpd_activity.cmpd_id_in_src
            WHERE drug_activity.drug = ?
    """
    params = (name,)
    dbConnection = get_db()   
    cur = dbConnection.cursor()
    cur.execute(query, params)

    for row in cur.fetchall():
        if row['cmpd_pubchem_cid'] is not None:
            
            element = get_element(name, 
                        this.biolink_class(this.OUTPUT_CLASS), 
                        this.SOURCE, 
                        this.PROVIDED_BY)
            element.id = this.add_prefix('pubchem', str(row['cmpd_pubchem_cid'])) 

            element.names_synonyms = Names(name=name,
                                            synonyms=[name],
                                            provided_by = this.PROVIDED_BY,
                                            source=this.SOURCE,), # add names & synonyms from the database
            
            element.identifiers['chembl'] = this.add_prefix('chembl', str(row['cmpd_chemblid'])) 
            element.identifiers['pubchem'] = this.add_prefix('pubchem', str(row['cmpd_pubchem_cid'])) 

            compound_list.append(element)