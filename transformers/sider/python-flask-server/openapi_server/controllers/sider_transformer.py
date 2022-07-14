from transformers.transformer import Transformer, Producer
import sqlite3
connection_db = sqlite3.connect("data/sider.sqlite", check_same_thread=False)
connection_db.row_factory = sqlite3.Row 

class SiderDrugProducer(Producer): # create drug producer

    variables = ['drug']

    def __init__(self, definition_file='info/drugs_transformer_info.json'):
        super().__init__(self.variables, definition_file)

    # find the cid_stereo given the drug name-------------------------------------------------------------------------------------
    def find_name(self, name):
        statement="""
        select cid_stereo from drug where drug_name = ?
        """
        cur = connection_db.cursor()
        cur.execute(statement, (name,))
        return [row['cid_stereo'] for row in cur.fetchall()]

    # find the cid_stereo name---------------------------------------------------------------------------------------------------
    def find_names(self, name):
        if self.has_prefix('pubchem', name, self.OUTPUT_CLASS):
            return find_cid(self, name)
        else:
            return self.find_name(name)

    # find corresponding drug name given cid stereo number-----------------------------------------------------------------------
    def get_compound_name(self, cid_stereo): 
        statement="""
        select drug_name from drug where cid_stereo = ?;
        """
        cur = connection_db.cursor()
        cur.execute(statement, (cid_stereo,))
        return [row['drug_name'] for row in cur.fetchall()]

    # Format the cid_stereo number----------------------------------------------------------------------------------------------
    def get_format_compound_identifier(self, cid):
        cid_string = ""
        # First remove the 'CID' substring from the cid
        string = str(cid)
        string = string[3:]
        # Now remove the zeros from the string. Note: diff cids have diff # of zeros
        for char in string:
            if char != "0": # reached the first occurrence of a non zero number
                idx = string.index(char) # find the index
                break
        cid_string = string[idx:]
        return cid_string
        
    # get the atc code given the cid_stereo number-----------------------------------------------------------------------------
    def get_compound_attributes(self, cid_stereo): 
        statement="""
        select atc from drug join atc on atc.cid_flat = drug.cid_flat where cid_stereo = ?;
        """
        cur = connection_db.cursor()
        cur.execute(statement, (cid_stereo,))
        atcs = [row['atc'] for row in cur.fetchall()]
        atc_attributes = []
        for atc in atcs:
            if atc != "null":
                atc_attributes.append(self.Attribute('atc', atc))
        return atc_attributes

    def create_element(self, cid_stereo):
        # compound = self.get_compound(cid)
        # identifiers = self.get_compound_identifiers(compound)
        cid = self.get_format_compound_identifier(cid_stereo)
        cid_prefix = self.add_prefix("pubchem", cid, self.OUTPUT_CLASS)
        element = self.Element(
            id = cid_prefix,
            biolink_class = self.biolink_class(self.OUTPUT_CLASS),
            identifiers = {'pubchem':cid_prefix},
            names_synonyms = [self.Names(name) for name in self.get_compound_name(cid_stereo)],
            attributes = self.get_compound_attributes(cid_stereo),
        )
        return element

class SideEffectsTransformer(Transformer): # create side effect transformer

    variables = []

    def __init__(self, definition_file='info/side_effects_transformer_info.json'):
        super().__init__(self.variables, definition_file)

    def map(self, compound_list, controls):
        side_effect_list = []
        side_effects = {}
        for compound in compound_list:
            for cid_stereo in find_drug(self, compound):
                for side_effect in self.find_side_effects(cid_stereo, compound.id):
                    umls_id = side_effect['umls_id']
                    se_id = side_effect['se_id']
                    element = side_effects.get(umls_id)
                    if element is None:
                        element = self.create_element(side_effect)
                        side_effect_list.append(element)
                        side_effects[umls_id] = element
                    element.connections.append(self.create_connection(compound.id, se_id, umls_id))
        return side_effect_list

    def find_side_effects(self, cid_stereo, source_element_id):
        statement="""
        select se_id, umls_id from side_effects where cid_stereo = ?;
        """
        cur = connection_db.cursor()
        cur.execute(statement, (cid_stereo,))
        return cur.fetchall()
        
    # get the name from the umls table--------------------------------------------------------------------------------------------------------
    def get_side_effect_name(self, umls_id): 
        statement="""
        select concept_name as side_effect_name from umls where umls_id = ?
        """
        name = None
        cur = connection_db.cursor()
        cur.execute(statement, (umls_id,))
        for row in cur.fetchall():
            name = row['side_effect_name']
        return name

    # get the label from the side effects labels table-------------------------------------------------------------------------------------
    def get_label_attributes(self, se_id, umls_id):
        statement="""
        select se_source_label from side_effects_labels where se_id = ?;
        """
        cur = connection_db.cursor()
        cur.execute(statement, (se_id,))
        labels = [row['se_source_label'] for row in cur.fetchall()]
        attributes = []
        for label in labels:
            # get rid of .html or .zip at end of url
            if label.rfind(".") > 0:
                url_label = label[0: label.rfind(".")]
                url = "http://sideeffects.embl.de/labels/" + url_label + "/" + umls_id + "/"
            else:
                url = None
            attribute = self.Attribute('label', label, url = url)
            attributes.append(attribute)
        return attributes

    # get the frequency data from the side effect frequency table as well as the sub attributes (placebo, low bound, upper bound)--------------
    def get_freq_attributes(self, se_id):
        attributes = []
        statement="""
        select frequency, placebo, lower_bound_freq, upper_bound_freq from side_effect_frequency where se_id = ?
        """
        cur = connection_db.cursor()
        cur.execute(statement, (se_id,))
        for row in cur.fetchall():
            attribute = self.Attribute('frequency', str(row['frequency']))
            sub_attributes = []
            if row['placebo'] is not None:
                sub_attributes.append(self.Attribute('placebo', str(row['placebo'])))
            if row['lower_bound_freq'] is not None:
                sub_attributes.append(self.Attribute('lower_bound_freq', str(row['lower_bound_freq'])))
            if row['upper_bound_freq'] is not None:
                sub_attributes.append(self.Attribute('upper_bound_freq', str(row['upper_bound_freq'])))
            attribute.attributes = sub_attributes
            attributes.append(attribute)
        return attributes
        
    def create_connection(self, source_element_id, se_id, umls_id):
        attributes = self.get_label_attributes(se_id, umls_id)
        attributes.extend(self.get_freq_attributes(se_id))# frequency from freq table and source label
        connection = self.Connection(
            source_element_id = source_element_id,
            predicate = self.PREDICATE, 
            inv_predicate =  self.INVERSE_PREDICATE, 
            attributes = attributes,
        )
        return connection

    def create_element(self, side_effect): #input the cid to get the side effect/
        umls_id = side_effect['umls_id'] #umls id
        se_id = side_effect['se_id'] # side effect id to be used for the attributes
        cid_prefix = self.add_prefix("umls", umls_id, self.OUTPUT_CLASS)
        element = self.Element(
            id = cid_prefix, # this should be the chembl prefix
            biolink_class = self.biolink_class(self.OUTPUT_CLASS),
            identifiers = {'umls':cid_prefix},
            names_synonyms = [self.Names(self.get_side_effect_name(umls_id), get_side_effect_synonyms(umls_id))],  # name from umls table and name from synonyms table
            attributes = [],
        )
        return element
        

class IndicationsTransformer(Transformer): # create indications transformer

    variables = []

    def __init__(self, definition_file='info/indications_transformer_info.json'):
        super().__init__(self.variables, definition_file)

    def map(self, compound_list, controls):
        indications_list = []
        indications = {}
        for compound in compound_list:
            for cid_stereo in find_drug(self, compound):
                for indication in self.find_indications(cid_stereo, compound.id):
                    umls_id = indication['umls_id']
                    indication_id = indication['indication_id']
                    element = indications.get(umls_id)
                    if element is None:
                        element = self.create_element(indication)
                        indications_list.append(element)
                        indications[umls_id] = element
                    element.connections.append(self.create_connection(compound.id, indication_id, umls_id))
        return indications_list

    # create function to get id and umls id from indications table------------------------------------------------------------------------------
    def find_indications(self, cid_stereo, source_element_id):
        statement="""
        select indication_id, umls_id from indications where cid_stereo = ?;
        """
        cur = connection_db.cursor()
        cur.execute(statement, (cid_stereo,))
        return cur.fetchall()

    # get the concept name from the umls table given the umls id
    def get_indication_name(self, umls_id):
        statement="""
        select concept_name as indication_name from umls where umls_id = ?;
        """
        indication_name = None
        cur = connection_db.cursor()
        cur.execute(statement, (umls_id,))
        for row in cur.fetchall():
            indication_name = row['indication_name']
        return indication_name

    # get the method of detection from the indications table using the indication id------------------------------------------------------------
    def get_detection_attributes(self, indication_id):
        statement="""
        select method_of_detection from indications where indication_id = ?
        """
        cur = connection_db.cursor()
        cur.execute(statement, (indication_id,))
        methods_of_detection = [row['method_of_detection'] for row in cur.fetchall()]
        return [self.Attribute('method', method) for method in methods_of_detection]

    # get the source label from the indications labels table-------------------------------------------------------------------------------------
    def get_indications_label_attributes(self, indication_id, umls_id):
        statement="""
        select source_label from indication_labels where indication_id = ?;
        """
        cur = connection_db.cursor()
        cur.execute(statement, (indication_id,))
        attributes = []
        labels = [row['source_label'] for row in cur.fetchall()]
        for label in labels:
            # get rid of .html or .zip at end of url
            if label.rfind(".") > 0:
                url_label = label[0: label.rfind(".")]
                url = "http://sideeffects.embl.de/labels/" + url_label + "/" + umls_id + "/"
            else:
                url = None
            attribute = self.Attribute('label', label, url = url)
            attributes.append(attribute)
        return attributes

    def create_connection(self, source_element_id, indication_id, umls_id):
        attributes = self.get_indications_label_attributes(indication_id, umls_id)
        attributes.extend(self.get_detection_attributes(indication_id)) # method of detection and source label
        connection = self.Connection(
            source_element_id = source_element_id,
            predicate = self.PREDICATE, 
            inv_predicate =  self.INVERSE_PREDICATE, 
            attributes = attributes,
        )
        return connection

    def create_element(self, indications):
        umls_id = indications['umls_id'] # get the umls id
        indication_id = indications['indication_id'] # indication id to be used for the attributes
        cid_prefix = self.add_prefix('umls', umls_id, self.OUTPUT_CLASS)
        element = self.Element(
            id = cid_prefix,
            biolink_class = self.biolink_class(self.OUTPUT_CLASS),
            identifiers = {'umls':cid_prefix},
            names_synonyms = [self.Names(self.get_indication_name(umls_id), get_side_effect_synonyms(umls_id))],
        )
        return element # this function will return the element



# Global Functions---------------------------------------------------------------------------------------------------------------------------------------------
 # Find the cid_stereo number given the shortened, formatted version----------------------------------------------------------
def find_cid(transformer, cid):
    # get rid of cid prefix and make as a cid stereo and return the cid stereo
    # get the shortened cid (just the numbers)
    cid_de_prefix = transformer.de_prefix('pubchem', cid, 'compound')
    zeros = ""
    digits = 9 - len(cid_de_prefix) # find the number of zeros needed for that cid and create a string
    for i in range(digits):
        zeros += "0"
    stereo = "CID" + zeros + cid_de_prefix
    return [stereo]

def find_drug(transformer, compound):
    cid = compound.identifiers.get("pubchem")
    return find_cid(transformer, cid)

def get_side_effect_synonyms(umls_id): 
    # get the synonym names for side effect transformer and indications transformer
    statement="""
    select meddra_term as synonyms from synonyms where umls_id = ?; 
    """
    cur = connection_db.cursor()
    cur.execute(statement, (umls_id,))
    return [row['synonyms'] for row in cur.fetchall()]
