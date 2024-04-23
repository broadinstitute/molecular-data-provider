from transformers.transformer import Transformer
from transformers.transformer import Producer

from openapi_server.encoder import JSONEncoder
from openapi_server.models.predicate import Predicate
from openapi_server.models.km_attribute import KmAttribute
from openapi_server.models.km_qualifier import KmQualifier

import sqlite3
import json
from collections import defaultdict


connection = sqlite3.connect("data/CTD.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def load_config_file(config_file):
    with open(config_file) as json_file:
        return json.load(json_file)


inverse_map = load_config_file('conf/ctd_inverses.json')


class CtdCompoundProducer(Producer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/chemicals_transformer_info.json')

    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = get_compound_count()
        info.knowledge_map.nodes[self.biolink_class('ChemicalEntity')].count = get_chemical_count()

#   Invoked by Transformer.transform(query) method because "function":"producer" is specified in the openapi.yaml file
    def produce(self, controls):
        self.map = {}
        return super().produce(controls)

    # Get the compound's synonyms (aliases) and attributes data
    def get_rows(self, where, name):
        query1 = """
                SELECT DISTINCT
                ChemicalName,
                ChemicalID,
                CasRN,
                Definition,
                ParentIDs,
                TreeNumbers,
                ParentTreeNumbers,
                Synonyms,
                PubChem_CID
                FROM chemicals_w_PubchemCID
                {};
                """.format(where)
        cur = connection.execute(query1, (name,))
        return cur.fetchall()

    def find_names(self, query_id):
        if self.has_prefix("pubchem", query_id, "compound"):
            rows = self.get_rows("WHERE PubChem_CID=? collate nocase",
                                 "CID:" + self.de_prefix('pubchem', query_id, "compound"))
        elif self.has_prefix("mesh", query_id, "compound"):
            rows = self.get_rows("WHERE ChemicalID=? collate nocase", self.de_prefix('mesh', query_id, "compound"))
        elif self.has_prefix("cas", query_id, "compound"):
            rows = self.get_rows("WHERE CasRN=? collate nocase", self.de_prefix('cas', query_id, "compound"))
        else:  # This would be a compound name like acetylcarnitine
            rows = self.get_rows("WHERE ChemicalName=? collate nocase", query_id)

        id_list = []
        for row in rows:
            if str(row['ChemicalID']) is not None and str(row['ChemicalID']) != "":
                id = str(row['ChemicalID'])
                self.map[id] = row
                id_list.append(id)

        return id_list

    def get_attributes(self, row, element):
        attributes_list = {"Definition":'biolink:description'}
        for attribute_key in attributes_list.keys():
            if row[attribute_key] is not None and row[attribute_key] != '':
                element.attributes.append(self.Attribute(
                    name = attribute_key,
                    value = str(row[attribute_key]),
                    type = attributes_list[attribute_key],
                    value_type = "string"
                ))
        return None

    def create_element(self, id):
        row = self.map[id]
        identifiers = {}
        element_id = None
        biolink_class = self.biolink_class('ChemicalEntity')
        if row['ChemicalID'] is not None and row['ChemicalID'] != '':
            identifiers['mesh'] = self.add_prefix('mesh', str(row['ChemicalID']))
            element_id = identifiers['mesh']
        if row['PubChem_CID'] is not None and row['PubChem_CID'] != '':
            identifiers['pubchem'] = self.add_prefix('pubchem', str(row['PubChem_CID'])[4:])
            element_id = identifiers['pubchem']
            biolink_class = self.biolink_class('SmallMolecule')
        if row['CasRN'] is not None and row['CasRN'] != '':
            identifiers['cas'] = self.add_prefix('cas', str(row['CasRN']))

        name = row['ChemicalName']
        names = self.Names(name=name, synonyms=str(row["Synonyms"]).split('|'))

        element = self.Element(
            id=element_id,
            biolink_class=biolink_class,
            identifiers=identifiers,
            names_synonyms=[names]
        )

        self.get_attributes(row, element)
        if element_id is None:
            return None
        return element


class CtdGeneInteractionsTransformer(Transformer):

    variables = []
    qualifier_map = load_config_file('conf/ctd_qualifiers.json')


    def __init__(self):
        super().__init__(self.variables, definition_file='info/gene_interactions_transformer_info.json')


    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            genes_added = 0
            for row in self.find_compounds(compound.identifiers):
                gene_id = str(row["GeneID"])
                #print('  gene_id:', gene_id)
                if gene_id not in genes:
                    gene = self.add_element(row, gene_id)
                    if gene is None:
                        continue
                    gene_list.append(gene)
                    genes[gene_id] = gene
                gene = genes[gene_id]
                # add connection element here by calling add_connection function
                self.add_connections(row, gene, compound)
                genes_added += 1

        return gene_list


    def find_compounds(self, identifiers):
        where = None
        if identifiers.get('pubchem') is not None:
            cid = self.de_prefix('pubchem', identifiers.get('pubchem'), "compound")
            compound_id = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
        if identifiers.get('mesh') is not None:
            mesh = self.de_prefix('mesh', identifiers.get('mesh'), "compound")
            compound_id = mesh
            where = "WHERE ChemicalID = ? collate nocase"
        if where is None or compound_id is None or compound_id == '':
            return []

        query1 = """
        SELECT DISTINCT
            IxnID,
            ChemicalID,
            AxnDegreeCode,
            AxnCode,
            ChemicalName,
            ChemicalForm,
            ChemicalFormQualifier,
            ChemicalPosition,
            GeneID,
            GeneName,
            GeneForm,
            GeneFormQualifier,
            GeneSeqID,
            AxnPosition,
            AxnName,
            TaxonID,
            TaxonName,
            ReferencePMIDs,
            PubChem_CID
        FROM chem_gene_ixns_w_axn_info
        {}
        """.format(where)
        cur = connection.execute(query1, (compound_id,))
        return cur.fetchall()


    # Creates element for genes
    def add_element(self, row, gene_id):
        # Set up identifiers
        entrez_id = self.add_prefix("entrez", str(gene_id))
        identifiers = {"entrez": entrez_id}

        # Set up names
        names = self.Names(str(row["GeneName"]), synonyms=[])
        gene = self.Element(
            id=entrez_id,
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[]
        )

        return gene


    # Function to get connections
    def add_connections(self, row, gene, compound):
        predicate = self.get_predicate(row)
        connection = self.Connection(
            source_element_id=compound.id,
            predicate=predicate,
            inv_predicate=inverse_map.get(predicate, predicate),
            qualifiers=self.get_qualifiers(row),
            attributes=self.get_connections_attributes(row)
        )
        gene.connections.append(connection)


    def get_predicate(self, row):
        if 'AxnCode' in row.keys() and 'AxnDegreeCode' in row.keys():
            axnCode = str(row['AxnCode'])+str(row['AxnDegreeCode'])
            predicate = self.qualifier_map['AxnCode'].get(axnCode, {}).get('predicate', self.PREDICATE)
            if row['ChemicalPosition'] == 2:
                predicate = inverse_map.get(predicate, predicate)
            return predicate
        return self.PREDICATE


    # This function handles the qualifiers
    def get_qualifiers(self, row):
        qualifiers = []
        if 'AxnCode' in row.keys() and 'AxnDegreeCode' in row.keys():
            if row['ChemicalPosition'] == 1:
                chem_pos = 'subject'
                gene_pos = 'object'
            else:
                chem_pos = 'object'
                gene_pos = 'subject'

            # chemical qualifiers
            for (qualifier_type, qualifier_value) in self.qualifier_map['ChemicalForm'].get(row['ChemicalForm'], {}).items():
                self.add_qualifier(qualifiers, chem_pos, qualifier_type, qualifier_value)

            # gene qualifiers
            axnCode = str(row['AxnCode'])+str(row['AxnDegreeCode'])
            for (qualifier_type, qualifier_value) in self.qualifier_map['AxnCode'].get(axnCode, {}).items():
                if qualifier_type != 'predicate':
                    if qualifier_type == 'qualified_predicate' and chem_pos == 'object':
                        self.add_qualifier(qualifiers, gene_pos, qualifier_type, inverse_map.get(qualifier_value, qualifier_value))
                    else:   
                        self.add_qualifier(qualifiers, gene_pos, qualifier_type, qualifier_value)
            for (qualifier_type, qualifier_value) in self.qualifier_map['GeneForm'].get(row['GeneForm'], {}).items():
                self.add_qualifier(qualifiers, gene_pos, qualifier_type, qualifier_value)
            for (qualifier_type, qualifier_value) in self.qualifier_map['GeneForm'].get(row['GeneFormQualifier'], {}).items():
                self.add_qualifier(qualifiers, gene_pos, qualifier_type, qualifier_value)

        return qualifiers


    def add_qualifier(self, qualifiers, position, qualifier_type, qualifier_value):
        qualifier_type_id = position + qualifier_type if qualifier_type.startswith('_') else qualifier_type
        qualifiers.append(self.Qualifier(qualifier_type_id, qualifier_value))

    attributes_list = [
        ("ChemicalPosition","ChemicalPosition","string"),
        ("ChemicalForm","ChemicalForm","string"),
        ("ChemicalFormQualifier","ChemicalFormQualifier","string"),
        ("GeneForm","GeneForm","string"),
        ("GeneFormQualifier","GeneFormQualifier","string"),
        ("GeneSeqID","GeneSeqID","string"),
        ("AxnDegreeCode","AxnDegreeCode","string"),
        ("AxnDegreeCode","AxnDegreeCode","string"),
        ("AxnPosition","AxnPosition","string"),
        ("AxnName","biolink:description","string")
    ]


    def get_connections_attributes(self, row):
        attributes = []
        primary_knowledge_source = self.Attribute(
            name="biolink:primary_knowledge_source",
            value="infores:ctd",
            value_type="biolink:InformationResource",
            url="http://ctdbase.org/detail.go?type=relationship&ixnId={}".format(row['IxnID'])
        )
        primary_knowledge_source.attribute_source="infores:molepro"
        attributes.append(primary_knowledge_source)

        if row['TaxonID'] is not None and row['TaxonName'] is not None:
            value_list = str(row['TaxonID']).split('|')
            description_list = str(row['TaxonName']).split('|')
            for (value, description) in zip(value_list, description_list):
                attributes.append(self.Attribute(
                    name="TaxonID",
                    value='NCBITaxon:' + value,
                    type="biolink:OrganismTaxon",
                    value_type="biolink:curie",
                    description=description
                    ))

        if row['ReferencePMIDs'] is not None and row['ReferencePMIDs'] != '':
            for value in str(row['ReferencePMIDs']).split('|'):
                attributes.append(self.Attribute(
                    name="ReferencePMIDs",
                    value='PMID:' + value,
                    type="biolink:Publication",
                    value_type="biolink:uriorcurie"
                ))

        for (attribute, attribute_type, value_type) in self.attributes_list:
            if row[attribute] is not None and row[attribute] != '':
                attributes.append(self.Attribute(
                    name=attribute,
                    value=str(row[attribute]),
                    type=attribute_type,
                    value_type=value_type
                ))

        attributes.append(self.Attribute('knowledge_level', self.KNOWLEDGE_LEVEL, 'biolink:knowledge_level', 'string'))
        attributes.append(self.Attribute('agent_type', self.AGENT_TYPE, 'biolink:agent_type', 'string'))

        return attributes


class CtdDiseaseAssociationsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/disease_associations_transformer_info.json')

    def map(self, compound_list, controls):
        disease_list = []
        diseases = {}
        for compound in compound_list:
            for row in self.find_compounds(compound.identifiers):
                disease_id = row["DiseaseID"]
                if disease_id not in diseases:
                    disease = self.get_disease(row, disease_id)
                    disease_list.append(disease)
                    diseases[disease_id] = disease
                disease = diseases[disease_id]
                # add connection element here by calling add_connection function

                connection = self.get_connection(row, compound.id)
                disease.connections.append(connection)

                #self.add_connections(row, disease, compound)
        return disease_list


    def find_compounds(self, identifiers):
        where = None
        if identifiers.get('pubchem') is not None:
            cid = self.de_prefix('pubchem', identifiers.get('pubchem'), "compound")
            compound_id = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
        if identifiers.get('mesh') is not None:
            mesh = self.de_prefix('mesh', identifiers.get('mesh'), "compound")
            compound_id = mesh
            where = "WHERE ChemicalID = ? collate nocase"
        if where is None or compound_id is None or compound_id == '':
            return []
        query = """
            SELECT
                ChemicalID,
                DiseaseName,
                DiseaseID,
                DirectEvidence,
                InferenceScore,
                group_concat(PubMedIDs,'|') AS PubMedIDs
            FROM chemicals_diseases
            {}
            GROUP BY ChemicalID, DiseaseName, DiseaseID, DirectEvidence, InferenceScore
        """.format(where)
        cur = connection.execute(query, (compound_id,))
        return cur.fetchall()


    def get_disease(self, row, disease_id):
        # Set up identifiers
        identifiers = {}

        if disease_id.startswith("OMIM:"):
            id = self.add_prefix("omim", str(disease_id[5:]))
            identifiers['omim'] = id
        elif disease_id.startswith("MESH:"):
            id = self.add_prefix("mesh",str(disease_id[5:]))
            identifiers['mesh'] = id
        else:
            id = disease_id

        # Set up synonyms
        synonyms = []

        names = self.Names(name=str(row["DiseaseName"]), synonyms=synonyms)

        disease = self.Element(
            id=id,
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[]
        )

        self.get_element_attributes(row, disease)
        return disease

    def get_element_attributes(self, row, disease):
        pass

    # Function to get connections
    def get_connection(self, row, source_element_id):
        predicate = self.PREDICATE
        if row['DirectEvidence'] == 'therapeutic':
            predicate = self.info.knowledge_map.edges[0].predicate
            inv_predicate = self.info.knowledge_map.edges[0].inverse_predicate
        if row['DirectEvidence'] == 'marker/mechanism':
            predicate = self.info.knowledge_map.edges[1].predicate
            inv_predicate = self.info.knowledge_map.edges[1].inverse_predicate
        if row['DirectEvidence'] is None:
            predicate = self.info.knowledge_map.edges[2].predicate
            inv_predicate = self.info.knowledge_map.edges[2].inverse_predicate
        connection = self.Connection(
            source_element_id=source_element_id,
            predicate=predicate,
            inv_predicate=inv_predicate,
            attributes=self.get_connections_attributes(row)
        )

        return connection


    def get_connections_attributes(self, row):
        attributes = []
        primary_knowledge_source = self.Attribute(
            name="biolink:primary_knowledge_source",
            value="infores:ctd",
            value_type="biolink:InformationResource",
            url="http://ctdbase.org/detail.go?type=chem&acc={}&view=disease".format(row['ChemicalID'])
        )
        primary_knowledge_source.attribute_source="infores:molepro"
        attributes.append(primary_knowledge_source)

        if row['DirectEvidence'] == 'therapeutic':
            knowledge_type = self.info.knowledge_map.edges[0].knowledge_level
            agent_type = self.info.knowledge_map.edges[0].agent_type
        if row['DirectEvidence'] == 'marker/mechanism':
            knowledge_type = self.info.knowledge_map.edges[1].knowledge_level
            agent_type = self.info.knowledge_map.edges[1].agent_type
        if row['DirectEvidence'] is None:
            knowledge_type = self.info.knowledge_map.edges[2].knowledge_level
            agent_type = self.info.knowledge_map.edges[2].agent_type
        attributes.append(self.Attribute('knowledge_type', knowledge_type, 'biolink:knowledge_type', 'string'))
        attributes.append(self.Attribute('agent_type', agent_type, 'biolink:agent_type', 'string'))

        if row['PubMedIDs'] is not None and row['PubMedIDs'] != '':
            for value in set(str(row['PubMedIDs']).split('|')):
                attributes.append(self.Attribute(
                    name="PubMedIDs",
                    value='PMID:' + value,
                    type="biolink:Publication",
                    value_type="biolink:uriorcurie"
                ))


        if row["DirectEvidence"] is not None and row["DirectEvidence"] != '':
            attributes.append(self.Attribute(
                name="DirectEvidence",
                value=str(row["DirectEvidence"]),
                value_type="string"
            ))

        if row["InferenceScore"] is not None and row["InferenceScore"] != '':
            score_reference = self.Attribute(
                name = 'biolink:Publication',
                value = 'PMID:23144783 ',
                description = ' King BL, Davis AP, Rosenstein MC, Wiegers TC, Mattingly CJ.'
                    +'Ranking Transitive Chemical-Disease Inferences Using Local Network Topology in the Comparative Toxicogenomics Database.'
                    +'PLoS One. 2012;7(11):e46524',
                url = "http://www.ncbi.nlm.nih.gov/pubmed/23144783",
                value_type="biolink:uriorcurie"
                )
            attributes.append(self.Attribute(
                name="InferenceScore",
                value=str(row["InferenceScore"]),
                attributes= [score_reference],
                value_type="decimal"
            ))


        return attributes


class CtdGoAssociationsTransformer(Transformer):

    variables = ['limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/go_associations_transformer_info.json')

    def map(self, compound_list, controls):
        limit = float(controls['limit'])
        go_term_list = []
        go_terms = {}
        for compound in compound_list:
            go_terms_added = 0
            for row in self.find_compounds(compound.identifiers):
                if limit <= 0 or go_terms_added < limit:
                    go_term_id = row["GOTermID"][3:]
                    if go_term_id not in go_terms:
                        go_term = self.get_go_term(row, go_term_id)[0]
                        go_term_list.append(go_term)
                        go_terms[go_term_id] = go_term
                    go_term = go_terms[go_term_id]
                    # add connection element here by calling add_connection function
                    self.add_connections(row, go_term, compound)
                    go_terms_added += 1
        return go_term_list


    def find_compounds(self, identifiers):
        where = None
        if identifiers.get('pubchem') is not None:
            cid = self.de_prefix('pubchem', identifiers.get('pubchem'), "compound")
            compound_id = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
        if identifiers.get('mesh') is not None:
            mesh = self.de_prefix('mesh', identifiers.get('mesh'), "compound")
            compound_id = mesh
            where = "WHERE ChemicalID = ? collate nocase"
        if where is None or compound_id is None or compound_id == '':
            return []
        query = """
            SELECT DISTINCT
                ChemicalName,
                ChemicalID,
                CasRN,
                Ontology,
                GOTermName,
                GOTermID,
                HighestGOLevel,
                PValue,
                CorrectedPValue,
                TargetMatchQty,
                TargetTotalQty,
                BackgroundMatchQty,
                BackgroundTotalQty
            FROM chem_go_enriched
            {}
            ORDER BY CorrectedPValue ASC;
        """.format(where)
        cur = connection.execute(query, (compound_id,))
        return cur.fetchall()


    def get_go_term(self, row, go_term_id):
        go_term_list = []
        self.add_element(row, go_term_id, go_term_list)
        return go_term_list


    def add_element(self, row, go_term_id, go_term_list):
        if row["Ontology"] == "Biological Process":
            bl_class = "BiologicalProcess"
        elif row["Ontology"] == "Molecular Function":
            bl_class = "MolecularActivity"
        else:
            bl_class = "CellularComponent"

        # Set up identifiers
        identifiers = {}
        id = self.add_prefix("go", str(go_term_id), bl_class)
        identifiers['go'] = id

        # Set up synonyms
        synonyms = []

        names = self.Names(name=str(row["GOTermName"]), synonyms=synonyms)

        go_term = self.Element(
            id=id,
            biolink_class=bl_class,
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[]
        )

        self.get_element_attributes(row, go_term)
        go_term_list.append(go_term)

    def get_element_attributes(self, row, go_term):
        if "GOTermName" in row.keys():
            attributes_list = [
                ("Ontology","Ontology","string"),
                ("HighestGOLevel","HighestGOLevel","int")
            ]
            for (attribute, attribute_type, value_type) in attributes_list:
                if row[attribute] is not None and row[attribute] != '':
                    go_term.attributes.append(self.Attribute(attribute, row[attribute], attribute_type, value_type))


    # Function to get connections
    def add_connections(self, row, go_term, compound):
        connection = self.Connection(
            source_element_id=compound.id,
            predicate=self.PREDICATE,
            inv_predicate=self.INVERSE_PREDICATE,
            attributes=self.get_connections_attributes(row)
        )
        go_term.connections.append(connection)

    def get_connections_attributes(self, row):
        attributes = []
        primary_knowledge_source = self.Attribute(
            name="biolink:primary_knowledge_source",
            value="infores:ctd",
            value_type="biolink:InformationResource",
            url="http://ctdbase.org/detail.go?type=chem&acc={}&view=go".format(row['ChemicalID'])
        )
        primary_knowledge_source.attribute_source="infores:molepro"
        attributes.append(primary_knowledge_source)
        attributes_list = [
            ("PValue","biolink:p_value","decimal"),
            ("CorrectedPValue","biolink:adjusted_p_value","decimal"),
            ("TargetMatchQty","TargetMatchQty","int"),
            ("TargetTotalQty","TargetTotalQty","int"),
            ("BackgroundMatchQty","BackgroundMatchQty","int"),
            ("BackgroundTotalQty","BackgroundTotalQty","int")
        ]
        for (attribute_name, attribute_type, value_type) in attributes_list:
            if row[attribute_name] is not None and row[attribute_name] != '':
                attributes.append(self.Attribute(attribute_name, row[attribute_name], attribute_type, value_type))
        attributes.append(self.Attribute('knowledge_level', self.KNOWLEDGE_LEVEL, 'biolink:knowledge_level', 'string'))
        attributes.append(self.Attribute('agent_type', self.AGENT_TYPE, 'biolink:agent_type', 'string'))
        return attributes


class CtdPathwayAssociationsTransformer(Transformer):

    variables = ['limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/pathway_associations_transformer_info.json')

    def map(self, compound_list, controls):
        limit = float(controls['limit'])
        pathway_list = []
        pathways = {}
        for compound in compound_list:
            pathways_added = 0
            for row in self.find_compounds(compound.identifiers):
                if limit <= 0 or pathways_added < limit:
                    pathway_id = row["PathwayID"]
                    if pathway_id not in pathways:
                        pathway = self.get_pathway(row, pathway_id)[0]
                        pathway_list.append(pathway)
                        pathways[pathway_id] = pathway
                    pathway = pathways[pathway_id]
                    # add connection element here by calling add_connection function
                    self.add_connections(row, pathway, compound)
                    pathways_added += 1
        return pathway_list


    def find_compounds(self, identifiers):
        where = None
        if identifiers.get('pubchem') is not None:
            cid = self.de_prefix('pubchem', identifiers.get('pubchem'), "compound")
            compound_id = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
        if identifiers.get('mesh') is not None:
            mesh = self.de_prefix('mesh', identifiers.get('mesh'), "compound")
            compound_id = mesh
            where = "WHERE ChemicalID = ? collate nocase"
        if where is None or compound_id is None or compound_id == '':
            return []
        query = """
            SELECT DISTINCT
                ChemicalName,
                ChemicalID,
                CasRN,
                PathwayName,
                PathwayID,
                PValue,
                CorrectedPValue,
                TargetMatchQty,
                TargetTotalQty,
                BackgroundMatchQty,
                BackgroundTotalQty
            FROM chem_pathways_enriched
            {}
            ORDER BY CorrectedPValue ASC;
        """.format(where)
        cur = connection.execute(query, (compound_id,))
        return cur.fetchall()


    def get_pathway(self, row, pathway_id):
        pathway_list = []
        self.add_element(row, pathway_id, pathway_list)
        return pathway_list

    def add_element(self, row, pathway_id, pathway_list):
        # Set up identifiers
        identifiers = {}

        if pathway_id.startswith("KEGG:"):
            id = self.add_prefix("kegg", str(pathway_id[5:]))
            identifiers['kegg'] = id
        elif pathway_id.startswith("REACT:"):
            id = self.add_prefix("reactome",str(pathway_id[6:]))
            identifiers['reactome'] = id
        else:
            id = pathway_id

        # Set up names
        names = self.Names(name=str(row["PathwayName"]), synonyms=[])

        pathway = self.Element(
            id=id,
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[]
        )

        self.get_element_attributes(row, pathway)
        pathway_list.append(pathway)

    def get_element_attributes(self, row, pathway):
        pass

    # Function to get connections
    def add_connections(self, row, pathway, compound):
        connection1 = self.Connection(
            source_element_id=compound.id,
            predicate=self.PREDICATE,
            inv_predicate=self.INVERSE_PREDICATE,
            attributes=self.get_connections_attributes(row)
        )
        pathway.connections.append(connection1)


    def get_connections_attributes(self, row):
        attributes = []
        primary_knowledge_source = self.Attribute(
            name="biolink:primary_knowledge_source",
            value="infores:ctd",
            value_type="biolink:InformationResource",
            url="http://ctdbase.org/detail.go?type=chem&acc={}&view=pathway".format(row['ChemicalID'])
        )
        primary_knowledge_source.attribute_source="infores:molepro"
        attributes.append(primary_knowledge_source)
        attributes_list = [
            ("PValue","biolink:p_value","decimal"),
            ("CorrectedPValue","biolink:adjusted_p_value","decimal"),
            ("TargetMatchQty","TargetMatchQty","int"),
            ("TargetTotalQty","TargetTotalQty","int"),
            ("BackgroundMatchQty","BackgroundMatchQty","int"),
            ("BackgroundTotalQty","BackgroundTotalQty","int")
        ]
        for (attribute_name, attribute_type, value_type) in attributes_list:
            if row[attribute_name] is not None and row[attribute_name] != '':
                attributes.append(self.Attribute(attribute_name, row[attribute_name], attribute_type, value_type))
        attributes.append(self.Attribute('knowledge_level', self.KNOWLEDGE_LEVEL, 'biolink:knowledge_level', 'string'))
        attributes.append(self.Attribute('agent_type', self.AGENT_TYPE, 'biolink:agent_type', 'string'))
        return attributes


class CtdPhenotypeInteractionsTransformer(Transformer):

    variables = []
    qualifier_map = load_config_file('conf/ctd_phenotypes.json')


    def __init__(self):
        super().__init__(self.variables, definition_file='info/phenotype_interactions_transformer_info.json')


    def update_transformer_info(self, info):
        info.knowledge_map.edges[0].count = get_phenotype_interactions_count()
        info.knowledge_map.nodes[self.biolink_class('BiologicalProcessOrActivity')].count = get_phenotypes_count()
        info.knowledge_map.nodes[self.biolink_class('ChemicalEntity')].count = get_phenotype_chemicals_count()


    def map(self, compound_list, controls):
        phenotype_list = []
        phenotypes = {}
        for compound in compound_list:

            for row in self.find_compounds(compound.identifiers):
                phenotype_id = row["phenotypeid"][3:]
                if phenotype_id not in phenotypes:
                    phenotype = self.get_phenotype(row, phenotype_id)[0]
                    phenotype_list.append(phenotype)
                    phenotypes[phenotype_id] = phenotype
                phenotype = phenotypes[phenotype_id]
                # add connection element here by calling add_connection function
                self.add_connections(row, phenotype, compound)
        return phenotype_list


    def find_compounds(self, identifiers):
        where = None
        if identifiers.get('pubchem') is not None:
            cid = self.de_prefix('pubchem', identifiers.get('pubchem'), "compound")
            compound_id = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
        if identifiers.get('mesh') is not None:
            mesh = self.de_prefix('mesh', identifiers.get('mesh'), "compound")
            compound_id = mesh
            where = "WHERE ChemicalID = ? collate nocase"
        if where is None or compound_id is None or compound_id == '':
            return []
        query = """
            SELECT DISTINCT
                chemicalname,
                chemicalid,
                casrn,
                phenotypename,
                phenotypeid,
                comentionedterms,
                organism,
                organismid,
                interaction,
                interactionactions,
                anatomyterms,
                inferencegenesymbols,
                pubmedids
            FROM pheno_term_ixns
            {}
        """.format(where)
        cur = connection.execute(query, (compound_id,))
        return cur.fetchall()


    def get_phenotype(self, row, phenotype_id):
        phenotype_list = []
        self.add_element(row, phenotype_id, phenotype_list)
        return phenotype_list

    def add_element(self, row, phenotype_id, phenotype_list):
        # Set up identifiers
        identifiers = {}

        identifiers['go'] = self.add_prefix("go", str(phenotype_id))

        # Set up names
        names = self.Names(name=str(row["phenotypename"]), synonyms=[])

        phenotype = self.Element(
            id=self.add_prefix("go", str(phenotype_id)),
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[]
        )

        self.get_element_attributes(row, phenotype)
        phenotype_list.append(phenotype)

    def get_element_attributes(self, row, phenotype):
        pass

    # Function to get connections
    def add_connections(self, row, phenotype, compound):
        connection1 = self.Connection(
            source_element_id=compound.id,
            predicate=self.PREDICATE,
            inv_predicate=self.INVERSE_PREDICATE,
            qualifiers=self.get_qualifiers(row),
            attributes=self.get_connections_attributes(row)
        )

        phenotype.connections.append(connection1)


    def get_qualifiers(self, row):
        qualifiers = []
        if "interactionactions" in row.keys() and row["interactionactions"] is not None:
            for (qualifier_type, qualifier_value) in self.qualifier_map.get(row["interactionactions"],{}).items():
                qualifiers.append(self.Qualifier(qualifier_type, qualifier_value))
        if "organismid" in row.keys() and row["organismid"] is not None and row["organismid"] != "":
            qualifiers.append(self.Qualifier("species_context_qualifier", "NCBITaxon:" + str(row["organismid"])))
        if "anatomyterms" in row.keys() and row["anatomyterms"] is not None:
            value_list = str(row["anatomyterms"]).split('|')
            for value in value_list:
                value_sublist = value.split('^')
                if len(value_sublist) >= 3:
                    qualifiers.append(self.Qualifier("anatomical_context_qualifier","MESH:" + str(value_sublist[2])))
        if "comentionedterms" in row.keys() and row["comentionedterms"] is not None:
            value_list = str(row["comentionedterms"]).split('|')
            for value in value_list:
                value_sublist = value.split('^')
                if value_sublist[2] == "MESH":
                    item = self.add_prefix('mesh', str(value_sublist[1]), 'SmallMolecule')
                elif value_sublist[2] == "GENE":
                    item = self.add_prefix('entrez', str(value_sublist[1]), 'Gene')
                else:
                    item = str(value_sublist[2]) + ":" + str(value_sublist[1])
                qualifiers.append(self.Qualifier("context_qualifier", item))
        return qualifiers


    def get_connections_attributes(self, row):
        attributes = []
        primary_knowledge_source = self.Attribute(
            name="biolink:primary_knowledge_source",
            value="infores:ctd",
            value_type="biolink:InformationResource",
            url="http://ctdbase.org/detail.go?type=chem&acc={}&view=phenotype".format(row['chemicalid'])
        )
        primary_knowledge_source.attribute_source="infores:molepro"
        attributes.append(primary_knowledge_source)
        if row["organismid"] is not None and row["organismid"] != '':
            attributes.append(self.Attribute(
                name="organismid",
                value="NCBITaxon:" + str(row["organismid"]),
                type="biolink:OrganismTaxon",
                value_type="biolink:curie",
                description=str(row["organism"])
            )
            )
        if "interaction" in row.keys():
            attributes_list = [
                ("comentionedterms","comentionedterms","biolink:curie"),
                ("interaction","biolink:description","string"),
                ("interactionactions","interactionactions","string"),
                ("anatomyterms","anatomyterms","biolink:curie"),
                ("inferencegenesymbols","inferencegenesymbols","biolink:curie"),
                ("pubmedids","biolink:Publication","biolink:curie"),
            ]
            for (attribute, attribute_type, value_type) in attributes_list:
                if row[attribute] is not None and row[attribute] != '':
                    if attribute == "pubmedids":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            attributes.append(self.Attribute(attribute, "PMID:" + value, type=attribute_type, value_type=value_type))

                    elif attribute == "comentionedterms":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            value_sublist = value.split('^')
                            if value_sublist[2] == "MESH":
                                item = self.add_prefix('mesh', str(value_sublist[1]), 'SmallMolecule')
                            elif value_sublist[2] == "GENE":
                                item = self.add_prefix('entrez', str(value_sublist[1]), 'Gene')
                            else:
                                item = str(value_sublist[2]) + ":" + str(value_sublist[1])
                            attributes.append(self.Attribute(attribute, item, value_type=value_type, description=str(value_sublist[0])))

                    elif attribute == "anatomyterms":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            value_sublist = value.split('^')
                            attributes.append(self.Attribute(attribute,"MESH:" + str(value_sublist[2]), value_type=value_type, description=str(value_sublist[1])))

                    elif attribute == "inferencegenesymbols":
                        value_list = str(row[attribute]).split('|')
                        genes = []
                        for value in value_list:
                            value_sublist = value.split('^')
                            if value_sublist[2] == "GENE":
                                gene_id = self.add_prefix("entrez", str(value_sublist[1]), 'Gene')
                            else:
                                gene_id = value_sublist[2] + ":" + str(value_sublist[1])
                            genes.append(gene_id)
                        attributes.append(self.Attribute(attribute, genes, attribute_type, value_type))

                    else:
                        attributes.append(self.Attribute(attribute, str(row[attribute]), attribute_type, value_type))

        attributes.append(self.Attribute('knowledge_level', self.KNOWLEDGE_LEVEL, 'biolink:knowledge_level', 'string'))
        attributes.append(self.Attribute('agent_type', self.AGENT_TYPE, 'biolink:agent_type', 'string'))

        return attributes


def get_compound_count():
    query = """
        SELECT count(ChemicalID) AS count
        FROM chemicals_w_PubchemCID
        WHERE PubChem_CID IS NOT NULL;
    """
    return get_count(query)

def get_chemical_count():
    query = """
        SELECT count(ChemicalID) AS count
        FROM chemicals_w_PubchemCID
        WHERE PubChem_CID IS NULL;
    """
    return get_count(query)

def get_phenotype_interactions_count():
    query = """
        SELECT count(rowid) AS count
        FROM pheno_term_ixns;
    """
    return get_count(query)

def get_phenotypes_count():
    query = """
        SELECT count(distinct phenotypeid) AS count
        FROM pheno_term_ixns;
    """
    return get_count(query)  

def get_phenotype_chemicals_count():
    query = """
        SELECT count(distinct chemicalid) AS count
        FROM pheno_term_ixns;
    """
    return get_count(query)  

def get_count(query):
    cur = connection.execute(query)
    for row in cur.fetchall():
        return row['count']
    return -1

subjects = {
    "SmallMolecule": "PubChem_CID is not null",
    "ChemicalEntity": "PubChem_CID is null"
}

predicates = {
    "affects": "AxnCode != 'b' AND ChemicalPosition = 1",
    "affected_by": "AxnCode != 'b' AND  ChemicalPosition = 2",
    "binds": "AxnCode == 'b' "
}

def get_edge(subject, predicate, transformer, where):
    count_query = """
        SELECT count(IxnID) AS count
        FROM chem_gene_ixns_w_axn_info
        WHERE {}
    """.format(where)
    print(count_query)
    edge = Predicate()
    edge.subject = subject
    edge.predicate = predicate
    edge.inverse_predicate = transformer.inverse_map[predicate]
    edge.object = 'Gene'
    edge.source = 'CTD'
    edge.count = get_count(count_query)
    edge.knowledge_level = 'knowledge_assertion'
    edge.agent_type = 'manual_agent'

    qualifiers = defaultdict(set)
    qual_query = """
        SELECT DISTINCT 
            ChemicalPosition,
            ChemicalForm,
            GeneForm,
            GeneFormQualifier,
            AxnCode,
            AxnDegreeCode
        FROM chem_gene_ixns_w_axn_info
        WHERE {}
    """.format(where)
    cur = connection.execute(qual_query)
    for row in cur.fetchall():
        for qualifier in transformer.get_qualifiers(row):
            qualifiers[qualifier.qualifier_type_id].add(qualifier.qualifier_value)
    edge.qualifiers = []
    for (qualifier_type, qualifier_values) in qualifiers.items():
        edge.qualifiers.append(KmQualifier(qualifier_type, sorted(qualifier_values)))

    edge.attributes = []
    edge.attributes.append(KmAttribute('biolink:primary_knowledge_source', source = 'CTD'))
    edge.attributes.append(KmAttribute('biolink:OrganismTaxon', source = 'CTD', names = ['TaxonID']))
    edge.attributes.append(KmAttribute('biolink:Publication', source = 'CTD', names = ['ReferencePMIDs']))
    for attribute in transformer.attributes_list:
        edge.attributes.append(KmAttribute(attribute, source = 'CTD'))
    return edge


def get_edges():
    transformer = CtdGeneInteractionsTransformer()
    edges = []
    for subject in subjects:
        for predicate in predicates:
            where = subjects[subject] + " AND " + predicates[predicate]
            edge = get_edge(subject, predicate, transformer, where)
            edges.append(edge)

    transformer.info.knowledge_map.edges = edges
    with open('data/gene_interactions_transformer_info.json', 'w') as json_file:
        json.dump(transformer.info, json_file, cls=JSONEncoder, indent=4, separators=(',', ': '))

def main():
    get_edges()

if __name__ == "__main__":
    main()
