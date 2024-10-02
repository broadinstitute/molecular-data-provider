import connexion
import sqlite3
import json
import re
import requests
import csv
import copy
from transformers.transformer import Transformer
from transformers.transformer import Producer
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection


SOURCE = 'Reactome'
database_connection = sqlite3.connect("data/reactome.sqlite", check_same_thread=False)
database_connection.row_factory = sqlite3.Row

# CONFIGURATION

def load_class_dict():
    classDict = {}
    csv_file = open("config/entityproducer_lookup.csv", encoding='utf-8-sig')
    for line in csv.DictReader(csv_file, delimiter=","):
        detailDict = {}
        detailDict['Class'] = line['Biolink_Class']
        classDict[line['Source']] = detailDict
    return classDict

classDict = load_class_dict()


#######################################################################################################
# Read JSON file (config/go_dictionary.json) that contains mapping of GO identifiers to aspects (ancestors).
# Then the JSON file is saved into a variable, aspect_map, for general usage by all class methods.
def load_apect_mapping():
    aspect_map = {}
    with open("config/go_dictionary.json") as json_file:
        aspect_map = json.load(json_file)
    return aspect_map


#######################################################################################################
# Read JSON file (config/species.json) that contains mapping of Reactome species.
# Then the JSON file is saved into a variable, speciesMap, for general usage by all class methods.
def load_species_mapping():
    species_map = {}
    with open("config/species.json") as json_file:
        species_map = json.load(json_file)
    return species_map

species_map = load_species_mapping()

#######################################################################################################
# Read JSON file (config/compartments.json) that contains mapping of compartment names to identifiers.
# Then the JSON file is saved into a variable, compartments_map, for general usage by all class methods.
def load_compartments_mapping():
    compartments_map = {}
    with open("config/compartments.json") as json_file:
        compartments_map = json.load(json_file)
    return compartments_map

compartments_map = load_compartments_mapping()

 




####################################################################################
# PRODUCER for handling:
# uniprot, e.g., UniProtKB:Q18048
# chebi, e.g., CHEBI:57865
# miRBase, e.g., miRBase:MI0000449
# gtopdb, e.g., GTOPDB:8967
# entrez, e.g., NCBIGene:4851
# ensembl, e.g., ENSEMBL:ENST00000378549
class ReactomeEntityProducer(Transformer):
    variables = ['compounds']
    compartments_map = None   # JSON mapping of compartment names to Gene Ontology CURIEs

    def __init__(self):
        super().__init__(self.variables, definition_file='info/entities_producer_transformer_info.json')

    def produce(self, controls):
        element_list = []
        elements = {}

        for name in controls[self.variables[0]]:
            for stable_id in self.find_names(name):
                element = self.create_element(stable_id)
                if element is not None:
                    if element.id not in elements:  # if the dictionary doesn't have the new element
                        elements[element.id] = element
                        element_list.append(element)
                    if element.id in elements:
                        elements[element.id].attributes.append(
                            self.Attribute(name='query name', value=name, type=''))
        return element_list


    ###########################################################################
    # Called by ReactomeEntityProducer.find_names() method to determine the
    # entity_stable_identifier corresponding to the entity_name or entity_native_identifier submitted
    # in the query graph. 
    # uniprot	UniProtKB:A0A0B4KH68
    # entrez	NCBIGene:43223
    # chebi     CHEBI:57865
    # miRBase   miRBase:MI0000449
    # gtopdb    GTOPDB:8967
    # ensembl   ENSEMBL:ENSG00000170920
    def find_names(self, query_identifier):
        search_column = None
        id_list = list()
        if ':' not in query_identifier:
            search_column = 'entity_name'    # by default, assume a search for entity by name
    #   check if submitted name is native CURIE, e.g., NCBIGENE:2244
    #   or else just a substance name, e.g., aspirin    
        elif query_identifier.upper().startswith('UNIPROTKB:') or query_identifier.upper().startswith('NCBIGENE:') or \
            query_identifier.upper().startswith('CHEBI:') or query_identifier.upper().startswith('MIRBASE:') or \
            query_identifier.upper().startswith('GTOPDB:') or query_identifier.upper().startswith('ENSEMBL:') or \
            query_identifier.upper().startswith('CID:') or query_identifier.upper().startswith('SID:') or \
            query_identifier.upper().startswith('EMBL:'):  # a search 
            search_column = 'entity_native_identifier'
        elif query_identifier.upper().startswith('reactome:'):
            search_column = None
        """
            Find entity_stable_identifier, if it exists
        """
        query = """
            SELECT DISTINCT 
                entity_stable_identifier
            FROM PHYSICAL_ENTITY
            WHERE {} = ?
        """.format(search_column)
        if search_column is not None:
            cur = database_connection.execute(query, (query_identifier,))
        #   for each hit (i.e., of the same substance name, an unlikely but possible occurrence)
            for row in cur.fetchall():
                id_list.append(row['entity_stable_identifier'])
        else:
            if query_identifier.lower().startswith('reactome:'):
                id_list.append(query_identifier)
        return id_list

    ###########################################################################
    # Called by Producer Base Class' produce() method, which was invoked by 
    # Transformer.transform(query) method because "function":"producer" is 
    # specified in the openapi.yaml file
    # Element ID should be entity_native_identifier. so e.g., we should have UniProtKB for proteins.
    def create_element(self, query_identifier):
        id = None
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)  # set a default class
        identifiers = {}        # dict of entity id's various identifiers 
        names_synonyms = None   # dict of entity id's various names & synonyms 
        entity = self.Element(id, 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
                                 
        self.get_entity_by_id(query_identifier, entity)
        if entity.identifiers == {}:
            return None
        if ':' in query_identifier: # if there is a CURIE identifier then create an element
            #Attributes are obtainable only with reactome entity_stable_identifier
            if type(entity.identifiers['reactome']) == list: 
                for entity_stable_identifier in entity.identifiers['reactome']:
                    self.get_attributes(entity_stable_identifier, entity)
            else:
                self.get_attributes(entity.identifiers['reactome'], entity) # also assign biolink_class based on INTERACTOR.interactor_type
            return entity


    ##############################################################
    # Called by Producer.create_element()
    # Get entity by stable id
    # ChEBI:27760
    # reactome:R-HSA-5690057
    # ENSEMBL:ENST00000378549
    # refseq:NP_068839.1
    def get_entity_by_id(self, identifier, entity):
        search_column = 'entity_name'
    #   check if submitted name is native CURIE, e.g., NCBIGENE:2244
    #   or else just a substance name, e.g., aspirin    
        if identifier.upper().startswith('UNIPROTKB:') or identifier.upper().startswith('NCBIGENE:') or \
            identifier.upper().startswith('CHEBI:') or identifier.upper().startswith('MIRBASE:') or \
            identifier.upper().startswith('GTOPDB:') or identifier.upper().startswith('ENSEMBL:') or \
            identifier.upper().startswith('CID:') or identifier.upper().startswith('SID:') or \
            identifier.upper().startswith('REACT:') or identifier.upper().startswith('EMBL:'):  # a search 
            search_column = 'entity_native_identifier'
        elif identifier.startswith('reactome:'):
            search_column = 'PHYSICAL_ENTITY.entity_stable_identifier'
        elif identifier.startswith('Reactome:'):
            search_column = 'PHYSICAL_ENTITY.entity_stable_identifier'
            identifier = 'reactome:'+ self.de_prefix('reactome', identifier, 'Pathway')
        query = """
                SELECT DISTINCT PHYSICAL_ENTITY.source,
                       INTERACTOR_NAME.source AS name_source,
                       INTERACTOR_NAME.name,
                       entity_native_identifier,
                       PHYSICAL_ENTITY.entity_stable_identifier,
                       entity_name,
                       compartment,
                       alt_id_interactor
                    FROM PHYSICAL_ENTITY
                    LEFT JOIN INTERACTOR_ID ON PHYSICAL_ENTITY.entity_stable_identifier = INTERACTOR_ID.entity_stable_identifier
                    LEFT JOIN INTERACTOR_NAME ON PHYSICAL_ENTITY.entity_stable_identifier = INTERACTOR_NAME.entity_stable_identifier
                    WHERE {} = ?
                """.format(search_column)
        cur = database_connection.execute(query,(identifier,))
        names_synonyms = []
        name_set = set()
        primary_name = None
        compartment = None
        identifiers = {}        # dict of interactor id's various identifiers         
        for row in cur.fetchall():
            # Set up identifiers, names & synonyms and biolink_class
            new_identifier = add_reactome_prefix(self, 'reactome', row['entity_stable_identifier'])
            if not 'reactome' in identifiers:                  # if dictionary is empty then set it to first identifier 
                identifiers['reactome'] = new_identifier       # add the first reactome entry
            elif type(identifiers['reactome']) == list:        # but if there is already a list
                identifiers['reactome'].append(new_identifier) #  then append to it.    
                      
            else:                                           # if there is just one identifier, add another one as part of a list
                if new_identifier != identifiers['reactome']:
                    identifiers['reactome'] = [identifiers.get('reactome'), new_identifier]
            if str(row['alt_id_interactor']).startswith('ChEBI:'):
                identifiers['chebi']= row['alt_id_interactor']
            if str(row['alt_id_interactor']).startswith('ENSEMBL:'):
                if  entity.biolink_class == 'Protein' and 'ENSEMBL:ENSP' in row['alt_id_interactor']:
                    if not 'ensembl' in identifiers:                           # if empty
                        identifiers['ensembl'] = row['alt_id_interactor']      # add the first ensembl entry
                    elif type(identifiers['ensembl']) == list:                 # but if there is already a list
                        identifiers['ensembl'].append(row['alt_id_interactor'])#  then append to it.
                    else:                                                      # else start a list of ensembl entries
                        identifiers['ensembl'] = [identifiers.get('ensembl'),row['alt_id_interactor']]
            if type(identifiers['reactome']) == list:    
                identifiers['reactome'] = list(set(identifiers['reactome']))   
            if str(row['alt_id_interactor']).startswith('reactome:'):
                identifiers['reactome']= add_reactome_prefix(self, 'reactome', row['alt_id_interactor'])
            if str(row['entity_native_identifier']).startswith('UniProtKB:'):
                identifiers['uniprot']= row['entity_native_identifier']
            if not entity.biolink_class == 'Protein' and not row['source'] == 'entrez':
                identifiers[row['source']] = row['entity_native_identifier']              
            if row['name'] != None:
                name_set.add(row['name'])
            if entity.id == None:
                entity.id = new_identifier
            primary_name = row['entity_name']
        #end of loop

        # Make sure it is a collection of unique ensembl identifiers
        if 'ensembl' in identifiers.keys():
            if type(identifiers['ensembl']) == list:
                identifiers['ensembl'] = list(set(identifiers['ensembl']))
        names_synonyms.append(
        self.Names(
            name = primary_name,
            type = 'primary name',
            synonyms =  list(name_set) )
        ) 
        entity.identifiers = copy.deepcopy(identifiers)
        # Check the identifiers for picking the right biolink class
        # and for displaying identifiers consistent with that biolink class
        self.check_identifiers(entity, identifiers)        
        entity.names_synonyms = names_synonyms
        

##############################################################
# Called by Producer.get_entity_by_id()
# It also gets the preferred value for biolink_class from
# INTERACTOR.interactor_type
    def get_attributes(self, entity_stable_identifier, entity):
        query = """
                SELECT
                    interactor_type,
                    interactor_taxid
                FROM INTERACTOR
                WHERE INTERACTOR.entity_stable_identifier = ?
                """
        cur = database_connection.execute(query,(entity_stable_identifier,))  
        for row in cur.fetchall():
            if ':' in row['interactor_taxid']:
                entity.attributes.append(self.Attribute(
                    name = 'interactor_taxid',
                    value= self.add_prefix('ncbi_taxon', str(row['interactor_taxid']).split('(')[0].split(':')[1], 'OrganismEntity'),                    
                    type = 'biolink:in_taxon')
                ) 
            if row['interactor_type'] is not None:
                 # Extract substrings between parentheses using regex
                interactor_type = re.findall(r'\(.*?\)', str(row['interactor_type']))  
                substrings = []
                start_index = interactor_type[0].find("(")
                while start_index != -1:
                    end_index = interactor_type[0].find(")", start_index+1)
                    if end_index != -1:
                        substrings.append(interactor_type[0][start_index+1:end_index])
                    start_index = interactor_type[0].find("(", start_index+1)


    ###########################################################################
    # Called by get_entity_by_entity_stable_id( )
    # 
    # 1. If ChEBI or GtoPdB identifier is obtained then Biolink class is Small Molecule
    # 2. If UniProt identifier is obtained then Biolink class is PROTEIN and exclude all non-Reactome identifiers.
    #    UniProt means PROTEIN, means no ENSEMBL names in the KG
    # 3. If mriBase identifier is obtained then Biolink class is Nucleic Acid Entity and exclude all non-Reactome identifiers.
    # 4. If entrez identifier is obtained and no other identifiers are provided then Biolink class is GENE and exclude all non-Reactome identifiers.
    # 5. If Ensembl  identifier is obtained and no other identifiers are provided then Biolink class is GENE.
    def check_identifiers(self, entity, identifier_dict):
        
        for source in identifier_dict:  # using the deep copy of entity's identifiers
            if source == 'uniprot':
                identifier_dict = self.remove_identifiers(entity, source, identifier_dict)

        # Assigning the proper Biolink Class according the non-Reactome identifier
        for key in classDict:
            if key != 'reactome' and key in identifier_dict:
                    entity.biolink_class = classDict[key]['Class']
                    #entity.id = identifier_dict[key]


    ################################################
    # Take out identifiers that will be inconsistent
    # with the entity's Biolink Class
    def remove_identifiers(self, entity, source, identifier_dict):
        for key in identifier_dict:
            if key != source and key != 'reactome':
                entity.identifiers.pop(key)
        identifier_dict = copy.deepcopy(entity.identifiers)
        return identifier_dict
        


class ReactomeReactionProducer(Producer):    
    variables = ['reactions']
    species_map = None     # JSON mapping of species name to NCBI Taxon ID

    def __init__(self):
        super().__init__(self.variables, definition_file='info/reaction_producer_transformer_info.json')


    ###########################################################################
    # Called by Producer Base Class' produce() method
    # use name from the query graph
    def find_names(self, name):
        ids = set()
        if 'pathway:' in name:
            ids.add(name)
        elif name.lower().startswith('reactome:'):
            ids.add('pathway:'+ self.de_prefix('reactome', name, 'Pathway'))
        else:
            ids=find_reaction_ids(name)
        return ids 


    ###########################################################################
    # Called by Producer Base Class' produce() method, which was invoked by 
    # Transformer.transform(query) method because "function":"producer" is 
    # specified in the openapi.yaml file
    def create_element(self, pathway_stable_id):
        reaction_name = None
        id = None
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)       # set default
        identifiers = {}        # dict of reaction id's various identifiers 
        names_synonyms = None   # dict of reaction id's various names & synonyms 
        reaction = self.Element(id, 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
        self.get_reaction_by_pathway_stable_id(pathway_stable_id, reaction)
        if reaction.id is None:
            return None
        return reaction


    def get_reaction_by_pathway_stable_id(self, pathway_stable_id, reaction):
        query = """ 
            SELECT 
                pathway_stable_identifier,
                reaction_url,
                reaction_name,
                species
            FROM REACTION
            WHERE pathway_stable_identifier = ?
        """
        cur = database_connection.execute(query, (pathway_stable_id,))
        #   for each hit (i.e., of the same reaction name)
        for row in cur.fetchall():
            reaction_url = row['reaction_url']
            species = row['species']
            identifiers = {}        # dict of reaction id's various identifiers 
            names_synonyms = []     
            names_synonyms.append(
                self.Names(
                    name = row['reaction_name'],
                    type = 'primary name')
            )
            prefix = row['pathway_stable_identifier'].split(':')[0]
            identifiers["reactome"] = add_reactome_prefix(self, prefix, row['pathway_stable_identifier'])
            reaction.names_synonyms = names_synonyms
            reaction.identifiers = identifiers
            reaction.attributes.append(self.Attribute(
                name = 'reaction_url',
                value= row['reaction_url'],
                type = 'biolink:url')
            ) 
            reaction.attributes.append(self.Attribute(
                name = 'species',
                value= self.add_prefix('ncbi_taxon', str(species_map[str(row['species'])]), 'OrganismEntity'),
                type = 'biolink:in_taxon')
            ) 
            reaction.id = add_reactome_prefix(self, prefix, row['pathway_stable_identifier'])



class ReactomePathwayProducer(Producer):
    variables = ['pathways']
    species_map = None     # JSON mapping of species name to NCBI Taxon ID

    def __init__(self):
        super().__init__(self.variables, definition_file='info/pathways_producer_transformer_info.json')

    ###########################################################################
    # Called by Producer Base Class' produce() method
    # use name from the query graph
    #
    def find_names(self, name):
        ids = set()
        if 'pathway:' in name:
            ids.add(name)
        else:
            find_pathway_ids(ids, name)
        return ids 


    ###########################################################################
    # Called by Producer Base Class' produce() method, which was invoked by 
    # Transformer.transform(query) method because "function":"producer" is 
    # specified in the openapi.yaml file
    #
    def create_element(self, pathway_stable_id):
        reaction_name = None
        id = None
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)       # set default
        identifiers = {}        # dict of pathway id's various identifiers 
        names_synonyms = None   # dict of pathway id's various names & synonyms 
        pathway = self.Element(id, 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
        self.get_pathway_by_pathway_stable_id(pathway_stable_id, pathway)
        return pathway


    #######################################################################
    # 
    def get_pathway_by_pathway_stable_id(self, pathway_stable_id, pathway):
        query = """ 
            SELECT 
                pathway_stable_identifier,
                pathway,
                species
            FROM PATHWAY
            WHERE pathway_stable_identifier = ?;
        """
        cur = database_connection.execute(query, (pathway_stable_id,))        
        #   for each hit (i.e., of the same pathway name)
        for row in cur.fetchall():
            identifiers = {}        # dict of pathway id's various identifiers 
            names_synonyms = []     
            names_synonyms.append(
                self.Names(
                    name = row['pathway'],
                    type = 'primary name')
            )
            identifiers["reactome"] = add_reactome_prefix(self, 'pathway', row['pathway_stable_identifier'])
            pathway.names_synonyms = names_synonyms
            pathway.identifiers = identifiers
            pathway.attributes.append(self.Attribute(
                name = 'species',
                value= self.add_prefix('ncbi_taxon', str(species_map[str(row['species'])]), 'OrganismEntity'),
                type = 'biolink:in_taxon')
            ) 
            pathway.id = add_reactome_prefix(self, 'pathway', row['pathway_stable_identifier'])


class ReactomeComplexProducer(Producer):
    variables = ['compounds']
    compartments_map = None     # JSON mapping of compartment names to Gene Ontology CURIEs

    def __init__(self):
        super().__init__(self.variables, definition_file='info/complexes_producer_transformer_info.json')
    ###########################################################################
    # Called by Producer Base Class' produce() method
    # use name from the query graph
    #
    def find_names(self, name):
        if name.lower().startswith('reactome:'):
            return ['reactome:'+ self.de_prefix('reactome', name, 'Pathway')]
        return find_complex_ids(name)



    ###########################################################################
    # Called by Producer Base Class' produce() method, which was invoked by 
    # Transformer.transform(query) method because "function":"producer" is 
    # specified in the openapi.yaml file
    def create_element(self, complex_stable_id):
        reaction_name = None
        id = None
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)       # set default
        identifiers = {}        # dict of complex id's various identifiers 
        names_synonyms = None   # dict of complex id's various names & synonyms 
        complex = self.Element(id, 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
        self.get_complex_by_complex_stable_id(complex_stable_id, complex)
        if complex.id is None:
            return None
        return complex


    def get_complex_by_complex_stable_id(self, complex_stable_id, complex):
        query = """ 
        SELECT DISTINCT
            COMPLEX.complex_stable_identifier,
            complex_name,
            compartment,
            pubmed_ids
        FROM COMPLEX
        WHERE COMPLEX.complex_stable_identifier = ?;
        """
        cur = database_connection.execute(query, (complex_stable_id,))        
        #   for each hit (i.e., of the same complex name)
        for row in cur.fetchall():
            identifiers = {}            # dict of complex id's various identifiers 
            names_synonyms = []     
            names_synonyms.append(
                self.Names(
                    name = row['complex_name'],
                    type = 'primary name')
            )    
            identifiers["reactome"] = add_reactome_prefix(self,'reactome', row['complex_stable_identifier'])
            complex.names_synonyms = names_synonyms
            complex.identifiers = identifiers
            complex.attributes.append(self.Attribute(
                name = 'compartment',
                value=  compartments_map.get(row['compartment']),
                description = row['compartment'],
                type = 'biolink:cellular_component')
            )
            if len(str(row['pubmed_ids']).split('-')[0]) > 1:    # check for PMID
                publications = str(row['pubmed_ids']).split('|') 
                complex.attributes.append(self.Attribute(
                    name = 'pubmed_ids',
                    value=  ['PMID:'+ publication for publication in publications],
                    type = 'biolink:publications')
                )
            complex.id = add_reactome_prefix(self, 'reactome', row['complex_stable_identifier'])


class ReactomeInteractionTransformer(Transformer):
    variables = []
    species_map = None     # JSON mapping of species name to NCBI Taxon ID
    aspect_map  = load_apect_mapping()     # JSON mapping of Gene Ontology CURIEs to ancestors (aspects)
    type_map = {
        'psi-mi:"MI:0326"(protein)': 'Protein',
        'psi-mi:"MI:0328"(small molecule)': 'SmallMolecule',
        'psi-mi:"MI:0329"(unknown participant)': None,
        'psi-mi:"MI:0319"(desoxyribonucleic acid)': None,
        'psi-mi:"MI:0320"(ribonucleic acid)': None
    }

    def __init__(self):
        super().__init__(self.variables, definition_file='info/interactions_transformer_info.json')


    def map(self, collection, controls):
        """
            Find interations by an interactor name
        """
        element_list = []        # Transformer's end product: list of elements containing interactors A & B
        interaction_dict = {}    # dictionary of interactor A & B pairs with their interaction info
        for element in collection:
            ids_set = {'reactome:'+ id for id in self.get_identifiers(element, 'reactome', de_prefix=True)}
            ids_set_uniprot = set(self.get_identifiers(element, 'uniprot', de_prefix=False))
            ids_set_chebi = set(self.get_identifiers(element, 'chebi', de_prefix=False))
            ids_set_native = ids_set_uniprot.union(ids_set_chebi)
            if len(ids_set_native) > 0:
                self.get_entity_stable_id(ids_set_native, ids_set) # convert ChEBI IDs to entity_stable_identifier

            query = """
            SELECT DISTINCT
                interaction_id,
                entity_stable_identifier_interactor_A as subject_stable_identifier,
                entity_stable_identifier_interactor_B as object_stable_identifier,
                interactor_id,
                interactor_type,
                interaction_identifier,
                interaction_detection_method,
                publication_first_author,
                publication_identifier,
                interaction_type,
                source_database,
                confidence_value,
                expansion_method,
                biological_role_interactor_A as subject_biological_role,
                biological_role_interactor_B as object_biological_role,
                host_organism
            FROM INTERACTION 
            JOIN INTERACTOR ON INTERACTOR.entity_stable_identifier = object_stable_identifier
            WHERE subject_stable_identifier = ?
            AND entity_stable_identifier_interactor_B IS NOT NULL
            UNION
            SELECT DISTINCT
                interaction_id,
                entity_stable_identifier_interactor_B as subject_stable_identifier,
                entity_stable_identifier_interactor_A as object_stable_identifier,
                interactor_id,
                interactor_type,
                interaction_identifier,
                interaction_detection_method,
                publication_first_author,
                publication_identifier,
                interaction_type,
                source_database,
                confidence_value,
                expansion_method,
                biological_role_interactor_B as subject_biological_role,
                biological_role_interactor_A as object_biological_role,
                host_organism
            FROM INTERACTION 
            JOIN INTERACTOR ON INTERACTOR.entity_stable_identifier = object_stable_identifier
            WHERE subject_stable_identifier = ?
            """
            for subject_stable_identifier in ids_set:  # for each interactor A get interactor_B & the interactions between them
                cur=database_connection.execute(query,(subject_stable_identifier,subject_stable_identifier,))
                for row in cur.fetchall():
                    object_native_identifier = row['interactor_id']
                    object_interactor_type = row['interactor_type']
                    interactor_tuple = (subject_stable_identifier, object_native_identifier, object_interactor_type)
                    if not interactor_tuple in interaction_dict:
                        interaction_list = []
                        interaction_dict[interactor_tuple] = interaction_list
                    interaction = Interaction(
                                        interaction_id = row['interaction_id'],
                                        interaction_detection_method =row['interaction_detection_method'], 
                                        publication_first_author =row['publication_first_author'], 
                                        publication_identifier =row['publication_identifier'], 
                                        interaction_type =row['interaction_type'], 
                                        source_database =row['source_database'], 
                                        interaction_identifier =row['interaction_identifier'], 
                                        confidence_value =row['confidence_value'], 
                                        expansion_method =row['expansion_method'], 
                                        subject_biological_role = row['subject_biological_role'], 
                                        object_biological_role = row['object_biological_role'],
                                        object_stable_identifier = row["object_stable_identifier"],
                                        host_organism = row['host_organism'])
                    interaction_dict[interactor_tuple].append(interaction)

            #Take interaction_dict to create elements and a connection for each interaction
            for tuple_key in interaction_dict:
                self.add_element(tuple_key, element_list, interaction_dict[tuple_key], element.id)
        return element_list


    def get_entity_stable_id(self, ids_set_native, ids_set):
        query = """
            SELECT entity_stable_identifier
            FROM INTERACTOR
            WHERE interactor_id = ? collate nocase
        """
        for interactor_id in ids_set_native:
            cur=database_connection.execute(query,(interactor_id.lower(),))
            for row in cur.fetchall():
                ids_set.add(row['entity_stable_identifier'])

    # Create elements for interactor interactor_A-interactor_B pairs and add them to a list
    def add_element(self, tuple_key, element_list, interactions_list, source_element_id):
        biolink_class = self.type_map.get(tuple_key[2])
        if biolink_class is None:
            return

        # Set up identifiers
        identifiers = {}        # dict of interaction id's various identifiers 
        object_entity_identifier = tuple_key[1]
        if object_entity_identifier.lower().startswith('chebi:'):
            object_entity_identifier = self.de_prefix('chebi', object_entity_identifier, biolink_class)
            object_entity_identifier = self.add_prefix('chebi', object_entity_identifier, biolink_class)
            identifiers['chebi'] = object_entity_identifier
        elif object_entity_identifier.lower().startswith('uniprotkb:'):
            object_entity_identifier = self.de_prefix('uniprot', object_entity_identifier, biolink_class)
            object_entity_identifier = self.add_prefix('uniprot', object_entity_identifier, biolink_class)
            identifiers['uniprot'] = object_entity_identifier
        indentifier_set = set()
        for interaction in interactions_list:
            indentifier_set.add(add_reactome_prefix(self, 'reactome', interaction.object_stable_identifier))
        if len(indentifier_set) > 0:
            identifiers['reactome'] = list(indentifier_set)

        interactor_element = Element(
                                id = object_entity_identifier,
                                biolink_class = biolink_class,
                                identifiers = identifiers,
                                names_synonyms = [],
                                attributes= [],
                                connections=[],
                                source=self.info.name
                            )
        element_list.append(interactor_element)
        self.add_connections (interactor_element, interactions_list, source_element_id)

    # Function to gather connections from interactions list (1 interaction == 1 connection) 
    def add_connections (self, interactor_element, interactions_list, source_element_id):
        for interaction in interactions_list:
            connection= self.Connection(
                source_element_id= source_element_id,
                predicate = self.info.knowledge_map.edges[0].predicate,
                inv_predicate = self.info.knowledge_map.edges[0].inverse_predicate, 
                attributes= []
            )
            self.get_connections_attributes(interaction,connection)
            interactor_element.connections.append(connection)


    def get_connections_attributes(self, interaction, connection):
        confidence_value_description = ''
        interaction_type = None
        self.get_interaction_term_attributes(interaction, connection)
        primary_knowledge_source = self.Attribute(
                name= 'biolink:primary_knowledge_source',
                value= 'infores:reactome',
                value_type= 'biolink:InformationResource',
                type= 'biolink:primary_knowledge_source',
                url = 'https://reactome.org/content/query?q=' + interaction.interaction_identifier
            )
        primary_knowledge_source.attribute_source = 'infores:molepro'
        connection.attributes.append(primary_knowledge_source)
        connection.attributes.append(self.Attribute(
                        name = 'biolink:knowledge_level',
                        value = self.KNOWLEDGE_LEVEL,
                        type = 'biolink:knowledge_level',
                        value_type = 'String')
                        )
        connection.attributes.append(self.Attribute(
                        name = 'biolink:agent_type',
                        value = self.AGENT_TYPE,
                        type = 'biolink:agent_type',
                        value_type = 'String')
                        )

        if type(interaction.publication_identifier) is list:
            for first_author, pmid in zip(interaction.publication_first_author, interaction.publication_identifier):
                connection.attributes.append(self.Attribute(
                    name = 'Publication',
                    value= pmid,
                    type = 'biolink:Publication',
                    description = first_author)
                )
        else:
            connection.attributes.append(self.Attribute(
                name = 'Publication',
                value= interaction.publication_identifier,
                type = 'biolink:Publication',
                description = interaction.publication_first_author)
            )

        if len(interaction.interaction_detection_method) > 1:
            start = interaction.interaction_detection_method.index('MI')
            end   = interaction.interaction_detection_method.index('\"(', start) - len(interaction.interaction_detection_method)
            res = interaction.interaction_detection_method[start:end]
            connection.attributes.append(self.Attribute(
                            name = 'interaction_detection_method',
                            description= interaction.interaction_detection_method.split('(')[1].replace(')',''),
                            type = 'interaction_detection_method',
                            value = res)
                        )
        if len(interaction.expansion_method) > 1:  
            start = interaction.expansion_method.index('MI')
            end   = interaction.expansion_method.index('\"(', start) - len(interaction.expansion_method)
            res = interaction.expansion_method[start:end]        
            connection.attributes.append(self.Attribute(
                            name = 'expansion_method',
                            description= interaction.expansion_method.split('(')[1].replace(')',''),
                            type = 'expansion_method',
                            value= res)
                        )
        if len(interaction.confidence_value.split(':')[1].split('(')) > 1:
            confidence_value_description = ' (' + interaction.confidence_value.split(':')[1].split('(')[1]
        connection.attributes.append(self.Attribute(
                        name = 'confidence_value',
                        value= interaction.confidence_value.split(':')[1].split('(')[0],
                        type = 'confidence_value',
                        description = interaction.confidence_value.split(':')[0] + confidence_value_description)
                        )
        prefix = interaction.interaction_identifier.split(':')[0]
        connection.attributes.append(self.Attribute(
                        name = 'interaction_identifier',
                        value= add_reactome_prefix(self, prefix, interaction.interaction_identifier),
                        type = 'interaction_identifier',
                        description = 'interaction product or pathway')
                        )
        connection.attributes.append(self.Attribute(
                        name = 'interaction_type',
                        value= interaction.interaction_type.split('(')[1].replace(')','').replace(' ','_'),
                        type = 'interaction_type',
                        description = 'reaction or association')
                        )

        subject_biological_role = ''
        object_biological_role = ''
        if 'enzyme' in interaction.subject_biological_role.split('(')[1].replace(')','').replace(' ','_'):
            subject_biological_role =  interaction.subject_biological_role.split('(')[1].replace(')','').replace(' ','_')
            if 'target' in subject_biological_role:
                subject_biological_role = subject_biological_role.split('_')[1]
            connection.qualifiers.append(self.Qualifier(
                                            qualifier_type_id= 'subject_role_qualifier',
                                            qualifier_value  = subject_biological_role))
        if 'enzyme' in interaction.object_biological_role.split('(')[1].replace(')','').replace(' ','_'):
            object_biological_role =  interaction.object_biological_role.split('(')[1].replace(')','').replace(' ','_')
            if 'target' in object_biological_role:
                object_biological_role = object_biological_role.split('_')[1]
            connection.qualifiers.append(self.Qualifier(
                                            qualifier_type_id= 'object_role_qualifier',
                                            qualifier_value  = object_biological_role))
        connection.qualifiers.append(self.Qualifier(
                                qualifier_type_id= 'species_context_qualifier',
                                qualifier_value  = 'NCBITaxon:' + interaction.host_organism.split('(')[0].split(':')[1]))

    ###########################################################
    # Create attribute & qualifier for compartment
    def get_interaction_term_attributes(self, interaction, connection):
            query = """
                    SELECT DISTINCT
                        interaction_id,
                        interaction_xref_source as go_source,
                        interaction_xref_id as go_id,
                        interaction_term  
                    FROM INTERACTION_MAP
                    WHERE interaction_id = ?
            """        
            cur = database_connection.execute(query, (interaction.interaction_id,))
            #   for each hit (i.e., of the same complex name)
            for row in cur.fetchall():
                if row['go_source'] == 'go':
                    description = None
                    if row['interaction_term'] is not None:
                        description = row['interaction_term']
                    #lookup correct biolink type in self.aspect_map
                    connection.attributes.append(self.Attribute(
                                    name = 'interaction_xref_id',
                                    value= row['go_id'],
                                    type = 'biolink:' + self.aspect_map[row['go_id']]['aspect'],
                                    description = description)
                                    )
                    if self.aspect_map[row['go_id']]['aspect'] == 'cellular_component': #i.e., get compartments only
                        connection.qualifiers.append(self.Qualifier(
                                    qualifier_type_id= 'anatomical_context_qualifier',
                                    qualifier_value  = row['go_id'])
                    )                

#####################################################################
# 
class ReactomeReactionTransformer(Transformer):

    variables = []
    species_map = load_species_mapping ()     # JSON mapping of species name to NCBI Taxon ID

    def __init__(self):
        super().__init__(self.variables, definition_file='info/reactions_transformer_info.json')


    def map(self, collection, controls):
        """
            Find reaction by interactor names
        """
        reaction_list = []
        for element in collection:
            ids_set = set(self.get_identifiers(element, 'reactome', de_prefix=False))
            query = """
                    SELECT DISTINCT    
                        entity_stable_identifier,
                        REACTION_MAP.pathway_stable_identifier,
                        evidence_code,
                        reaction_url,
                        reaction_name,
                        species 
                    FROM REACTION_MAP
                    JOIN REACTION ON REACTION_MAP.pathway_stable_identifier = REACTION.pathway_stable_identifier
                    WHERE entity_stable_identifier = ?
            """
            for interactor in ids_set:  # for each interactor get the reactions it is involved in.
                if interactor.startswith('Reactome:'):
                    interactor = 'reactome:' + self.de_prefix('reactome', interactor, 'Pathway')
                cur = database_connection.execute(query,(interactor,))
                for row in cur.fetchall():
                    self.add_element(reaction_list, row, element.id)
        return reaction_list

    # Creates element for a reaction and add it to a list
    def add_element(self,reaction_list, row, source_element_id):
        # Set up identifiers
        identifiers = {}
        prefix = row['pathway_stable_identifier'].split(':')[0]
        identifier = add_reactome_prefix(self, prefix, row['pathway_stable_identifier'])
        identifiers['reactome']=  identifier  # make the reaction as the identifier
        pathway_element = Element(
                                id = identifier,
                                biolink_class='MolecularActivity',
                                identifiers = identifiers,
                                names_synonyms = [],
                                attributes= [],
                                connections=[],
                                source=self.info.name
                            )
        pathway_element.names_synonyms.append(
                                        self.Names(
                                            name = row['reaction_name'],
                                            type = 'primary name')) 
        self.add_connections (pathway_element, row, source_element_id)
        reaction_list.append(pathway_element)


    # Function to get connections 
    def add_connections (self, reaction_element, row, source_element_id):
            predicate_list = self.get_connection_predicate(row['entity_stable_identifier'], row['pathway_stable_identifier'])
            if len(predicate_list) > 0:
                for (predicate, inv_predicate) in predicate_list:
                    connection= self.Connection(
                        source_element_id= source_element_id,
                        predicate = predicate,
                        inv_predicate = inv_predicate, 
                        attributes= []
                    )
                    self.get_pubmeds(reaction_element, connection)
                    self.get_connections_attributes(row,connection)
                    reaction_element.connections.append(connection)                  
            else:
                connection= self.Connection(
                    source_element_id= source_element_id,
                    predicate = 'biolink:participates_in',
                    inv_predicate = 'biolink:has_participant', 
                    attributes= []
                )
                self.get_pubmeds(reaction_element, connection)
                self.get_connections_attributes(row,connection)
                reaction_element.connections.append(connection)


    def get_connection_predicate(self, entity_stable_identifier, pathway_stable_identifier):
            query = """
                SELECT DISTINCT 
                    entity_stable_identifier,
                    SUBSTR(interactor_id, (INSTR(interactor_id, ':')+1), 
                    (LENGTH(interactor_id)-INSTR(interactor_id, ':'))) as protein,
                    role,
                    pathway_stable_identifier
                FROM INTERACTOR
                JOIN PROTEIN_ROLE_REACTIONS ON protein = uniprot_id
                WHERE interactor_id LIKE ("uniprotkb:%")
                AND entity_stable_identifier = ?
                AND pathway_stable_identifier = ?;
            """
            predicate_role_dict = {
                'input': ('biolink:is_input_of', 'biolink:has_input'),
                'output': ('biolink:is_output_of', 'biolink:has_output'),
                'catalystActivity': ('biolink:catalyzes', 'biolink:has_catalyst'),
                'regulatedBy': ('biolink:regulated_by','biolink:regulates'),
                'entityFunctionalStatus': ('biolink:participates_in', 'biolink:has_participant')
            }
            predicate_set = set()
            cur = database_connection.execute(query,(entity_stable_identifier, pathway_stable_identifier,))
            for row in cur.fetchall():
                predicate_set.add( predicate_role_dict[row['role']])
            return list(predicate_set)      


    def get_connections_attributes(self,row,connection):
        primary_knowledge_source = self.Attribute(
                name= 'biolink:primary_knowledge_source',
                value= 'infores:reactome',
                value_type= 'biolink:InformationResource',
                type= 'biolink:primary_knowledge_source',
                url = row['reaction_url']
            )
        primary_knowledge_source.attribute_source = 'infores:molepro'
        connection.attributes.append(primary_knowledge_source)
        connection.attributes.append(self.Attribute(
                        name = 'biolink:knowledge_level',
                        value = self.KNOWLEDGE_LEVEL,
                        type = 'biolink:knowledge_level',
                        value_type = 'String')
                        )
        connection.attributes.append(self.Attribute(
                        name = 'biolink:agent_type',
                        value = self.AGENT_TYPE,
                        type = 'biolink:agent_type',
                        value_type = 'String')
                        )
        connection.qualifiers.append(self.Qualifier(
                        qualifier_type_id= 'species_context_qualifier',
                        qualifier_value  = 'NCBITaxon:' + str(species_map[str(row['species'])]))
        )


    def get_pubmeds(self, pathway_element, connection):
        query = """
            SELECT 
                pathway_stable_identifier,
                PubMed_citation_identifier
            FROM PUBMED
            WHERE pathway_stable_identifier = ?
        """
        cur= database_connection.execute(query,(pathway_element.identifiers['reactome'],))
        pubmed_list = []
        for row in cur.fetchall():
            pubmed_list.append(row['PubMed_citation_identifier'])
        if len(pubmed_list) > 0:
            connection.attributes.append(self.Attribute(
                name = 'PubMed_citation_identifier',
                value=  pubmed_list,
                type = 'biolink:publications'
                )
            )
    
#####################################################################
# 
class ReactomeComplexTransformer(Transformer):
    variables = []
    compartments_map = None     # JSON mapping of compartment names to Gene Ontology CURIEs

    def __init__(self):
        super().__init__(self.variables, definition_file='info/complexes_transformer_info.json')


    def map(self, collection, controls):
        """
            Find complex by complex participant
        """
        complex_list = []
        for element in collection:
            ids_set = set(self.get_identifiers(element, 'uniprot', de_prefix=False))
            if len(ids_set) == 0:
                ids_set = set(self.get_identifiers(element, 'chebi', de_prefix=False))
            if len(ids_set) == 0:
                ids_set = set(self.get_identifiers(element, 'gtopdb', de_prefix=False))
            if len(ids_set) == 0:
                ids_set = set(self.get_identifiers(element, 'pubchem', de_prefix=False))
            if len(ids_set) == 0:
                ids_set = set(self.get_identifiers(element, 'ensembl', de_prefix=False))
            if len(ids_set) == 0:
                ids_set = set(self.get_identifiers(element, 'mirbase', de_prefix=False))
            if len(ids_set) == 0:
                ids_set = {'reactome:'+ id for id in self.get_identifiers(element, 'reactome', de_prefix=True)}
            
            query = """
            SELECT 
                COMPLEX_PARTICIPANT.complex_stable_identifier,
                complex_participant_identifier,
                complex_name,
                compartment,
                pubmed_ids               
            FROM COMPLEX_PARTICIPANT
            JOIN COMPLEX ON COMPLEX_PARTICIPANT.complex_stable_identifier = COMPLEX.complex_stable_identifier
            WHERE COMPLEX_PARTICIPANT.complex_participant_identifier =  ?
            """
            for complex_participant in ids_set:  # for each participant get the complex it is involved in.
                cur = database_connection.execute(query,(complex_participant,))
                for row in cur.fetchall():
                    self.add_element(complex_list, row, element.id)
        return complex_list

    # Creates element for a complex and add it to a list
    def add_element(self,complex_list, row, source_element_id):
        # Set up identifiers
        identifiers = {}                # dict of complex id's various identifiers 
        identifier = add_reactome_prefix(self, 'reactome', row['complex_stable_identifier'])
        identifiers['reactome'] = identifier # make the complex name as an identifier
        complex_element = Element(
                                id = identifier,
                                biolink_class= self.info.knowledge_map.output_class,
                                identifiers = identifiers,
                                names_synonyms = [],
                                attributes= [],
                                connections=[],
                                source=self.info.name
                            )
        complex_element.names_synonyms.append(
                                        self.Names(
                                            name = row['complex_name'],
                                            type = 'primary name')) 
        self.add_connections (complex_element, row, source_element_id)
        complex_list.append(complex_element)

    # Function to gather connections  
    def add_connections (self, interactor_element, row, source_element_id):
        pubmed_list = []
        connection= self.Connection(
            source_element_id= source_element_id,
            predicate = self.info.knowledge_map.edges[0].predicate,
            inv_predicate = self.info.knowledge_map.edges[0].inverse_predicate, 
            attributes= []
        )
        if len(str(row['pubmed_ids'])) > 1:
            publications = str(row['pubmed_ids']).split('|')
            for publication in publications:
                pubmed_list.append('PMID:'+ publication)
            if len(pubmed_list) > 0:
                connection.attributes.append(self.Attribute(
                    name = 'pubmed_ids',
                    value=  pubmed_list,
                    type = 'biolink:publications')
                )
        primary_knowledge_source = self.Attribute(
                name= 'biolink:primary_knowledge_source',
                value= 'infores:reactome',
                value_type= 'biolink:InformationResource',
                type= 'biolink:primary_knowledge_source'
            )
        primary_knowledge_source.attribute_source = 'infores:molepro'
        connection.attributes.append(primary_knowledge_source)
        connection.attributes.append(self.Attribute(
                        name = 'biolink:knowledge_level',
                        value = self.KNOWLEDGE_LEVEL,
                        type = 'biolink:knowledge_level',
                        value_type = 'String')
                        )
        connection.attributes.append(self.Attribute(
                        name = 'biolink:agent_type',
                        value = self.AGENT_TYPE,
                        type = 'biolink:agent_type',
                        value_type = 'String')
                        )
        connection.attributes.append(self.Attribute(
            name = 'compartment',
            value=  compartments_map.get(row['compartment']) if compartments_map.get(row['compartment']) is not None else row['compartment'],
            description = row['compartment'],
            type = 'biolink:cellular_component')
        )       
        connection.qualifiers.append(self.Qualifier(
                        qualifier_type_id= 'anatomical_context_qualifier',
                        qualifier_value  = compartments_map.get(row['compartment']) if compartments_map.get(row['compartment']) is not None else row['compartment'])
        ) 
        interactor_element.connections.append(connection)


#####################################################################
# 
class ReactomePathwayTransformer(Transformer):
    variables = []
    species_map = None     # JSON mapping of species name to NCBI Taxon ID

    def __init__(self):
        super().__init__(self.variables, definition_file='info/pathways_transformer_info.json')


    def map(self, collection, controls):
        """
            Find pathway by complex participant or physical entity
        """ 
        pathway_list = []
        for element in collection:
            ids_set = set(self.get_identifiers(element, 'reactome', de_prefix=False))
            query = """
                SELECT 
                    COMPLEX_PATHWAY_MAP.complex_stable_identifier,
                    COMPLEX_PATHWAY_MAP.pathway_stable_identifier,
                    top_level_pathway,
                    taxon_id,
                    pathway,
                    parent_pathway,
                    child_pathway
                FROM COMPLEX_PATHWAY_MAP
                JOIN PATHWAY ON COMPLEX_PATHWAY_MAP.pathway_stable_identifier = PATHWAY.pathway_stable_identifier
                JOIN PATHWAY_MAP ON COMPLEX_PATHWAY_MAP.pathway_stable_identifier = PATHWAY_MAP.child_pathway
                WHERE COMPLEX_PATHWAY_MAP.complex_stable_identifier =  ?
            """
            for complex_participant in ids_set:  # for each participant get the complex it is involved in.
                cur = database_connection.execute(query,(complex_participant,))
                for row in cur.fetchall():
                    self.add_element(pathway_list, row, element.id)
        return pathway_list

    # Creates element for a pathway and add it to a list
    def add_element(self, pathway_list, row, source_element_id):
        # Set up identifiers
        identifiers = {}    # dict of pathway id's various identifiers
        prefix = row['pathway_stable_identifier'].split(':')[0]
        identifier = add_reactome_prefix(self, prefix, row['pathway_stable_identifier'])
        identifiers['reactome']= identifier # make the complex name as an identifier
        pathway_element = Element(
                                id = identifier,
                                biolink_class= self.info.knowledge_map.output_class,
                                identifiers = identifiers,
                                names_synonyms = [],
                                attributes= [],
                                connections=[],
                                source=self.info.name
                            )
        pathway_element.names_synonyms.append(
                                        self.Names(
                                            name = row['pathway'],
                                            type = 'primary name')) 
        self.add_connections (pathway_element, row, source_element_id)
        pathway_list.append(pathway_element)


    # Function to gather connections  
    def add_connections (self, pathway_element, row, source_element_id):
        connection= self.Connection(
            source_element_id= source_element_id,
            predicate = self.info.knowledge_map.edges[0].predicate,
            inv_predicate = self.info.knowledge_map.edges[0].inverse_predicate, 
            attributes= []
        )     
        self.get_connections_attributes(row,connection)
        pathway_element.connections.append(connection)


    def get_connections_attributes(self,row,connection):
        primary_knowledge_source = self.Attribute(
                name= 'biolink:primary_knowledge_source',
                value= 'infores:reactome',
                value_type= 'biolink:InformationResource',
                type= 'biolink:primary_knowledge_source',
                url = 'https://reactome.org/content/query?q='+ row['pathway_stable_identifier'].split(':')[1] + '&types=Pathway'
            )
        primary_knowledge_source.attribute_source = 'infores:molepro'
        connection.attributes.append(primary_knowledge_source)
        connection.attributes.append(self.Attribute(
                        name = 'biolink:knowledge_level',
                        value = self.KNOWLEDGE_LEVEL,
                        type = 'biolink:knowledge_level',
                        value_type = 'String')
                        )
        connection.attributes.append(self.Attribute(
                        name = 'biolink:agent_type',
                        value = self.AGENT_TYPE,
                        type = 'biolink:agent_type',
                        value_type = 'String')
                        )
        connection.qualifiers.append(self.Qualifier(
                        qualifier_type_id= 'species_context_qualifier',
                        qualifier_value  = 'NCBITaxon:' + row['taxon_id'])
        )


class Interaction():
    interaction_id = None
    interaction_detection_method = None
    publication_first_author = None
    publication_identifier = None
    interaction_type = None
    source_database = None
    interaction_identifier = None
    confidence_value = None
    expansion_method = None
    subject_biological_role = None
    object_biological_role = None
    object_stable_identifier = None
    host_organism = None
    def __init__(self, interaction_id, interaction_detection_method, publication_first_author, publication_identifier=None, interaction_type=None, source_database=None, interaction_identifier=None, confidence_value=None, expansion_method=None, subject_biological_role=None, object_biological_role=None, object_stable_identifier = None, host_organism=None): 
        self.interaction_id = interaction_id
        self.interaction_detection_method = interaction_detection_method

        if publication_first_author is not None and '|' in publication_first_author:
            pub_first_author_list = publication_first_author.split('|')
            self.publication_first_author = pub_first_author_list
        else:
            self.publication_first_author = publication_first_author

        publication_list = publication_identifier.split('|')
        pub_list = []
        for pub in publication_list:
            if 'pubmed' in pub:
                if len(pub.split(':')[1]) > 1:
                    pub = 'PMID:' + pub.split(':')[1]
                else:
                    pub = ''
                pub_list.append(pub)
        self.publication_identifier = pub_list
        if len(pub_list) == 1:     # just save  the PMID string if just one pub
             self.publication_identifier = pub_list[0]
    
        self.interaction_type = interaction_type
        self.source_database = source_database
        self.interaction_identifier = interaction_identifier
        self.confidence_value = confidence_value
        self.expansion_method = expansion_method
        self.subject_biological_role = subject_biological_role
        self.object_biological_role = object_biological_role
        self.object_stable_identifier = object_stable_identifier
        self.host_organism = host_organism


########################################### Common Functions #######################################################################################

###########################################################################
# Called by ReactomeEntityProducer.find_names() method to determine the
# entity_stable_identifier corresponding to the entity_name or entity_native_identifier submitted
# in the query graph. 
# uniprot	UniProtKB:A0A0B4KH68
# entrez	NCBIGene:43223
# chebi     CHEBI:57865
# miRBase   miRBase:MI0000449
# gtopdb    GTOPDB:8967
# ensembl   ENSEMBL:ENSG00000170920
def find_substance_ids(self, query_identifier):
    search_column = None
    id_list = list()
    if ':' not in query_identifier:
        search_column = 'entity_name'    # by default, assume a search for entity by name
#   check if submitted name is native CURIE, e.g., NCBIGENE:2244
#   or else just a substance name, e.g., aspirin    
    elif query_identifier.upper().startswith('UNIPROTKB:') or query_identifier.upper().startswith('NCBIGENE:') or \
        query_identifier.upper().startswith('CHEBI:') or query_identifier.upper().startswith('MIRBASE:') or \
        query_identifier.upper().startswith('GTOPDB:') or query_identifier.upper().startswith('ENSEMBL:') or \
        query_identifier.upper().startswith('CID:') or query_identifier.upper().startswith('SID:') or \
        query_identifier.upper().startswith('REACT:') or query_identifier.upper().startswith('EMBL:'):  # a search 
        search_column = 'entity_native_identifier'
    """
        Find entity_stable_identifier, if it exists
    """
    query = """
        SELECT DISTINCT 
            entity_stable_identifier
        FROM PHYSICAL_ENTITY
        WHERE {} = ?
    """.format(search_column)
    if search_column is not None:
        cur = database_connection.execute(query, (query_identifier,))
    #   for each hit (i.e., of the same substance name, an unlikely but possible occurrence)
        for row in cur.fetchall():
            id_list.append(query_identifier)
    else:
        if query_identifier.upper().startswith('reactome:'):
            id_list.append(query_identifier)
    return id_list


###########################################################################
# Called by find_names() method to determine type of name submitted
# in the query graph. 
def find_reaction_ids(name_value):
    query = """ 
        SELECT 
            pathway_stable_identifier,
            reaction_url,
            reaction_name,
            species
        FROM REACTION
        WHERE reaction_name = ?
    """
    cur = database_connection.execute(query, (name_value,))
    #   for each hit (i.e., of the same reaction name)
    id_set = set()
    for row in cur.fetchall():
        id_set.add(row['pathway_stable_identifier'])
    return id_set


###########################################################################
# Called by find_names() method to determine type of name submitted
# in the query graph. 
def find_pathway_ids(id_set, name_value):
    query = """ 
        SELECT 
            pathway_stable_identifier
        FROM PATHWAY
        WHERE pathway = ?;
    """

    cur = database_connection.execute(query, (name_value,))
    #   for each hit (i.e., of the same reaction name)
    for row in cur.fetchall():
        id_set.add(row['pathway_stable_identifier'])


###########################################################################
# Called by find_names() method to determine type of name submitted
# in the query graph. 
def find_complex_ids(name_value):
    query = """ 
        SELECT 
            COMPLEX.complex_stable_identifier,
            complex_name,
            compartment,
            pubmed_ids,
            taxon_id
        FROM COMPLEX
        JOIN COMPLEX_PATHWAY_MAP ON COMPLEX.complex_stable_identifier = COMPLEX_PATHWAY_MAP.complex_stable_identifier
        WHERE COMPLEX.complex_name = ?;
        """
    cur = database_connection.execute(query, (name_value,))
    #   for each hit (i.e., of the same reaction name)
    id_set = set()
    for row in cur.fetchall():
        id_set.add(row['complex_stable_identifier'])
    return id_set





#######################################################################################################
# It is necessary to change the prefix of the reactome identifiers from the Reactome database to be
# the acceptable Biolink prefix (based on content of prefixMap.json).
def add_reactome_prefix(self, prefix, identifier, biolink_class = 'Pathway'):
    if identifier.startswith(prefix):
        identifier = identifier[len(prefix)+1:]
    return self.add_prefix('reactome', identifier, biolink_class)
