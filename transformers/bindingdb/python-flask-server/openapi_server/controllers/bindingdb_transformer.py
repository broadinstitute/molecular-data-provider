import sqlite3
import re
from collections import defaultdict

from transformers.transformer import Transformer, Producer
from openapi_server.models.element import Element

connection = sqlite3.connect("data/BindingDB.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

class BindingDbLigandProducer(Producer):

    variables = ['ligand']

    def __init__(self, definition_file='info/ligands_transformer_info.json'):
        super().__init__(self.variables, definition_file)


    def find_names(self, name):
        if self.has_prefix('bindingdb', name, self.OUTPUT_CLASS):
            ligand_id = self.de_prefix('bindingdb', name, self.OUTPUT_CLASS)
            if ligand_id.startswith('BDBM'):
                ligand_id = ligand_id[4:]
            return find_ligand_by_id(ligand_id)
        elif inchikey_regex.match(name) is not None:
            return find_ligand_by_inchikey(name)
        else:
            return find_ligand_by_name(name)


    id_map = {
        'smiles':'SMILES',
        'inchi':'InChI',
        'inchikey':'InChI_Key',
        'pubchem':'PubChem_CID',
        'pubchem-sid':'PubChem_SID',
        'chebi':'ChEBI_ID',
        'chembl':'ChEMBL_ID',
        'drugbank':'DrugBank_ID',
        'kegg':'KEGG_ID',
    }


    def create_element(self, ligand_id):
        id = self.add_prefix('bindingdb', ligand_id)
        row = get_ligand(ligand_id)
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)
        identifiers = {'bindingdb': id}
        for fieldname in self.id_map.keys():
            column_name = self.id_map[fieldname]
            if row[column_name] is not None and row[column_name]:
                identifiers[fieldname] = self.add_prefix(fieldname, row[column_name])
        names = self.get_names(ligand_id)
        attributes = [self.Attribute('Ligand_Link', row['Ligand_Link'], type='biolink:url', value_type='biolink:URI', url=row['Ligand_Link'])]
        element = self.Element(id, biolink_class, identifiers, names_synonyms=names, attributes=attributes)
        return element


    def get_names(self, ligand_id):
        names = get_ligand_names(ligand_id)
        if len(names) > 0:
            name = names[0]
            synonyms = names[1:]
            return [self.Names(name, synonyms)]
        return []


TARGET_CHAINS = 'TARGET_CHAINS'
TARGET_NAME = 'TARGET_NAME'
TARGET_URL = 'TARGET_URL'
TARGET_ORGANISM = 'TARGET_ORGANISM'

class BindingDbTransformer(Transformer):

    variables = ['threshold']

    def __init__(self, definition_file='info/bindings_transformer_info.json'):
        super().__init__(self.variables, definition_file)


    Curation_DataSources = {
        'Curated from the literature by BindingDB': 'infores:bindingdb',
        'US Patent': 'infores:bindingdb',
        'PubChem': 'infores:pubchem',
        'PDSP Ki': 'infores:ki-database',
        'Taylor Research Group, UCSD': 'infores:bindingdb',
        'CSAR': 'infores:community-sar',
        'D3R': 'infores:drug-design',
        'ChEMBL': 'infores:chembl',
    }


    attr_prefix_map = {
        'PMID': 'PMID:',
        'Article_DOI': 'doi:'
    }


    attr_type_map = {
        'Authors': 'biolink:authors',
        'PMID': 'biolink:Publication',
        'Article_DOI': 'biolink:Publication'
    }


    def map(self, compound_list, controls):
        target_list = []
        targets = {}
        for compound in compound_list:
            connections = {}
            for ligand_id in self.find_ligand_ids(compound):
                for row in find_bindings(ligand_id):
                    target_id = row['Target_ID']
                    if target_id not in targets:
                        target = self.get_target(target_id)
                        targets[target_id] = target
                        target_list.extend(target.get(TARGET_CHAINS))
                    complex = self.get_complex(targets[target_id])
                    for target_element in targets[target_id][TARGET_CHAINS]:
                        self.add_connection(compound.id, row, target_element, complex, connections, float(controls['threshold']))
        return [target for target in target_list if len(target.connections) > 0]


    def find_ligand_ids(self, compound):
        identifiers = self.get_identifiers(compound, 'bindingdb')
        if len(identifiers) > 0:
            ligand_ids = []
            for id in identifiers:
                ligand_ids.extend(find_ligand_by_id(id))
            if len(ligand_ids) > 0:
                return ligand_ids
        identifiers = self.get_identifiers(compound, 'inchikey')
        for id in identifiers:
            ligand_ids = []
            if inchikey_regex.match(id):
                ligand_ids.extend(find_ligand_by_inchikey(id))
            return ligand_ids
        return []


    def get_identifiers(self, compound: Element, field_name: str, de_prefix = True):
        if field_name in compound.identifiers and compound.identifiers[field_name] is not None:
            identifiers = compound.identifiers[field_name]
            if isinstance(identifiers, str):
                identifiers = [identifiers]
            if isinstance(identifiers, list):
                if de_prefix:
                    identifiers = [self.de_prefix(field_name, id) for id in identifiers]
                return [id for id in identifiers if id is not None]
        return []


    def get_target(self, target_id):
        target = {}
        elements = []
        for row in find_target(target_id):
            target[TARGET_NAME] = row['Target_Name']
            target[TARGET_URL] = row['Target_Link']
            uniprot_id = row['UniProt_ID'] if row['UniProt_ID'] is not None else row['TrEMBL_ID']
            if uniprot_id is not None:
                uniprot_id = self.add_prefix('uniprot', uniprot_id, 'Protein')
                names = []
                if row['UniProt_Name'] is not None and row['UniProt_Name'] != '':
                    uniprot_name = self.Names(row['UniProt_Name'], name_source='infores:uniprot')
                    names.append(uniprot_name)
                identifiers = {'uniprot': uniprot_id}
                attributes = []
                if row['Sequence'] is not None and row['Sequence'] != '':
                    seq_attribute = self.Attribute('BindingDB Target Chain  Sequence', row['Sequence'], 'biolink:has_biological_sequence')
                    attributes.append(seq_attribute)
                if row['Target_Organism'] is not None and row['Target_Organism'] != '':
                    species_attribute = self.Attribute(
                        'Target Source Organism According to Curator or DataSource', 
                        row['Target_Organism'], 
                        type = 'qualifier:species_context_qualifier'
                    )
                    target[TARGET_ORGANISM] = species_attribute
                    attributes.append(species_attribute)
                elements.append(self.Element(
                    id = uniprot_id,
                    biolink_class = 'Protein',
                    identifiers = identifiers,
                    names_synonyms = names,
                    attributes = attributes
                ))
        target[TARGET_CHAINS] = elements
        if len(elements) == 1:
            elements[0].names_synonyms.append(self.Names(target[TARGET_NAME], name_source='infores:bindingdb'))
            url_attribute = self.Attribute('Link to Target in BindingDB', target[TARGET_URL], type = 'biolink:url')
            elements[0].attributes.append(url_attribute)
        return target


    def get_complex(self, target):
        if len(target.get(TARGET_CHAINS)) < 2 or TARGET_NAME not in target:
            return None
        sub_attributes = []
        for chain in target.get(TARGET_CHAINS):
            chain_name = chain.names_synonyms[0].name if len(chain.names_synonyms) > 0 else None
            sub_attributes.append(self.Attribute('target_chain', chain.id, description=chain_name))
        return self.Attribute('target_complex',target[TARGET_NAME], url=target.get(TARGET_URL), attributes=sub_attributes)

    
    def add_connection(self, source_element_id, row, target_element, complex, connections, threshold):
        binding_value = self.get_binding_value(row)
        if binding_value is None or self.numeric_value(binding_value[1]) >= threshold:
            return
        infores = self.Curation_DataSources.get(row['Curation_DataSource'],'infores:bindingdb')
        if (target_element.id,infores) in connections:
            connection = connections[(target_element.id,infores)]
        else:
            attributes = [
                self.Attribute('Curation_DataSource', infores, type = 'biolink:primary_knowledge_source', value_type='biolink:infores'),
                self.Attribute('Binding_Link', row['Binding_Link'], value_type='biolink:url'),
            ]
            if infores != 'infores:bindingdb':
                attributes.append(self.Attribute('biolink:aggregator_knowledge_source','infores:bindingdb',value_type='biolink:infores'))
            if complex is not None:
                attributes.append(complex)
            connection = self.Connection(
                source_element_id = source_element_id,
                predicate = 'biolink:binds',
                inv_predicate = 'biolink:binds',
                attributes = attributes
            )
            target_element.connections.append(connection)
            connections[(target_element.id,infores)] = connection
        connection_attribute = self.connection_attribute(row)
        if connection_attribute:
            connection.attributes.append(connection_attribute)


    def get_binding_value(self, row):
        for key in ['Ki','IC50','Kd','EC50','kon','koff']:
            if row[key] is not None and row[key] != '':
                return (key, row[key])
        return None


    def numeric_value(self, value):
        return float(value.replace('<','').replace('>',''))


    def connection_attribute(self, row):
        (binding_type, value) = self.get_binding_value(row)
        sub_attributes = []
        for key in ['Ki','IC50','Kd','EC50','kon','koff','pH','Temperature','Curation_DataSource','Article_DOI','PMID','PubChem_AID','Patent_Number','Authors','Institution']:
            if key != binding_type and row[key] is not None:
                prefix = self.attr_prefix_map.get(key, '')
                attribute_type = self.attr_type_map.get(key, key)
                attribute = self.Attribute(key, prefix+row[key], type = attribute_type)
                sub_attributes.append(attribute)
        return self.Attribute(binding_type, value, attributes=sub_attributes)


def find_ligand_by_id(ligand_id):
    query = '''
        select Ligand_ID
        from LIGAND
        where Ligand_ID = ?
    '''
    return find_ligand(query, ligand_id)


def find_ligand_by_name(ligand_name):
    query = '''
        select Ligand_ID
        from LIGAND_NAME
        where Ligand_Name = ? COLLATE NOCASE
    '''
    return find_ligand(query, ligand_name)


def find_ligand_by_inchikey(inchikey):
    query = '''
        select Ligand_ID
        from LIGAND
        where InChI_Key = ?
    '''
    return find_ligand(query, inchikey)


def find_ligand(query, arg):
    cur = connection.cursor()
    cur.execute(query,(arg,))
    return [row['Ligand_ID'] for row in cur.fetchall()]


def get_ligand(ligand_id):
    query = '''
        select 
            Ligand_ID,
            SMILES,
            InChI,
            InChI_Key,
            Ligand_Link,
            PubChem_CID,
            PubChem_SID,
            ChEBI_ID,
            ChEMBL_ID,
            DrugBank_ID,
            KEGG_ID
        from LIGAND
        where Ligand_ID = ?
    '''
    cur = connection.cursor()
    cur.execute(query,(ligand_id,))
    for row in cur.fetchall():
        return row
    return None


def get_ligand_names(ligand_id):
    query = '''
        select Ligand_Name
        from LIGAND_NAME
        where Ligand_ID = ?
    '''
    cur = connection.cursor()
    cur.execute(query,(ligand_id,))
    return [row['Ligand_Name'] for row in cur.fetchall()]


def find_bindings(ligand_id):
    query = """
        select
            Target_ID,
            Ki,
            IC50,
            Kd,
            EC50,
            kon,
            koff,
            pH,
            Temperature,
            Curation_DataSource,
            Article_DOI,
            PMID,
            PubChem_AID,
            Patent_Number,
            Authors,
            Institution,
            Binding_Link,
            PDB_IDs
        from BINDING
        where Ligand_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(ligand_id,))
    return cur.fetchall()


def find_target(target_id):
    query = """
        select
            Number_of_Chains,
            Target_Name,
            Target_Organism,
            Target_Link,
            Sequence,
            UniProt_Name,
            UniProt_Entry_Name,
            UniProt_ID,
            TrEMBL_Submitted_Name,
            TrEMBL_Entry_Name,
            TrEMBL_ID
        from TARGET
        join TARGET_CHAIN_MAP on TARGET_CHAIN_MAP.Target_ID = TARGET.Target_ID
        join TARGET_CHAIN on TARGET_CHAIN.Target_Chain_ID = TARGET_CHAIN_MAP.Target_Chain_ID
        where TARGET.Target_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(target_id,))
    return cur.fetchall()
