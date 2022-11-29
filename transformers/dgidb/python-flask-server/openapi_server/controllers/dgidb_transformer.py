from flask import g
from collections import defaultdict
from transformers.transformer import Transformer
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection
import sqlite3

SOURCE = 'DGIdb'                                            

###############################################################
# This class provides all the DGIdb information about the drugs 
# in the request query to the DGIdb Transformer REST API
###############################################################
class DGIdbProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')

#   Invoked by Transformer.transform(query) method because "function":"producer" is specified in the openapi.yaml file
    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')

    #   find drug data for each compound name that were submitted
        for name in names:
            name = name.strip()
            DGIdbDataSupply.find_compound_by_name(self.info.name, compound_list, name)

    #   send back to the REST client the entire list of the compounds' data (attributes & synonyms)
        return compound_list







###############################################################
# This class transforms a collection of compounds in the 
# request query to the DGIdb Transformer REST API into 
# information about the corresponding target genes 
###############################################################
class DGIdbTargetTransformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/targets_transformer_info.json')

    def map(self, collection, controls):
        gene_list = []

    #   find connection data for each compound that were submitted
        for compound in collection:
            try:
                bio_class = compound.biolink_class
                compound.identifiers['chembl']  # the compound must be identified with a chembl id 
                DGIdbDataSupply.find_genes_by_drug(self.info.name, gene_list, compound)
            except KeyError as e:
                print ('FYI - a ', bio_class,' is missing "%s"' % str(e))
                

    #   send back to the REST client the entire list of targets (genes that interact with the drugs)
        return gene_list







###############################################################
# This class transforms a collection of genes in the 
# request query to the DGIdb Transformer REST API into 
# information about the corresponding drugs (compounds)
###############################################################
class DGIdbInhibitorTransformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/inhibitors_transformer_info.json')

    def map(self, collection, controls):
        drug_list = []

    #   find connection (gene-inhibitor interaction) data for each gene that were submitted
        for gene in collection:
            try:
                gene.identifiers['entrez']    # the gene must be identified with an entrez id 
                DGIdbDataSupply.find_drugs_by_gene(self.info.name, drug_list, gene)
            except KeyError as e:
                print ('I got a KeyError - reason "%s"' % str(e))

    #   send back to the REST client the entire list of targets (genes that interact with the drugs)
        return drug_list








###############################################################
# This class contains common code for retrieving genes and drugs 
# based on the request query to the DGIdb Transformer REST API 
###############################################################
class DGIdbDataSupply(Transformer):

    def get_db():
        if 'db' not in g:
            g.db = sqlite3.connect("data/DGIdb.db",
                    detect_types=sqlite3.PARSE_DECLTYPES
            ) # SQLite database file is located in the python-flask-server/data directory
            g.db.row_factory = sqlite3.Row
        return g.db

    def close_db(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()


#   Get the compound's synonyms (aliases) and attributes data
    def find_compound_by_name(info_name, compound_list, name):
        """
            Find compound by a name
        """
        query1 = """
        SELECT DISTINCT 
            drugs.id AS drug_id,
            drugs.name AS drug_name, 
            drugs.fda_approved, 
            drugs.immunotherapy, 
            drugs.anti_neoplastic, 
            drugs.chembl_id AS ChEMBL_id
        FROM drugs
        JOIN drug_aliases ON drugs.id = drug_aliases.drug_id
        WHERE drugs.name = upper(?)
        OR drug_aliases.alias = ?;
        """
        global connection
        connection = DGIdbDataSupply.get_db()   
        cur = connection.execute(query1,(name,name))
    
        # for each hit (i.e., of the same drug name, an unlikely but possible occurrence)
        for row in cur.fetchall():

            id = "ChEMBL:"+row['ChEMBL_id']
            identifiers = {'chembl':id}
            type=name           # Interim solution for providing "type", pending Consortium's final decision

            compound = Element(
                id = id,
                biolink_class = 'ChemicalSubstance',
                identifiers = identifiers,
                names_synonyms = [Names(name=name,
                                        synonyms=[],
                                        source=SOURCE)], # add names & synonyms from the database
                attributes = [
                    Attribute(
                            name='query name', 
                            value=name,
                            provided_by=info_name, 
                            source=SOURCE
                            ),
                ],
                connections = [],
                source = info_name
            )

          # Append synonyms
            DGIdbDataSupply.get_names_synonyms(row['drug_id'], compound)

          # Append additional attributes collected from DGIdb drugs table
            if (row['fda_approved'] == 't'):
                compound.attributes.append(
                        Attribute(
                            provided_by=info_name,
                            name='FDA approval', 
                            value="approved",
                            source=SOURCE, 
                            type='FDA approval'
                        )
                )

            if (row['immunotherapy'] == 't'):
                compound.attributes.append(
                        Attribute(
                            provided_by=info_name,
                            name="Drug Class" ,
                            value="immunotherapy",
                            source=SOURCE,
                            type="Drug Class"
                        )
                )            
            if (row['anti_neoplastic'] == 't'):
                compound.attributes.append(
                        Attribute(
                            provided_by=info_name,
                            name="Drug Class" ,
                            value="anti_neoplastic",
                            source=SOURCE,
                            type="Drug Class"
                        )
                )

        #   Append additional attributes from drug attributes table     
            DGIdbDataSupply.get_drug_attributes(info_name, row['drug_id'],compound)   
            compound_list.append(compound)


#   Get the genes that are targets of the compound
    def find_genes_by_drug(info_name, gene_list, compound): 
            """
            Collect all the genes that the drug interact with
            """
            if compound.identifiers['chembl'] is None:
                return []
            drugs_chembl_id = compound.identifiers['chembl'].split(":",1)[1].strip()
    #       Targets SQL query.
            query2 = """ 
            SELECT
                drugs.id AS drug_id,
                genes.entrez_id,
                genes.name AS symbol,
                genes.long_name AS name,
                genes.id AS gene_id,
                interactions.id AS interaction_id
            FROM drugs
            JOIN interactions on interactions.drug_id = drugs.id
            JOIN genes ON genes.id = interactions.gene_id
            WHERE drugs.chembl_id = ?;
            """  
            global connection
            connection = DGIdbDataSupply.get_db() 
            cur2 = connection.execute(query2,(drugs_chembl_id,))

            for row in cur2.fetchall():             # loop for each gene interaction
                dgidb_gene_id  = row['gene_id']
                interaction_id = row['interaction_id']
                id = "NCBIGene:"+str(row['entrez_id'])
                gene = Element(
                    id = id,
                    biolink_class = "Gene",
                    identifiers = {"entrez":id},
                    names_synonyms = [],
                    attributes = [],
                    connections = [],
                    source = info_name
                )

            #   Start adding the gene name & symbol from the genes table
                gene.names_synonyms.append(
                    Names(
                        name = row['name'],
                        synonyms = [row['symbol']],
                        source = info_name,
                    )
                )

            #   Append to gene additional attributes collected from DGIdb gene_attributes table
                DGIdbDataSupply.get_gene_attributes(gene, info_name, dgidb_gene_id)

            #   Append connection to gene, per interaction_id
                DGIdbDataSupply.get_connection_data(gene, info_name, interaction_id, compound.id, "affects")

                gene_list.append(gene)


    def get_gene_attributes(gene, info_name, dgidb_gene_id):
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
        global connection
        connection = DGIdbDataSupply.get_db()         
        cur3 = connection.execute(query3,(dgidb_gene_id,))        
        for row in cur3.fetchall():
            gene.attributes.append(
                    Attribute(
                        name = row['attribute_name'],
                        provided_by = info_name,
                        value = row['attribute_value'],
                        source = row['source_db_name']+'@' + SOURCE,
                        type = row['attribute_name'],  # Interim solution for providing "type", pending Consortium's final decision
                    )
            )


    def find_drugs_by_gene(info_name, drug_list, gene): 
            """
            Collect all the drugs that inhibit the gene
            """
            if gene.identifiers['entrez'] is None:
                return []
            entrez_id = gene.identifiers['entrez'].split(":",1)[1].strip()
            print(entrez_id)
    #       Inhibitors SQL query.
            query4 = """ 
                    SELECT
                        drugs.id AS drug_id,
                        drugs.chembl_id,
                        drugs.name AS name,
                        drugs.immunotherapy,
                        drugs.anti_neoplastic,
                        drugs.fda_approved,
                        genes.long_name AS name,
                        interactions.id AS interaction_id
                    FROM genes
                    JOIN interactions on interactions.gene_id = genes.id
                    JOIN drugs ON drugs.id = interactions.drug_id
                    WHERE genes.entrez_id = ?;
                    """
            global connection
            connection = DGIdbDataSupply.get_db()       
            cur4 = connection.execute(query4,(entrez_id,)) 

            for row in cur4.fetchall():             # loop for each drug interaction
                dgidb_drug_id  = row['drug_id']
                interaction_id = row['interaction_id']
                id = "ChEMBL:"+(row['chembl_id'])
                drug = Element(
                    id = id,
                    biolink_class = "ChemicalSubstance",
                    identifiers = {'chembl':id},
                    names_synonyms = [],
                    attributes = [],
                    connections = [],
                    source = info_name
                )

            #   Start adding drug name & synonyms from the drugs table
                drug.names_synonyms.append(
                    Names(
                        name = row['name'],
                        synonyms = [],
                        source = info_name,
                     #   type = row['name'],        # Interim solution for providing "type", pending Consortium's final decision
                     #   provided_by = info_name
                    )
                )

                DGIdbDataSupply.get_names_synonyms(dgidb_drug_id, drug)

            #   Append to drug additional attributes collected from DGIdb drug_attributes table
                DGIdbDataSupply.get_drug_attributes(info_name, dgidb_drug_id, drug)

            #   Append connection to gene, per interaction_id
                DGIdbDataSupply.get_connection_data(drug, info_name, interaction_id, gene.id, "affected_by")

                drug_list.append(drug)


#   Based this function on one in chembl transformer code
    def get_names_synonyms(id, compound):  
        """
            Build names and synonyms list
        """
    #   Query for data to fill the Names class.
        query5 = """ 
            SELECT
                drug_aliases.alias,
                sources.source_db_name AS alias_source
            FROM drug_aliases
            JOIN drug_aliases_sources ON drug_aliases.id = drug_aliases_sources.drug_alias_id
            JOIN sources ON drug_aliases_sources.source_id = sources.id
            WHERE drug_id = ?;
        """
    #   Dictionary to collect the lists of synonyms (aliases) and their respective sources.
        synonyms_dictionary = defaultdict(list)
        global connection
        connection = DGIdbDataSupply.get_db()
        cur5 = connection.execute(query5,(id,))

        for row in cur5.fetchall():
            # alias
            # alias_source
            synonyms_dictionary[row['alias_source']].append(row['alias'])
 
        for syn_type, syn_list in synonyms_dictionary.items():
                compound.names_synonyms.append(
                    Names(
                        name = syn_list[0] if len(syn_list) == 1 else  None,
                        synonyms = syn_list if len(syn_list) > 1 else  None,
                        source = syn_type+'@DGIdb',
                    )
                )


    def get_drug_attributes(info_name, id, compound): 
    #   query to fill the attributes array.
        query6 = """ 
            SELECT
                drug_attributes.name,
                drug_attributes.value,
                sources.source_db_name AS attribute_source
            FROM drug_attributes
            JOIN drug_attributes_sources ON drug_attributes.id = drug_attributes_sources.drug_attribute_id
            JOIN sources ON drug_attributes_sources.source_id = sources.id
            WHERE drug_attributes.drug_id = ?;
        """
        global connection
        connection = DGIdbDataSupply.get_db()
        cur6 = connection.execute(query6,(id,))

        for row in cur6.fetchall(): 
            compound.attributes.append(
                    Attribute(
                        name = row['name'],
                        provided_by = info_name,
                        value = row['value'],
                        source = row['attribute_source']+'@DGIdb',
                        type = row['name'],              # Interim solution for providing "type", pending Consortium's final decision
                    )
            )


    def get_interaction_attributes(info_name, drug_gene_interaction, interaction_id):
    #   Connection attributes SQL query:
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
        global connection
        connection = DGIdbDataSupply.get_db()
        cur7 = connection.execute(query7,(interaction_id,))  

        for row in cur7.fetchall():
        #   append interaction attributes
            drug_gene_interaction.attributes.append(
                            Attribute(
                                name = row['name'],
                                provided_by = info_name,
                                value = row['value'],
                                source = str(row['source_db_name'])+'@' + SOURCE,
                                type = row['name'],  # Interim solution for providing "type", pending Consortium's final decision
                            )        
            )        


#   Based on the interaction_id, add publication information and other attribute information
    def get_connection_data(entity, info_name, interaction_id, id, type):
        """
            Gather all the information about the drug-gene interaction (i.e., connection)
        """
        drug_gene_interaction  = Connection(
                                    source_element_id = id,
                                    type = type,
                                    evidence_type = "",
                                    attributes = [],
                                )

    #   Connections publications SQL query:
        query8 = """ 
                SELECT 
                    publications.pmid,
                    publications.citation
                FROM interactions
                JOIN interactions_publications on interactions_publications.interaction_id = interactions.id
                JOIN publications ON publications.id = interactions_publications.publication_id
                WHERE interactions.id =?;
                """
        global connection
        connection = DGIdbDataSupply.get_db()
        cur8 = connection.execute(query8,(interaction_id,))  

        for row in cur8.fetchall():                     # loop for each PubMed citation
            drug_gene_interaction.attributes.append(
                            Attribute(
                                name = "publication",
                                value = "PMID:"+str(row['pmid']),
                                type = "IAO:0000311", 
                                source = SOURCE,
                                url = "https://pubmed.ncbi.nlm.nih.gov/" + str(row['pmid']),
                                provided_by = info_name
                            )        
            )

    #   append Interaction Attributes from interaction_attributes table
        DGIdbDataSupply.get_interaction_attributes(info_name, drug_gene_interaction, interaction_id) 
        
    #   append the completed Interaction to the drug's or gene's connections array                   
        entity.connections.append(drug_gene_interaction)


########################################################################################################

def main():
    pass

if __name__ == '__main__':
    main()
