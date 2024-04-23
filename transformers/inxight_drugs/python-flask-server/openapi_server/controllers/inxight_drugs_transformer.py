import sqlite3
import re
import json
from flask import g
from collections import defaultdict
from transformers.transformer import Producer # noqa: E501
from transformers.transformer import Transformer


db_connection = sqlite3.connect("data/Inxight_Drugs.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
db_connection.row_factory = sqlite3.Row

#SOURCE = 'Inxight:Drugs'

#########################################################################
# 1. This class provides all the Inxight_Drugs information about the  
# substances in the request query to the Inxight_Drugs Transformer REST API
# The Producer function takes each name and returns an element of substance
# information
# GitHub Issue #52 The producers should accept name, InChIKeys, 
# and native CURIES (RXCUI, UNII, CID) as input.
#########################################################################
class Inxight_SubstancesProducer(Producer):
    variables = ['substances']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/substances_transformer_info.json')


    ###########################################################################
    # Called by Producer Base Class' produce() method
    # use name from the query graph
    #
    def find_names(self, name):
        ids = []
        search_string = ''
        find_substance_ids(ids, name, search_string)
        return ids 


    ###########################################################################
    # Called by Producer Base Class' produce() method
    #
    def create_element(self, substance_uuid):
        compound_name = None
        id = None
        biolink_class = self.biolink_class('ChemicalEntity')        # set default
        identifiers = {}        # dict of substance_uuid's various identifiers 
        names_synonyms = None   # dict of substance_uuid's various names & synonyms 
        substance = self.Element(id, 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
        get_substance_details(self, substance_uuid, substance)
        return substance


#########################################################################
#
# 2. RelationshipTransformer takes an UNII value and gives back all
#  connected substances, including any mixtures and components of the UNII substance.
#
#########################################################################
class Inxight_DrugsRelationshipTransformer(Transformer):
    variables = ['substances']
    relations_map = None   # JSON mapping of Inxight Drugs relationship types to Biolink CURIES and qualifiers

    def __init__(self):
        super().__init__(self.variables, definition_file='info/relationships_transformer_info.json')

    ###############################################################
    #  As a child class of Transformer, this method is 
    #  called by default but returns relations to chemical entities.
    #  The collection & controls come from the query graph.
    ###############################################################
    def map(self, collection, controls):
        related_list = []
        get_relations_mapping(self)         # load the relations_map
        
    #   find relationship data for each substance that were submitted
        for substance in collection:
            list_of_identifiers = []
            if 'unii' in substance.identifiers:
                for unii in self.get_identifiers(substance, 'unii'):
                    list_of_identifiers.append(unii)
                get_relationships(self, related_list, substance, list_of_identifiers)
    #   send back to the REST client the entire list of related substances (substances that interact with the drugs)
        return related_list



############################################################################
# 3. This class provides all the Inxight_Drugs information about the  
# drugs in the request query to the Inxight_Drugs Transformer REST API
# The Producer function takes each name and returns an element of drug
# information including the RXCUI and biolink_class of Drug
#
############################################################################
class Inxight_DrugsTransformer(Producer):

    variables = ['drugs']   # for use in controls['drugs']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/drugs_transformer_info.json')


    ###########################################################################
    # Called by Producer Base Class' produce() method
    # use name from the query graph
    #
    def find_names(self, name):
        ids = []
        search_string = ' status = "approved" and approvalID IS NOT NULL AND '
        find_substance_ids(ids, name, search_string)
        return ids


    ###########################################################################
    # Called by Producer Base Class' produce() method
    #
    def create_element(self, substance_uuid):
        compound_name = None
        id = None
        biolink_class = self.biolink_class('Drug')            # set default
        identifiers = {}        # dict of substance_uuid's various identifiers 
        names_synonyms = None   # dict of substance_uuid's various names & synonyms 
        substance = self.Element(id, 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
        get_substance_details(self, substance_uuid, substance)
        return substance


#########################################################################
#
# 4. This Active Ingredients Transformer take a drug's RXCUI value  
# and returns the drug's active ingredients & their biolink class
#
#########################################################################
class Inxight_DrugsActiveIngredientsTransformer(Transformer):
    variables = []
    def __init__(self):
        super().__init__(self.variables, definition_file='info/drugs_active_ingredients_transformer_info.json')
    ###############################################################
    #  As a child class of Transformer, this method is 
    #  called by default but returns active ingredients.
    #  The collection & controls come from the query graph.
    ###############################################################
    def map(self, collection, controls):
        active_ingredients = []
    #   find active_ingredients data for each drug that was submitted
        for drug in collection:
            list_of_identifiers = []
            if 'rxnorm' in drug.identifiers:
                for rxcui in self.get_identifiers(drug, 'rxnorm'):
                    list_of_identifiers.append(rxcui)
                get_active_ingredients(self, active_ingredients, drug, list_of_identifiers)
    #   send back to the REST client the entire list of active ingredients (substances in the drugs)
        return active_ingredients



################################################  Common Functions  #################################################
# This is common code for retrieving substances
# relationships and drugs based on the request query
# to the Inxight_Drugs Transformer REST API 
###############################################################

#connection = sqlite3.connect("data/Inxight_Drugs.sqlite", check_same_thread=False)
#connection.row_factory = sqlite3.Row


########################################################################################################
# Lookup the table of Inxight Drugs relations and their qualifiers
# to find a relation's corresponding predicates
def get_predicates(self,relation):
#   create and return a tuple of predicates
    if relation not in self.relations_map:
        return None
    predicate = self.relations_map[relation]['predicate']
    inv_predicate = self.relations_map[relation]['inv_predicate']
    if predicate is None or inv_predicate is None:
        return None
    return (predicate, inv_predicate)


########################################################################################################
# Lookup the table of Inxight Drugs relations and their qualifiers
# to find a relation's corresponding qualifiers
def get_qualifiers(self,relation):
#   create and return a list of qualifiers
    return (self.relations_map[relation]['qualifiers'])


########################################################################################################
# Lookup the table of Inxight Drugs relations and their attribute
# to find a relation's corresponding tab-delimited list of attributes
def get_attributes(self,relation):
#   create and return attributes in a dictionary
    attributes_list = self.relations_map[relation].get('attributes')
    return attributes_list




#######################################################################################################
# 
# Read JSON file (config/relations.json) that contains mapping of Inxight Drugs relationship type
# with the  the spreadsheet prefixMap.csv.
#
# Then the JSON file is saved into a variable, relationsMap, for general usage by all class methods.
#
def get_relations_mapping(self):      
    with open('config/relations.json') as json_file:
        self.relations_map = json.load(json_file)                          



###########################################################################
# Called by find_names() method to determine type of name submitted
# in the query graph.
#
def find_substance_ids(id_list, name_value, search_string):
    search_column = '_name'                 # by default, assume a search for substance by name
    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

#   check if submitted name is native CURIE, e.g., CID:2244
#   or InChiKey, e.g., BSYNRYMUTXBXSQ-UHFFFAOYSA-N
#   or else just a substance name, e.g., aspirin
    if ':' in name_value:                   # presume to be CURIE
        if 'UNII' in name_value:            # a search for substance by UNII, i.e., column 'substanceUNII'
            search_column = 'substanceUNII'
        elif 'CID' in name_value:           # a search for substance by CID, i.e., column 'structurePubChem'
            search_column = 'structurePubChem'
        elif 'RXCUI' in name_value:         # a search for substance by RXCUI, i.e., column 'RXCUI'
            search_column = 'RXCUI'
        name = name_value.split(":",1)[1].strip()
    elif inchikey_regex.match(name_value) is not None:
        search_column = 'structureInChiKey' # a search for substance by inchikey, i.e., column 'structureInChiKey'
        name = name_value
    else:
        name = name_value
        search_column = '_name'
    """
        Find substance by a name
    """
    query = """
        SELECT DISTINCT 
            substances.uuid AS substance_uuid,
            substanceClass,
            substances.UNII AS substanceUNII,
            _name,
            structurallyDiverse,
            structure_id,
            structures.InChiKey AS structureInChiKey,
            structures.pubChem AS structurePubChem,
            RXCUI,
            NCBI
        FROM substances
        LEFT JOIN structures ON substances.structure_id = structures.id
        JOIN unii_lookup ON substances.UNII = unii_lookup.UNII
        WHERE {search_string} {search_column} = ?
        COLLATE NOCASE;
    """.format(search_column = search_column, search_string = search_string)
    if search_column is not None:
        cur = db_connection.execute(query, (name,))
    #   for each hit (i.e., of the same substance name, an unlikely but possible occurrence)
    for row in cur.fetchall():
        uuid = row["substance_uuid"]
        biolink_class = None
#       Select the correct biolink_class based on substanceClass
        if(row['substanceClass'] in ['structurallyDiverse', 'polymer', 'protein', 'nucleicAcid', 'chemical', 'mixture']):
            biolink_class = get_biolink_class( row['substanceClass'], row['structureInChiKey'] )
        if biolink_class != 'ignore':
            id_list.append(uuid)


###########################################################################
# Called by create_element() method of Inxight_SubstancesProducer & 
# Inxight_DrugsTransformer
#
def get_substance_details(self, id, substance):
    """
        Find substance details by its id
    """
    query = """
        SELECT DISTINCT 
            substances.uuid AS substance_uuid,
            substanceClass,
            substances.UNII AS substanceUNII,
            _name,
            structurallyDiverse,
            protein,
            nucleicAcid,
            mixture,
            polymer,
            structure_id,
            formula,
            opticalActivity,
            atropisomerism,
            stereoCenters,
            definedStereo,
            ezCenters,
            charge,
            mwt AS molecularWeight,
            stereochemistry,
            structures.InChiKey AS structureInChiKey,
            structures.pubChem AS structurePubChem,
            RXCUI,
            NCBI,
            stereoComments
        FROM substances
        LEFT JOIN structures ON substances.structure_id = structures.id
        JOIN unii_lookup ON substances.UNII = unii_lookup.UNII
        WHERE substances.uuid = ?;
    """
    cur = db_connection.execute(query,(id,))
    #   for each hit (i.e., of the same substance name, an unlikely but possible occurrence)
    for row in cur.fetchall():
            uuid = row["substance_uuid"]
            inchikey = None
            biolink_class = None
            substanceClass = row['substanceClass']
    #       Create identifiers by annotating ids with appropriate CURIE 
            id = "UNII:" + row['substanceUNII']
            identifiers = {'unii':id}
            if  (row['structureInChiKey']):
                identifiers["inchikey"]  = row['structureInChiKey']    
            if  (row['structurePubChem']):
                identifiers["pubchem"]  = "CID:" +  row['structurePubChem'] 
            substance.identifiers = identifiers
    #       Select the correct biolink_class based on substanceClass
            if(row['substanceClass'] in ['structurallyDiverse', 'polymer', 'protein', 'nucleicAcid', 'chemical', 'mixture']):
                biolink_class = get_biolink_class( row['substanceClass'], row['structureInChiKey'] )
                substance.biolink_class = biolink_class
            substance.id = id

        #   Append additional attributes collected from Inxight:Drugs substances & unii tables 
            attributes_list= ['substanceClass', 'formula', 'opticalActivity', 'atropisomerism', 'stereoCenters', 'definedStereo', 'ezCenters', 'charge', 'molecularWeight', 'stereochemistry', 'NCBI']
            for attribute in attributes_list:
                
                if row[attribute] is not None and len(row[attribute].strip())>0:
                    if attribute == 'formula':
                        substance.attributes.append(
                        self.Attribute(
                            name= attribute,
                            value= row[attribute],
                            type= 'biolink:has_chemical_formula'
                            )
                        )
                    elif attribute == 'NCBI':
                        substance.attributes.append(
                        self.Attribute(
                            name= 'OrganismTaxon',
                            value= 'NCBITaxon:' + row[attribute],
                            type= 'biolink:in_taxon'
                            )
                        )
                    else:
                        substance.attributes.append(
                        self.Attribute(
                            name= attribute,
                            value= str(row[attribute]),
                            type= attribute
                            )
                    )

            # Append synonyms to the substance
            get_names_synonyms(self, uuid, substance, row['_name'])

            # Append references to the substance
            get_references(self, uuid, substance)

            # Append codes as references to the substance
            get_codes(self, uuid, substance, biolink_class)

            # Need to put this in a dictionary with protein, polymer, nucleic acid, ...
            if substanceClass == 'protein':
                get_protein_info(self, uuid, substance)
            elif substanceClass == 'nucleicAcid':
                get_nucleicAcid_info(self, uuid, substance)


#####################################################
# Match Inxight's substance class to a Biolink class
# 
def get_biolink_class(substanceClass, inchiKey):
        biolinkClass = None
        biolinkClass_dict = {
            'structurallyDiverse':'ChemicalEntity',
            'polymer':'ChemicalEntity',
            'protein':'Protein',
            'mixture_InChiKey':'MolecularMixture',
            'mixture_NoInChiKey':'ChemicalEntity',
            'concept':'ignore',
            'nucleicAcid' :'GenomicEntity',
            'chemical':'SmallMolecule',
            'specifiedSubstanceG1':'ChemicalEntity'
        }
    #   When there are two kinds of mixtures
        if(substanceClass == 'mixture' and inchiKey):
            substanceClass = 'mixture_InChiKey'
        elif(substanceClass == 'mixture'):
            substanceClass = 'mixture_NoInChiKey'   
    #   Select the correct biolink_class based on substanceClass
        biolinkClass = biolinkClass_dict.get(substanceClass, 'ignore')
        return biolinkClass


#####################################################
# Use the UUID to find all the substance's names
# 
def get_names_synonyms(self, uuid, substance, default_name):  
    """
        Build names and synonyms list
    """
    primary_name = None
#   Query for data to fill the Names class.
    query = """ 
        SELECT 
            names.name AS name, 
            names.type AS type,
            names.preferred, 
            names.displayName
        FROM substance_names
        JOIN names ON substance_names.name_id = names.uuid
        WHERE substance_id = ? ;
    """
#   Dictionary to collect the lists of synonyms (aliases) and their respective sources.
    synonyms_dictionary = defaultdict(list)
    cur2 = db_connection.execute(query,(uuid,))
    for row in cur2.fetchall():
    #   powerful statement to build a dictionary (a map) of name types with name lists
        name_type = row['type']
        if row['name'].endswith('[INN]'):
            name = row['name'][:-5].strip()
            synonyms_dictionary['INN'].append(name)
        elif row['preferred'] == 1:
            synonyms_dictionary['Preferred Name'].append(row['name'])
            primary_name = row['name']
        elif row['displayName'] == 1:
            synonyms_dictionary['Display Name'].append(row['name'])
            primary_name = row['name']
        elif name_type != 'Chemical Description':
            synonyms_dictionary[name_type].append(row['name'])
##### OFFICIAL NAME
        if name_type == 'Official Name' and primary_name is None:
            primary_name = row['name']
##### CHEMICAL DESCRIPTION
        if name_type == 'Chemical Description':
            attribute = row['name']
            substance.attributes.append(
                self.Attribute(
                    name = 'chemical description',
                    value = row['name'],
                    type = 'biolink:description'
                )
            )
   
    if primary_name is None:
        primary_name = default_name
    if primary_name is not None:
        substance.names_synonyms.append(
            self.Names(
                name = primary_name,
                type = 'primary name'
            )
        )

    for name_type, syn_list in synonyms_dictionary.items():
        substance.names_synonyms.append(
            self.Names(
                name = syn_list[0] if len(syn_list) == 1 else  None,
                synonyms = syn_list if len(syn_list) > 1 else  None,
                type = name_type
            )
        )


#####################################################
# Use the UUID to find all the substance's references
# 
def get_references(self, uuid, substance):
    """
        Add references to attributes
    """
    query = """ 
        SELECT 
            _references.uuid, 
            citation, 
            id, 
            docType, 
            publicDomain, 
            url, 
            uploadedFile
        FROM entity_references
        JOIN _references ON entity_references.reference_id = _references.uuid
        WHERE entity_references.entity_id = ? ;
    """
    cur4 = db_connection.execute(query, (uuid,))
    for row in cur4.fetchall():
        reference = row['citation']
        url = row['url']
        if (str(row['citation']).lower().find('http') > -1  and str(row['url']).lower().find('http') == -1 ):
            reference = row['url']  # swap
            url = row['citation']   # swap
        if( url is not None and len(str(url).strip()) > 0 ):
            if reference is None:
                reference = url
        if not str(row['url']).lower().startswith('http'):
            url = None
        if reference is not None and (row['docType'] == 'JA' or row['docType'] == 'JOURNAL ARTICLE'):
            substance.attributes.append(
                self.Attribute(
                    name = 'reference',
                    value = reference,
                    type = 'biolink:Publication',
                    url = url
                )
            ) 


#####################################################
# Use the UUID to find all the substance's codes 
# from Inxight:Drugs, which is information that are 
# also references
#  
def get_codes(self, uuid, substance, biolink_class):

    with open('config/codeSystem.json') as json_file:
        codes_map = json.load(json_file)

    """
        Add codes as references to attributes
    """
    query3 = """ 
        SELECT 
            _name,
            type,
            codeSystem,
            comments,
            code,
            url,
            codeText
        FROM substances
        JOIN substance_codes ON substances.uuid = substance_codes.substance_id
        JOIN codes ON substance_codes.code_id = codes.uuid
        WHERE substances.uuid = ?;
    """
    cur3 = db_connection.execute(query3, (uuid,))
    for row in cur3.fetchall():
        if row['codeSystem'] in codes_map:
            prefix = self.get_prefix(codes_map[row['codeSystem']], biolink_class)
            if prefix is not None:
                substance.identifiers[ codes_map[row['codeSystem']]  ] = prefix + row['code']



#####################################################
# Provide attribute information
# 
def get_protein_info(self, uuid, substance):
    """
        Add protein information to attributes
    """
    query = """
            SELECT DISTINCT
                substances.uuid,
                proteinType,
                proteinSubType,
                sequenceType,
                sequenceOrigin,
                disulfideLinks,
                glycosylationType,
                sequence,
                length
            FROM substances
            JOIN proteins ON substances.uuid = proteins.substance_id
            JOIN protein_sequences ON proteins.uuid = protein_sequences.protein_id
            WHERE substances.uuid = ?;
        """
    cur8 = db_connection.execute(query, (uuid,))
    for row in cur8.fetchall():
    #   Append additional attributes collected from Inxight:Drugs substances table 
        attributes_list= ['proteinType', 'proteinSubType', 'sequenceType', 'sequenceOrigin', 'disulfideLinks', 'glycosylationType', 'sequence', 'length']
        for attribute in attributes_list:
            if row[attribute] is not None and len(str(row[attribute]).strip())>0:
                if attribute == 'sequence':
                    attribute_type = 'biolink:has_biological_sequence'
                else:
                    attribute_type = attribute
                substance.attributes.append(
                self.Attribute(
                    name= attribute,
                    value= str(row[attribute]),
                    type= attribute_type
                )
            )           


#####################################################
# Provide attribute information
#
def get_nucleicAcid_info(self, uuid, substance):
    """
        Add Nucleic Acid information to attributes
    """
    query = """
        SELECT DISTINCT
            substances.uuid,
            nucleicAcidType,
            sequenceType,
            sequenceOrigin,
            sequence,
            length
        FROM substances
        JOIN nucleic_acids ON substances.uuid = nucleic_acids.substance_id
        JOIN nucleic_acid_sequences ON nucleic_acids.uuid = nucleic_acid_sequences.nucleic_acid_id
        WHERE substances.uuid = ?;
        """
    cur = db_connection.execute(query, (uuid,))
    for row in cur.fetchall():
    #   Append additional attributes collected from Inxight:Drugs substances table 
        attributes_list= ['nucleicAcidType', 'sequenceType', 'sequenceOrigin',  'sequence', 'length']
        for attribute in attributes_list:
            if row[attribute] is not None and len(str(row[attribute]).strip())>0:
                if attribute == 'sequence':
                    attribute_type = 'biolink:has_biological_sequence'
                else:
                    attribute_type = attribute
                substance.attributes.append(
                self.Attribute(
                    name= attribute,
                    value= str(row[attribute]),
                    type= attribute_type
                )
            )      


#####################################################
# Called by Inxight_DrugsActiveIngredientsTransformer
#
def get_active_ingredients(self, related_list, drug, identifiers_list):
    relationDict = {}

    # using list comprehension to convert each identifier to string and adding delim
    delim = ","
    string_of_identifiers = delim.join([str('"'+ identifier +'"') for identifier in identifiers_list])

    source_element_id = drug.id.strip()
    query7 = """
        SELECT DISTINCT
            unii_lookup.PT,
            unii_lookup.RXCUI,
            unii_lookup.PUBCHEM,
            unii_lookup.NCBI,
            substances._name,
            relatedSubstances._name AS related_substance,
            relatedSubstances.uuid AS related_substance_uuid,
            relatedSubstances.UNII AS related_substance_unii,
            relatedSubstances.substanceClass AS related_substance_class,
            relationships.type AS relationships_type,
            relationships.qualification,
            relationships.amount_average AS average,
            relationships.amount_high AS high,
            relationships.amount_low AS low,
            relationships.amount_units,
            unii_lookup.INCHIKEY AS InChiKey,
            unii_lookup.INGREDIENT_TYPE
        FROM unii_lookup
        JOIN substances ON unii_lookup.UNII = substances.UNII
        LEFT JOIN relationships ON substances.uuid = relationships.substance_id
        JOIN substances AS relatedSubstances ON relationships.relatedSubstance_id = relatedSubstances.uuid
        WHERE
            relationships.type = 'ACTIVE MOIETY'
            AND RXCUI IN ({identifiers}); 
    """.format(identifiers = string_of_identifiers)
    cur7 = db_connection.execute(query7,)

    for row in cur7.fetchall():                         # loop for each related substance found
        biolink_class = get_biolink_class( row['related_substance_class'], row['InChiKey'])
        if (biolink_class != 'ignore' and row['related_substance_unii'] is not None):
            relatedSubstance_id = "UNII:"+str(row['related_substance_unii'])
            if relatedSubstance_id in relationDict:
                related_substance = relationDict[relatedSubstance_id] 
            else:
                uuid = row['related_substance_uuid']
                identifiers = {'unii':relatedSubstance_id}
                if row['InChiKey']:
                    identifiers['inchikey'] = row['InChiKey']
                if  (row['PUBCHEM']):
                    identifiers["pubchem"]  = "CID:" +  row['PUBCHEM'] 
                name = row['related_substance']

                relationships_type = row['relationships_type']
                if  row['RXCUI'] and biolink_class == 'Drug':
                    identifiers["rxnorm"]  = "RXCUI:" +  row['RXCUI'] 
                ingredient = self.Element(
                        id = relatedSubstance_id,
                        biolink_class = biolink_class,
                        identifiers = identifiers,
                        names_synonyms = [] # add name & later synonyms from the database
                )
                # Append synonyms to the substance
                get_names_synonyms(self, uuid, ingredient, name)

            predicate = self.PREDICATE
            inverse_predicate = self.INVERSE_PREDICATE
            ingredient_attribute = self.Attribute('biolink:primary_knowledge_source','infores:inxight_drugs')
            ingredient_attribute.attribute_source = 'infores:molepro'
            relationship  = self.Connection(
                            source_element_id = source_element_id,
                            predicate = predicate,
                            inv_predicate= inverse_predicate,
                            attributes = [ingredient_attribute]
                            )
            relationship.qualifiers = []
            if(row['qualification']):
            #   active ingredients attributes
                attributes_list= ['average', 'high', 'low']
                name = None
                value = None
                for attribute_value in attributes_list:
                    if row[attribute_value] is not None and len(row[attribute_value].strip()) > 0:
                        name  = attribute_value + ' ' + str(row['qualification']) + ' (' + str(row['amount_units']) + ')'
                        value = str(row[attribute_value])
                        relationship.attributes.append(
                        self.Attribute(
                            name  = name,
                            value = value,
                            type  = name
                            )
                        )
                    if( name != None and value != None):
                        relationship.qualifiers.append(self.Qualifier(qualifier_type_id='quantifier qualifier', qualifier_value= name + ' ' + value))

            if(row['relationships_type']):
                relationship.attributes.append(
                self.Attribute(
                    name  = 'relation',
                    value = row['relationships_type'],
                    type  = 'relation'
                    )
                )                

            ingredient.connections.append(relationship)
            relationDict[relatedSubstance_id] = ingredient   # put new related substance in dictionary for future reference

        # Collect all the unique elements for chemicalEntity-substance relationships
        for relatedSubstance_element in relationDict:
            related_list.append(relationDict[relatedSubstance_element]) 



################################################################
# find the relationship data for a substance that was submitted
# in the query
#
def get_relationships(self, relationship_list, substance, identifiers_list):
            relationDict = {}
            # using list comprehension to convert each identifier to string and adding delim
            delim = ","
            string_of_identifiers = delim.join([str('"'+ identifier +'"') for identifier in identifiers_list])

            source_element_id = substance.id.strip()  # This should be Biolink's most preferred id for this substance (e.g., CID:244)

            # check if substance is a mixture that must have components
            get_components(self, relationDict, string_of_identifiers, source_element_id) 
          
            # also check if substance is a component of mixtures
            get_mixtures(self, relationDict, string_of_identifiers, source_element_id)

            """
            Find relationships to other substances by a substance UNII
            """
            query5 = """
            SELECT 
                substances._name AS substance_name,
                substances.UNII,
                substances.mixture,
                relationships.type AS relationships_type,
                relationships.mediatorSubstance_id,
                relationships.interactionType AS interaction_type,
                relationships.qualification,
                relationships.amount_average AS average,
                relationships.amount_high AS high,
                relationships.amount_low AS low,
                relationships.amount_units,
                relationships.comments,
                related.uuid AS related_uuid,
                related._name AS related_substance,
                related.UNII AS related_substance_unii,
                related.substanceClass,
                unii_lookup.RXCUI AS relatedRXCUI,
                unii_lookup.PUBCHEM AS relatedPUBCHEM,
                unii_lookup.INCHIKEY AS InChiKey,
                unii_lookup.NCBI
            FROM substances
            JOIN relationships ON substances.uuid = relationships.substance_id
            JOIN substances AS related ON relationships.relatedSubstance_id = related.uuid
            JOIN unii_lookup ON related.UNII = unii_lookup.UNII
            WHERE substances.UNII IN ({identifiers});
        """.format(identifiers = string_of_identifiers)
            cur5 = db_connection.execute(query5,)

            for row in cur5.fetchall():                         # loop for each related substance found
                # Ignore substance_name and related_substance
                predicate_tuple = get_predicates(self, row['relationships_type'])
                if (predicate_tuple is not None and row['substance_name'] != row['related_substance']):  # check that related substance is not also the substance
                    biolink_class  = get_biolink_class(row['substanceClass'], row['InChiKey'])
                    if (biolink_class != 'ignore' and row['related_substance_unii'] is not None):
                        relatedSubstance_id = "UNII:"+str(row['related_substance_unii'])
                        if relatedSubstance_id in relationDict:
                            related_substance = relationDict[relatedSubstance_id] 
                        else:                       
                            name = row['related_substance']
                        #   Create identifiers by annotating ids with appropriate CURIE prefix
                            identifiers = {'unii':relatedSubstance_id}
                            if  (row['InChiKey']):
                                identifiers["inchikey"]  = row['InChiKey']    
                            if  (row['relatedPUBCHEM']):
                                identifiers["pubchem"]  = "CID:" +  row['relatedPUBCHEM'] 
                        
                            if  row['relatedRXCUI'] and biolink_class == 'Drug':
                                identifiers["rxnorm"]  = "RXCUI:" +  row['relatedRXCUI'] 
                            related_substance = self.Element(
                                id = relatedSubstance_id,
                                biolink_class = biolink_class,
                                identifiers = identifiers,
                                names_synonyms = [self.Names(name=name,
                                                    synonyms=[])] # add name & later synonyms from the database
                            )
                        #   Append additional attributes collected from Inxight:Drugs substances & unii tables 
                            attributes_list= ['substanceClass', 'NCBI']
                            for attribute in attributes_list:
                                if row[attribute] is not None and len(row[attribute].strip())>0: 
                                    if attribute != 'NCBI':
                                        related_substance.attributes.append(
                                            self.Attribute(
                                                name= attribute,
                                                value= str(row[attribute]),
                                                type= attribute
                                            )
                                        )
                                    else: # NCBI id
                                        related_substance.attributes.append(
                                            self.Attribute(
                                                name= 'OrganismTaxon',
                                                value= 'NCBITaxon:' + row[attribute],
                                                type= 'biolink:in_taxon'
                                            )
                                    )
                            relationDict[relatedSubstance_id] = related_substance   # put new related substance in dictionary for future reference

                        #  Build up a connection
                        primary_knowledge = self.Attribute('biolink:primary_knowledge_source','infores:inxight_drugs')
                        primary_knowledge.attribute_source = 'infores:molepro'
                        predicate, inverse_predicate = predicate_tuple
                    #   primary_knowledge URL should be a list of relationships and substance URLs
                        relationship_url = 'https://drugs.ncats.io/substance/' + row['UNII'] + '#relationships'
                        related_substance_url =  'https://drugs.ncats.io/substance/' + row['related_substance_unii']
                        primary_knowledge.value_url =relationship_url + '\t' + related_substance_url
                        relationship  = self.Connection(
                                        predicate = predicate,
                                        inv_predicate = inverse_predicate,
                                        source_element_id = source_element_id,
                                        attributes = [primary_knowledge]
                                    )
                        relationship.qualifiers = get_qualifiers(self,row['relationships_type'])
                        relationship.qualifiers = []
                        #  Append additional attributes collected from Inxight:Drugs relationships table 
                        attributes_list= ['interaction_type', 'comments', 'relationships_type']
                        for attribute in attributes_list:
                            if attribute == 'relationships_type':
                                attribute_name = 'relation'
                            else:
                                attribute_name = attribute
                            if row[attribute] is not None and len(row[attribute].strip())>0:
                                relationship.attributes.append(
                                self.Attribute(
                                    name= attribute_name,
                                    value= str(row[attribute]),
                                    type= attribute_name
                                    )
                            )
                        if(row['qualification']):
                            attributes_list= ['average', 'high', 'low']
                            for attribute in attributes_list:
                                if row[attribute] is not None and len(row[attribute].strip()) > 0:
                                    # e.g., attribute.name: average IC50 (NANOMOLAR), attribute.value: 2.7
                                    name  = attribute + ' ' + str(row['qualification']) + ' (' + str(row['amount_units']) + ')'
                                    value = str(row[attribute])
                                    relationship.attributes.append(
                                    self.Attribute(
                                        name  = name,
                                        value = value,
                                        type  = name
                                        )
                                    )
                        #   Append any attribute from relations_map
                        attribute_list = get_attributes(self,row['relationships_type'])
                        if attribute_list:
                            for attribute_value in attribute_list:
                                if attribute_value:
                                    attr_type, attr_value = attribute_value.split(':',1)
                                    if attr_type.startswith('biolink.'):
                                        attr_type = 'biolink:' + attr_type[8:]
                                    relationship.attributes.append(
                                        self.Attribute(
                                            name  = attr_type,
                                            value = json.loads(attr_value)
                                            )
                                    )                            

                        for qualifier in get_qualifiers(self,row['relationships_type']):
                            relationship.qualifiers.append(qualifier)
                        related_substance.connections.append(relationship)

            # Collect all the unique elements for chemicalEntity-substance relationships
            for relatedSubstance_element in relationDict:
                relationship_list.append(relationDict[relatedSubstance_element]) 


################################################################
#  In case the substance is a mixture that must have components
# Called by Inxight_DrugsRelationshipTransformer.get_relationships()
# 
def get_components(self, relationDict, string_of_identifiers, source_element_id):
    """
        Get components that are "part of" the substance mixture,
        so append components to the relationship_list
        and annotate their Connection per biolink:
        (https://biolink.github.io/biolink-model/docs/part_of)
    """
    query13 = """
        SELECT 
            substances.UNII,
            substances._name AS substance_name,
            component_substances.uuid AS component_uuid,
            component_substances._name AS component_substance,
            component_substances.UNII AS component_substance_unii,
            component_substances.substanceClass,
            unii_lookup.RXCUI AS component_RXCUI,
            unii_lookup.PUBCHEM AS component_PUBCHEM,
            unii_lookup.INCHIKEY AS component_InChiKey,
            unii_lookup.NCBI AS component_NCBI
        FROM substances
        JOIN mixtures ON substances.mixture = mixtures.uuid
        JOIN components ON mixtures.uuid = components.mixture_id
        JOIN substances AS component_substances ON components.refuuid = component_substances.uuid
        JOIN unii_lookup ON component_substances.UNII = unii_lookup.UNII 
        WHERE substances.UNII IN ({string_of_identifiers});
        """.format(string_of_identifiers = string_of_identifiers)

    cur13 =  db_connection.execute(query13, )

    for row in cur13.fetchall():                         # loop for each component substance found
        biolink_class  = get_biolink_class(row['substanceClass'], row['component_InChiKey'])
        if (biolink_class != 'ignore' and row['component_substance_unii'] is not None):
            componentSubstance_id = "UNII:"+str(row['component_substance_unii'])
            if componentSubstance_id in relationDict:
                component = relationDict[componentSubstance_id]
            else:
                name = row['component_substance']
            #   Create identifiers by annotating ids with appropriate CURIE prefix
                identifiers = {'unii':componentSubstance_id}
                if  (row['component_InChiKey']):
                    identifiers["inchikey"]  = row['component_InChiKey']    
                if  (row['component_PUBCHEM']):
                    identifiers["pubchem"]  = "CID:" +  row['component_PUBCHEM'] 
                if  row['component_RXCUI'] and biolink_class == 'Drug':
                        identifiers["rxnorm"]  = "RXCUI:" +  row['component_RXCUI'] 

                component = self.Element(
                    id = componentSubstance_id,
                    biolink_class = biolink_class,
                    identifiers = identifiers,
                    names_synonyms = [self.Names(name=name,
                                            synonyms=[])], # add name & later synonyms from the database
                    attributes = []
                )
                relationDict[componentSubstance_id] = component   # put new related substance in dictionary for future reference

            #   Build up a connection
            predicate = 'biolink:has_part'
            inverse_predicate = 'biolink:part_of'

            primary_knowledge = self.Attribute('biolink:primary_knowledge_source','infores:inxight_drugs')
            primary_knowledge.attribute_source = 'infores:molepro'
        #   primary_knowledge URL should be a list of relationships and substance URLs
            relationship_url = 'https://drugs.ncats.io/substance/' + row['UNII'] + '#components'
            related_substance_url =  'https://drugs.ncats.io/substance/' + row['component_substance_unii']
            primary_knowledge.value_url =relationship_url + '\t' + related_substance_url

            relationship = self.Connection(
                        predicate = predicate,
                        inv_predicate = inverse_predicate,                
                        source_element_id = source_element_id,
                        attributes = [primary_knowledge]
                    )
            relationship.attributes.append(
                    self.Attribute(
                        name  = 'relation',
                        value = 'HAS_PART',
                        type  = 'relation'
                        )
                    )
            
            component.connections.append(relationship)



################################################################
# Check if substance is a component of any mixtures
#
def get_mixtures(self, relationDict, string_of_identifiers, source_element_id):
        """
            Get mixtures that "has part" that includes the substance as a component,
            so append any mixtures to the relationship_list
            and annotate their Connection per biolink: 
            (https://biolink.github.io/biolink-model/docs/has_part.html)
        """
        query14 = """
            SELECT 
                substances.UNII,
                substances._name AS substance_name,
                mixture_substances.uuid AS mixture_uuid,
                mixture_substances._name AS mixture_substance,
                mixture_substances.UNII AS mixture_substance_unii,
                mixture_substances.substanceClass,
                unii_lookup.RXCUI AS mixture_RXCUI,
                unii_lookup.PUBCHEM AS mixture_PUBCHEM,
                unii_lookup.INCHIKEY AS mixture_InChiKey,
                unii_lookup.NCBI AS mixture_NCBI
            FROM substances
            JOIN components ON substances.uuid = components.refuuid
            JOIN mixtures ON components.mixture_id = mixtures.uuid
            JOIN substances AS mixture_substances ON mixtures.uuid = mixture_substances.mixture
            JOIN unii_lookup ON mixture_substances.UNII = unii_lookup.UNII 
            WHERE substances.UNII IN ({string_of_identifiers}) ;
            """.format(string_of_identifiers = string_of_identifiers)


        cur14 = db_connection.execute(query14, )
        for row in cur14.fetchall():                         # loop for each mixture substance found
            biolink_class  = get_biolink_class(row['substanceClass'], row['mixture_InChiKey'])
            if (biolink_class != 'ignore' and row['mixture_substance_unii'] is not None):
                mixture_id = "UNII:"+str(row['mixture_substance_unii'])
                if mixture_id in relationDict:
                    mixture = relationDict[mixture_id]
                else:
                    name = row['mixture_substance']
                #   Create identifiers by annotating ids with appropriate CURIE prefix
                    identifiers = {'unii':mixture_id}
                    if  (row['mixture_InChiKey']):
                        identifiers["inchikey"]  = row['mixture_InChiKey']    
                    if  (row['mixture_PUBCHEM']):
                        identifiers["pubchem"]  = "CID:" +  row['mixture_PUBCHEM'] 
                    
                    biolink_class = get_biolink_class( row['substanceClass'], row['mixture_InChiKey'])
                    if  row['mixture_RXCUI'] and biolink_class == 'Drug':
                            identifiers["rxnorm"]  = "RXCUI:" +  row['mixture_RXCUI'] 
                    mixture = self.Element(
                        id = mixture_id,
                        biolink_class = biolink_class,
                        identifiers = identifiers,
                        names_synonyms = [self.Names(name=name,
                                                synonyms=[])], # add name & later synonyms from the database
                        attributes = []
                    )
                    relationDict[mixture_id] = mixture   # put new related substance in dictionary for future reference

            #   Build up a connection
                primary_knowledge = self.Attribute('biolink:primary_knowledge_source','infores:inxight_drugs')
                primary_knowledge.attribute_source = 'infores:molepro'
                predicate = 'biolink:part_of'
                inverse_predicate = 'biolink:has_part'

            #   primary_knowledge URL should be a list of relationships and substance URLs
                relationship_url = 'https://drugs.ncats.io/substance/' + row['UNII']
                related_substance_url =  'https://drugs.ncats.io/substance/' + row['mixture_substance_unii'] + '#components'
                primary_knowledge.value_url = related_substance_url + '\t' + relationship_url
                relationship = self.Connection(
                            predicate = predicate,
                            inv_predicate = inverse_predicate,                
                            source_element_id = source_element_id,
                            attributes = [primary_knowledge]
                        )
                relationship.attributes.append(
                self.Attribute(
                    name  = 'relation',
                    value = 'IS_PART_OF',
                    type  = 'relation'
                    )
                )
                        
                mixture.connections.append(relationship)


def get_relationship_types(self, json_obj, search_string):  
        if search_string is not None:
            search = search_string
        else: 
            search = '1 = 1'
        """
            get all the relationship types of substances
        """
        query10 = """
            SELECT DISTINCT
                relationships.type
            FROM relationships 
            WHERE {search}
            GROUP BY relationships.type;
            """.format(search=search)
        db_connection.row_factory = sqlite3.Row
        cur10 = db_connection.execute(query10)
        ############ TBD json_obj["knowledge_map"]["edges"][0]["relations"].clear()  # step 1, clear the list of old relations
        ############ TBD for row in cur10.fetchall():
        #   step 2, fill the list of relations 
        ############ TBD     json_obj["knowledge_map"]["predicates"][0]["relations"].append(row["type"])


def get_substance_counts(self, json_obj):  
        """
            count all the undeprecated rows in substances table
        """
        query11 = """
            SELECT COUNT ( DISTINCT uuid ) AS "Number of substances" 
            FROM substances;
            """
        db_connection.row_factory = sqlite3.Row
        cur11 = db_connection.execute(query11)
        json_obj["knowledge_map"]["nodes"]["ChemicalSubstance"]["count"] = -1  # step 1, clear the old count
        for row in cur11.fetchall():
        #   step 2, fill the count value 
            json_obj["knowledge_map"]["nodes"]["ChemicalSubstance"]["count"] = (row["Number of substances"])


def get_drug_counts(self, json_obj):  
        """
            count all the substances that are drugs
        """
        query12 = """
            SELECT COUNT ( DISTINCT uuid ) AS "Number of drugs" 
            FROM substances
            JOIN unii_lookup ON substances.UNII = unii_lookup.UNII
            WHERE NOT RXCUI ISNULL AND LENGTH(RXCUI) > 0;
            """
        #connection = sqlite3.connect("data/Inxight_Drugs.sqlite",
        #            detect_types=sqlite3.PARSE_DECLTYPES) # SQLite database file is located in the python-flask-server/data directory
        db_connection.row_factory = sqlite3.Row
        cur12 = db_connection.execute(query12)
        json_obj["knowledge_map"]["nodes"]["Drug"]["count"] = -1  # step 1, clear the old count
        for row in cur12.fetchall():
        #   step 2, fill the count value 
            json_obj["knowledge_map"]["nodes"]["Drug"]["count"] = (row["Number of drugs"])






       
