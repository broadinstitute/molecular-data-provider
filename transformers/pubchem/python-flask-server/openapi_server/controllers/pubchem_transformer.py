import sqlite3
import requests
import re
from contextlib import closing
from time import sleep

import xml.etree.ElementTree as ET

from transformers.transformer import Transformer

X_Throttling_Control = 0


def x_throttling_control(response_obj):
    global X_Throttling_Control
    try:
        header = response_obj.headers['X-Throttling-Control']
        max_percent = 10
        status = header.split(',')
        max_percent = max(max_percent, percent(status[0]))
        max_percent = max(max_percent, percent(status[1]))
        max_percent = max(max_percent, percent(status[2])/10.0)
        X_Throttling_Control = max_percent * 0.01
        if max_percent > 50:
            print(header)
            X_Throttling_Control = X_Throttling_Control + (max_percent-50) * 0.02
    except:
        pass


def percent(status):
    percent = status.split('(')[1]
    percent = percent.split('%')[0]
    return int(percent)

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


connection = sqlite3.connect("database/PubChem.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


class PubChemProducer(Transformer):

    variables = ['compound']


    def __init__(self, definition_file='info/transformer_info.json'):
        super().__init__(self.variables, definition_file=definition_file)
        self.synonym_types = self.get_synonym_types()


    def produce(self, controls):
        compound_list = []
        compounds = {}
        for name in controls['compound']:
            for cid in self.find_compound(name):
                if cid not in compounds:
                    compound = self.get_compound(cid)
                    if compound is not None:
                        id = self.de_prefix('pubchem', compound.id, 'compound')
                        if id not in compounds:
                            compounds[id]=compound
                            compound_list.append(compound)
                        compounds[cid]=compound
                if cid in compounds:
                    compound = compounds[cid]
                    compound.attributes.append(
                        self.Attribute(name='query name', value=name, type='')
                    )
        return compound_list


    def find_compound(self, name):
        # by CID
        if self.has_prefix('pubchem', name, 'compound'):
            return [self.de_prefix('pubchem', name, 'compound')]
        if (name.startswith('PUBCHEM.COMPOUND:')):
            return [name[17:]]
        # by InChIKey
        if inchikey_regex.match(name) is not None:
            return self.find_compound_by_inchikey_db(name)
        #by name
        cids = self.find_compound_by_title_db(name)
        if len(cids) == 0:
            cids = self.find_compounds_by_synonym_db(name)
        if len(cids) == 0:
            try:
                cids = self.find_compound_api(name)
                for cid in cids:
                    print("INFO: name API " + str(cid))
            except:
                print("WARN: API query failed :" + str(name))
        return cids


    def get_compound(self, cid):
        element = self.get_compound_db(cid)
        if element is None:
            preferred_cid = self.find_preferred_cid(cid)
            if preferred_cid is not None:
                element = self.get_compound_db(preferred_cid)
                cid = preferred_cid
            else:
                return self.get_compound_api(cid)
        if element is not None:
            self.add_synonyms_db(cid, element)
        return element


    def find_compound_api(self, name):
        if (name.startswith('CID:')):
            return [name[4:]]
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/cids/JSON'
        query = 'name='+name
        with closing(requests.post(url, data=query)) as response_obj:
            x_throttling_control(response_obj)
            sleep(X_Throttling_Control) # PubChem only allows 5 requests per second
            response = response_obj.json()
            if 'IdentifierList' in response:
                if 'CID' in response['IdentifierList']:
                    return response['IdentifierList']['CID']
            return []


    def get_compound_api(self, cid):
        try:
            identifiers = self.get_structure_api(cid)
            if identifiers is not None:
                print("INFO: API " + str(cid))
                title = self.get_title_api(cid)
                synonyms = self.get_synonyms_api(cid)
                element = self.Element(
                    id = self.add_prefix('pubchem', str(cid)),
                    biolink_class = 'ChemicalSubstance',
                    identifiers = identifiers,
                    names_synonyms=[self.Names(name=title,synonyms=synonyms)],
                    attributes=[]
                )
                return element
            print("WARN: not found via API " + str(cid))
        except:
            print("WARN: API query failed CID: " + str(cid))
        return None


    def get_structure_api(self, cid):
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/property/IsomericSMILES,InChI,InChIKey/JSON'
        url = url.format(cid)
        with closing(requests.get(url)) as response_obj:
            x_throttling_control(response_obj)
            sleep(X_Throttling_Control) # PubChem only allows 5 requests per second
            response = response_obj.json()
            if 'PropertyTable' in response:
                if 'Properties' in response['PropertyTable']:
                    for property in response['PropertyTable']['Properties']:
                        if str(cid) == str(property.get('CID')):
                            identifiers = {
                                'pubchem': self.add_prefix('pubchem', str(cid)),
                                'inchi': property['InChI'],
                                'inchikey': property['InChIKey'],
                                'smiles': property['IsomericSMILES']
                            }
                            return identifiers
        return None


    def get_title_api(self, cid):
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/description/JSON'
        url = url.format(cid)
        with closing(requests.get(url)) as response_obj:
            x_throttling_control(response_obj)
            sleep(X_Throttling_Control) # PubChem only allows 5 requests per second
            response = response_obj.json()
            if 'InformationList' in response:
                if 'Information' in response['InformationList']:
                    for description in response['InformationList']['Information']:
                        if 'Title' in description:
                            return description['Title']
        title = self.add_prefix('pubchem', str(cid))
        return title


    def get_synonyms_api(self,cid):
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/synonyms/JSON'
        url = url.format(cid)
        with closing(requests.get(url)) as response_obj:
            x_throttling_control(response_obj)
            sleep(X_Throttling_Control) # PubChem only allows 5 requests per second
            response = response_obj.json()
            if 'InformationList' in response:
                if 'Information' in response['InformationList']:
                    for synonyms in response['InformationList']['Information']:
                        if 'Synonym' in synonyms:
                            return synonyms['Synonym']
        return []


    def find_compound_by_inchikey_db(self, inchikey):
        where = ' WHERE STANDARD_INCHIKEY = ?'
        return self.find_compound_db('COMPOUND', where, inchikey)
        

    def find_compound_by_title_db(self, title):
        where = ' WHERE TITLE = ? COLLATE NOCASE'
        return self.find_compound_db('COMPOUND', where, title)
        

    def find_compounds_by_synonym_db(self, synonym):
        where = ' WHERE SYNONYM = ? COLLATE NOCASE'
        return self.find_compound_db('SYNONYM', where, synonym)


    def find_compound_db(self, table, where, name):
        cids = []
        query = 'SELECT DISTINCT CID FROM ' + table + where
        cur = connection.cursor()
        cur.execute(query,(name,))
        for row in cur.fetchall():
            cids.append(row['CID'])
        return cids


    def find_preferred_cid(self, retired_cid):
        query = """
        SELECT PREFERRED_CID 
        FROM PREFERRED 
        WHERE RETIRED_CID = ?
        """
        cur = connection.cursor()
        preferred_cid = None
        cur.execute(query,(retired_cid,))
        for row in cur.fetchall():
            preferred_cid = row['PREFERRED_CID']
        return preferred_cid


    attribute_names = ['HBA_COUNT', 'HBD_COUNT', 'ROTATABLE_BOND_COUNT', 'PSA',
                'MONOISOTOPIC_WEIGHT', 'MOLECULAR_WEIGHT', 'MOLECULAR_FORMULA']

    def get_compound_db(self, cid):
        element = None
        query = """
            SELECT 
                TITLE, 
                HBA_COUNT,
                HBD_COUNT,
                ROTATABLE_BOND_COUNT,
                PSA,
                MONOISOTOPIC_WEIGHT,
                MOLECULAR_WEIGHT,
                MOLECULAR_FORMULA,
                PREFERRED_IUPAC_NAME,
                STANDARD_INCHI,
                STANDARD_INCHIKEY,
                ISOMERIC_SMILES
            FROM COMPOUND
            WHERE CID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(cid,))
        for row in cur.fetchall():
            id = self.add_prefix('pubchem', str(cid))
            title = row['TITLE']
            iupac_name = row['PREFERRED_IUPAC_NAME']
            if title is None:
                title = id
            identifiers = {
                'pubchem': id,
                'inchi': row['STANDARD_INCHI'],
                'inchikey': row['STANDARD_INCHIKEY'],
                'smiles': row['ISOMERIC_SMILES']
            }
            attributes = []
            for attr_name in self.attribute_names:
                attr_value = row[attr_name]
                if attr_value is not None:
                    attributes.append(self.Attribute(attr_name, str(attr_value)))
            element = self.Element(
                id = id,
                biolink_class = 'ChemicalSubstance',
                identifiers = identifiers,
                names_synonyms = [
                    self.Names(name=title, synonyms=[], type = ''),
                    self.Names(name=iupac_name, synonyms=[], type='IUPAC'),
                ],
                attributes = attributes
            )
        return element


    synonym_type_map = { #len == 1 => name/synonym; len == 2 => identifier
        'sio:CHEMINF_000339': ['depositor'],	
        'sio:CHEMINF_000382': ['IUPAC'],
        'sio:CHEMINF_000447': ['IENECS'],
        'sio:CHEMINF_000467': ['identifier'],
        'sio:CHEMINF_000562': ['INN'],
        'sio:CHEMINF_000565': ['NCS'],
        'sio:CHEMINF_000109': [''],
        'sio:CHEMINF_000566': ['RTECS'],
        'sio:CHEMINF_000561': ['tradeName'],
        'sio:CHEMINF_000446': ['cas','CAS:'],
        'sio:CHEMINF_000409': ['kegg','KEGG.COMPOUND:'],
        'sio:CHEMINF_000563': ['unii','UNII:'],
        'sio:CHEMINF_000407': ['chebi','CHEBI:'],
        'sio:CHEMINF_000412': ['chembl','ChEMBL:'],
        'sio:CHEMINF_000406': ['drugbank','DrugBank:'],
        'sio:CHEMINF_000564': ['lipidmaps','LIPIDMAPS:'],
        'pubchem-retired':    ['pubchem-retired','CID:']
    }


    def get_synonym_types(self):
        synonym_types = []
        query = "SELECT SYNONYM_TYPE_ID, SYNONYM_TYPE FROM SYNONYM_TYPE"
        cur = connection.cursor()
        cur.execute(query)
        for row in cur.fetchall():
            index = row['SYNONYM_TYPE_ID']
            if len(synonym_types) <= index:
                synonym_types.extend([None]*(index-len(synonym_types)+1))
            synonym_types[index] = self.synonym_type_map.get(row['SYNONYM_TYPE'])
        print('Loaded ' + str(len(synonym_types)) + ' synonym types')
        return synonym_types


    def add_synonyms_db(self, cid, element):
        query = """
            SELECT SYNONYM_TYPE_ID, SYNONYM
            FROM SYNONYM
            WHERE CID = ?
        """
        cur = connection.cursor()
        cur.execute(query,(cid,))
        synonyms_by_type = {names.name_type: names for names in element.names_synonyms}
        for row in cur.fetchall():
            synonym_type_id = row['SYNONYM_TYPE_ID']
            if len(self.synonym_types[synonym_type_id]) == 1: # name
                name_type = self.synonym_types[synonym_type_id][0]
                synonym = row['SYNONYM']
                if name_type not in synonyms_by_type:
                    names = self.Names(name=synonym, synonyms=[], type=name_type)
                    element.names_synonyms.append(names)
                    synonyms_by_type[name_type] = names
                else:
                    synonyms = synonyms_by_type[name_type].synonyms
                    if name_type != '' and len(synonyms) == 0:
                        synonyms.append(synonyms_by_type[name_type].name)
                        synonyms_by_type[name_type].name = None
                    synonyms.append(synonym)
            if len(self.synonym_types[synonym_type_id]) == 2: # id
                key = self.synonym_types[synonym_type_id][0]
                prefix = self.synonym_types[synonym_type_id][1]
                id = row['SYNONYM']
                if id.upper().startswith(prefix.upper()):
                    id = id[len(prefix):]
                if key == 'cas' and id.lower().startswith('cas-'):
                    id = id[4:]
                if id == self.add_prefix(key, id):
                    id = prefix + id.upper()
                else:
                    id = self.add_prefix(key, id)
                if key not in element.identifiers:
                    element.identifiers[key] = id
                else:
                    prev_ids = element.identifiers[key]
                    if type(prev_ids) == list:
                        prev_ids.append(id)
                    else:
                        prev_ids = [prev_ids, id]

class PubChemSimilarityTransformer(PubChemProducer):

    variables = []


    def __init__(self):
        super().__init__(definition_file='info/neighbors_transformer_info.json')


    def map(self, collection, controls):
        compound_list = []
        compounds = {}
        for compound in collection:
            for neighbor_cid in self.get_neighbors(compound):
                if neighbor_cid not in compounds:
                    neighbor = self.get_compound(neighbor_cid)
                    if neighbor is not None:
                        compound_list.append(neighbor)
                        compounds[neighbor_cid] = neighbor
                neighbor = compounds[neighbor_cid]
                if neighbor is not None:
                    neighbor.connections.append(self.get_connection(compound.id))
                # print(neighbor)
        return compound_list
        

    def get_neighbors(self, compound):
        neighbors = []
        if compound.identifiers.get('pubchem') is not None:
            for cid1 in self.find_compound(compound.identifiers.get('pubchem')):
                neighbors.extend(self.find_neighbors(cid1))
        return neighbors


    def find_neighbors(self, cid1):
        query = """
        SELECT CID2
        FROM NEIGHBOR 
        WHERE CID1 = ?
        """
        cur = connection.cursor()
        cur.execute(query, (int(cid1),))
        return [row['CID2'] for row in cur.fetchall()]


    def get_connection(self, source_element_id):
        attributes = [self.Attribute('biolink:original_knowledge_source','infores:pubchem', value_type='biolink:InformationResource')]
        return self.Connection(source_element_id, self.PREDICATE, self.INVERSE_PREDICATE, attributes = attributes)
