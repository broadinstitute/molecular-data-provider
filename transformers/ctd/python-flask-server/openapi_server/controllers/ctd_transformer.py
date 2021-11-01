from transformers.transformer import Transformer
from transformers.transformer import Producer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

import sqlite3
import re

SOURCE = 'CTD'
connection = sqlite3.connect("data/CTD.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


class CtdCompoundProducer(Producer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/chemicals_transformer_info.json')

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
            if str(row['PubChem_CID']) is not None and str(row['PubChem_CID']) != "":
                id = str(row['PubChem_CID'])
                self.map[id] = row
                id_list.append(id)

        return id_list

    def get_attributes(self, row, element):
        attributes_list = ["Definition"]
        for attribute in attributes_list:
            if row[attribute] is not None and row[attribute] != '':
                element.attributes.append(Attribute(
                    attribute_type_id=attribute,
                    original_attribute_name=attribute,
                    value=str(row[attribute]),
                    attribute_source=self.SOURCE,
                    provided_by=self.PROVIDED_BY
                ))
        return None

    def create_element(self, id):
        row = self.map[id]
        identifiers = {}
        if row['ChemicalID'] is not None and row['ChemicalID'] != '':
            identifiers['mesh'] = self.add_prefix('mesh', str(row['ChemicalID']))
        if row['PubChem_CID'] is not None and row['PubChem_CID'] != '':
            identifiers['pubchem'] = self.add_prefix('pubchem', str(row['PubChem_CID'])[4:])
        if row['CasRN'] is not None and row['CasRN'] != '':
            identifiers['cas'] = self.add_prefix('cas', str(row['CasRN']))

        name = row['ChemicalName']
        synonyms = []
        names = Names(name=name, synonyms=str(row["Synonyms"]).split('|'), source=self.SOURCE, provided_by=self.PROVIDED_BY)

        element = Element(
            id=self.add_prefix('pubchem', str(row['PubChem_CID'])[4:]),
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_attributes(row, element)

        return element


class CtdGeneInteractionsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/gene_interactions_transformer_info.json')

    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            if compound.identifiers.get('pubchem') is None:
                continue
            cid = self.de_prefix('pubchem', compound.identifiers.get('pubchem'), "compound")
            cid = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
            query1 = """
            SELECT DISTINCT
                IxnID,
                ChemicalID,
                ChemicalName,
                ChemicalForm,
                ChemicalFormQualifier,
                ChemicalPosition,
                GeneID,
                GeneName,
                GeneForm,
                GeneFormQualifier,
                GeneSeqID,
                AxnName,
                TaxonID,
                TaxonName,
                ReferencePMIDs,
                PubChem_CID
            FROM chem_gene_ixns_w_axn_info
            {}
            """.format(where)
            genes_added = 0
            cur = connection.execute(query1, (cid,))

            for row in cur.fetchall():
                gene_id = row["GeneID"]
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

            query2 = """
                        SELECT DISTINCT
                            ChemicalName,
                            ChemicalID,
                            CasRN,
                            GeneSymbol,
                            GeneID,
                            GeneForms,
                            Organism,
                            OrganismID,
                            Interaction,
                            InteractionActions,
                            PubMedIDs
                        FROM chem_gene_ixns
                        {}
                        """.format(where)

            cur = connection.execute(query2, (cid,))

            for row in cur.fetchall():
                gene_id = row["GeneID"]
                if gene_id not in genes:
                    gene = self.add_element(row, gene_id)
                    gene_list.append(gene)
                    genes[gene_id] = gene
                gene = genes[gene_id]
                # add connection element here by calling add_connection function
                self.add_connections(row, gene, compound)
                genes_added += 1

        return gene_list

    # Creates element for genes
    def add_element(self, row, gene_id):
        # Set up identifiers
        identifiers = {}

        identifiers['entrez'] = self.add_prefix("entrez", str(gene_id))

        # Set up synonyms
        synonyms = []

        if "GeneName" in row.keys():
            names = Names(str(row["GeneName"]), synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)
        else:
            names = Names(str(row["GeneSymbol"]), synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)

        if "ChemicalForm" in row.keys():
            if row["ChemicalForm"] == "analog":
                return None

        Element()
        gene = Element(
            id=self.add_prefix("entrez", str(gene_id)),
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )
        self.get_element_attributes(row, gene)

        return gene

    def get_element_attributes(self, row, gene):
        if "GeneID" in row.keys():
            attributes_list = [
                'GeneSeqID',
                'OrganismID'
            ]
            for attribute in attributes_list:
                if attribute in row.keys():
                    if row[attribute] is not None and row[attribute] != '':

                        if attribute == 'OrganismID':
                            gene.attributes.append(Attribute(
                                attribute_type_id='biolink:OrganismTaxon',
                                original_attribute_name=attribute,
                                value="NCBITaxon:" + str(row[attribute]),
                                description=str(row['Organism']),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                        else:
                            gene.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value=str(row[attribute]),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )

    # Function to get connections
    def add_connections(self, row, gene, compound):
        if "ChemicalForm" in row.keys():
            if row["ChemicalForm"] == "analog":
                return None

        connection1 = Connection(
            source_element_id=compound.id,
            biolink_predicate=self.PREDICATE,
            inverse_predicate=self.INVERSE_PREDICATE,
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=[]
        )

        self.get_connections_attributes(row, connection1)
        gene.connections.append(connection1)

    def get_connections_attributes(self, row, connection1):
        if "GeneID" in row.keys():
            connection1.attributes.append(Attribute(
                attribute_type_id="biolink:primary_knowledge_source",
                original_attribute_name="primary_knowledge_source",
                value="infores:ctd",
                attribute_source="infores:molepro",
                provided_by=self.PROVIDED_BY
            ))

            if "ChemicalPosition" in row.keys():
                relations = ""
                value_list = str(row['AxnName']).split(';')
                for value in value_list:
                    relation = ''
                    if row["ChemicalForm"] is not None:
                        relation = relation + row["ChemicalForm"]
                    if relation != "" and relation[-1] != " ":
                        relation = relation + " "
                    if row["ChemicalFormQualifier"] is not None:
                        relation = relation + str(row["ChemicalFormQualifier"])
                    if relation != "" and relation[-1] != " ":
                        relation = relation + " "
                    if int(row['ChemicalPosition']) != 1:
                        where = "WHERE OriginalAxnName = ? collate nocase"
                        query = """
                                    SELECT DISTINCT
                                        OriginalAxnName,
                                        InverseAxnName
                                    FROM axn_name_inverses
                                    {}
                                    """.format(where)
                        cur = connection.execute(query, (value,))
                        for inverse_row in cur.fetchall():
                            relation = relation + inverse_row["InverseAxnName"]
                    else:
                        relation = relation + value
                    if relation[-1] == " ":
                        relation = relation[:-1]
                    if relations != "":
                        relations = relations + ";"
                    relations = relations + relation

                connection1.attributes.append(Attribute(
                    attribute_type_id="Relation",
                    original_attribute_name="Relation",
                    value=relations,
                    attribute_source=self.SOURCE,
                    provided_by=self.PROVIDED_BY
                )
                )

            attributes_list = [
                'GeneForms'
                'GeneForm',
                'GeneFormQualifier',
                'ReferencePMIDs',
                'Interaction',
                'InteractionActions',
                'PubMedIDs',
                'TaxonID'
            ]
            for attribute in attributes_list:
                if attribute in row.keys():
                    if row[attribute] is not None and row[attribute] != '':
                        if attribute == 'GeneForms' or attribute == 'InteractionActions':
                            for value in str(row[attribute]).split('|'):
                                connection1.attributes.append(Attribute(
                                    attribute_type_id=attribute,
                                    original_attribute_name=attribute,
                                    value=value,
                                    attribute_source=self.SOURCE,
                                    provided_by=self.PROVIDED_BY
                                )
                                )
                        if attribute == 'TaxonID':
                            value_list = str(row[attribute]).split('|')
                            description_list = str(row['TaxonName']).split('|')
                            for i, value in enumerate(value_list):
                                connection1.attributes.append(Attribute(
                                    attribute_type_id='biolink:OrganismTaxon',
                                    original_attribute_name=attribute,
                                    value='NCBITaxon:' + value,
                                    description=description_list[i],
                                    attribute_source=self.SOURCE,
                                    provided_by=self.PROVIDED_BY
                                )
                                )
                        elif attribute == 'PubMedIDs' or attribute == 'ReferencePMIDs':
                            value_list = str(row[attribute]).split('|')
                            for value in value_list:
                                connection1.attributes.append(Attribute(
                                    attribute_type_id=attribute,
                                    original_attribute_name=attribute,
                                    value="PMID:" + value,
                                    attribute_source=self.SOURCE,
                                    provided_by=self.PROVIDED_BY
                                )
                                )
                        else:
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value=str(row[attribute]),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )


class CtdDiseaseAssociationsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/disease_associations_transformer_info.json')

    def map(self, compound_list, controls):
        disease_list = []
        diseases = {}
        for compound in compound_list:
            if compound.identifiers.get('pubchem') is None:
                continue
            cid = self.de_prefix('pubchem', compound.identifiers.get('pubchem'), "compound")
            cid = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
            query = """
            SELECT DISTINCT
                DiseaseName,
                DiseaseID,
                DirectEvidence,
                InferenceGeneSymbol,
                InferenceScore,
                OmimIDs,
                PubMedIDs
            FROM chemicals_diseases
            {}
            """.format(where)
            diseases_added = 0
            cur = connection.execute(query, (cid,))

            for row in cur.fetchall():
                disease_id = row["DiseaseID"]
                if disease_id not in diseases:
                    disease = self.get_disease(row, disease_id)[0]
                    disease_list.append(disease)
                    diseases[disease_id] = disease
                disease = diseases[disease_id]
                # add connection element here by calling add_connection function
                self.add_connections(row, disease, compound)
                diseases_added += 1
        return disease_list

    def get_disease(self, row, disease_id):
        disease_list = []
        self.add_element(row, disease_id, disease_list)
        return disease_list

    def add_element(self, row, disease_id, disease_list):
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

        names = Names(name=str(row["DiseaseName"]), synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)

        Element()
        disease = Element(
            id=id,
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_element_attributes(row, disease)
        disease_list.append(disease)

    def get_element_attributes(self, row, disease):
        pass

    # Function to get connections
    def add_connections(self, row, disease, compound):
        connection1 = Connection(
            source_element_id=compound.id,
            biolink_predicate=self.PREDICATE,
            inverse_predicate=self.INVERSE_PREDICATE,
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=[]
        )

        self.get_connections_attributes(row, connection1)
        disease.connections.append(connection1)

    def get_connections_attributes(self, row, connection1):
        if "DirectEvidence" in row.keys():
            connection1.attributes.append(Attribute(
                attribute_type_id="biolink:primary_knowledge_source",
                original_attribute_name="primary_knowledge_source",
                value="infores:ctd",
                attribute_source="infores:molepro",
                provided_by=self.PROVIDED_BY
            ))
            attributes_list = [
                "DirectEvidence",
                "InferenceGeneSymbol",
                "InferenceScore",
                "OmimIDs",
                "PubMedIDs"]
            for attribute in attributes_list:
                if row[attribute] is not None and row[attribute] != '':
                    if attribute == "OmimIDs":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value="OMIM:" + str(value),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    elif attribute == "PubMedIDs":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value="PMID:" + str(value),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    else:
                        connection1.attributes.append(Attribute(
                            attribute_type_id=attribute,
                            original_attribute_name=attribute,
                            value=row[attribute],
                            attribute_source=self.SOURCE,
                            provided_by=self.PROVIDED_BY
                        )
                        )


class CtdGoAssociationsTransformer(Transformer):

    variables = ['limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/go_associations_transformer_info.json')

    def map(self, compound_list, controls):
        limit = float(controls['limit'])
        go_term_list = []
        go_terms = {}
        for compound in compound_list:
            if compound.identifiers.get('pubchem') is None:
                continue
            cid = self.de_prefix('pubchem', compound.identifiers.get('pubchem'), "compound")
            cid = "CID:" + cid
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
            WHERE PubChem_CID = ? collate nocase
            ORDER BY CorrectedPValue ASC;
            """
            go_terms_added = 0
            cur = connection.execute(query, (cid,))

            for row in cur.fetchall():
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

        identifiers['go'] = self.add_prefix("go", str(go_term_id), bl_class)

        # Set up synonyms
        synonyms = []

        names = Names(name=str(row["GOTermName"]), synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)

        Element()
        go_term = Element(
            id=self.add_prefix("go", str(go_term_id), bl_class),
            biolink_class=bl_class,
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_element_attributes(row, go_term)
        go_term_list.append(go_term)

    def get_element_attributes(self, row, go_term):
        if "GOTermName" in row.keys():
            attributes_list = [
                "Ontology",
                "HighestGOLevel"
            ]
            for attribute in attributes_list:
                if row[attribute] is not None and row[attribute] != '':
                    go_term.attributes.append(Attribute(
                        attribute_type_id=attribute,
                        original_attribute_name=attribute,
                        value=row[attribute],
                        attribute_source=self.SOURCE,
                        provided_by=self.PROVIDED_BY
                    )
                    )

    # Function to get connections
    def add_connections(self, row, go_term, compound):
        connection1 = Connection(
            source_element_id=compound.id,
            biolink_predicate=self.PREDICATE,
            inverse_predicate=self.INVERSE_PREDICATE,
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=[]
        )

        self.get_connections_attributes(row, connection1)
        go_term.connections.append(connection1)

    def get_connections_attributes(self, row, connection1):
        if "PValue" in row.keys():
            connection1.attributes.append(Attribute(
                attribute_type_id="biolink:primary_knowledge_source",
                original_attribute_name="primary_knowledge_source",
                value="infores:ctd",
                attribute_source="infores:molepro",
                provided_by=self.PROVIDED_BY
            ))
            attributes_list = [
                "PValue",
                "CorrectedPValue",
                "TargetMatchQty",
                "TargetTotalQty",
                "BackgroundMatchQty",
                "BackgroundTotalQty"
            ]
            for attribute in attributes_list:
                if row[attribute] is not None and row[attribute] != '':
                    connection1.attributes.append(Attribute(
                        attribute_type_id=attribute,
                        original_attribute_name=attribute,
                        value=row[attribute],
                        attribute_source=self.SOURCE,
                        provided_by=self.PROVIDED_BY
                    )
                    )


class CtdPathwayAssociationsTransformer(Transformer):

    variables = ['limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/pathway_associations_transformer_info.json')

    def map(self, compound_list, controls):
        limit = float(controls['limit'])
        pathway_list = []
        pathways = {}
        for compound in compound_list:
            if compound.identifiers.get('pubchem') is None:
                continue
            cid = self.de_prefix('pubchem', compound.identifiers.get('pubchem'), "compound")
            cid = "CID:" + cid
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
            WHERE PubChem_CID = ? collate nocase
            ORDER BY CorrectedPValue ASC;
            """
            pathways_added = 0
            cur = connection.execute(query, (cid,))

            for row in cur.fetchall():
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

        # Set up synonyms
        synonyms = []

        names = Names(name=str(row["PathwayName"]), synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)

        Element()
        pathway = Element(
            id=id,
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_element_attributes(row, pathway)
        pathway_list.append(pathway)

    def get_element_attributes(self, row, pathway):
        pass

    # Function to get connections
    def add_connections(self, row, pathway, compound):
        connection1 = Connection(
            source_element_id=compound.id,
            biolink_predicate=self.PREDICATE,
            inverse_predicate=self.INVERSE_PREDICATE,
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=[]
        )

        self.get_connections_attributes(row, connection1)
        pathway.connections.append(connection1)

    def get_connections_attributes(self, row, connection1):
        if "PValue" in row.keys():
            connection1.attributes.append(Attribute(
                attribute_type_id="biolink:primary_knowledge_source",
                original_attribute_name="primary_knowledge_source",
                value="infores:ctd",
                attribute_source="infores:molepro",
                provided_by=self.PROVIDED_BY
            ))
            attributes_list = [
                "PValue",
                "CorrectedPValue",
                "TargetMatchQty",
                "TargetTotalQty",
                "BackgroundMatchQty",
                "BackgroundTotalQty"
            ]
            for attribute in attributes_list:
                if row[attribute] is not None and row[attribute] != '':
                    connection1.attributes.append(Attribute(
                        attribute_type_id=attribute,
                        original_attribute_name=attribute,
                        value=row[attribute],
                        attribute_source=self.SOURCE,
                        provided_by=self.PROVIDED_BY
                    )
                    )


class CtdPhenotypeInteractionsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/phenotype_interactions_transformer_info.json')

    def map(self, compound_list, controls):
        phenotype_list = []
        phenotypes = {}
        for compound in compound_list:
            if compound.identifiers.get('pubchem') is None:
                continue
            cid = self.de_prefix('pubchem', compound.identifiers.get('pubchem'), "compound")
            cid = "CID:" + cid
            where = "WHERE PubChem_CID = ? collate nocase"
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
            phenotypes_added = 0
            cur = connection.execute(query, (cid,))

            for row in cur.fetchall():
                phenotype_id = row["phenotypeid"][3:]
                if phenotype_id not in phenotypes:
                    phenotype = self.get_phenotype(row, phenotype_id)[0]
                    phenotype_list.append(phenotype)
                    phenotypes[phenotype_id] = phenotype
                phenotype = phenotypes[phenotype_id]
                # add connection element here by calling add_connection function
                self.add_connections(row, phenotype, compound)
                phenotypes_added += 1
        return phenotype_list

    def get_phenotype(self, row, phenotype_id):
        phenotype_list = []
        self.add_element(row, phenotype_id, phenotype_list)
        return phenotype_list

    def add_element(self, row, phenotype_id, phenotype_list):
        # Set up identifiers
        identifiers = {}

        identifiers['go'] = self.add_prefix("go", str(phenotype_id))

        # Set up synonyms
        synonyms = []

        names = Names(name=str(row["phenotypename"]), synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)

        Element()
        phenotype = Element(
            id=self.add_prefix("go", str(phenotype_id)),
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_element_attributes(row, phenotype)
        phenotype_list.append(phenotype)

    def get_element_attributes(self, row, phenotype):
        pass

    # Function to get connections
    def add_connections(self, row, phenotype, compound):
        connection1 = Connection(
            source_element_id=compound.id,
            biolink_predicate=self.PREDICATE,
            inverse_predicate=self.INVERSE_PREDICATE,
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=[]
        )

        self.get_connections_attributes(row, connection1)
        phenotype.connections.append(connection1)

    def get_connections_attributes(self, row, connection1):
        if row["organismid"] is not None and row["organismid"] != '':
            connection1.attributes.append(Attribute(
                attribute_type_id="biolink:OrganismTaxon",
                original_attribute_name="organismid",
                value="NCBITaxon:" + str(row["organismid"]),
                description=str(row["organism"]),
                attribute_source=self.SOURCE,
                provided_by=self.PROVIDED_BY
            )
            )
        if "interaction" in row.keys():
            connection1.attributes.append(Attribute(
                attribute_type_id="biolink:primary_knowledge_source",
                original_attribute_name="primary_knowledge_source",
                value="infores:ctd",
                attribute_source="infores:molepro",
                provided_by=self.PROVIDED_BY
            ))
            attributes_list = [
                "comentionedterms",
                "interaction",
                "interactionactions",
                "anatomyterms",
                "inferencegenesymbols",
                "pubmedids"
            ]
            for attribute in attributes_list:
                if row[attribute] is not None and row[attribute] != '':
                    if attribute == "pubmedids":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value="PMID:" + value,
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
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
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value=item,
                                description=str(value_sublist[0]),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    elif attribute == "anatomyterms":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            value_sublist = value.split('^')
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value="MESH:" + str(value_sublist[2]),
                                description=str(value_sublist[1]),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    elif attribute == "interactionactions":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value=value,
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    elif attribute == "inferencegenesymbols":
                        value_list = str(row[attribute]).split('|')
                        for value in value_list:
                            value_sublist = value.split('^')
                            if value_sublist[2] == "GENE":
                                gene_id = self.add_prefix("entrez", str(value_sublist[1]), 'Gene')
                            else:
                                gene_id = value_sublist[2] + ":" + str(value_sublist[1])
                            connection1.attributes.append(Attribute(
                                attribute_type_id=attribute,
                                original_attribute_name=attribute,
                                value=gene_id,
                                description=value_sublist[0],
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    else:
                        connection1.attributes.append(Attribute(
                            attribute_type_id=attribute,
                            original_attribute_name=attribute,
                            value=str(row[attribute]),
                            attribute_source=self.SOURCE,
                            provided_by=self.PROVIDED_BY
                        )
                        )
