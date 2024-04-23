import sqlite3
import re

from transformers.transformer import Transformer


connection = sqlite3.connect("data/KinomeScan.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

class KinomeScanProducer(Transformer):
    
    variables = ["small_molecule"]
    
    def __init__(self):
        super().__init__(self.variables, definition_file='info/smallmolecule_transformer_info.json')
        self.HMSL = self.info.knowledge_map.nodes['SmallMolecule'].id_prefixes[0]
        self.PUBCHEM = self.info.knowledge_map.nodes['SmallMolecule'].id_prefixes[1]

    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')

    def produce(self, controls):
        small_molecule_list = []
        small_molecules = {}
        names  = controls.get("small_molecule", [])
        for name in names:
            # build element using hmsl identifier
            for hms_id in self.find_compounds(name):
                if hms_id not in small_molecules:
                    small_molecule = self.create_element(hms_id)
                    if small_molecule is not None:
                        small_molecules[hms_id] = small_molecule
                        small_molecule_list.append(small_molecule)
                    if hms_id in small_molecules:
                        small_molecules[hms_id].attributes.append(self.Attribute(name='query name', value=name))   
        return small_molecule_list

    def find_compounds(self, name):
        if name.startswith("HMSL"):
            return [name]
        elif name.startswith("CID:"):
            name = name[4:]
            return self.find_compound_by_CID(name)
        elif self.inchikey_regex.match(name) != None:
            return self.find_compound_by_inchi_key(name)
        else:
            return self.find_compound_by_name(name)

    
    def find_compound_by_CID(self,name):
        compounds = []
        query_id = name
        query = "SELECT SM_HMS_LINCS_ID FROM SMALL_MOLECULE WHERE PUBCHEM_CID = ?"
        cur = connection.cursor()
        cur.execute(query,(query_id,))
        for row in cur.fetchall():
            compounds.append(row["SM_HMS_LINCS_ID"])
        return compounds

    def find_compound_by_inchi_key(self,name):
        compounds =[]
        query_id = name
        query = "SELECT SM_HMS_LINCS_ID FROM SMALL_MOLECULE WHERE INCHI_KEY = ?"
        cur = connection.cursor()
        cur.execute(query,(query_id,))
        for row in cur.fetchall():
            compounds.append(row["SM_HMS_LINCS_ID"])
        return compounds

    def find_compound_by_name(self,name):
        # need to look through names within the activity table as well 
        compounds = []
        query_id = name
        query_1 = "SELECT SM_HMS_LINCS_ID FROM SMALL_MOLECULE WHERE SM_NAME = ?"
        query_2 = "SELECT SM_HMS_LINCS_ID FROM SMALL_MOLECULE_NAMES WHERE SM_ALTERNATIVE_NAMES = ?"
        cur_1 = connection.cursor()
        cur_1.execute(query_1,(query_id,))
        cur_2 = connection.cursor()
        cur_2.execute(query_2,(query_id,))
        for row in cur_1.fetchall():
            compounds.append(row["SM_HMS_LINCS_ID"])
        for row in cur_2.fetchall():
            compounds.append(row["SM_HMS_LINCS_ID"])
        return compounds   

    def get_compound_name(self, hms_id):
        query_id = hms_id
        query = "SELECT SM_NAME, MOLECULAR_MASS FROM SMALL_MOLECULE WHERE SM_HMS_LINCS_ID = ?"
        cur = connection.cursor()
        cur.execute(query,(query_id,))
        return cur.fetchall()

    def get_compound_id(self, hms_id):
        query_id = hms_id
        query = "SELECT PUBCHEM_CID, SMILES, INCHI, INCHI_KEY, CHEMBL_ID, SM_LINCS_ID FROM SMALL_MOLECULE WHERE SM_HMS_LINCS_ID = ?"
        cur = connection.cursor()
        cur.execute(query,(query_id,))
        return cur.fetchall()

    def get_identifiers(self,hms_id):
        identifiers = {}
        for row in self.get_compound_id(hms_id):
            if row['PUBCHEM_CID'] is not None and row['PUBCHEM_CID'] != '':
                identifiers['pubchem']= self.add_prefix("pubchem", row['PUBCHEM_CID'])
            if row['SMILES'] is not None and row['SMILES'] != '':
                identifiers['smiles']= row['SMILES']
            if row['INCHI'] is not None and row['INCHI'] != '':
                identifiers['inchi']= row['INCHI']
            if row['INCHI_KEY'] is not None and row['INCHI_KEY'] != '':
                identifiers['inchikey']= row['INCHI_KEY']
            if row['SM_LINCS_ID'] is not None and row['SM_LINCS_ID'] != '': 
                identifiers['lincs']= self.add_prefix("lincs",row['SM_LINCS_ID'])
        return identifiers
    
    def get_alt_name(self, hms_id):
        query_id = hms_id
        query = "SELECT SM_ALTERNATIVE_NAMES FROM SMALL_MOLECULE_NAMES WHERE SM_HMS_LINCS_ID = ?"
        cur = connection.cursor()
        cur.execute(query,(query_id,))
        return cur.fetchall()

    def get_synonyms(self, hms_id):
        synonyms =[]
        for row in self.get_alt_name(hms_id):
            synonyms.append(row["SM_ALTERNATIVE_NAMES"])
        return synonyms
    # Review Type
    def create_element(self, hms_id):
        id = self.add_prefix("lincs", hms_id)
        sm_name = None
        sm_mass = None
        for row in self.get_compound_name(hms_id):
            sm_name = row['SM_NAME'] 
            sm_mass = row['MOLECULAR_MASS']
        if sm_name == None: 
            return None
        element = self.Element(
            id = id,
            biolink_class = self.biolink_class("SmallMolecule"),
            identifiers = self.get_identifiers(hms_id),
            names_synonyms = [
                self.Names(
                    name = sm_name,
                    synonyms = self.get_synonyms(hms_id),
                    type = ""
                )
            ],
            attributes = [
                self.Attribute(
                    name = 'compound molecular mass',
                    value = str(sm_mass),
                    type = ''
                )
            ]
        ) 
        return element

class ActivityTranformer(Transformer):
    # small molecule to protein 
    # thershold value for percentage and kd 
    variables = ["Kd nMol threshold", "percent control threshold"]
    def __init__(self):
        super().__init__(self.variables, definition_file = "info/activity_transformer_info.json")

    def map(self, small_molecule_list, controls):
        protein_list = []
        proteins = {}
        for sm in small_molecule_list:
            kd_thershold = controls.get("Kd nMol threshold")
            percent_thershold = controls.get("percent control threshold")
            for hmsl_id in self.get_small_molecules(sm):
                activity_info = []
                if kd_thershold != None and kd_thershold > 0:
                    activity_info = self.get_activity_by_kd(hmsl_id, kd_thershold)
                if percent_thershold != None and percent_thershold > 0:
                    activity_info.extend(self.get_activity_by_percent(hmsl_id, percent_thershold))
                for row in activity_info:
                    protein_id = row["UNIPROT_ID"]
                    if protein_id not in proteins:
                        protein_element = self.create_protein_element(protein_id)
                        if protein_element is not None:
                            proteins[protein_id] = protein_element
                            protein_list.append(protein_element)
                    else:
                        protein_element = proteins[protein_id]
                    # predicate: assess
                    if protein_element is not None: 
                        connection = self.create_connection(sm.id, row)
                        protein_element.connections.append(connection)
        return protein_list
    
    def get_small_molecules(self, sm):
        pubchem_cid = self.get_identifiers(sm, 'pubchem')
        hmsl_ids = self.find_compound_by_id(pubchem_cid, 'PUBCHEM_CID', as_str = False)
        if len(hmsl_ids) > 0:
            return hmsl_ids
        inchikeys = self.get_identifiers(sm, 'inchikey')
        hmsl_ids = self.find_compound_by_id(inchikeys, 'INCHI_KEY', as_str = True)
        if len(hmsl_ids) > 0:
            return hmsl_ids
        lincs_ids = self.get_identifiers(sm, 'lincs')
        hmsl_ids = self.find_compound_by_id(lincs_ids, 'SM_LINCS_ID', as_str = True)
        return hmsl_ids

    def find_compound_by_id(self, query_ids, column, as_str = False):
        if len(query_ids) == 0:
            return []
        if as_str:
            query_ids = ["'"+query_id+"'" for query_id in query_ids]
        query = "SELECT SM_HMS_LINCS_ID FROM SMALL_MOLECULE WHERE {} in ({})"
        cur = connection.cursor()
        cur.execute(query.format(column, ",".join(query_ids)))
        return [row["SM_HMS_LINCS_ID"] for row in cur.fetchall()]

    def create_connection(self, source_element_id, row):
        attributes = self.get_connection_attributes(row)
        qualifiers = []
        if row["MUTATION"] is not None and row["MUTATION"] != "":
            qualifiers.append(self.Qualifier("object_form_or_variant_qualifier", row["MUTATION"]))
        if row["PHOSPHORYLATION_STATE"] is not None and row["PHOSPHORYLATION_STATE"] != "":
            qualifiers.append(self.Qualifier("object_form_or_variant_qualifier", row['PHOSPHORYLATION_STATE']))
        if row["DOMAIN"] is not None and row["DOMAIN"] != "":
            qualifiers.append(self.Qualifier("object_form_or_variant_qualifier", row["DOMAIN"]))
        if row["SOURCE_ORGANISM"] is not None and row["SOURCE_ORGANISM"] == "Homo sapiens":
            qualifiers.append(self.Qualifier("species_context_qualifier", "NCBITaxon:9606"))
        connection = self.Connection(source_element_id, "biolink:assess", "biolink:is_assessed_by", attributes=attributes, qualifiers=qualifiers)
        return connection 

    def get_activity_by_kd(self, sm_id, kd_thershold):
        # specify columns for every star in queries
        ####
        query = """
        SELECT UNIPROT_ID, KD, PERCENT_CONTROL, AMINO_ACID_SEQUENCE, PROTEIN_SOURCE, MUTATION, 
               PHOSPHORYLATION_STATE, DOMAIN, PROTEIN_DESCRIPTION, DATASET_URL, SOURCE_ORGANISM
        FROM ACTIVITY
        JOIN PROTEIN ON PROTEIN.PROTEIN_HMS_LINCS_ID = ACTIVITY.PROTEIN_HMS_LINCS_ID 
        WHERE SM_HMS_LINCS_ID = ? AND KD <= ?
        """
        cur = connection.cursor()
        cur.execute(query,(sm_id, kd_thershold,))
        return cur.fetchall()
    
    def get_activity_by_percent(self, sm_id, percent_thershold):
        query = """
        SELECT PROTEIN_NAME, UNIPROT_ID, KD, PERCENT_CONTROL, AMINO_ACID_SEQUENCE, PROTEIN_SOURCE, MUTATION, 
               PHOSPHORYLATION_STATE, DOMAIN, PROTEIN_DESCRIPTION, DATASET_URL, SOURCE_ORGANISM
        FROM ACTIVITY 
        JOIN PROTEIN ON PROTEIN.PROTEIN_HMS_LINCS_ID = ACTIVITY.PROTEIN_HMS_LINCS_ID 
        WHERE SM_HMS_LINCS_ID = ? AND PERCENT_CONTROL <= ? 
        """
        cur = connection.cursor()
        cur.execute(query,(sm_id, percent_thershold,))
        return cur.fetchall()

    def get_protein_info(self, protein_id):
        query = "SELECT PROTEIN_NAME, UNIPROT_ID, GENE_SYMBOL, SOURCE_ORGANISM, GENE_ID, PROTEIN_HMS_LINCS_ID FROM PROTEIN WHERE UNIPROT_ID = ?"
        cur = connection.cursor()
        cur.execute(query,(protein_id,))
        return cur.fetchall()
    
    def get_protein_identifiers(self,row):
        identifiers = {}
        if row['UNIPROT_ID'] is not None and row['UNIPROT_ID'] != '':
            identifiers['uniprot']= self.add_prefix("uniprot",row['UNIPROT_ID'])
        identifiers["lincs"] = self.add_prefix("lincs", row["PROTEIN_HMS_LINCS_ID"])
        return identifiers

    def get_element_attributes(self, row):
        attributes = []
        # need to build this (which will be element attribute (shared by all) and which will my connection attribute)
        if row["GENE_SYMBOL"] is not None and row['GENE_SYMBOL'] != '':
            attributes.append(self.Attribute(name = 'gene symbol',value = row['GENE_SYMBOL'],type = 'biolink:symbol'))
        if row["SOURCE_ORGANISM"] is not None and row['SOURCE_ORGANISM'] != '':
            attributes.append(self.Attribute(name = 'source organism',value = row['SOURCE_ORGANISM']))
        if row["GENE_ID"] is not None and row['GENE_ID'] != '':
            attributes.append(self.Attribute(name = 'gene id',value = row['GENE_ID']))
        return attributes

    def get_connection_attributes(self, row):
        attributes =[]
        infores = self.info.infores
        url = row['DATASET_URL'] + 'results' if row['DATASET_URL'] is not None else None
        attributes.append(self.Attribute('biolink:primary_knowledge_source', infores, value_type = 'biolink:InformationResource', url = url))
        if row["KD"] != None:
            attributes.append(self.Attribute(name = 'Kd', value = row["KD"]))
        if row["PERCENT_CONTROL"] != None:
            attributes.append(self.Attribute(name = 'percent control', value = row["PERCENT_CONTROL"]))
        if row['AMINO_ACID_SEQUENCE'] is not None and row['AMINO_ACID_SEQUENCE'] != '':
            attributes.append(self.Attribute(name = 'amino acid sequence',value = row['AMINO_ACID_SEQUENCE']))
        if row["PROTEIN_SOURCE"] is not None and row['PROTEIN_SOURCE'] != '':
            attributes.append(self.Attribute(name = 'protein source',value = row['PROTEIN_SOURCE']))
        # Mutation would be qualifier in new molepro update
        if row["MUTATION"] is not None and row['MUTATION'] != '':
            attributes.append(self.Attribute(name = 'mutation',value = row['MUTATION']))
        if row["PHOSPHORYLATION_STATE"] is not None and row['PHOSPHORYLATION_STATE'] != '':
            attributes.append(self.Attribute(name = 'phosphorylation state',value = row['PHOSPHORYLATION_STATE']))
        if row["DOMAIN"] is not None and row['DOMAIN'] != '':
            attributes.append(self.Attribute(name = 'domain',value = row['DOMAIN']))
        if row["PROTEIN_DESCRIPTION"] is not None and row['PROTEIN_DESCRIPTION'] != '':
            attributes.append(self.Attribute(name = 'protein description',value = row['PROTEIN_DESCRIPTION']))
        return attributes

    def create_protein_element(self, protein_id):
        element = None
        if protein_id is not None:
            for row in self.get_protein_info(protein_id):
                element = self.Element(
                    id = self.add_prefix("uniprot",row["UNIPROT_ID"]),
                    biolink_class = self.biolink_class("Protein"),
                    identifiers = self.get_protein_identifiers(row),
                    names_synonyms = [
                        self.Names(
                            name = row["GENE_SYMBOL"] if row["GENE_SYMBOL"] is not None else row["PROTEIN_NAME"],
                            synonyms = [],
                            type = ""
                        )
                    ],
                    attributes = self.get_element_attributes(row)
                ) 
        return element


class ScreeningTranformer(Transformer):
    # Chemical output
    # Screening data as connection
    # thershold value for percentage and kd 
    variables = ["Kd nMol threshold", "percent control threshold"]
    def __init__(self):
        super().__init__(self.variables, definition_file = "info/screening_transformer_info.json")
    
    def map(self, protein_list, controls):
        small_molecule_list = []
        small_molecules = {}
        for protein in protein_list:
            
            kd_thershold = controls.get("Kd nMol threshold")
            percent_thershold = controls.get("percent control threshold")
            for uniprot_id in self.get_identifiers(protein, "uniprot"):
                protein_id = self.get_protein_id(uniprot_id)
                activity_info = []
                if protein_id is not None and kd_thershold is not None and kd_thershold > 0:
                    activity_info = self.get_activity_by_kd(protein_id, kd_thershold)
                if protein_id is not None and percent_thershold is not None and percent_thershold > 0:
                    activity_info.extend(self.get_activity_by_percent(protein_id, percent_thershold))
                
                for row in activity_info:
                    sm_id = row["SM_HMS_LINCS_ID"]
                    if sm_id not in small_molecules:
                        sm_element = self.create_sm_element(sm_id)
                        small_molecules[sm_id] = sm_element
                        small_molecule_list.append(sm_element)
                    else:
                        sm_element = small_molecules[sm_id]
                    connection = self.Connection(protein.id,"biolink:is_assessed_by", "biolink:assess", attributes= self.get_connection_attributes(row))
                    sm_element.connections.append(connection)
        return small_molecule_list

    def get_connection_attributes(self, row):
        attributes =[]
        infores = self.info.infores
        attributes.append(self.Attribute('biolink:primary_knowledge_source', infores, value_type = 'biolink:InformationResource'))
        if row["KD"] != None:
            attributes.append(self.Attribute(name = 'Kd', value = row["KD"]))
        if row["PERCENT_CONTROL"] != None:
            attributes.append(self.Attribute(name = 'percent control', value = row["PERCENT_CONTROL"]))
        return attributes


    def get_protein_id(self, protein_id):
        query = "SELECT PROTEIN_HMS_LINCS_ID FROM PROTEIN WHERE UNIPROT_ID = ?"
        cur = connection.cursor()
        cur.execute(query,(protein_id,))
        for row in cur.fetchall():
            return row["PROTEIN_HMS_LINCS_ID"]
        return None
    
    def get_activity_by_kd(self, protein_id, kd_thershold):
        query = "SELECT SM_HMS_LINCS_ID, KD, PERCENT_CONTROL FROM ACTIVITY WHERE PROTEIN_HMS_LINCS_ID = ? AND KD <= ?"
        cur = connection.cursor()
        cur.execute(query,(protein_id, kd_thershold,))
        return cur.fetchall()
    
    def get_activity_by_percent(self, protein_id, percent_thershold):
        query = "SELECT SM_HMS_LINCS_ID, KD, PERCENT_CONTROL FROM ACTIVITY WHERE PROTEIN_HMS_LINCS_ID = ? AND PERCENT_CONTROL <= ?"
        cur = connection.cursor()
        cur.execute(query,(protein_id, percent_thershold,))
        return cur.fetchall()

    def get_sm_info(self, sm_id):
        query = "SELECT SM_NAME, SM_LINCS_ID, PUBCHEM_CID, CHEMBL_ID, INCHI, INCHI_KEY, SMILES, MOLECULAR_MASS FROM SMALL_MOLECULE WHERE SM_HMS_LINCS_ID = ?"
        cur = connection.cursor()
        cur.execute(query,(sm_id,))
        return cur.fetchall()
    
    def get_sm_identifiers(self,row):
        identifiers = {}
        if row['SM_LINCS_ID'] is not None and row['SM_LINCS_ID'] != '':
            identifiers['lincs']= self.add_prefix("lincs", row['SM_LINCS_ID'])
        if row['PUBCHEM_CID'] is not None and row['PUBCHEM_CID'] != '':
            identifiers['pubchem']= self.add_prefix("pubchem", row['PUBCHEM_CID'])
        if row['CHEMBL_ID'] is not None and row['CHEMBL_ID'] != '':
            identifiers['chembl']= self.add_prefix("chembl", row['CHEMBL_ID'])
        if row['INCHI'] is not None and row['INCHI'] != '':
            identifiers['inchi']= row['INCHI']
        if row['INCHI_KEY'] is not None and row['INCHI_KEY'] != '':
            identifiers['inchikey']= row['INCHI_KEY']
        if row['SMILES'] is not None and row['SMILES'] != '':
            identifiers['smiles']= row['SMILES']
        return identifiers

    def get_attributes(self, row):
        attributes =[]
        if row['MOLECULAR_MASS'] is not None and row['MOLECULAR_MASS'] != '':
            attributes.append(self.Attribute(name = 'compound molecular mass',value = str(row['MOLECULAR_MASS'])))
        return attributes
    
    def get_alt_name(self,sm_id):
        query_id = sm_id
        query = "SELECT SM_ALTERNATIVE_NAMES FROM SMALL_MOLECULE_NAMES WHERE SM_HMS_LINCS_ID = ?"
        cur = connection.cursor()
        cur.execute(query,(query_id,))
        return cur.fetchall()

    def get_synonyms(self, sm_id):
        synonyms =[]
        for row in self.get_alt_name(sm_id):
            synonyms.append(row["SM_ALTERNATIVE_NAMES"])
        return synonyms

    def create_sm_element(self, sm_id):
        for row in self.get_sm_info(sm_id):
            element = self.Element(
                id = self.add_prefix("lincs",sm_id),
                biolink_class = self.biolink_class("SmallMolecule"),
                identifiers = self.get_sm_identifiers(row),
                names_synonyms = [
                    self.Names(
                        name = row["SM_NAME"],
                        synonyms = self.get_synonyms(sm_id),
                        type = ""
                    )
                ],
                attributes = self.get_attributes(row)
            ) 
        return element

    

