import connexion
import six
import sqlite3
import json
import requests

from transformers.transformer import Transformer
from transformers.transformer import Producer


SOURCE = 'StringDB'
connection = sqlite3.connect("data/STRING.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

class StringTransformer(Transformer):

    variables = [
        'minimum combined score',
        'maximum number of genes'
    ]

    def __init__(self):
        super().__init__(self.variables, definition_file='info/transformer_info.json')


    ######################################################################################### 
    # controls    = the parameters in the transformer_info.json file
    # query_genes = the query's collection of input genes
    def expand(self, query_genes, controls):
        if len(query_genes) == 0:
            return []
        gene_dict = {}
        gene_list = []    # for the output knowledge graph
        for query_gene in query_genes:  # copy input genes into working dictionary
            if query_gene.identifiers['entrez'] is not None: 
              # convert to a proper element
                gene = self.Element(
                            attributes= [],
                            id = query_gene.id,
                            biolink_class='Gene',
                            identifiers = query_gene.identifiers,
                            names_synonyms = query_gene.names_synonyms
                        )

                for gene_id in self.get_identifiers(query_gene, 'entrez', de_prefix=False):
                    gene_dict[gene_id] = gene 
        query_gene_list = list(gene_dict.values())  # Create list for iteration (should not iterate a dynamic dictionary)
        for query_gene in query_gene_list:
            self.get_partners_STRING_DB(query_gene, controls['maximum number of genes'], controls['minimum combined score']*1000, gene_dict)            
        gene_list = list(gene_dict.values())          
        return gene_list


    #######################################################################################
    # Take a protein's Ensembl ID to find the linked protein in the database.
    #
    def get_partners_STRING_DB(self, input_gene, top, minimum_combined_score, gene_list):
        limit = 'LIMIT {}'.format(top) if top > 0 else ''
        query = '''SELECT
                        string_protein_id1,
                        string_protein_id2,
                        taxon_id2,
                        combined_score,
                        neighborhood_score,
                        fusion_score,
                        cooccurence_score,
                        homology_score,
                        coexpression_score,
                        experiments_score,
                        database_score,
                        textmining_score,
                        neighborhood_transferred,
                        coexpression_transferred,
                        experiments_transferred,
                        database_transferred,
                        textmining_transferred,
                        PROTEINS_2.EnsemblGene,
                        PROTEINS_2.preferred_name AS partner_2_preferred_name,
                        PROTEINS_2.annotation,
                        PROTEINS_1.preferred_name AS partner_1_preferred_name
                    FROM LINKS
                    JOIN PROTEINS AS PROTEINS_2 ON string_protein_id2 = PROTEINS_2.string_protein_id
                    JOIN PROTEINS AS PROTEINS_1 ON string_protein_id1 = PROTEINS_1.string_protein_id
                    WHERE string_protein_id1 = ?
                    AND combined_score >= {}
                    ORDER BY combined_score DESC
                    {};
                '''.format(minimum_combined_score, limit)
        for gene_id in self.get_identifiers(input_gene, 'entrez', de_prefix=True):
            protein = get_protein_string_id(gene_id)
            cur = connection.execute(query,(protein['string_protein_id'],))
            # Iterate through query results to build gene list with connections
            for row in cur.fetchall():
                add_element(self, input_gene, row, gene_list)


    ####################################################################
    # connection attributes from LINKS table
    ####################################################################
    def get_connections_attributes (self, row, connection):
        attributes_list= ['homology_score', 'combined_score', 'neighborhood_score', 'fusion_score', 'cooccurence_score', 'coexpression_score',
         'experiments_score', 'database_score','textmining_score']
        for attribute in attributes_list:
                # Note: the scores must be displayed as values from 0 to 1
                # (the highest possible scores in the database is 1,000)
                    connection.attributes.append(self.Attribute(
                        name= attribute,
                        value= (float(row[attribute])/1000),
                        type= attribute,
                        value_type = 'Double'
                        )
                    )




##################################################################################
# This class returns the protein-protein physical links information in the
# PHYSICAL_LINKS table of theSTRING database.
class StringPhysicalLinkTransformer(Transformer):

    variables = [
        'minimum combined score',
        'maximum number of genes'
    ]

    def __init__(self):
        super().__init__(self.variables, definition_file='info/physical_transformer_info.json')    


    ######################################################################################### 
    # controls    = the parameters in the transformer_info.json file
    # query_genes = the query's collection of input genes
    def expand(self, query_genes, controls):
        if len(query_genes) == 0:
            return []
        gene_dict = {}
        gene_list = []    # for the output knowledge graph
        gene = None
        for query_gene in query_genes:  # copy input genes into output knowledge graph
            if query_gene.identifiers['entrez'] is not None:
        # convert to a proper element
                gene = self.Element(
                            attributes= [],
                            id = query_gene.id,
                            biolink_class='Gene',
                            identifiers = query_gene.identifiers,
                            names_synonyms = query_gene.names_synonyms
                        )

                for gene_id in self.get_identifiers(query_gene, 'entrez', de_prefix=False):
                    gene_dict[gene_id] = gene   
        query_gene_list = list(gene_dict.values())
        for query_gene in query_gene_list:
            self.get_partners_STRING_DB(query_gene, controls['maximum number of genes'], controls['minimum combined score']*1000, gene_dict)               
        gene_list = list(gene_dict.values())  

        return gene_list


    #######################################################################################
    # Take a protein's Ensembl ID to find the physical-linked protein in the database.
    #
    def get_partners_STRING_DB(self, input_gene, top, minimum_combined_score, gene_dict):
        limit = 'LIMIT {}'.format(top) if top > 0 else ''
        query = '''SELECT
                        string_protein_id1,
                        string_protein_id2,
                        taxon_id2,
                        homology_score,
                        combined_score,
                        experiments_score,
                        experiments_transferred,
                        database_score,  
                        database_transferred,
                        textmining_score,
                        textmining_transferred,
                        PROTEINS_2.EnsemblGene,
                        PROTEINS_2.preferred_name AS partner_2_preferred_name,
                        PROTEINS_2.annotation,
                        PROTEINS_1.preferred_name AS partner_1_preferred_name
                    FROM PHYSICAL_LINKS
                    JOIN PROTEINS AS PROTEINS_2 ON string_protein_id2 = PROTEINS_2.string_protein_id
                    JOIN PROTEINS AS PROTEINS_1 ON string_protein_id1 = PROTEINS_1.string_protein_id
                    WHERE string_protein_id1 = ?
                    AND combined_score >= {}
                    ORDER BY combined_score DESC
                    {};
            '''.format(minimum_combined_score, limit)
        protein = get_protein_string_id(self.de_prefix('entrez', input_gene.identifiers['entrez']))
        cur = connection.execute(query,(protein['string_protein_id'],))
        # Iterate through query results to build gene list with connections
        for row in cur.fetchall():
            add_element(self, input_gene, row, gene_dict)
     

    ####################################################################
    # connection attributes from PHYSICAL_LINKS table
    ####################################################################
    def get_connections_attributes (self, row, connection):
        attributes_list= ['homology_score', 'combined_score', 'experiments_score', 'experiments_transferred',
        'database_score','database_transferred','textmining_score','textmining_transferred']
        for attribute in attributes_list:
                # Note: the scores must be displayed as values from 0 to 1
                # (the highest possible scores in the database is 1,000)
                    connection.attributes.append(self.Attribute(
                        name= attribute,
                        value= (float(row[attribute])/1000.0),
                        type= attribute,
                        value_type = 'Double'
                        )
                    )

################################################  Common Functions  #################################################
# This is common code for retrieving protein-related data
#####################################################################################################################

####################################################################
# Useful for getting identifiers of partner proteins
####################################################################
def get_identifiers_by_protein_id(self, string_protein_id, names_synonyms):
    identifiers = {}
    ensembl_hgnc_symbol = None
    entrez = None
    query = '''
        SELECT taxon_id, string_protein_id, alias, source
        FROM PROTEIN_ALIAS
        WHERE string_protein_id = ?
        AND source in (
            "Ensembl_HGNC_omim_id", "Ensembl_HGNC_entrez_id","Ensembl_HGNC_hgnc_id",
            "Ensembl_HGNC_ensembl_gene_id","Ensembl_HGNC_name", "Ensembl_HGNC_symbol",
            "Ensembl_gene"
         );
  '''
    cur = connection.execute(query,(string_protein_id,))
    for row in cur.fetchall():
        if row['source'] == 'Ensembl_HGNC_hgnc_id': 
            identifiers['hgnc'] = row['alias']
        elif row['source'] == 'Ensembl_gene':
            identifiers['ensembl'] = row['alias']
        elif row['source'] == 'Ensembl_HGNC_ensembl_gene_id':
            if 'ensembl' not in identifiers:
                identifiers['ensembl'] = row['alias']
        elif row['source'] == 'Ensembl_HGNC_entrez_id': 
            identifiers['entrez'] = 'NCBIGene:' + str(row['alias'])
            entrez = 'NCBIGene:' + str(row['alias'])
        elif row['source'] == 'Ensembl_HGNC_omim_id':
            identifiers['mim'] = row['alias']   
        elif row['source'] == 'Ensembl_HGNC_name':
            names_synonyms.append(
                self.Names(
                    name = row['alias'] ,
                    type = 'primary name'
                )
            )  
        elif row['source'] == 'Ensembl_HGNC_symbol':
            ensembl_hgnc_symbol = row['alias']
    return (identifiers, ensembl_hgnc_symbol)

#################################################################################
# Find the ENSP identifier and Ensembl_HGNC_symbol that match the query's entrez ID
#################################################################################    
def get_protein_string_id(entrez_id):
    query = '''
        SELECT PROTEIN_ALIAS.string_protein_id, PROTEIN_ALIAS2.alias
        FROM PROTEIN_ALIAS
        JOIN PROTEIN_ALIAS AS PROTEIN_ALIAS2 ON PROTEIN_ALIAS.string_protein_id = PROTEIN_ALIAS2.string_protein_id
        WHERE PROTEIN_ALIAS.alias = ? 
        AND PROTEIN_ALIAS2.source = "Ensembl_HGNC_symbol"
    '''
    cur = connection.execute(query,(entrez_id,))
    row = cur.fetchone()
    return row


################################################################################# 
# Creates element for genes
################################################################################# 
def add_element(self, input_gene, row, gene_dict):
    # Set up identifiers
    
    names_synonyms = []
    (identifiers, ensembl_hgnc_symbol) = get_identifiers_by_protein_id(self, row["string_protein_id2"], names_synonyms)
    gene_id = identifiers.get('entrez')
    if gene_id is None:
        gene_id = identifiers.get('ensembl')

    # Check that gene dictionary does not already have an element for the gene
    # If not, add the gene to gene dictionary  Else, add to the connections of the gene on the gene dictionary
    gene = gene_dict.get(gene_id)

    if gene_id is None:
        print('WARNING: No gene_id for: ', row['string_protein_id2'])
        return
    if gene is None : # create a new element and add to the gene_list
        attributes= []
        if ensembl_hgnc_symbol is not None and ensembl_hgnc_symbol != "":
            attributes.append(self.Attribute(
                        type = "biolink:symbol",
                        name = "Ensembl_HGNC_symbol",
                        value = ensembl_hgnc_symbol,
                        value_type = 'String'
                    ))
        gene = self.Element(
                    attributes= attributes,
                    id = gene_id,
                    biolink_class='Gene',
                    identifiers = identifiers,
                    names_synonyms = names_synonyms
                )
        gene_dict[gene_id] = gene
    else:
        gene.identifiers = identifiers
        gene.names_synonyms = names_synonyms
    connection = self.Connection(
        source_element_id = input_gene.id,
        predicate = self.PREDICATE,
        inv_predicate = self.INVERSE_PREDICATE, 
        attributes= []
    )
    # Find and add attributes to the connection 
    self.get_connections_attributes(row, connection)

    connection.attributes.append(self.Attribute(
    type = "biolink:primary_knowledge_source",
    name = "primary_knowledge_source",
    value = "infores:string",
    value_type = 'biolink:InformationResource',
    url = "https://string-db.org/interaction/{}.{}/{}.{}".format(row['taxon_id2'],row['string_protein_id1'],row['taxon_id2'],row['string_protein_id2'])
    ))

    connection.attributes.append(self.Attribute(
        name = 'knowledge level',
        value = self.KNOWLEDGE_LEVEL,
        type = 'biolink:knowledge_level',
        value_type = 'String'
    ))
    connection.attributes.append(self.Attribute(
        name = 'agent type',
        value = self.AGENT_TYPE,
        type = 'biolink:agent_type',
        value_type = 'String'
    ))
    species = 'NCBITaxon:'+str(row['taxon_id2'])
    connection.qualifiers.append(self.Qualifier(qualifier_type_id = 'species_context_qualifier', qualifier_value = species))
    gene.connections.append(connection)  

