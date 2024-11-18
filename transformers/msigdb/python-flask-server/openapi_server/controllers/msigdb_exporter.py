from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from transformers.transformer import Transformer, Producer
import sqlite3
import json

###########################################################################################################################
# The Molecular Signatures Database (MSigDB) is a resource of tens of thousands of annotated gene sets for use with GSEA 
# software, divided into Human and Mouse collections. From this web site, you can. Examine a gene set and its annotations. 
# See, for example, the HALLMARK_APOPTOSIS human gene set page.
# ... provides Molecular Signatures Database (MSigDB) gene sets typically used with the 
# Gene Set Enrichment Analysis (GSEA) software

SOURCE = 'MSigDB'
database_connection = sqlite3.connect('data/MSigDB.sqlite', check_same_thread=False)
database_connection.row_factory = sqlite3.Row

class MSigDBPathwayProducer(Producer): # create pathway producer

    variables = ['pathway']
    species_map = None

    def __init__(self):
        super().__init__(self.variables,definition_file='info/pathways_producer_transformer_info.json')
        get_species_mapping(self)

    ############################################################################################
    # Called to determine the gene_set_id corresponding to the GO identifier or Reactome identifier
    # in the query graph. 
    # go	GO:0000003
    # Note that in all cases of tables with an id primary key column, these primary key values 
    # are generated synthetically and will not be considered stable across different versions 
    # of MSigDB (and likewise when used as a foreign key). In other words, the id of a particular 
    # gene set, gene symbol, author, etc. will likely have a different value in the next version 
    # of MSigDB. While usable within a given database for JOIN queries and so on, these values 
    # should not be relied upon outside of that context.
    def find_names(self, query_identifier):
        search_column = None
        id_list = list()
        if query_identifier.upper().startswith('GO:') or query_identifier.lower().startswith('reactome:'):  # a search 
            search_column = 'exact_source'
            if query_identifier.lower().startswith('reactome:'):
                query_identifier = self.de_prefix('reactome', query_identifier,'Pathway')
        elif query_identifier.lower().startswith('msigdb:'):
            query_identifier = self.de_prefix('msigdb', query_identifier,'Pathway')
            search_column = 'primary_name'    # by default, assume a search for gene_set_id by standard_name / primary_name  
        """
            Find gene_set_id, if it exists
        """
        query = """
        SELECT gene_set_details.gene_set_id, exact_source, standard_name primary_name,
                    ( SELECT MSigDB_base_URL FROM MSigDB WHERE version_name = '2024.1.Hs' )
                        ||'/geneset/'||standard_name URL,
                publication_id,
                contributor,
                contrib_organization contributor_organization,
                title,
                PMID,
                DOI,
                publication.URL pub_URL
                FROM gene_set gset
                JOIN gene_set_details on gset.id = gene_set_details.gene_set_id
                LEFT JOIN publication on publication_id = publication.id
                WHERE {} = ?
        """.format(search_column)
        if search_column is not None:    
            cur = database_connection.execute(query, (query_identifier,))
        #   for each hit (i.e., of the same substance name, an unlikely but possible occurrence)
            for row in cur.fetchall():
                id_list.append(row['primary_name'])
        return id_list

    ###########################################################################
    # Called by Producer Base Class' produce() method, which was invoked by 
    # Transformer.transform(query) method because "function":"producer" is 
    # specified in the openapi.yaml file
    def create_element(self, element_id):
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)  # set a default class
        identifiers = {}        # dict of entity id's various identifiers 
        names_synonyms = None   # dict of entity id's various names & synonyms 
        element = self.Element(self.add_prefix('msigdb', element_id, 'Pathway'), 
                                 biolink_class, 
                                 identifiers, 
                                 names_synonyms)
        self.get_entity_by_id(element_id, element)
        return element


    ##############################################################
    # Called by Producer.create_element()
    # Get element by element_id (unique identifier MSigDB standard_name/primary_name)
    # e.g., AAGCCAT_MIR135A_MIR135B
    def get_entity_by_id(self, element_id, element):
        names_synonyms = []   
        query = """
        SELECT gene_set_details.gene_set_id,
                exact_source, 
                standard_name primary_name,
                ( SELECT MSigDB_base_URL FROM MSigDB WHERE version_name = '2024.1.Hs' )
                    ||'/geneset/'||standard_name 
                URL,
                license_code,
                description_brief,
                description_full,
                species_name,
                SUBSTR(collection_name,1,2) category_code,
                CASE WHEN INSTR(collection_name, ":") > 0 THEN SUBSTR(collection_name, INSTR(collection_name, ":")+1) ELSE Null END AS subcategory_code,
                contributor,
                contrib_organization contributor_organization
        FROM gene_set gset
        INNER JOIN gene_set_gene_symbol gsgs on gset.id = gsgs.gene_set_id
        INNER JOIN gene_symbol gsym on gsym.id = gene_symbol_id
        JOIN gene_set_details on gsgs.gene_set_id = gene_set_details.gene_set_id
        JOIN species on source_species_code = species.species_code
        WHERE primary_name = ?
        GROUP BY standard_name
        ORDER BY standard_name ASC
                """
        cur = database_connection.execute(query,(element_id,))
        for row in cur.fetchall():
            primary_name = self.add_prefix('msigdb', row['primary_name'], 'Pathway')
            element.identifiers = {'msigdb':primary_name}
            element.names_synonyms = names_synonyms
            names_synonyms.append(
                    self.Names(
                        name = row['primary_name'],
                        type = 'primary name')
            ) 
            element.attributes.append(self.Attribute(
                name = 'URL',
                value= row['URL'],
                type = 'biolink:url')
            )
            element.attributes.append(self.Attribute(
                name = 'license_code',
                value=  row['license_code'],
                type = 'biolink:license')
            )
            element.attributes.append(self.Attribute(
                name = 'species_name',
                value = self.add_prefix('ncbi_taxon', str(self.species_map[row['species_name']]), 'OrganismEntity'),
                type = 'biolink:in_taxon'))  

            if row['description_full'] is not None:
                element.attributes.append(self.Attribute(
                                name = 'description_full',
                                value = row['description_full'],
                                type = 'biolink:description'))
                element.attributes.append(self.Attribute('description_brief', row['description_brief']))    
            elif row['description_brief'] is not None:              
                element.attributes.append(self.Attribute(
                                name = 'description_brief',
                                value = row['description_brief'],
                                type = 'biolink:description'))   

            attribute_fields = ['category_code','subcategory_code','contributor','contributor_organization']
            for attr in attribute_fields:
                if row[attr] is not None:
                    attribute = self.Attribute(attr, row[attr])
                    element.attributes.append(attribute)

            identifier = row['exact_source']
            if identifier is not None:
                if row['exact_source'].startswith('R-'):
                    identifier = self.add_prefix('reactome',row['exact_source'], 'Pathway')
                    element.identifiers['reactome'] = identifier
                elif row['exact_source'].startswith('GO:'):
                    element.identifiers['go'] = identifier
                element.attributes.append(self.Attribute(
                    name = 'exact_source',
                    value=  identifier,
                    type = 'exact_source'
                    )
                )


###########################################
# gene to pathway transformer
class MSigDBPathwayTransformer(Transformer):
    variables = []
    species_map = None

    def __init__(self):
        super().__init__(self.variables,definition_file='info/pathways_transformer_info.json')

    # Dictionary for determining field name in the identifiers
    # Related to gene_set.collection_name, e.g., C2:CP:BIOCARTA
    sub_categories = {
        'CP:KEGG': 'kegg',
        'CP:WIKIPATHWAYS':'wikipathways',
        'HPO': 'hpo',
        'GO:BP':'go',
        'GO:CC':'go',
        'GO:MF':'go',
        'CP:REACTOME': 'reactome',
        'CP:BIOCARTA': 'biocarta'
    }

    predicate_map = {
        'CP:KEGG': ('biolink:associated_with','biolink:associated_with'),
        'HPO': ('biolink:associated_with','biolink:associated_with'),
        'GO:CC': ('biolink:associated_with','biolink:associated_with'),
        'CP:BIOCARTA': ('biolink:associated_with','biolink:associated_with')
    }

    def identifier(self, field_name, value):
        biolink_class = 'pathway'     # i.e., reactome, kegg, wikipathways, biocarta
        if field_name == 'hpo':
            biolink_class = 'disease' 
        if field_name == 'go':
            biolink_class = 'BiologicalProcess' 
        return self.add_prefix(field_name, value, biolink_class)


    def export(self, collection, controls):
        get_species_mapping(self)
        pathway_list = []
        for element in collection:
            identifier_list = self.get_identifiers(element, 'entrez', de_prefix=False)
            
            for identifier in identifier_list:
                self.get_pathways(element.id, identifier, pathway_list)
        return pathway_list

    ########################################################
    # Called by MSigDBPathwayTransformer.export()
    def get_pathways(self, source_element_id, identifier, pathway_list):
        gene_id = self.de_prefix('entrez',identifier)
        query = """
        SELECT gene_set_details.gene_set_id,
            exact_source, 
            standard_name primary_name,
            ( SELECT MSigDB_base_URL FROM MSigDB WHERE version_name = '2024.1.Hs' )
            ||'/geneset/'||standard_name URL, 
            description_brief, 
            description_full,
            collection_name, 
            SUBSTR(collection_name,1,2) category_code,
            CASE WHEN INSTR(collection_name, ":") > 0 THEN SUBSTR(collection_name, INSTR(collection_name, ":")+1) ELSE Null END AS subcategory_code,
            publication_id,
            contributor,
            contrib_organization contributor_organization,
            description_brief,
            description_full,
            title,
            PMID,
            DOI,
            publication.URL pub_URL,
            species_name,
            external_details_URL
        FROM gene_symbol gsym
        JOIN gene_set_gene_symbol gsetgs on gsym.id = gsetgs.gene_symbol_id
        JOIN gene_set gset on gsetgs.gene_set_id = gset.id
        JOIN gene_set_details on gset.id = gene_set_details.gene_set_id
        LEFT JOIN publication on publication_id = publication.id
        JOIN species on source_species_code = species.species_code
        WHERE NCBI_id =  ?;
        """
        cur = database_connection.cursor()
        cur.execute(query,(gene_id,))
        for row in cur.fetchall():
            id = self.add_prefix('msigdb', str(row['primary_name']))
            biolink_class = self.biolink_class(self.OUTPUT_CLASS)  # set a default class
            identifiers = {'msigdb':id}                            # dict of entity id's various identifiers 
            sub_category = row['subcategory_code']
            if sub_category in self.sub_categories and row['exact_source'] is not None:
                        field_name = self.sub_categories[sub_category]
                        identifiers[field_name] = self.identifier(field_name, row['exact_source'])
            names_synonyms = [self.Names(name = str(row['primary_name']))]   # dict of entity id's various names & synonyms 
            element = self.Element(id, biolink_class, identifiers, names_synonyms)
            predicate = self.PREDICATE
            inverse_predicate = self.INVERSE_PREDICATE
            if sub_category in self.predicate_map:
                predicate, inverse_predicate = self.predicate_map[sub_category]
            connection = self.Connection(source_element_id, predicate,inverse_predicate)
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
            primary_knowledge_source = self.Attribute(
                    name= 'biolink:primary_knowledge_source',
                    value= 'infores:msigdb',
                    value_type= 'biolink:InformationResource',
                    type= 'biolink:primary_knowledge_source',
                    url = row['URL']
                )
            primary_knowledge_source.attribute_source = 'infores:molepro'
            connection.attributes.append(primary_knowledge_source)
            if row['publication_id'] is not None:
                if row['pub_URL'] is not None and len(row['pub_URL'].strip()) > 0:
                    publication_attribute = self.Attribute('PMID', 'PMID:'  + str(row['PMID']), type='biolink:Publication', description=self.get_publication_authors(row['publication_id']),url=row['pub_URL']) 
                else:
                    publication_attribute = self.Attribute('PMID', 'PMID:'  + str(row['PMID']), type='biolink:Publication', description=self.get_publication_authors(row['publication_id'])) 
                element.attributes.append(publication_attribute)
                connection.attributes.append(publication_attribute)
            
            ################################################
            # Trawl for Reactome or GO identifiers
            if row['exact_source'] is not None:
                identifier = row['exact_source']
                if row['exact_source'].startswith('R-'):
                    identifier = self.add_prefix('reactome',row['exact_source'], 'Pathway')
                    element.identifiers['reactome'] = identifier
                elif row['exact_source'].startswith('GO:'):
                    element.identifiers['go'] = identifier
                elif row['exact_source'].startswith('HP:'):
                    element.identifiers['hpo'] = identifier
                attribute = self.Attribute('exact_source', identifier)
                element.attributes.append(attribute)

            if row['description_full'] is not None:
                element.attributes.append(self.Attribute(
                                name = 'description_full',
                                value = row['description_full'],
                                type = 'biolink:description'))
                element.attributes.append(self.Attribute('description_brief', row['description_brief']))    
            elif row['description_brief'] is not None:              
                element.attributes.append(self.Attribute(
                                name = 'description_brief',
                                value = row['description_brief'],
                                type = 'biolink:description'))   

            if row['external_details_URL'] is not None:
                element.attributes.append(self.Attribute(
                        name= 'external_details_URL',
                        value= row['external_details_URL'],
                        type= 'biolink:url'))            

            element.attributes.append(self.Attribute(
                name = 'URL',
                value= row['URL'],
                type = 'biolink:url')
            )
            #'species_name'
            element.attributes.append(self.Attribute(
                name = 'species_name',
                value = self.add_prefix('ncbi_taxon', str(self.species_map[row['species_name']]), 'OrganismEntity'),
                type = 'biolink:in_taxon')
            ) 
            attribute_fields = ['category_code','subcategory_code','contributor','contributor_organization']
            for attr in attribute_fields:
                if row[attr] is not None:
                    attribute = self.Attribute(attr, row[attr])
                    element.attributes.append(attribute)

            connection.qualifiers.append(self.Qualifier(
                        qualifier_type_id= 'species_context_qualifier',
                        qualifier_value  =  self.add_prefix('ncbi_taxon', str(self.species_map[row['species_name']]), 'OrganismEntity')))

            element.connections.append(connection)

            # ADD ELEMENT TO PATHWAY LIST
            pathway_list.append(element)


    ########################################################
    # Called by MSigDBPathwayTransformer.get_pathways()
    def get_publication_authors(self, publication_id):
        query = """
            SELECT group_concat(display_name, ',') authors
            FROM publication_author
            JOIN author on publication_author.author_id = author.id
            WHERE publication_id = ?
            ORDER BY author_order ASC;
        """
        cur = database_connection.cursor()
        cur.execute(query,(publication_id,))
        for row in cur.fetchall():
            return row['authors']



###########################################
# pathway to gene Transformer
class MSigDBGeneTransformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables,definition_file='info/genes_transformer_info.json')
    
    def export(self, collection, controls):  
        gene_list = []
        genes = {}

        for element in collection:
            #pathway_id = self.de_prefix('msigdb',pathway.identifiers.get("msigdb"),"pathway")
            identifier_list = self.get_identifiers(element, 'msigdb', de_prefix=False)
            for identifier in identifier_list:
                self.get_genes(element.id, identifier, gene_list)
        return gene_list

    ####################################################################
    # Retrieve all the genes (possibly 100s) in the pathway (gene set)
    #
    def get_genes(self, source_element_id, identifier, gene_list):
        pathway_id = self.de_prefix('msigdb', identifier)
        query = """
            SELECT gene_set_details.gene_set_id, 
            exact_source, 
            standard_name primary_name, 
            collection_name,
                ( SELECT MSigDB_base_URL FROM MSigDB WHERE version_name = '2023.1.Hs' )
                    ||'/geneset/'||standard_name URL, 
            symbol gene, 
            NCBI_id
            FROM gene_set gset
            INNER JOIN gene_set_gene_symbol gsgs on gset.id = gsgs.gene_set_id
            INNER JOIN gene_symbol gsym on gsym.id = gene_symbol_id
            JOIN gene_set_details on gsgs.gene_set_id = gene_set_details.gene_set_id
            WHERE primary_name = ?;
        """
        cur = database_connection.cursor()
        cur.execute(query,(pathway_id,))
        for row in cur.fetchall():
            id = self.add_prefix('entrez', str(row['NCBI_id']))
            biolink_class = self.biolink_class(self.OUTPUT_CLASS)  # set a default class
            identifiers = {'entrez':id}                         # dict of entity id's various identifiers

            names_synonyms = [self.Names(name = row['gene'])]   # dict of entity id's various names & synonyms 
            element = self.Element(id, biolink_class, identifiers, names_synonyms)
            connection = self.Connection(source_element_id, self.PREDICATE,self.INVERSE_PREDICATE)
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
            element.connections.append(connection)
            ################################################
            # Trawl for Reactome or GO identifiers
            if row['exact_source'] is not None:
                identifier = row['exact_source']
                if row['exact_source'].startswith('R-'):
                    identifier = self.add_prefix('reactome',row['exact_source'], 'Pathway')
                    element.identifiers['reactome'] = identifier
                elif row['exact_source'].startswith('GO:'):
                    element.identifiers['go'] = identifier
                elif row['exact_source'].startswith('HP:'):
                    element.identifiers['hpo'] = identifier
                attribute = self.Attribute('exact_source', identifier)
                element.attributes.append(attribute)

            primary_knowledge_source = self.Attribute(
                    name= 'biolink:primary_knowledge_source',
                    value= 'infores:msigdb',
                    value_type= 'biolink:InformationResource',
                    type= 'biolink:primary_knowledge_source',
                    url = row['URL']
                )
            primary_knowledge_source.attribute_source = 'infores:molepro'
            connection.attributes.append(primary_knowledge_source)

            # ADD ELEMENT TO GENE LIST
            gene_list.append(element)


#######################################################################################################
# Read JSON file (config/species.json) that contains mapping of Reactome species.
# Then the JSON file is saved into a variable, speciesMap, for general usage by all class methods.
def get_species_mapping(self):      
    with open('config/species.json') as json_file:
        self.species_map = json.load(json_file)  


#######################################################################################################
# It is necessary to change the prefix of the reactome identifiers from the Reactome database to be
# the acceptable Biolink prefix (based on content of prefixMap.json).
def fix_reactome_prefix(self, fieldname, identifier):
    return self.add_prefix('reactome', self.de_prefix(fieldname, identifier,'Pathway'), 'Pathway')
