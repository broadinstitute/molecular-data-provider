import sqlite3
import json

from transformers.transformer import Transformer, Producer
from openapi_server.models.element import Element

PRIMARY_KNOWLEDGE_SOURCE_INFORES = {
    'ChEMBL': 'infores:chembl',
    'Guide to Pharmacology': 'infores:gtopdb',
    'TCRD': 'infores:pharos',
}



###################################################################################
#
#  INPUT FROM REST REQUEST: Name 
#       -- acetylcholine
#       -- adenosine
#       -- bicalutamide
#       -- bortezomib
#   
class PharosCompoundProducer(Producer):
    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/producer_transformer_info.json')

    def produce(self, controls):
        names = [name.strip() for name in controls[self.variables[0]]]
        names = list(dict.fromkeys(name for name in names if name))
        return super().produce({self.variables[0]: names})


    def find_names(self, name):
        ids = []
        for row in self.find_compounds(name):
            id = self.get_compound_id(row)
            if id is not None and id not in ids:
                ids.append(id)
        return ids


    def find_compounds(self, name):
        # handle puchem ID search
        if name.startswith('CID:'):
            pubchem_cid = self.de_prefix('pubchem', name, self.OUTPUT_CLASS)
            return find_compound_by_pubchem_id(pubchem_cid)
        # handle ChEMBL ID search
        if name.upper().startswith('CHEMBL'):
            chembl_id = self.de_prefix('chembl', name, self.OUTPUT_CLASS)
            return find_compound_by_chembl_id(chembl_id)
        else:
            return find_compounds_by_name(name)


    # PubChem CID is the preferred id, with ChEMBL id as a fallback
    def get_compound_id(self, row):
        if row['pubchem'] is not None:
            return self.add_prefix('pubchem', str(row['pubchem']))
        if row['chembl'] is not None:
            return self.add_prefix('chembl', str(row['chembl']))
        return None


    def create_element(self, id):
        row = self.get_compound(id)
        if row is None:
            return None
        identifiers = {}
        if row['chembl'] is not None:
            identifiers['chembl'] = self.add_prefix('chembl', str(row['chembl']))
        if row['pubchem'] is not None:
            identifiers['pubchem'] = self.add_prefix('pubchem', str(row['pubchem']))
        if row['smiles'] is not None:
            identifiers['smiles'] = row['smiles']
        names = self.Names(name=row['name'], synonyms=[row['name']], type='primary_name')
        return self.Element(id, self.biolink_class(self.OUTPUT_CLASS), identifiers, names_synonyms=[names])


    def get_compound(self, id):
        if self.has_prefix('pubchem', id, self.OUTPUT_CLASS):
            pubchem_id = self.de_prefix('pubchem', id, self.OUTPUT_CLASS)
            compounds = find_compound_by_pubchem_id(pubchem_id)
            if compounds:
                return compounds[0]
        if self.has_prefix('chembl', id, self.OUTPUT_CLASS):
            chembl_id = self.de_prefix('chembl', id, self.OUTPUT_CLASS)
            compounds = find_compound_by_chembl_id(chembl_id)
            if compounds:
                return compounds[0]
        return None


class PharosGeneInteractionsTransformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/gene_targets_transformer_info.json')
        self.tdl_map = get_tdl_mapping()
        self.action_map = get_action_mapping()

    #################################################
    # Request Query Body:
    #   {
    #    'alternative_identifiers': None,
    #    'attributes': None,
    #    'biolink_class': 'SmallMolecule',
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
        for chembl_id in self.get_identifiers(element_compound, 'chembl', de_prefix=True):
            self.get_targets_of_drug(element_compound.id, chembl_id, target_list, targetDict)
            self.get_targets_of_compound(element_compound.id, chembl_id, target_list, targetDict, True)
        for pubchem_cid in self.get_identifiers(element_compound, 'pubchem', de_prefix=True):
            self.get_targets_of_compound(element_compound.id, pubchem_cid, target_list, targetDict)
        return None


    def create_drug_connection(self, source_element_id, action_type):
        action = self.action_map.get(action_type.upper()) if action_type is not None else None
        if action is None:
            return self.Connection(source_element_id, self.PREDICATE, self.INVERSE_PREDICATE)
        qualifiers = [self.Qualifier(q['qualifier_type_id'], q['qualifier_value']) for q in action['qualifiers']]
        return self.Connection(source_element_id, action['predicate'], action['inv_predicate'], qualifiers=qualifiers)


    def add_connection_attributes(self, connection, primary_knowledge_source):
        attributes = [
            self.Attribute('biolink:primary_knowledge_source', primary_knowledge_source, value_type='biolink:InformationResource'),
            self.Attribute('biolink:knowledge_level', self.KNOWLEDGE_LEVEL),
            self.Attribute('biolink:agent_type', self.AGENT_TYPE),
        ]
        for attribute in attributes:
            attribute.attribute_source = 'infores:molepro'
        connection.attributes.extend(attributes)


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
    def get_targets_of_drug(self, id, identifier, target_list, targetDict):
        source_element_id = id

        for row in find_drug_targets(identifier):
            if row['geneid'] is None:
                continue
            gene_connection = None
            element = targetDict.get(row['geneid'])  # look for pre-existing gene target

            if element is None:  # Add a new target to target_list
                element = self.Element('', self.biolink_class(self.OUTPUT_CLASS), {})
                tdl = self.tdl_map.get(row['target_development_level'])
                if tdl is not None:
                    element.attributes.append(self.Attribute('target_development_level', tdl))
                if row['sym'] is not None:
                    element.attributes.append(self.Attribute('symbol', row['sym']) )
                targetDict[row['geneid']] = element
                target_list.append(element)

            gene_connection = self.create_drug_connection(source_element_id, row['action_type'])
            if row['act_value'] is not None and row['act_type'] is not None:
                gene_connection.attributes.append(self.Attribute(row['act_type'], str(row['act_value'])) )
            if row['action_type'] is not None:
                gene_connection.attributes.append(self.Attribute("action_type", row['action_type'] ) )
            if  row['reference'] is not None:
                pubmed_prefix = 'http://www.ncbi.nlm.nih.gov/pubmed/'
                if row['source'] == 'SCIENTIFIC LITERATURE' and row['reference'].startswith(pubmed_prefix) and row['reference'][len(pubmed_prefix):].isdigit():
                    pub_attribute = self.Attribute("publication", 'PMID:' + row['reference'][len(pubmed_prefix):])
                    pub_attribute.attribute_type_id = 'biolink:publication'
                else:
                    pub_attribute = self.Attribute("reference", row['reference'], url=row['reference'] )
                    pub_attribute.attribute_type_id = 'reference'
                pub_attribute.value_type_id = row['source']
                gene_connection.attributes.append(pub_attribute)
            element.connections.append(gene_connection)
            element.names_synonyms = [self.Names(name=row['description'],
                                            synonyms=[row['sym']] if row['sym'] is not None else [],
                                            type='name')] # add names & synonyms from the database

            element.id = self.add_prefix('entrez', str(row['geneid']))
            element.identifiers['entrez'] = element.id


        #   category attribute
            self.add_connection_attributes(gene_connection, 'infores:pharos')


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
    def get_targets_of_compound(self, id, cid, target_list, targetDict, is_chembl = None):
        source_element_id = id

        if is_chembl:
            rows = find_compound_targets_by_chembl_id(cid)
        else:
            rows = find_compound_targets_by_pubchem_cid(cid)

        for row in rows:
            if row['geneid'] is None:
                continue
            gene_connection = None
            element = targetDict.get(row['geneid'])  # look for pre-existing gene target
            if element is None:  # Add a new target to target_list
                element = self.Element('', self.biolink_class(self.OUTPUT_CLASS), {})
                tdl = self.tdl_map.get(row['target_development_level'])
                if tdl is not None:
                    element.attributes.append(self.Attribute('target_development_level', tdl))
                if row['sym'] is not None:
                    element.attributes.append(self.Attribute('symbol', row['sym']) )

                gene_connection = self.Connection(source_element_id, self.PREDICATE, self.INVERSE_PREDICATE)
                element.connections.append(gene_connection)

                element.names_synonyms = [self.Names(name=row['description'],
                                                synonyms=[row['sym']] if row['sym'] is not None else [],
                                                type='name')] # add names & synonyms from the database
                element.id = self.add_prefix('entrez', str(row['geneid']))
                element.identifiers['entrez'] = element.id

            #   category attribute
                self.add_connection_attributes(gene_connection, PRIMARY_KNOWLEDGE_SOURCE_INFORES.get(row['catype'], row['catype']))

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
                        gene_connection = self.Connection(source_element_id, self.PREDICATE, self.INVERSE_PREDICATE) # create the element's new connection
                        element.connections.append(gene_connection)
                    #   category attribute
                        self.add_connection_attributes(gene_connection, PRIMARY_KNOWLEDGE_SOURCE_INFORES.get(row['catype'], row['catype']))
                else:
                    gene_connection = element.connections[last]                           # use the element's last connection

        #   Check when sometimes there is just a null, zero-length string or '-' for act_type
            if row['act_type'] is None or (len(str(row['act_type'])) == 0 or str(row['act_type']) == '-'):
                if row['pubmed_ids'] is not None:
                    gene_connection.attributes.append(self.Attribute('activity', str(row['act_value'])) )
            else:
                gene_connection.attributes.append(self.Attribute(row['act_type'], str(row['act_value'])) )

            if row['pubmed_ids'] is not None:
                pubmeds = str(row['pubmed_ids']).split('|') # There are cases with concatenated multiple PMIDs
                for pubmed in pubmeds:
                    already_cited = False
                    pubmed_citation = 'PMID:' + pubmed
                    for attr in gene_connection.attributes:  # eliminate duplicate citation in JSON output
                        if attr.value == pubmed_citation:
                            already_cited = True
                    if not already_cited:
                        pub_attribute = self.Attribute("publication", pubmed_citation )
                        pub_attribute.attribute_type_id = 'biolink:publication'
                        pub_attribute._value_type_id = 'biolink:uriorcurie'
                        gene_connection.attributes.append(pub_attribute)



#########################################################################################################################
db_connection = sqlite3.connect("data/Pharos.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) 
db_connection.row_factory = sqlite3.Row

def get_db():
    return db_connection

def close_db(self, e=None):
    pass

#######################################################################################################
# 
# Read JSON file (data/TargetDevelopmentLeveljson) that contains mapping of the four Pharos TDLs
#
def get_tdl_mapping():      
    with open('data/TargetDevelopmentLevel.json') as json_file:
        tdl_map = json.load(json_file)                           
    return tdl_map


# action_type (upper case) -> predicate, inverse predicate and qualifiers
def get_action_mapping():
    with open('conf/pharos_qualifiers.json') as json_file:
        return json.load(json_file)


#############################################################################
#
# 
#-- ********** Used by TEST Pharos producer transformer
#
#
COMPOUND_QUERY = """
SELECT name, chembl, pubchem, smiles FROM (
    SELECT d.drug                                            AS name,
           d.cmpd_chemblid                                   AS chembl,
           c.cmpd_pubchem_cid                                AS pubchem,
           COALESCE(c.smiles, d.smiles)                      AS smiles
    FROM drug_activity d
    LEFT JOIN cmpd_activity c
           ON d.cmpd_chemblid = c.cmpd_id_in_src
           AND c.catype = 'ChEMBL'
    WHERE d.cmpd_chemblid IS NOT NULL

    UNION

    SELECT c.cmpd_name_in_src                                AS name,
           c.cmpd_id_in_src                                  AS chembl,
           c.cmpd_pubchem_cid                                AS pubchem,
           c.smiles                                          AS smiles
    FROM cmpd_activity c
    WHERE c.catype = 'ChEMBL'
    AND NOT EXISTS (
        SELECT 1 FROM drug_activity d
        WHERE d.cmpd_chemblid = c.cmpd_id_in_src
    )    
)
"""


def find_compounds_by_name(name):
    cur = get_db().cursor()
    cur.execute(COMPOUND_QUERY + " WHERE name = ? COLLATE NOCASE", (name,))
    return cur.fetchall()


def find_compound_by_chembl_id(id):
    cur = get_db().cursor()
    cur.execute(COMPOUND_QUERY + " WHERE chembl = ? LIMIT 1", (id,))
    return cur.fetchall()


def find_compound_by_pubchem_id(id):
    if not str(id).isdigit():
        return []
    cur = get_db().cursor()
    cur.execute(COMPOUND_QUERY + " WHERE pubchem = ? LIMIT 1", (int(id),))
    return cur.fetchall()


#############################################################################
#
#-- ********** Used by Pharos gene target transformer
#
#
DRUG_TARGETS_QUERY = """
SELECT
    drug_activity.drug,
    drug_activity.act_type,
    drug_activity.act_value,
    drug_activity.action_type,
    drug_activity.source,
    drug_activity.reference,
    target.tdl AS target_development_level,
    protein.description,
    protein.geneid,
    protein.sym,
    protein.uniprot,
    protein.stringid,
    protein.name
FROM drug_activity
    JOIN target ON target.id = drug_activity.target_id
    JOIN protein ON protein.id = drug_activity.target_id
"""

COMPOUND_TARGETS_QUERY = """
SELECT
    cmpd_activity.cmpd_name_in_src,
    cmpd_activity.catype,
    cmpd_activity.act_type,
    cmpd_activity.act_value,
    cmpd_activity.reference,
    cmpd_activity.pubmed_ids,
    target.tdl AS target_development_level,
    protein.description,
    protein.geneid,
    protein.sym,
    protein.uniprot,
    protein.stringid,
    protein.name
FROM cmpd_activity
    JOIN target ON target.id = cmpd_activity.target_id
    JOIN protein ON protein.id = cmpd_activity.target_id
"""


def find_drug_targets(chembl_id):
    cur = get_db().cursor()
    cur.execute(DRUG_TARGETS_QUERY + " WHERE cmpd_chemblid = ?", (chembl_id,))
    return cur.fetchall()


def find_compound_targets_by_chembl_id(chembl_id):
    cur = get_db().cursor()
    cur.execute(COMPOUND_TARGETS_QUERY + " WHERE cmpd_activity.cmpd_id_in_src = ?", (chembl_id,))
    return cur.fetchall()


def find_compound_targets_by_pubchem_cid(pubchem_cid):
    cur = get_db().cursor()
    cur.execute(COMPOUND_TARGETS_QUERY + " WHERE cmpd_pubchem_cid = ?", (pubchem_cid,))
    return cur.fetchall()

