import connexion
import sqlite3
import requests
import re
from transformers.transformer import Transformer
from transformers.transformer import Producer
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection


SOURCE = 'DSSToxDB'
database_connection = sqlite3.connect("data/dsstoxDB.sqlite", check_same_thread=False)
database_connection.row_factory = sqlite3.Row

####################################################################################
# PRODUCER for handling:
# dtxsid
# preferred_name
# casrn
class DSSToxDB_ChemicalProducer(Producer):
    variables = ['compound']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/chemical_transformer_info.json')


    ###########################################################################
    # Called by Producer Base Class' produce() method
    # name
    #
    def find_names(self, name):
        ids = []
        self.find_compound(name, ids)
        return ids

    ###########################################################################
    # Called by Producer Base Class' produce() method
    #
    #    select id, name, source, parent_id, pharmgkb_accession,
    #    status, definition, star, modified_on, created_by
    def create_element(self, compound_id):
        identifiers = {}
        compound_name = None
        attribute_list = []
        for chemical_identifiers in self.get_identifiers(compound_id):
            if chemical_identifiers['dtxsid'] is not None:
                identifiers['comptox'] = 'comptox:' + chemical_identifiers['dtxsid']
            if chemical_identifiers['preferred_name'] is not None:
                compound_name = chemical_identifiers['preferred_name']
            if chemical_identifiers['casrn'] is not None:
                identifiers['cas'] = 'CAS:' + chemical_identifiers['casrn']
            if chemical_identifiers['inchikey'] is not None:
                identifiers['inchikey'] = chemical_identifiers['inchikey']
            if chemical_identifiers['iupac_name'] is not None:
                identifiers['iupac'] = chemical_identifiers['iupac_name']
            if chemical_identifiers['smiles'] is not None:
                identifiers['smiles'] = chemical_identifiers['smiles']
            if chemical_identifiers['unii'] is not None:
                identifiers['unii'] = 'UNII:' + chemical_identifiers['unii']   
            if chemical_identifiers['molecular_formula'] is not None:
                attribute_list.append(self.Attribute(
                    name = 'molecular_formula',
                    value = chemical_identifiers['molecular_formula'],
                    type = 'biolink:has_chemical_formula'
                ))
            if chemical_identifiers['average_mass'] is not None:
                attribute_list.append(self.Attribute(
                    name = 'average_mass',
                    value = chemical_identifiers['average_mass'],
                    type = 'average_mass'
                ))
            if chemical_identifiers['monoisotopic_mass'] is not None:
                attribute_list.append(self.Attribute(
                    name = 'monoisotopic_mass',
                    value = chemical_identifiers['monoisotopic_mass'],
                    type = 'monoisotopic_mass'
                ))
        # Gather the name & synonyms
        names_synonyms = self.get_synonyms(compound_name, compound_id)
        biolink_class = self.biolink_class('ChemicalEntity')
        element = self.Element(compound_id, biolink_class, identifiers, names_synonyms)
        self.get_attributes(compound_id, attribute_list, element)
        return element


    #################################################################
    #
    def get_synonyms(self, primary_name, compound_id):
        name_set = set()
        names_synonyms = []  # list of the element's various names & synonyms
        query = """
            SELECT name
            FROM SYNONYM
            WHERE dtxsid = ?
            AND name IS NOT NULL;
        """        
        cur = database_connection.cursor()
        cur.execute(query,(compound_id,))
        for row in cur.fetchall():
            name_set.add(row['name']) 
        names_synonyms.append(
        self.Names(
            name = primary_name,
            type = 'primary name',
            synonyms =  list(name_set) )
        ) 
        return names_synonyms


    #################################################################
    # Called by create_element() to retrieve:
    #     dtxsid, preferred_name, casrn, inchikey, iupac_name, smiles
    #     molecular_formula, unii, average_mass, monoisotopic_mass
    # 
    def get_identifiers(self, id):
        query = """
            SELECT dtxsid, preferred_name, casrn, inchikey, iupac_name, smiles,
            molecular_formula, unii, average_mass, monoisotopic_mass
            FROM IDENTIFIER
            WHERE dtxsid = ?
        """
        cur = database_connection.cursor()
        cur.execute(query,(id,))
        return cur.fetchall()


    ###########################################################################
    # 
    def find_compound_in_identifiers(self, name, where, ids):
        query_0 = """
            SELECT dtxsid, preferred_name, casrn, inchikey, iupac_name, smiles,
            molecular_formula, unii, average_mass, monoisotopic_mass
            FROM IDENTIFIER
            """
        query = query_0 + where
        cur = database_connection.cursor()
        cur.execute(query,(name,))
        for row in cur.fetchall():
            ids.append(row['dtxsid'])     
        

    ###########################################################################
    # Called by find_names() method to determine type of name submitted
    # in the query graph.
    def find_compound(self, name, ids):
        prefix = name.split(':')[0]
        if ':' in name:
            name = name.split(':')[1]
        where = None
        inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')
        if inchikey_regex.match(name) is not None:
            where = 'WHERE inchikey = ?'
        elif prefix == 'CAS':
            where = 'WHERE casrn = ?'
        elif 'DTXSID' in name:
            ids.append(name)
            return
        if where is not None:
            self.find_compound_in_identifiers(name, where, ids)
        else:
            self.find_compound_by_name(name, ids)


    #####################################################
    #  called by find_compound()
    # 
    def find_compound_by_name(self, name, ids):
        query = """
            SELECT DISTINCT dtxsid 
            FROM SYNONYM
            WHERE name = ?
        """
        cur = database_connection.cursor()
        cur.execute(query,(name,))
        for row in cur.fetchall():
            ids.append(row['dtxsid'])


      #####################################################
    #  called by create_element()
    # 
    def get_attributes(self, compound_id, attribute_list, element):

        element.attributes.extend(attribute_list)

        attribute = self.Attribute(
            name = 'comptox_url',
            value = 'https://comptox.epa.gov/dashboard/chemical/executive-summary/' + compound_id,
            type = 'biolink:url'
        )
        element.attributes.append(attribute)
