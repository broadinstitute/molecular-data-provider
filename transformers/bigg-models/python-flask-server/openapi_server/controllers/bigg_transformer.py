
import requests
import sqlite3
import re

from transformers.transformer import Transformer, Producer # noqa: E501
from openapi_server.models.element import Element


####################################### Set up SQLite database connection #####################################################################################
db_connection = sqlite3.connect("data/BiGG.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) 
db_connection.row_factory = sqlite3.Row


##########################################################################
# Post request to transformer
# http://localhost:8420/bigg/metabolites/transform
#
# BiGG Producer Class
#
##########################################################################
class BiGG_Compound_Producer(Producer):
    variables = ['compounds']    #   i.e., the name value in the incoming Request query
    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')  # to be used in find_metabolite()

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compound_list_producer_transformer_info.json')

    ###########################################################################
    #
    # Called by Producer Base Class' produce() method
    #
    def find_names(self, name):
        ids = []
        for row in self.find_metabolite(name):
            ids.append(row['metabolite_bigg_id'])
        return ids

    
    ###########################################################################
    #
    # Called by Producer Base Class' produce() method
    # 
    def create_element(self, metabolite_bigg_id):
        element = None
        names = None
        identifiers = {} 
        for row in self.get_metabolite(metabolite_bigg_id):
            metabolite_name = row['name']
            names = [self.Names(metabolite_name)]
        self.get_identifiers(metabolite_bigg_id, identifiers)
        id = 'BIGG.METABOLITE:'+ metabolite_bigg_id    
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)
           
        element = self.Element(id, biolink_class, identifiers, names)

        return element


    #######################################################################################
    #
    # Gathering the identifiers of the metabolite
    #
    def get_metabolite(self, metabolite_bigg_id):
        query = """
            SELECT DISTINCT 
                metabolite.metabolite_bigg_id,
                metabolite.name
            FROM metabolite
            WHERE metabolite.metabolite_bigg_id = ?;
        """
        cur = db_connection.cursor()
        cur.execute(query,(metabolite_bigg_id,))
        return cur.fetchall()


    #######################################################
    #
    # Take a given name and get its metabolite info to
    # append to a compound list.
    #
    # The parameter "name" can be Inchikey, BiGG Id or
    # just a name such as 'adenosine'.
    #
    def find_metabolite(self, name):

        rows = list()
        parameters = list()

        query1 = """
                SELECT
                DISTINCT metabolite.metabolite_bigg_id,
                name
                FROM metabolite
                WHERE name = ?
                COLLATE NOCASE;
        """

        query2 = """
                SELECT 
                DISTINCT metabolite.metabolite_bigg_id
                FROM metabolite
                WHERE metabolite_bigg_id = ?
                COLLATE NOCASE;
        """

        query3 = """
                SELECT
                DISTINCT metabolite_bigg_id
                FROM metabolite_db
                WHERE db_id = ?;
        """

        if self.has_prefix("bigg", name, "compound"):
            parameters = (self.de_prefix("bigg", name, "compound"),)
            query = query2
        elif self.has_prefix("kegg", name, "compound"):
            parameters = (name,)
            query = query3
        elif self.has_prefix("chebi", name, "compound"):
            parameters = (name,)
            query = query3
        elif self.inchikey_regex.match(name):
            parameters = (name,)
            query = query3
        else:
            parameters = (name,)
            query = query1

        cur = db_connection.cursor()
        rows = cur.execute(query, parameters)

        return rows


    #######################################################
    #
    # Take a given input id and get its identifiers to
    # append to an output element.
    #
    def get_identifiers(self, id, identifiers):
        # A look-up dictionary for determining the field names of the identifiers
        #  put into the response output JSON
        name_dict = {'InChI Key':'inchikey', 'CHEBI':'chebi', 'KEGG Compound':'kegg'}

        chebi_list = []

        query = """
            SELECT
            DISTINCT metabolite.metabolite_bigg_id,
            name,
            formula,
            db_id,
            database
            FROM metabolite
            JOIN metabolite_db ON metabolite.metabolite_bigg_id = metabolite_db.metabolite_bigg_id
            WHERE metabolite.metabolite_bigg_id = ?;
        """
        parameters = (id,)
        cur = db_connection.cursor()
        cur.execute(query, parameters)

        for row in cur.fetchall():
            if row['database'] == 'CHEBI':
                chebi_list.append(row['db_id'])
            else:
                identifiers[name_dict[row['database']]] = row['db_id']
        
            identifiers[name_dict['CHEBI']] = chebi_list
            identifiers['bigg'] = 'BIGG.METABOLITE:' + row['metabolite_bigg_id']



#################################################
# Post request to transformer
# http://localhost:8420/bigg/reactions/transform
#
#   This transformer finds the reactions that are
#   associated with a metabolite (aka compound)
#
#
class BiGG_Compound_Reactions_Transformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compound_reaction_transformer_info.json')

    #################################################
    #
    # There can be one-to-many relationship between
    # metabolite and reactions
    #
    # reaction attributes:
    #   rxn_string
    #   model_id
    #
    # connection attributes:
    #   compartment
    #   stoichiometry
    #
    #
    def map(self, metabolite_list, controls):
        reaction_list = []    # list of all reactions collected by this transformer
    #   find connection data for each metabolite that was submitted in the query
        for metabolite in metabolite_list:
            self.get_reactions(metabolite, reaction_list)         
    #   send back to the REST client the entire list of reactions
        return reaction_list


    #################################################
    #
    # Sort out the preferred metabolite identifier
    #
    def get_reactions(self, input_element_compound: Element, reaction_list):

        source_element_id = input_element_compound.id
        identifiers_dict = {}
        for fieldname in input_element_compound.identifiers:  #collect all the input identifiers into a dictionary for inspection next
            identifiers_dict[fieldname] = input_element_compound.identifiers.get(fieldname)
    #   There is an order of precedence for which input identifier to process: bigg > inchikey > chebi > kegg
        if 'bigg' in identifiers_dict:
            compound_id = self.de_prefix('bigg', input_element_compound.identifiers.get('bigg'), self.INPUT_CLASS)
            self.get_reactions_of_metabolite(source_element_id, compound_id, reaction_list, True )
        elif 'inchikey' in identifiers_dict:
            self.get_reactions_of_metabolite(source_element_id, input_element_compound.identifiers.get('inchikey'), reaction_list )
        elif 'chebi' in identifiers_dict:
            if isinstance(input_element_compound.identifiers.get('chebi'), list):
                got_an_element = False
                for identifier in input_element_compound.identifiers.get('chebi'):
                    if not got_an_element:
                        got_an_element = self.get_reactions_of_metabolite(source_element_id, identifier, reaction_list )
            else:
                self.get_reactions_of_metabolite(source_element_id, input_element_compound.identifiers.get('chebi'), reaction_list )
        elif 'kegg' in identifiers_dict:
            self.get_reactions_of_metabolite(source_element_id, input_element_compound.identifiers.get('kegg'), reaction_list )
        


    #################################################
    #
    # 
    # 
    #
    def get_reactions_of_metabolite(self, source_element_id, metabolite_id, reaction_list, is_bigg=None):
        query0 = """
        -- This is a nested SELECT query to enable group concatenation of multiple model_ids into a string
        SELECT DISTINCT
            sub.reaction_id,
            sub.metabolite_bigg_id,
            group_concat(DISTINCT sub.model_id) AS Models,
            name,
            rxn_string
        FROM (
        SELECT DISTINCT
            reaction.reaction_id,
            metabolite_map.metabolite_bigg_id,
            metabolite_map.model_id,
            reaction.name,
            reaction.rxn_string
        FROM metabolite_map
        JOIN reaction ON metabolite_map.reaction_id = reaction.reaction_id
        WHERE metabolite_map.metabolite_bigg_id = ? COLLATE NOCASE
        ) AS sub
        GROUP BY sub.reaction_id, sub.metabolite_bigg_id, name;
        """

        query = """
        -- This is a nested SELECT query to enable group concatenation of multiple model_ids into a string
        SELECT DISTINCT 
            sub.reaction_id,
            sub.metabolite_bigg_id,
            group_concat(DISTINCT sub.model_id) AS Models,
            name,
            rxn_string
        FROM (
        SELECT DISTINCT 
            reaction.reaction_id,
            metabolite_db.metabolite_bigg_id,
            model_id,
            name,
            rxn_string
        FROM metabolite_db
        JOIN metabolite_map ON metabolite_db.metabolite_bigg_id = metabolite_map.metabolite_bigg_id
        JOIN reaction ON metabolite_map.reaction_id = reaction.reaction_id
        WHERE metabolite_db.db_id = ? 
        ) AS sub
        GROUP BY sub.reaction_id, sub.metabolite_bigg_id, name;
        """

        if is_bigg:
            query = query0

        cur = db_connection.cursor()
        cur.execute(query,(metabolite_id,))
        rows = cur.fetchall()
        for row in rows:
            id = 'BIGG.REACTION:'+ row['reaction_id']   
            biolink_class = self.biolink_class(self.OUTPUT_CLASS)
            identifiers = {}
            names = []
            element = self.Element(id, biolink_class, identifiers, names)

            element.attributes.append( self.Attribute('reaction string', row['rxn_string']) )
            element.attributes.append( self.Attribute('models', '[' + row['Models'] + ']') )

            element.names_synonyms.append( (self.Names(name=row['name'],
                                     synonyms=[],) ) )# add names & synonyms from the database

            self.get_reaction_details( source_element_id, element, row['reaction_id'], row['metabolite_bigg_id'] )

            reaction_list.append(element)
        if len(rows) > 0:
            return True
        else:
            return False


    #################################################
    #
    # 
    # 
    #
    def get_reaction_details(self, source_element_id, element, reaction_id, metabolite_bigg_id):

        query = """
            SELECT DISTINCT 
                reaction.reaction_id,
                compartment.compartment_bigg_id,
                compartment,  
                stoichiometry
            FROM metabolite_map
            JOIN reaction ON metabolite_map.reaction_id = reaction.reaction_id
            JOIN compartment ON metabolite_map.compartment_bigg_id = compartment.compartment_bigg_id
            WHERE reaction.reaction_id = ? AND metabolite_bigg_id = ?;
        """

        cur = db_connection.cursor()
        cur.execute(query,(reaction_id, metabolite_bigg_id,))
        for row in cur.fetchall():
            reaction_connection = self.Connection(source_element_id, self.PREDICATE, self.INVERSE_PREDICATE)
            
            source_attribute = self.Attribute('biolink:primary_knowledge_source','infores:bigg-models')
            source_attribute.value_type_id = 'biolink:InformationResource'
            source_attribute.attribute_source = 'infores:molepro'
            reaction_connection.attributes.append( source_attribute )
            compartment_attribute = self.Attribute('compartment', 'BIGG.COMPARTMENT:' + row['compartment_bigg_id'])
            compartment_attribute.description = row['compartment']
            reaction_connection.attributes.append( compartment_attribute )
            if row['stoichiometry'] is not None:
                stoichiometry = float(row['stoichiometry'])
                stoichiometry_attribute = self.Attribute('stoichiometry',  str(stoichiometry))
                stoichiometry_attribute.description = 'stoichiometry in ' + row['compartment']
                reaction_connection.attributes.append( stoichiometry_attribute )
                if stoichiometry < 0:
                    reaction_connection.biolink_predicate = 'is_input'
                    reaction_connection.inverse_predicate = 'has_input'
                else:
                    reaction_connection.biolink_predicate = 'is_output'
                    reaction_connection.inverse_predicate = 'has_output'

            element.connections.append(reaction_connection)

        self.get_identifiers(element, reaction_id, element.identifiers)
    

    #################################################
    #
    # Collect reaction identifiers
    # 
    #
    def get_identifiers(self, element, reaction_id, identifiers):
        reactions_dict = {}
        identifier_dict = {'MetaNetX (MNX) Equation':'metanetx',
                           'RHEA':'rhea',
                           'KEGG Reaction':'kegg',
                           'BioCyc':'biocyc',
                           'Reactome Reaction':'reactome',
                           'EC Number':'ec',
                           'SEED Reaction':'seed'
                           }
        query = """
                SELECT DISTINCT
                    reaction_bigg_id,
                    db_id,
                    database
                FROM reaction_db
                WHERE reaction_bigg_id = ?;
        """
        cur = db_connection.cursor()
        cur.execute(query,(reaction_id,))
        for row in cur.fetchall():
            db_id = None
            if 'BIOCYC:META' in str(row['db_id']):
                db_id = str(row['db_id']).replace('BIOCYC:META', 'MetaCyc')
            elif 'REACTOME.REACTION' in str(row['db_id']):
                db_id = str(row['db_id']).replace('REACTOME.REACTION', 'REACT')
            else:
                db_id = row['db_id']
            identifier_name = identifier_dict[row['database']]
            if identifier_name in reactions_dict:
                reactions_dict[identifier_name].append(db_id)
            else:
                reactions_dict[identifier_name] = [db_id]
        for key in reactions_dict:
            if len(reactions_dict[key]) > 1:
                identifiers[key] = reactions_dict[key]
            else:
                identifiers[key] = reactions_dict[key][0]
        identifiers['bigg'] = 'BIGG.REACTION:' + reaction_id



####################################################
# Post request to transformer
# http://localhost:8420/bigg/genes/transform 
#
class BiGG_Compound_Gene_Transformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compound_gene_transformer_info.json')


    #################################################
    #
    # There can be one-to-many relationship between
    # metabolite and genes
    #
    #   gene attributes:
    #       gene name
    #       chromosome
    #       strand
    #       model_id
    #
    #   connections:
    #       gene_reaction_rule
    #
    #
    def map(self, metabolite_list, controls):
        gene_list = []    # list of all genes collected by this transformer
    #   find connection data for each metabolite that was submitted in the query
        for metabolite in metabolite_list:
            self.get_genes(metabolite, gene_list)         
    #   send back to the REST client the entire list of genes
        return gene_list


    #################################################
    #
    # Sort out the preferred metabolite identifier
    #
    def get_genes(self, input_element_compound: Element, gene_list):

        source_element_id = input_element_compound.id
        identifiers_dict = {}
        for fieldname in input_element_compound.identifiers:  #collect all the input identifiers into a dictionary for inspection next
            identifiers_dict[fieldname] = input_element_compound.identifiers.get(fieldname)

    #   There is an order of precedence for which input identifier to process: bigg > inchikey > chebi > kegg
        if 'bigg' in identifiers_dict:
            compound_id = self.de_prefix('bigg', input_element_compound.identifiers.get('bigg'), self.INPUT_CLASS)
            self.get_genes_for_metabolite(source_element_id, compound_id, gene_list, True )
        elif 'inchikey' in identifiers_dict:
            self.get_genes_for_metabolite(source_element_id, input_element_compound.identifiers.get('inchikey'), gene_list )
        elif 'chebi' in identifiers_dict:
            if isinstance(input_element_compound.identifiers.get('chebi'), list):
                got_an_element = False
                for identifier in input_element_compound.identifiers.get('chebi'):
                    if not got_an_element:
                        got_an_element = self.get_genes_for_metabolite(source_element_id, identifier, gene_list ) 
            else:
                self.get_genes_for_metabolite(source_element_id, input_element_compound.identifiers.get('chebi'), gene_list )
        elif 'kegg' in identifiers_dict:
            self.get_genes_for_metabolite(source_element_id, input_element_compound.identifiers.get('kegg'), gene_list )


    #########################################################################
    # connection attribute
    #   group_concat(DISTINCT sub.model_id) AS Models,
    #   source_element_id
    #
    # gene id  
        # sub.gene_bigg_id,
    #
    def get_genes_for_metabolite(self, source_element_id, metabolite, gene_list, is_bigg=None):
        query0 = """
                SELECT DISTINCT
                    group_concat(DISTINCT sub.model_id) AS Models,
                    gene_reaction_rule,
                    sub.gene_bigg_id AS gene_bigg_id,
                    sub.reaction_id,
                    sub.name
                FROM
                (SELECT DISTINCT
                    metabolite_map.metabolite_bigg_id AS metabolite_bigg_id,

                    metabolite_map.model_id,
                    reaction.reaction_id,
                    gene.gene_bigg_id,
                    gene.name,
                    gene_map.gene_reaction_rule
                FROM metabolite_map 
                JOIN reaction ON metabolite_map.reaction_id = reaction.reaction_id
                JOIN gene_map ON (reaction.reaction_id = gene_map.reaction_id and gene_map.model_id = metabolite_map.model_id)
                JOIN gene ON gene_map.gene_bigg_id = gene.gene_bigg_id
                WHERE metabolite_map.metabolite_bigg_id = ? COLLATE NOCASE) AS sub
                GROUP BY sub.gene_bigg_id, sub.metabolite_bigg_id,  gene_reaction_rule;
        """
        query = """
                SELECT DISTINCT
                    group_concat(DISTINCT sub.model_id) AS Models,
                    gene_reaction_rule,
                    sub.gene_bigg_id AS gene_bigg_id,
                    sub.reaction_id,
                    sub.name
                FROM
                (SELECT DISTINCT
                    metabolite_db_metabolite_bigg_id AS metabolite_bigg_id,

                    metabolite_map.model_id,
                    reaction.reaction_id,
                    gene.gene_bigg_id,
                    gene.name,
                    gene_reaction_rule
                FROM (SELECT DISTINCT metabolite_bigg_id as metabolite_db_metabolite_bigg_id  FROM metabolite_db WHERE metabolite_db.db_id = ?)
                JOIN metabolite_map ON metabolite_db_metabolite_bigg_id = metabolite_map.metabolite_bigg_id
                JOIN reaction ON metabolite_map.reaction_id = reaction.reaction_id
                JOIN gene_map ON reaction.reaction_id = gene_map.reaction_id
                JOIN gene ON gene_map.gene_bigg_id = gene.gene_bigg_id
                ) AS sub
                GROUP BY sub.gene_bigg_id, sub.metabolite_bigg_id, gene_reaction_rule;
        """

        if is_bigg:
            query = query0

        cur = db_connection.cursor()
        cur.execute(query,(metabolite,))

        rows = cur.fetchall()

        for row in rows:      # iterate through all the collected genes
            id = 'BIGG.GENE:'+ row['gene_bigg_id']   
            biolink_class = self.biolink_class(self.OUTPUT_CLASS)
            identifiers = {'bigg':id}
            names = []
            element = self.Element(id, biolink_class, identifiers, names)
            element.attributes.append( self.Attribute('models', '[' + row['Models'] + ']') )
            element.names_synonyms.append(self.Names(name = row['name'],
                     synonyms=[],) ) # add names & synonyms from the database
            self.get_gene_details(row['gene_bigg_id'], element, gene_list)
            self.get_gene_reaction_rule(source_element_id, row['gene_bigg_id'], row['reaction_id'], element, gene_list)

        if len(rows) > 0:
            return True
        else:
            return False


    #########################################################################
    #
    # gene attribute  
        #   name
        #   chromosome
        #   strand
        #
        #   gene.gene_bigg_id
        #
    def get_gene_details(self, gene_bigg_id, element, gene_list):
        name_set = set()
        chromosome_set = set()
        strand_set = set()
        query = """
            SELECT DISTINCT 
                gene.gene_bigg_id,
                name,
                chromosome,
                strand,
                db_id,
                database
            FROM gene
            JOIN gene_db ON gene.gene_bigg_id = gene_db.gene_bigg_id
            WHERE gene.gene_bigg_id = ?;
        """
        cur = db_connection.cursor()
        cur.execute(query,(gene_bigg_id,))
        rows = cur.fetchall()
        for row in rows:
            name_set.add(row['name']) 
            chromosome_set.add(row['chromosome'])
            strand_set.add(row['strand']) 

        for name in name_set:
            element.attributes.append( self.Attribute('name',  name ) )
        for chromosome in chromosome_set:
            element.attributes.append( self.Attribute('chromosome',  chromosome ) )
        for strand in strand_set:
            element.attributes.append( self.Attribute('strand',  strand )  )
        
        self.get_identifiers(rows, gene_bigg_id, element.identifiers)


    #########################################################################
    #
    # Collect gene identifiers
        #  sub.db_id
    #
    def get_identifiers(self, rows, gene_bigg_id, identifiers):
        identifier_dict = {'CCDS':'ccds','Online Mendelian Inheritance in Man':'omim', 'NCBI Entrez Gene':'entrez'}
        ccds_list = []

        for row in rows:
            if row['database'] == 'CCDS':
                ccds_list.append(row['db_id'])
            else:
                identifiers[identifier_dict[row['database']]] = row['db_id']

        identifiers[identifier_dict['CCDS']] = ccds_list


    #########################################################################
    #
    # Add connection attribute  
    #   - sub.gene_reaction_rule
    #
    def get_gene_reaction_rule(self, source_element_id, gene_bigg_id, reaction_id, element, gene_list):
        query = """
            SELECT DISTINCT
                reaction_id,
                gene_reaction_rule
            FROM gene_map
            WHERE gene_bigg_id = ? AND reaction_id = ?;
        """
        cur = db_connection.cursor()
        cur.execute(query,(gene_bigg_id, reaction_id,))

        gene_connection = self.Connection(source_element_id, self.PREDICATE, self.INVERSE_PREDICATE)
        source_attribute = self.Attribute('biolink:primary_knowledge_source','infores:bigg-models')
        source_attribute.value_type_id = 'biolink:InformationResource'
        source_attribute.attribute_source = 'infores:molepro'
        gene_connection.attributes.append( source_attribute )
        for row in cur.fetchall():
            gene_connection.attributes.append( self.Attribute('gene_reaction_rule', row['gene_reaction_rule'] ) )
        element.connections.append(gene_connection)

        gene_list.append(element)



####################################################
# Post request to transformer
# http://localhost:8420/bigg/gene-reactions/transform 
#
# BiGG Gene - Reaction Transformer
#
class BiGG_Gene_Reaction_Transformer(Transformer):
    variables = []
    
    def __init__(self):
        super().__init__(self.variables, definition_file='info/gene_reaction_transformer_info.json')


    #################################################
    #
    # There will be one-to-many relationship between
    # a gene and reactions
    def map(self, gene_list, controls):
        reactions_list = []    # list of all reactions collected by this transformer
    #   find connection data for each gene that was submitted in the query
        for gene in gene_list:
            self.get_reactions(gene, reactions_list)         
    #   send back to the REST client the entire list of reactions
        return reactions_list


    #################################################
    #
    # First, translate gene's CURIE
    # into one or more BiGG's gene_bigg_id
    #
    def get_reactions(self, input_element_compound: Element, reaction_list):
        source_element_id = input_element_compound.id

        query = """
            SELECT DISTINCT 
                gene_bigg_id
            FROM gene_db
            WHERE db_id = ?;
        """
        for fieldname in input_element_compound.identifiers:
            if fieldname == 'entrez':
                identifier = input_element_compound.identifiers.get(fieldname)
                cur = db_connection.cursor()
                cur.execute(query,(identifier,))
                for row in cur.fetchall():
                    self.get_reactions_for_gene(source_element_id, row['gene_bigg_id'], reaction_list )



    #################################################
    #
    #
    def get_reactions_for_gene(self, source_element_id, gene, reaction_list):
        query = """
            SELECT DISTINCT
                group_concat(DISTINCT sub.model_id) AS Models,
                sub.db_id AS source_element_id,
                sub.reaction_id,
                gene_bigg_id,
                sub.name AS reaction_name,
                rxn_string
            FROM
            (SELECT DISTINCT 
                gene_db.gene_bigg_id AS gene_bigg_id,
                gene_db.db_id,
                reaction.reaction_id,
                gene_map.model_id,
                reaction.name,
                rxn_string
            FROM gene_db
            JOIN gene_map ON gene_db.gene_bigg_id = gene_map.gene_bigg_id
            JOIN reaction ON gene_map.reaction_id = reaction.reaction_id
            JOIN gene ON gene.gene_bigg_id =  gene_db.gene_bigg_id  
            WHERE gene.gene_bigg_id = ?) AS sub
            GROUP BY sub.gene_bigg_id, reaction_id;
        """           
        cur = db_connection.cursor()
        cur.execute(query,(gene,))  
        rows = cur.fetchall()
        for row in rows:   
            id = 'BIGG.REACTION:'+ row['reaction_id']   
            biolink_class = self.biolink_class(self.OUTPUT_CLASS)
            identifiers = {}
            names = []
            element = self.Element(id, biolink_class, identifiers, names)

            element.names_synonyms.append(self.Names(name = row['reaction_name'],
                                synonyms=[],)) # add names & synonyms from the database
            element.attributes.append( self.Attribute('reaction string', row['rxn_string']) )
            element.attributes.append( self.Attribute('models', '[' + row['Models'] + ']') )
                   
            self.get_compartment(element, source_element_id, row['gene_bigg_id'], row['reaction_id'])
            self.get_identifiers(element, row['reaction_id'], identifiers)

            reaction_list.append(element)
 

    #################################################
    #
    #
    def get_compartment(self, element, source_element_id, gene_bigg_id, reaction_bigg_id):
        query = """
            SELECT DISTINCT 
                reaction.reaction_id,
                metabolite_bigg_id,
                compartment.compartment_bigg_id,
                compartment.compartment
            FROM gene_map
            JOIN reaction ON gene_map.reaction_id = reaction.reaction_id
            JOIN metabolite_map ON reaction.reaction_id = metabolite_map.reaction_id
            JOIN compartment ON metabolite_map.compartment_bigg_id = compartment.compartment_bigg_id
            WHERE reaction.reaction_id = ? AND gene_bigg_id = ?;
        """
        cur = db_connection.cursor()
        cur.execute(query,(reaction_bigg_id, gene_bigg_id,))  
        rows = cur.fetchall()
        source_attribute = self.Attribute('biolink:primary_knowledge_source','infores:bigg-models')
        source_attribute.value_type_id = 'biolink:InformationResource'
        source_attribute.attribute_source = 'infores:molepro'

        reaction_connection = None
        for row in rows:   
            reaction_connection = self.Connection(source_element_id, self.PREDICATE, self.INVERSE_PREDICATE)
            compartment_attribute = self.Attribute('compartment', 'BIGG.COMPARTMENT:' + row['compartment_bigg_id'])
            compartment_attribute.description = row['compartment']

            reaction_connection.attributes.append( compartment_attribute )
            reaction_connection.attributes.append( source_attribute )
        if reaction_connection is not None:
            element.connections.append(reaction_connection)


    #################################################
    #
    # Collect reaction identifiers from the database
    # 
    #
    def get_identifiers(self, element, reaction_id, identifiers):
        reactions_dict = {}
        identifier_dict = {'MetaNetX (MNX) Equation':'metanetx',
                           'RHEA':'rhea',
                           'KEGG Reaction':'kegg',
                           'BioCyc':'biocyc',
                           'Reactome Reaction':'reactome',
                           'EC Number':'ec',
                           'SEED Reaction':'seed'
                           }
        query = """
                SELECT DISTINCT
                    reaction_bigg_id,
                    db_id,
                    database
                FROM reaction_db
                WHERE reaction_bigg_id = ?;
        """
        cur = db_connection.cursor()
        cur.execute(query,(reaction_id,))
        for row in cur.fetchall():
            db_id = None
            if 'BIOCYC:META' in row['db_id']:
                db_id = str(row['db_id']).replace('BIOCYC:META', 'MetaCyc')
            elif 'REACTOME.REACTION' in str(row['db_id']):
                db_id = str(row['db_id']).replace('REACTOME.REACTION', 'REACT')
            else:
                db_id = row['db_id']            
            identifier_name = identifier_dict[row['database']]
        #   Populate the reactions_dict with various collected reaction identifiers
            if identifier_name in reactions_dict:
                reactions_dict[identifier_name].append(db_id)
            else:
                reactions_dict[identifier_name] = [db_id]
        for key in reactions_dict:
            if len(reactions_dict[key]) > 1:
                identifiers[key] = reactions_dict[key]
            else:
                identifiers[key] = reactions_dict[key][0]

        identifiers['bigg'] = 'BIGG.REACTION:' + reaction_id

        