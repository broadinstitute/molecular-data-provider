from transformers.transformer import Transformer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

import sqlite3
import re

connection = sqlite3.connect("data/STITCH.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row
inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')
SOURCE = "STITCH"

class StitchProducer(Transformer):

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
            name = name.upper()
            if name.startswith("CIDM"):
                compound_list.extend(self.get_compound_by_cidm(name))
            elif name.startswith("CIDS") or name.startswith("CID:"):
                compound_list.extend(self.get_compound_by_cids(name))
            elif inchikey_regex.match(name) is not None:
                compound_list.extend(self.get_compound_by_inchikey(name))
            else:  # This would be a compound name like acetylcarnitine
                compound_list.extend(self.find_compound_by_name(name))
        return compound_list

    # Get compound query (to plug in where clause from cid, ligand id, and inchikey functions)
    def get_compound(self, where, name):
        compounds = []
        query1 = """
                SELECT DISTINCT
                    name, 
                    source_cid,
                    molecular_weight, 
                    SMILES_string, 
                    flat_chemical_id, 
                    stereo_chemical_id,
                    inchikey 
                FROM chemical_data INNER JOIN chemicals_inchikeys 
                ON chemical = stereo_chemical_id
                {}
                """.format(where)
        cur = connection.execute(query1, (name,))
        for row in cur.fetchall():
            stereo = row['stereo_chemical_id'][4:]
            stereo = int(stereo)
            source = int(row['source_cid'])
            if stereo == source:
                self.add_element(row, compounds)
        return compounds

    # Get compound by cid
    def get_compound_by_cidm(self, name):
        # Ensure that 'name' has the leading zeros expected by the database
        if len(name) < 12:
            zeros_to_add = 12 - len(name)
            name = name[:4] + ('0' * zeros_to_add) + name[4:]
        where = "WHERE flat_chemical_id = ?"
        return self.get_compound(where, name)

    def get_compound_by_cids(self, name):
        if name.startswith("CID:"):
            name = "CIDs" + name[4:]
        #Ensure that 'name' has the leading zeros expected by the database
        if len(name) < 12:
            zeros_to_add = 12 - len(name)
            name = name[:4] + ('0' * zeros_to_add) + name[4:]
        where = "WHERE stereo_chemical_id = ?"
        return self.get_compound(where, name)

    # Get compound by inchikey
    def get_compound_by_inchikey(self, name):
        where = "WHERE inchikey=?"
        return self.get_compound(where, name)

#   Get the compound's synonyms (aliases) and attributes data
    def find_compound_by_name(self, name):
        compounds = []
        query1 = """
                SELECT DISTINCT
                name,
                source_cid, 
                molecular_weight, 
                SMILES_string, 
                flat_chemical_id, 
                stereo_chemical_id,
                inchikey 
                FROM chemical_data INNER JOIN chemicals_inchikeys 
                ON chemical = stereo_chemical_id
                WHERE name = ?;
                """
        cur = connection.execute(query1, (name,))
        for row in cur.fetchall():
            stereo = row['stereo_chemical_id'][4:]
            stereo = int(stereo)
            source = int(row['source_cid'])
            if stereo == source:
                self.add_element(row, compounds)
        return compounds

    def add_element(self, row, compounds):
        # Set up identifiers
        identifiers = {}
        if row['SMILES_string'] is not None and row['SMILES_string'] != '':
            identifiers['smiles'] = str(row['SMILES_string'])
        if row['stereo_chemical_id'] is not None and row['stereo_chemical_id'] != '':
            cids_digits_as_int = int(str(row['stereo_chemical_id'])[4:])
            cids_digits_as_short_str = str(cids_digits_as_int)
            identifiers['pubchem'] = "CID:" + cids_digits_as_short_str
        if row['inchikey'] is not None and row['inchikey'] != '':
            identifiers['inchikey'] = str(row['inchikey'])

        name = row['name']
        synonyms = []
        names = Names(name=name, synonyms=synonyms, source=SOURCE)

        compound = Element(
            id=str(row['STEREO_CHEMICAL_ID']),
            biolink_class='ChemicalSubstance',
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.info.name
        )
        self.get_attributes(row, compound)
        compounds.append(compound)

    def get_attributes (self,row,compound):
        attributes_list = ['molecular_weight']
        for attribute in attributes_list:
            if row[attribute] is not None and row[attribute] != '':
                compound.attributes.append(Attribute(
                    name=attribute,
                    value=str(row[attribute]),
                    provided_by=self.info.name,
                    type=attribute,
                    source=self.info.label
                )
                )

class StitchLinksTransformer(Transformer):

    variables = ['score_threshold', 'limit']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/links_transformer_info.json')

    # Takes a compound and returns a pubchemCID
    def get_pubchemCID(self, compound):
        cid= compound.identifiers['pubchem']
        if cid.startswith('CID:'):
            cid=cid[4:]
        return cid

    def map(self, compound_list, controls):
        min_score = str(controls['score_threshold'])
        limit = float(controls['limit'])
        #Find targets by compound names
        protein_list = []
        proteins = {}
        for compound in compound_list:
            if compound.identifiers['pubchem'] is not None:
                cid_without_leading_zeros = self.get_pubchemCID(compound)
                cid = "CIDs" + "0" * (8 - len(cid_without_leading_zeros)) + cid_without_leading_zeros
                query = """
                SELECT DISTINCT
                    chemical,
                    protein,
                    experimental_direct,
                    experimental_transferred,
                    prediction_direct,
                    prediction_transferred,
                    database_direct,
                    database_transferred,
                    textmining_direct,
                    textmining_transferred,
                    combined_score
                FROM protein_chemical_links_transfer 
                WHERE chemical = ? AND combined_score >= ?
                ORDER BY combined_score DESC;
                """
                proteins_added = 0
                cur = connection.execute(query, (cid,min_score))
                for row in cur.fetchall():
                    if proteins_added < limit:
                        protein_id = "ENSEMBL:" + row["protein"][9:]
                        if protein_id not in proteins:
                            protein = self.get_protein(protein_id)[0]
                            protein_list.append(protein)
                            proteins[protein_id] = protein
                        #else: protein = proteins[protein_id]
                        protein = proteins[protein_id]
                        # add connection element here by calling add_connection function
                        self.add_connections(row, protein, compound)
                        proteins_added += 1
        return protein_list

    # Gets information about target from target id and creates element and adds to gene_list
    def get_protein(self,protein_id):
        protein_list=[]
        self.add_element(protein_id, protein_list)
        return protein_list

    # Creates element for proteins
    def add_element(self, protein_id, protein_list):
        # Set up identifiers
        identifiers = {}
        # Add only if HGNC_ID is present (human target)
        identifiers['ensembl'] = protein_id

        #Set up synonyms
        synonyms = []

        names = Names(name=protein_id, synonyms=synonyms, source=SOURCE)

        Element()
        protein = Element(
            id=protein_id,
            biolink_class='Protein',
            identifiers=identifiers,
            names_synonyms=[names],
            attributes=[],
            connections=[],
            source=self.info.name
        )
        self.get_element_attributes(protein)

        protein_list.append(protein)

    def get_element_attributes(self,protein):
        pass

    # Function to get connections
    def add_connections(self, row, protein, compound):
        connection1 = Connection(
            source_element_id=compound.id,
            type=self.info.knowledge_map.predicates[0].predicate,
            attributes=[]
        )

        self.get_connections_attributes(row, connection1)
        protein.connections.append(connection1)

    # Function to get attributes from remaining characteristics in Interactions table (currently appending attributes to
    # element object). Also queries the Action table.
    def get_connections_attributes (self,row,connection1):
        attributes_list= ['experimental_direct', 'experimental_transferred', 'prediction_direct',
            'prediction_transferred', 'database_direct', 'database_transferred', 'textmining_direct',
            'textmining_transferred', 'combined_score']
        for attribute in attributes_list:
            if row[attribute] is not None and row[attribute] != '':
                connection1.attributes.append(Attribute(
                    name=attribute,
                    value=row[attribute],
                    provided_by=self.info.name,
                    type=attribute,
                    source=SOURCE
                )
                )
        query = """
        SELECT DISTINCT
            item_id_a,
            item_id_b,
            a_is_acting,
            mode,
            action,
            score
        FROM actions
        WHERE (item_id_a = ? AND item_id_b = ?) OR (item_id_a = ? AND item_id_b = ?);
        """
        chem_name = row['chemical']
        prot_name = row['protein']
        cur = connection.execute(query, (chem_name, prot_name, prot_name, chem_name))
        for actions_row in cur.fetchall():
            prot_is_item_a = actions_row['item_id_a'].startswith('9606')
            item_a_is_acting = actions_row['a_is_acting'].startswith('t')
            prot_is_acting = (prot_is_item_a == item_a_is_acting)
            connection1.attributes.append(Attribute(
                name='protein_is_acting',
                value=prot_is_acting,
                provided_by=self.info.name,
                type='protein_is_acting',
                source=SOURCE
            )
            )
            attributes_list = ['mode', 'action', 'score']
            for attribute in attributes_list:
                if actions_row[attribute] is not None and actions_row[attribute] != '':
                    connection1.attributes.append(Attribute(
                        name=attribute,
                        value=actions_row[attribute],
                        provided_by=self.info.name,
                        type=attribute,
                        source=SOURCE
                    )
                    )
