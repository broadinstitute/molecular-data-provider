from transformers.transformer import Transformer
from transformers.transformer import Producer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

import sqlite3
import re

SOURCE = 'ProbeMiner'
connection = sqlite3.connect("data/probeminer.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


class ProbeMinerCompoundProducer(Producer):

    variables = ['compounds']
    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

    def __init__(self):
        super().__init__(self.variables, definition_file='info/chemicals_transformer_info.json')

#   Invoked by Transformer.transform(query) method because "function":"producer" is specified in the openapi.yaml file
    def produce(self, controls):
        self.map = {}
        return super().produce(controls)

    def find_names(self, query_id):
        xref_prefixes = ['bindingdb', 'chembl', 'drugstore', 'pdb', 'pubchem', 'xchem']
        xref_prefixes_in_sqlite = ['BindingDB', 'ChEMBL', 'DrugStore', 'PDB', 'PubChem', 'XChem']
        if self.has_prefix("cansar", query_id, "compound") \
                and not self.de_prefix('cansar', query_id, "compound").startswith(('B','b')):
            rows = self.get_rows("WHERE COMPOUND_ID=?",
                                 self.de_prefix('cansar', query_id, "compound"), 'chemicals')
        elif self.has_prefix("cansar", query_id, "compound"):
            rows = self.get_rows("WHERE xref=? AND database=canSAR",
                                 self.de_prefix('cansar', query_id, "compound"), 'xrefs')
        elif self.inchikey_regex.match(query_id):
            rows = self.get_rows("WHERE inchi_key=?", query_id, 'chemicals')
        else:
            for i, xref_prefix in enumerate(xref_prefixes):
                if self.has_prefix(xref_prefix, query_id, "compound"):
                    rows = self.get_rows("WHERE xref=? AND database='"+str(xref_prefixes_in_sqlite[i])+"'",
                                         self.de_prefix(xref_prefix, query_id, "compound"), 'xrefs')
                    break
                else:  # This would be a compound name like acetylcarnitine
                    rows = self.get_rows("WHERE compound_name=? collate nocase", query_id, 'compound_names')

        id_list = []
        for row in rows:
            if str(row['inchi_key']) is not None and str(row['inchi_key']) != "":
                id = str(row['inchi_key'])
                if id not in self.map:
                    self.map[id] = row
                id_list.append(id)

        return id_list

    # Get the compound's synonyms (aliases) and attributes data
    def get_rows(self, where, name, table):
        rows = []
        query = """
                SELECT
                *
                FROM {} 
                {};
                """.format(table, where)
        cur = connection.execute(query, (name,))
        if table == 'chemicals':
            rows.extend(cur.fetchall())
        else:
            for row in cur.fetchall():
                name = row['COMPOUND_ID']
                where = "WHERE COMPOUND_ID=?"
                query = """
                        SELECT DISTINCT
                        *
                        FROM chemicals
                        {};
                        """.format(where)
                cur = connection.execute(query, (name,))
                rows.extend(cur.fetchall())
        return rows

    def get_attributes(self, row, element):
        attributes_list = \
            ['pains_free',
                'is_cell_potency',
                'no_celllines',
                'no_secondary',
                'no_targets',
                'no_celllines_active',
                'selectivity_comp3',
                'pains_text',
                'cell_potency',
                'uci',
                'chemical_probes_portal_identifier',
                'chemical_probes_portal_rating',
                'level1_scaffold']
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

        # find identifiers
        identifiers = {}
        if row['inchi_key'] is not None and row['inchi_key'] != "":
            identifiers['inchikey'] = self.add_prefix('inchikey', str(row['inchi_key']))
        if row['inchi'] is not None and row['inchi'] != "":
            identifiers['inchi'] = self.add_prefix('inchi', (str(row['inchi'])))
        if row['smiles'] is not None and row['smiles'] != "":
            identifiers['smiles'] = self.add_prefix('smiles', str(row['smiles']))
        if row['COMPOUND_ID'] is not None and row['COMPOUND_ID'] != "":
            identifiers['cansar'] = self.add_prefix('cansar', str(row['COMPOUND_ID']))
        query = """
                SELECT 
                *
                FROM xrefs 
                WHERE COMPOUND_ID=?;
                """
        cur = connection.execute(query, (row['COMPOUND_ID'],))

        xref_prefixes = ['bindingdb', 'chembl', 'drugstore', 'pdb', 'pubchem', 'xchem']
        xref_prefixes_in_sqlite = ['BindingDB', 'ChEMBL', 'DrugStore', 'PDB', 'PubChem', 'XChem']
        for xref_row in cur.fetchall():
            if xref_row['database'] in xref_prefixes_in_sqlite:
                i = xref_prefixes_in_sqlite.index(xref_row['database'])
                identifiers[xref_prefixes[i]] = self.add_prefix(xref_prefixes[i], str(xref_row['xref']))

        # find names
        query = """
                SELECT 
                *
                FROM compound_names 
                WHERE COMPOUND_ID=?;
                """
        cur = connection.execute(query, (row['COMPOUND_ID'],))

        list_of_names = []
        for name_row in cur.fetchall():
            list_of_names.append(name_row['compound_name'])
        if len(list_of_names) == 0:
            names_synonyms = []
        elif len(list_of_names) == 1:
            name = list_of_names[0]
            synonyms = list_of_names[1:]
            names_synonyms = [Names(name=name, synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)]
        else:
            name = None
            synonyms = list_of_names
            names_synonyms = [Names(name=name, synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)]

        element = Element(
            id=self.add_prefix('inchikey', str(row['inchi_key'])),
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=names_synonyms,
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_attributes(row, element)

        return element


# Input: compounds. Output: proteins.
class ProbeMinerChemicalInteractionsTransformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/chemical_interactions_transformer_info.json')

    def map(self, compound_list, controls):
        protein_list = []
        proteins = {}
        for compound in compound_list:
            if compound.identifiers.get('inchikey') is not None and compound.identifiers.get('inchikey') != '':
                inchikey = self.de_prefix('inchikey', compound.identifiers.get('inchikey'), "compound")
                query = """
                        SELECT DISTINCT
                        COMPOUND_ID
                        FROM chemicals 
                        WHERE inchi_key=?;
                        """
                cur = connection.execute(query, (inchikey,))
                row_list = cur.fetchall()
                if row_list == []:
                    continue
                for row in row_list:
                    cpd_id = row['COMPOUND_ID']
                    where = "WHERE COMPOUND_ID=?"
            elif compound.identifiers.get('cansar') is not None and compound.identifiers.get('cansar') != '':
                cpd_id = self.de_prefix('cansar', compound.identifiers.get('cansar'), "compound")
            else:
                continue
            query = """
                    SELECT DISTINCT
                        COMPOUND_ID,
                        UNIPROT_ACCESSION,
                        median_absolute_deviation,
                        selectivity_information_content,
                        selectivity,
                        sar_raw,
                        no_secondary_targets_unselective,
                        is_inactive_analogs,
                        is_target_potency,
                        active,
                        target_potency_raw,
                        is_sar,
                        no_secondary_targets,
                        suitable_probe,
                        auc,
                        selectivity_comp2,
                        selectivity_comp1,
                        target_potency,
                        global,
                        inactive_analogs_raw,
                        is_selectivity,
                        inactive_analogs,
                        no_secondary_targets_selective,
                        sar,
                        median_target_potency,
                        is_suitable_probe,
                        chemical_probes_portal_is_probe_for_this_target,
                        rank_global,
                        pubmed_ids
                    FROM interactions
                    WHERE COMPOUND_ID = ?
                    """
            proteins_added = 0
            cur = connection.execute(query, (cpd_id,))

            for row in cur.fetchall():
                protein_id = row["UNIPROT_ACCESSION"]
                if protein_id not in proteins:
                    protein = self.add_element(row, protein_id)
                    protein_list.append(protein)
                    proteins[protein_id] = protein
                protein = proteins[protein_id]
                self.add_connections(row, protein, compound)
                proteins_added += 1
        return protein_list

    def add_element(self, row, protein_id):
        identifiers = {}
        id = self.add_prefix("uniprot", str(protein_id))
        identifiers['uniprot'] = id

        Element()
        protein = Element(
            id=id,
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=[],
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_element_attributes(protein)
        return protein

    def get_element_attributes(self, protein):
        query = """
                SELECT DISTINCT
                auc_max,
                auc_min,
                sic_max,
                sic_min
                FROM proteins 
                WHERE UNIPROT_ACCESSION=?;
                """
        cur = connection.execute(query, (self.de_prefix('uniprot', protein.identifiers.get('uniprot'), "protein"),))
        for row in cur.fetchall():
            for attribute in row.keys():
                if row[attribute] is not None and row[attribute] != '':
                    protein.attributes.append(Attribute(
                        attribute_type_id=attribute,
                        original_attribute_name=attribute,
                        value=str(row[attribute]),
                        attribute_source=self.SOURCE,
                        provided_by=self.PROVIDED_BY
                    )
                    )

    # Function to get connections
    def add_connections(self, row, protein, compound):
        connection = Connection(
            source_element_id=compound.id,
            biolink_predicate=self.PREDICATE,
            inverse_predicate=self.INVERSE_PREDICATE,
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=[]
        )

        self.get_connection_attributes(row, connection)
        protein.connections.append(connection)

    def get_connection_attributes(self, row, connection):
        connection.attributes.append(Attribute(
            attribute_type_id="biolink:aggregator_knowledge_source",
            original_attribute_name="aggregator_knowledge_source",
            value="infores:probe-miner",
            value_type_id="biolink:InformationResource",
            value_url="https://probeminer.icr.ac.uk/#/",
            attribute_source="infores:molepro",
            provided_by=self.PROVIDED_BY
        ))
        for attribute in row.keys():
            if attribute != 'COMPOUND_ID' and attribute != 'UNIPROT_ACCESSION':
                if row[attribute] is not None and row[attribute] != '':
                    if attribute == "pubmed_ids":
                        value_list = str(row[attribute]).split(';')
                        for value in value_list:
                            connection.attributes.append(Attribute(
                                attribute_type_id='publication',
                                original_attribute_name=attribute,
                                value="PMID:" + str(value),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    elif attribute not in ['sar_raw', 'sar', 'is_sar', 'is_inactive_analogs',
                                           'inactive_analogs',
                                           'inactive_analogs_raw', 'target_potency', 'is_target_potency',
                                           'target_potency_raw', 'is_suitable_probe', 'suitable_probe']:
                        connection.attributes.append(Attribute(
                            attribute_type_id=attribute,
                            original_attribute_name=attribute,
                            value=str(row[attribute]),
                            attribute_source=self.SOURCE,
                            provided_by=self.PROVIDED_BY
                        )
                        )
        connection.attributes.append(self.create_attribute('is_suitable_probe', row))
        connection.attributes.append(self.create_attribute('is_sar', row, ['sar_raw']))
        connection.attributes.append(self.create_attribute('is_target_potency', row, ['target_potency',
                                                                                      'target_potency_raw']))
        connection.attributes.append(self.create_attribute('is_inactive_analogs', row, ['inactive_analogs',
                                                                                        'inactive_analogs_raw']))

    def create_attribute(self, attribute, row, nested_attribute_names=[]):
        nested_attributes = []
        for nested in nested_attribute_names:
            nested_attributes.append(self.create_attribute(nested, row))

        attr = Attribute(
            attribute_type_id=attribute,
            original_attribute_name=attribute,
            value=str(row[attribute]),
            attribute_source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=nested_attributes
        )

        return attr


# Input: proteins. Output: compounds.
class ProbeMinerProteinInteractionsTransformer(Transformer):

    variables = ['limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/protein_interactions_transformer_info.json')

    def map(self, protein_list, controls):
        limit = int(controls['limit'])
        compound_list = []
        compounds = {}
        for protein in protein_list:
            if protein.identifiers.get('uniprot') is not None:
                uniprot = self.de_prefix('uniprot', protein.identifiers.get('uniprot'), "protein")
            else:
                continue
            query = """
                        SELECT DISTINCT
                            COMPOUND_ID,
                            UNIPROT_ACCESSION,
                            median_absolute_deviation,
                            selectivity_information_content,
                            selectivity,
                            sar_raw,
                            no_secondary_targets_unselective,
                            is_inactive_analogs,
                            is_target_potency,
                            active,
                            target_potency_raw,
                            is_sar,
                            no_secondary_targets,
                            suitable_probe,
                            auc,
                            selectivity_comp2,
                            selectivity_comp1,
                            target_potency,
                            global,
                            inactive_analogs_raw,
                            is_selectivity,
                            inactive_analogs,
                            no_secondary_targets_selective,
                            sar,
                            median_target_potency,
                            is_suitable_probe,
                            chemical_probes_portal_is_probe_for_this_target,
                            rank_global,
                            pubmed_ids
                        FROM interactions
                        WHERE UNIPROT_ACCESSION = ?
                        """
            cur = connection.execute(query, (uniprot,))

            compounds_added = 0  # actually represents connections_added; could be fewer cpds than connections
            for row in cur.fetchall():
                if limit <= 0 or compounds_added < limit:
                    cpd_id = row["COMPOUND_ID"]
                    if cpd_id not in compounds:
                        compound = self.add_element(cpd_id)
                        compound_list.append(compound)
                        compounds[cpd_id] = compound
                    compound = compounds[cpd_id]
                    # add connection here by calling add_connection function
                    self.add_connections(row, compound, protein)
                    compounds_added += 1
        return compound_list

    def add_element(self, cpd_id):
        identifiers = {}
        where = "WHERE COMPOUND_ID=?"
        query = """
                SELECT DISTINCT
                *
                FROM chemicals
                {};
                """.format(where)
        cur = connection.execute(query, (cpd_id,))
        for row in cur.fetchall():
            if str(row['inchi_key']) is not None and str(row['inchi_key']) != "":
                id = self.add_prefix("inchikey", str(row['inchi_key']))
                identifiers['inchikey'] = id
                identifiers['cansar'] = self.add_prefix("cansar", cpd_id)
            else:
                id = self.add_prefix("cansar", cpd_id)
                identifiers['cansar'] = id
            identifiers['inchi'] = self.add_prefix('inchi', (str(row['inchi'])))
            identifiers['smiles'] = self.add_prefix('smiles', str(row['smiles']))

        where = "WHERE COMPOUND_ID=?"
        query = """
                SELECT DISTINCT
                database,
                xref
                FROM xrefs
                {};
                """.format(where)
        cur = connection.execute(query, (cpd_id,))
        xref_prefixes = ['bindingdb', 'chembl', 'drugstore', 'pdb', 'pubchem', 'xchem']
        xref_prefixes_in_sqlite = ['BindingDB', 'ChEMBL', 'DrugStore', 'PDB', 'PubChem', 'XChem']
        for xref_row in cur.fetchall():
            if xref_row['database'] in xref_prefixes_in_sqlite:
                i = xref_prefixes_in_sqlite.index(xref_row['database'])
                identifiers[xref_prefixes[i]] = self.add_prefix(xref_prefixes[i], str(xref_row['xref']))

        where = "WHERE COMPOUND_ID=?"
        query = """
                        SELECT
                        *
                        FROM compound_names
                        {};
                        """.format(where)
        cur = connection.execute(query, (cpd_id,))

        list_of_names = []
        for name_row in cur.fetchall():
            list_of_names.append(name_row['compound_name'])
        if len(list_of_names) == 0:
            names_synonyms = []
        elif len(list_of_names) == 1:
            name = list_of_names[0]
            synonyms = list_of_names[1:]
            names_synonyms = [Names(name=name, synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)]
        else:
            name = None
            synonyms = list_of_names
            names_synonyms = [Names(name=name, synonyms=synonyms, source=self.SOURCE, provided_by=self.PROVIDED_BY)]

        Element()
        compound = Element(
            id=id,
            biolink_class=self.biolink_class(self.OUTPUT_CLASS),
            identifiers=identifiers,
            names_synonyms=names_synonyms,
            attributes=[],
            connections=[],
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY
        )

        self.get_element_attributes(row, compound)
        return compound

    def get_element_attributes(self, row, compound):
        attribute_list = ['pains_free', 'pains_text', 'is_cell_potency', 'no_celllines', 'no_secondary',
                          'no_targets', 'no_celllines_active', 'selectivity_comp3', 'cell_potency', 'uci',
                          'chemical_probes_portal_identifier', 'chemical_probes_portal_rating', 'level1_scaffold']
        for attribute in attribute_list:
            if row[attribute] is not None and row[attribute] != '':
                compound.attributes.append(Attribute(
                    attribute_type_id=attribute,
                    original_attribute_name=attribute,
                    value=str(row[attribute]),
                    attribute_source=self.SOURCE,
                    provided_by=self.PROVIDED_BY
                )
                )

    def add_connections(self, row, compound, protein):
        connection = Connection(
            source_element_id=protein.id,
            biolink_predicate=self.PREDICATE,
            inverse_predicate=self.INVERSE_PREDICATE,
            source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=[]
        )

        self.get_connection_attributes(row, connection)
        compound.connections.append(connection)

    def get_connection_attributes(self, row, connection):
        # sar and is_sar, and suitable_probe and is_suitable_probe, are the same
        # sar_raw is different than sar
        # target_potency and is_target_potency are different, and there is a value in the former even when latter's 0
        # inactive_analogs and is_inactive_analogs are different, as is inactive_analogs_raw
        connection.attributes.append(Attribute(
            attribute_type_id="biolink:aggregator_knowledge_source",
            original_attribute_name="aggregator_knowledge_source",
            value="infores:probe-miner",
            value_type_id="biolink:InformationResource",
            value_url="https://probeminer.icr.ac.uk/#/",
            attribute_source="infores:molepro",
            provided_by=self.PROVIDED_BY
        ))
        for attribute in row.keys():
            if attribute != 'COMPOUND_ID' and attribute != 'UNIPROT_ACCESSION':
                if row[attribute] is not None and row[attribute] != '':
                    if attribute == "pubmed_ids":
                        value_list = str(row[attribute]).split(';')
                        for value in value_list:
                            connection.attributes.append(Attribute(
                                attribute_type_id='publication',
                                original_attribute_name=attribute,
                                value="PMID:" + str(value),
                                attribute_source=self.SOURCE,
                                provided_by=self.PROVIDED_BY
                            )
                            )
                    elif attribute not in ['sar_raw', 'sar', 'is_sar', 'is_inactive_analogs', 'inactive_analogs',
                                           'inactive_analogs_raw', 'target_potency', 'is_target_potency',
                                           'target_potency_raw', 'is_suitable_probe', 'suitable_probe']:
                        connection.attributes.append(Attribute(
                            attribute_type_id=attribute,
                            original_attribute_name=attribute,
                            value=str(row[attribute]),
                            attribute_source=self.SOURCE,
                            provided_by=self.PROVIDED_BY
                        )
                        )
        connection.attributes.append(self.create_attribute('is_suitable_probe', row))
        connection.attributes.append(self.create_attribute('is_sar', row, ['sar_raw']))
        connection.attributes.append(self.create_attribute('is_target_potency', row, ['target_potency',
                                                                                      'target_potency_raw']))
        connection.attributes.append(self.create_attribute('is_inactive_analogs', row, ['inactive_analogs',
                                                                                        'inactive_analogs_raw']))

    def create_attribute(self, attribute, row, nested_attribute_names=[]):
        nested_attributes = []
        for nested in nested_attribute_names:
            nested_attributes.append(self.create_attribute(nested, row))

        attr = Attribute(
            attribute_type_id=attribute,
            original_attribute_name=attribute,
            value=str(row[attribute]),
            attribute_source=self.SOURCE,
            provided_by=self.PROVIDED_BY,
            attributes=nested_attributes
        )

        return attr
