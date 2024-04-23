import sqlite3
import csv


from transformers.transformer import Transformer
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection


# CURIE prefixes
DRUGBANK = 'DrugBank:'
PUBCHEM = 'CID:'
CHEMBL = 'ChEMBL:'
CHEBI = 'CHEBI:'

biolinkClass_dict = {
    'carrier':'transport_affected_by',
    'enzyme':'affected_by',
    'target':'affects',
    'transporter':'transport_affected_by'
}


######################################################################
#
#   TODO - WORK-IN-PROGRESS complete this class
#
class DrugBankDrugProducer(Transformer):
    variables = ['drugs']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/drugs_transformer_info.json')




###################################################################################
#
#  INPUT FROM REST REQUEST:   Name || DRUGBANK:Drugbank_ID || PUBCHEM ||  inchikey 
#  PRODUCES: MolecularEntity OR SmallMolecule
#   
class DrugBankMolecularProducer(Transformer):
    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')

    def produce(self, controls):
        compound_list = []
        compounds = {}
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            for drug in find_drug(name):
                if drug['DRUG_TYPE'] == 'small molecule':
                    biolink_class = 'SmallMolecule' 
                if drug['DRUG_TYPE'] == 'biotech':
                    biolink_class = 'MolecularEntity' 
                element = get_drug(self, drug, biolink_class)  # Use the tuple of the drug's identifiers
                if element.id not in compounds:
                    element.attributes = get_attributes(self, drug['DRUG_ID'])
                    compounds[element.id] = element
                    compound_list.append(element)
                compounds[element.id].attributes.append(
                    self.Attribute(
                        name='query name', 
                        value=name
                    )
                )
        return compound_list


###################################################################################
#
#  INPUT FROM REST REQUEST:    Name || DRUGBANK:Drugbank_ID || PUBCHEM ||  inchikey 
#   
class DrugBankCompoundProducer(Transformer):
    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/compounds_transformer_info.json')

    def produce(self, controls):
        compound_list = []
        compounds = {}
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            for drug in find_drug(name):
                if drug['DRUG_TYPE'] == 'small molecule':
                    element = get_drug(self, drug, 'ChemicalSubstance')  # Use the tuple of the drug's identifiers
                    if element.id not in compounds:
                        element.attributes = get_attributes(self, drug['DRUG_ID'])
                        compounds[element.id] = element
                        compound_list.append(element)
                    compounds[element.id].attributes.append(
                        self.Attribute(
                            name='query name', 
                            value=name
                        )
                    )
        return compound_list



class DrugBankInhibitorsTransformer(Transformer):

    variables = []

    biolinkClass_dict = {
        'carrier':'affects_transport_of',
        'enzyme':'affects',
        'target':'affected_by',
        'transporter':'affects_transport_of'
    }


    def __init__(self, target_type, transformer_name):
        super().__init__(self.variables, definition_file='info/inhibitors_transformer_info.json')
        self.SOURCE = self.info.label
        self.PROVIDED_BY = self.info.name
        self.target_type = target_type
        self.info.knowledge_map.predicates[0].predicate = biolinkClass_dict[target_type]
        self.info.name = "DrugBank " + transformer_name + " transformer"

    def map(self, gene_list, controls):
        compound_list = []
        compounds = {}
        for gene in gene_list:
            if 'hgnc' in gene.identifiers and gene.identifiers['hgnc'] is not None:
                gene_id = gene.identifiers['hgnc']
                inhibitors = get_inhibitors(gene_id, self.target_type)
                for inhibitor in inhibitors:
                    if inhibitor['DRUG_TYPE'] == 'small molecule':
                        drug_bank_id = inhibitor['DRUG_BANK_ID']
                        compound = compounds.get(drug_bank_id)
                        if compound is None:
                            compound = get_drug(self, inhibitor,'ChemicalSubstance')
                            compound.source = self.info.name
                            compound_list.append(compound)
                            compounds[drug_bank_id] = compound
                        compound.connections.append(self.connection(gene.id, inhibitor))
        return compound_list

    
    def connection(self, source_element_id, row):
        connection = Connection(
            source_element_id = source_element_id,
            type = self.biolinkClass_dict[row['TAG']],
            relation = '',
            source = self.SOURCE,
            provided_by = self.PROVIDED_BY,
            attributes = [
                    self.Attribute(
                        name= 'known action',
                        value= row['KNOWN_ACTION'],
                        type= 'known action'
                    )
            ]
        )
        get_connection_properties(self, self.PROVIDED_BY, row['CONNECTION_ID'], connection)   # add attributes from CONNECTION_PROPERTY table
        get_connection_references(self, self.PROVIDED_BY, row['CONNECTION_ID'], connection)   # add attributes from REFERENCE table
                          
        return connection

#############################################################################
#
#   Use Biolink CURIE prefix (i.e., DRUGBANK:) in DrugBank Transformer responses.
#
#-- ********** DrugBank protein/gene interaction transformer
#-- => connection (TAG -> relation)
#-- => connection attributes (KNOWN_ACTION, TARGET_NAME, TARGET_IDENTIFIER)
#-- => protein attributes(ORGANISM)
#-- => protein names(POLYPEPTIDE_NAME)
#-- => protein identifiers(POLYPEPTIDE_IDENTIFIER, POLYPEPTIDE_IDENTIFIER_SOURCE)
#
#
class DrugBankInteractionsTransformer(Transformer):
    variables = []

    # WARNING: The following is only a Superclass constructor. 
    # Do not copy for use in non-Superclasses.
    def __init__(self, target_type, definition_file):
       super().__init__(self.variables, definition_file)
       self.target_type = target_type


    def map(self, compound_list, controls):
        target_list = []
        targetDict = {} 
        target_id  = ''
    #   find connection data for each compound that was submitted
        for compound in compound_list:
            drug = self.find_drug(compound)   # DRUG_ID, DRUG_BANK_ID, DRUG_NAME
            if drug is not None:
                connectionsDict = {}
                targets = get_compound_targets(self, self.info.name, self.target_type, connectionsDict, drug, compound)       # get a list of targets
                for target in targets:                                  # step through all targets (genes or proteins)
                    element = targetDict.get(target)                    # look up dictionary for the target's element
                    if element is None:                                 # if we haven't found the target
                        element = self.get_element(target_id, target)   # then call the subclass method
                        if element.id is not None:
                            target_list.append(element)                     # add element to the list
                            targetDict[target] = element                    # add element to the dictionary
                            get_target_names(self, target, element)               # add element names
                            #add element attributes
                            get_target_attributes(self, target, element)
                    #add connection
                    connection = connectionsDict[target]
                    element.connections.append(connection)
    #   send back to the REST client the entire list of targets (genes that interact with the drugs)
        return target_list



    #################################################
    # Called from map()
    # Sort out the preferred metabolite identifier
    #
    def find_drug(self, input_element_compound: Element):
        if input_element_compound.identifiers is not None:
            if input_element_compound.identifiers.get('drugbank') is not None:
                drug_bank_id = de_prefix(DRUGBANK,input_element_compound.identifiers.get('drugbank'))
                for drug in find_drug_by_drug_bank_id(drug_bank_id):
                    return drug
            if input_element_compound.identifiers.get('pubchem') is not None:
                cid = de_prefix(PUBCHEM, input_element_compound.identifiers.get('pubchem'))
                for drug in find_drug_by_identifier(cid, 'PubChem Compound'):
                    return drug
        return None            



#################################################################
#
# Subclass of DrugBankInteractionsTransformer
#
class DrugBankGeneInteractionsTransformer(DrugBankInteractionsTransformer):
    variables = []
    def __init__(self, target_type):
        super().__init__(target_type, definition_file='info/gene_interactions_transformer_info.json')
        self.info.knowledge_map.predicates[0].predicate = biolinkClass_dict[target_type]
        self.info.name = "DrugBank " + target_type + " genes transformer"

    def get_element(self, gene_id, polypeptideId):
        element = Element(
                id = None,
                biolink_class = "Gene",
                identifiers = {},
                names_synonyms = [],
                attributes = [],
                connections = [],
                source = self.info.name
        )
        # e.g., HGNC:1097
        get_connection_polypeptide_identifiers( polypeptideId, element, 'HUGO Gene Nomenclature Committee (HGNC)' )# query database for gene id for given polypeptide id
                  # (RESOURCE = HUGO Gene Nomenclature Committee (HGNC))
        return element


#################################################################
#
# Subclass of DrugBankInteractionsTransformer
#
class DrugBankProteinInteractionsTransformer(DrugBankInteractionsTransformer):
    def __init__(self, target_type):
        super().__init__(target_type, definition_file='info/protein_interactions_transformer_info.json')
        self.info.knowledge_map.predicates[0].predicate = biolinkClass_dict[target_type]
        self.info.name = "DrugBank " + target_type + " proteins transformer"

    def get_element(self, protein_id, polypeptideId):

        element = Element(
            id = None,
            biolink_class = "Protein",
            identifiers = {},
            names_synonyms = [],
            attributes = [],
            connections = [],
            source = self.info.name
        )
        get_connection_polypeptide_identifiers(polypeptideId, element, 'UniProtKB' )
                 # query database for protein id for given polypeptide id
                 # (RESOURCE = UniProtKB )
        return element


connection = sqlite3.connect("data/DrugBank.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False) 
connection.row_factory = sqlite3.Row


def get_db():
    return connection

def close_db(self, e=None):
    pass


def find_drug_by_drug_bank_id(drug_name):
    query = """
        SELECT DISTINCT DRUG_ID, DRUG_BANK_ID, DRUG_TYPE, DRUG_NAME 
        FROM DRUG
        WHERE DRUG_BANK_ID = ?
    """
    dbConnection = get_db() 
    cur = dbConnection.cursor()
    cur.execute(query,(drug_name,))
    return cur.fetchall()


def find_drug_by_name(drug_name):
    query = """
        SELECT DISTINCT DRUG_ID, DRUG_BANK_ID, DRUG_TYPE, DRUG_NAME 
        FROM DRUG
        WHERE DRUG_BANK_ID = ? OR DRUG_NAME = ?
    """
    dbConnection = get_db() 
    cur = dbConnection.cursor()
    cur.execute(query,(drug_name,drug_name))
    return cur.fetchall()


def find_drug_by_synonym(synonym):
    query = """
        SELECT DISTINCT DRUG.DRUG_ID, DRUG_BANK_ID, DRUG_TYPE, DRUG_NAME FROM DRUG
        INNER JOIN SYNONYM ON SYNONYM.DRUG_ID = DRUG.DRUG_ID
        WHERE SYNONYM.SYNONYM = ?
    """
    dbConnection = get_db() 
    cur = dbConnection.cursor()
    cur.execute(query,(synonym,))
    return cur.fetchall()


def find_drug_by_identifier(identifier, source = None):
    query = """
        SELECT DISTINCT DRUG.DRUG_ID, DRUG_BANK_ID, DRUG_TYPE, DRUG_NAME
        FROM DRUG
        INNER JOIN DRUG_IDENTIFIER ON DRUG_IDENTIFIER.DRUG_ID = DRUG.DRUG_ID
        JOIN RESOURCE ON DRUG_IDENTIFIER.RESOURCE_ID = RESOURCE.RESOURCE_ID
        WHERE DRUG_IDENTIFIER.IDENTIFIER = ?
    """

    params = (identifier,)
    if source is not None:
        query = query + " AND RESOURCE.RESOURCE = ?"
        params = (identifier,source)
    dbConnection = get_db()   
    cur = dbConnection.cursor()
    cur.execute(query, params)
    return cur.fetchall()


#############################################
# 
# Determine if "name" is a:
# (1) DRUGBANK Id
# (2) Drug synonym
# (3) identifier
#
def find_drug(name):
    if name.upper().startswith(DRUGBANK.upper()):
        return find_drug_by_drug_bank_id(name[9:])
    drugs = find_drug_by_name(name)           # name may be ordinary name
    if len(drugs) == 0:
        drugs = find_drug_by_synonym(name)
    if len(drugs) == 0:
        drugs = find_drug_by_identifier(name) # name may be an inchikey
    return drugs


def get_synonyms(drug_id):
    query = """
        SELECT SYNONYM FROM SYNONYM WHERE DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur = dbConnection.cursor()
    cur.execute(query,(drug_id,))
    return [synonym[0] for synonym in cur.fetchall()]



###########################################################################################
#
# Exclude: 
# Drugs Product Database (DPD), KEGG Drug, PubChem Substance, RxCUI, Wikipedia, PharmGKB,
# ChemSpider, IUPHAR, Therapeutic Targets Database, ZINC
#

def get_identifiers(drug_id):
#    {  RESOUCE : field name }
    fieldname_map_dict = { 
        'PubChem Compound' : 'pubchem',
        'ChEMBL'   : 'chembl',
        'ChEBI'    : 'chebi',
        'DrugBank' : 'drugbank',
        'HMDB'     : 'hmdb',
        'InChIKey' : 'inchikey',
        'InChI'	   : 'inchi',
        'SMILES'   : 'smiles',
        'MESH'     : 'mesh',
        'UNII'     : 'unii',
        'ChemBank' : 'chembank',
        'CAS'      : 'cas',
        'DrugCentral'      : 'drugcentral',
        'Mychem_Info'      : 'mychem_info',
        'Mygene_Info'      : 'mygene_info',
        'Disease_Ontology' : 'disease_ontology',
        'KEGG Compound'    : 'kegg',
        'Guide to Pharmacology' : 'gtopdb',
        'BindingDB': 'bindingdb',
        'PDB'      : 'pdb',
        'HUGO Gene Nomenclature Committee (HGNC)' : 'hgnc',
        #'UniProtKB': 'uniprot',
    }


    query = """
            SELECT 
                RESOURCE,
                IDENTIFIER 
            FROM DRUG_IDENTIFIER
            JOIN RESOURCE ON (RESOURCE.RESOURCE_ID = DRUG_IDENTIFIER.RESOURCE_ID)
            WHERE DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur = dbConnection.cursor()
    cur.execute(query,(drug_id,))
    identifiers = {}
    prefix = ''

    for row in cur.fetchall():
        if row['RESOURCE'] not in ['Drugs Product Database (DPD)', 'KEGG Drug', 'PubChem Substance', 'RxCUI', 'Wikipedia',
                                   'PharmGKB', 'ChemSpider', 'IUPHAR', 'Therapeutic Targets Database', 'ZINC', 'UniProt Accession',
                                   'GenBank','GenBank Gene Database','GenBank Protein Database']:       
            fieldName = fieldname_map_dict.get(str(row['RESOURCE']))
            prefix = get_find_MoleProPrefix(fieldName)
            if fieldName is not None:
                identifiers[fieldName] = prefix + row['IDENTIFIER']
    return identifiers


def prefix(prefix, value):
    return prefix + value if value is not None else None

def de_prefix(prefix, value):
    return value[len(prefix):] if value.upper().startswith(prefix.upper()) else value


##########################################
#
# Process the tuple of a drug's identifiers
# (1) Drug Id
# (2) DrugBank Id
# (3) Drug name
#
# Element.id should be a CURIE
# (1) CID if available, 
# (2) DrugBank otherwise.
#
def get_drug(transformer, row, biolink_class):
    drug_id = row['DRUG_ID']
    drug_bank_id = prefix('DrugBank:',row['DRUG_BANK_ID'])
    drug_name = row['DRUG_NAME']
    identifiers = get_identifiers(drug_id)
    identifiers['drugbank'] = drug_bank_id
    compound_id = 'CID:'+identifiers['PubChem Compound'] if 'PubChem Compound' in identifiers else drug_bank_id

   # Create an object of type openapi_server.models.element  (version 2.2)
    element = transformer.Element(
                    id = compound_id,
                    biolink_class = biolink_class,
                    identifiers = identifiers,
                    names_synonyms = [transformer.Names(name=drug_name,
                                        synonyms=[]
                                        )], # add names & synonyms from the database
                    attributes = []
                )
    get_names(element, drug_id)
    return element


def get_targets(drug_id):
    query = """
        SELECT TARGET.GENE_ID, TARGET_MAP.ACTIONS FROM TARGET
        INNER JOIN TARGET_MAP ON TARGET.TARGET_ID = TARGET_MAP.TARGET_ID
        WHERE TARGET_MAP.DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur = dbConnection.cursor()
    cur.execute(query,(drug_id,))
    return cur.fetchall()


def get_inhibitors(gene_id, target_type):
    query = """
        SELECT DISTINCT
        DRUG.DRUG_ID,
        DRUG_BANK_ID,
        DRUG_TYPE,
        DRUG_NAME,
        TAG,
        CONNECTION_ID,
        KNOWN_ACTION
        FROM POLYPEPTIDE_IDENTIFIER
        JOIN POLYPEPTIDE ON POLYPEPTIDE.POLYPEPTIDE_ID = POLYPEPTIDE_IDENTIFIER.POLYPEPTIDE_ID
        JOIN TARGET ON TARGET.TARGET_ID = POLYPEPTIDE.TARGET_ID
        JOIN CONNECTION ON CONNECTION.TARGET_ID = POLYPEPTIDE.TARGET_ID
        JOIN TAG ON (TAG.TAG_ID = CONNECTION.TAG_ID)
        JOIN DRUG ON DRUG.DRUG_ID = CONNECTION.DRUG_ID
        WHERE TAG = ? AND POLYPEPTIDE_IDENTIFIER.IDENTIFIER = ?
    """
    dbConnection = get_db() 
    cur = dbConnection.cursor()
    cur.execute(query,(target_type,gene_id))
    return cur.fetchall()


###################################################################
# Used by Compound Producer
# Populate the Element with attributes from various DrugBank tables
#
def get_attributes(transformer, drug_id):
    attributes = []
    #attributes.extend(get_category_attributes(transformer, drug_id))
    attributes.extend(get_property_attributes(transformer, drug_id))
    attributes.extend(get_reference_attributes(transformer, drug_id))
    attributes.extend(get_patent_attributes(transformer, drug_id))
    attributes.extend(get_snp_attributes(transformer, drug_id))
    return attributes


##################################################################################
# Used by Compound Producer
# Attributes (SOURCE+' '+TAG -> name/type, CATEGORY_XREF || CATEGORY -> value)
# SOURCE+' '+TAG, if SOURCE is null, use TAG only.
# CATEGORY_XREF || CATEGORY use CATEGORY_XREF if it is not null, otherwise use CATEGORY.
#
def get_category_attributes(self, transformer, drug_id):
    query1 = """
            SELECT DISTINCT
                SOURCE,
                TAG, 
                CATEGORY,
                CATEGORY_XREF
            FROM CATEGORY_MAP
            JOIN CATEGORY ON (CATEGORY.CATEGORY_ID = CATEGORY_MAP.CATEGORY_ID)
            JOIN TAG ON (TAG.TAG_ID = CATEGORY.TAG_ID)
            WHERE DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur1 = dbConnection.cursor()
    cur1.execute(query1,(drug_id,))

    attributes = []
    for row in cur1.fetchall(): 
        name = ''
        atype = ''
        value = ''
        if (row['CATEGORY_XREF'] is not None ):
            value = row['CATEGORY_XREF']
        else:
            value = row['CATEGORY']
        if (row['SOURCE'] is not None ): 
            if ( len(row['SOURCE'].strip()) > 0  ):
                name = row['SOURCE'] + ' ' + row['TAG']
                atype = row['SOURCE'] + ' ' + row['TAG']
        else:
            name = row['TAG']
            atype = row['TAG']
        attributes.append(
                        self.Attribute(
                            name= name,
                            value= value,
                            type= atype
                            )
                        )
    return attributes


#############################################################
# Used by Compound Producer
# Attributes (TAG/KIND -> name/type, VALUE -> value)
# attributes (TAG|+"/"+KIND -> name/&type, VALUE -> value)
#
def get_property_attributes(transformer, drug_id):

    query2 = """
            SELECT   
                DRUG_ID,
                TAG,
                KIND,
                VALUE,
                SOURCE
            FROM DRUG_PROPERTY
            JOIN PROPERTY ON (PROPERTY.PROPERTY_ID = DRUG_PROPERTY.PROPERTY_ID)
            JOIN TAG ON (TAG.TAG_ID = PROPERTY.TAG_ID)
            WHERE DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur2 = dbConnection.cursor()
    cur2.execute(query2,(drug_id,))

    attributes = []
    for row in cur2.fetchall(): 
        name1 = row['TAG']
        name2 = ''
        value = row['VALUE']
        if (row['KIND'] is not None ):
            if ( len(row['KIND'].strip()) > 0  ):
                name2 = '/' + row['KIND']
        name = name1 + name2
        attributes.append(
                transformer.Attribute(
                        name= name,
                        value= value,
                        type= name
                        )
                    )
    return attributes


#############################################################
# Used by Compound Producer
# Attribute for drug references :
#
def get_reference_attributes(transformer, drug_id):
    query3 = """
            SELECT 
                PUBMED_ID,
                ISBN,
                CITATION,
                TITLE,
                URL,
                REFERENCE_TYPE
            FROM DRUG_REFERENCE
            JOIN REFERENCE ON DRUG_REFERENCE.REFERENCE_ID = REFERENCE.REFERENCE_ID
            JOIN REFERENCE_TYPE ON REFERENCE.REFERENCE_TYPE_ID = REFERENCE_TYPE.REFERENCE_TYPE_ID
            WHERE DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur3 = dbConnection.cursor()
    cur3.execute(query3,(drug_id,))

    attributes = []
    for row in cur3.fetchall(): 
        name = row['REFERENCE_TYPE']
        atype = 'biolink:Publication'
        value = None
        if row['PUBMED_ID'] is not None:
            value = 'PMID:' + str(row['PUBMED_ID'])
        else:
            if row['URL'] is not None:
                value = row['URL']
        url = row['URL']
        if value is not None:
            attributes.append(
               transformer.Attribute(
                        name= name,
                        value= value,
                        type= atype,
                        url = url
                        )
                    )
    return attributes


#############################################################
# Used by Compound Producer
# Attribute for patents :
#        
def get_patent_attributes(self, drug_id):
    query4 = """
    SELECT
    PATENT_NUMBER,
    APPROVED,
    EXPIRES,
    COUNTRY
    FROM PATENT
    JOIN PATENT_MAP ON PATENT.PATENT_ID = PATENT_MAP.PATENT_ID
    JOIN DRUG ON PATENT_MAP.DRUG_ID = DRUG.DRUG_ID
    JOIN COUNTRY ON PATENT.COUNTRY_ID = COUNTRY.COUNTRY_ID
    WHERE DRUG.DRUG_ID = ?
    ORDER BY APPROVED ASC;
    """
    dbConnection = get_db() 
    cur4 = dbConnection.cursor()
    cur4.execute(query4,(drug_id,))

    attributes = []
    for row in cur4.fetchall(): 
        name = row['COUNTRY'] + ' patent'
        atype = 'patent'
        value = row['PATENT_NUMBER']
        attributes.append(
                self.Attribute(
                        name= name,
                        value= value,
                        type= atype
                        )
                    )
    return attributes


#############################################################
# Used by Compound Producer
# Attribute for SNP effects :
#        
def get_snp_attributes(self, drug_id):
    query5 = """
    SELECT
        TAG,
        GENE_SYMBOL,
        PROTEIN_NAME,
        RS_ID,
        ALLELLE,
        ADVERSE_REACTION,
        DESCRIPTION,
        PUBMED_ID,
        DEFINING_CHANGE
    FROM SNP_EFFECT
    JOIN TAG ON SNP_EFFECT.TAG_ID = TAG.TAG_ID
    WHERE DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur5 = dbConnection.cursor()
    cur5.execute(query5,(drug_id,))

    attributes = []
    for row in cur5.fetchall(): 
        name = 'SNP ' + str(row['GENE_SYMBOL']) + ' ' + str(row['RS_ID'])
        if str(row['TAG']) == 'reaction' :
            atype = 'snp adverse drug reaction'
        else:
            if str(row['TAG']) == 'effect':
                atype = 'snp effect'
        value = str(row['DESCRIPTION'])
        attributes.append(
                self.Attribute(
                        name= name,
                        value= value,
                        type= atype
                        )
                    )
    return attributes    


#############################################################
# Used by Compound Producer
# Attribute for PFAM info :
#        
def get_pfam_attributes(self, element):
    query6 = """
            SELECT 
                TAG,
                TARGET_IDENTIFIER,
                NAME AS TARGET_NAME,
                POLYPEPTIDE_NAME,
                PFAM_IDENTIFIER,
                PFAM_NAME
            FROM CONNECTION
            JOIN TAG ON CONNECTION.TAG_ID = TAG.TAG_ID
            JOIN TARGET ON CONNECTION.TARGET_ID = TARGET.TARGET_ID
            JOIN POLYPEPTIDE ON TARGET.TARGET_ID = POLYPEPTIDE.TARGET_ID
            JOIN PFAM_MAP ON POLYPEPTIDE.POLYPEPTIDE_ID = PFAM_MAP.POLYPEPTIDE_ID
            JOIN PFAM ON PFAM.PFAM_ID = PFAM_MAP.PFAM_MAP_ID
            WHERE DRUG_ID = ?
"""
    dbConnection = get_db() 
    cur6 = dbConnection.cursor()
    cur6.execute(query6,(element.id,))
    for row in cur6.fetchall(): 
        name = row['TARGET_NAME']
        atype = row['PFAM_NAME']
        value = row['PFAM_IDENTIFIER']
        element.attributes.append(
                self.Attribute(
                        name= name,
                        value= value,
                        type= atype
                        )
                    )
    close_db(self, e=None) 



#############################################################
# Used By DrugBank interactions transformer
# 
# 
# Connection info for gene interaction :
#-- => connection attributes (KNOWN_ACTION, TARGET_NAME, TARGET_IDENTIFIER)
#
#
def get_compound_targets(transformer, info_name, target_type, connectionsDict, drug, compound):
    targetList = []

    query8 = """
            SELECT 
                CONNECTION_ID,
                POLYPEPTIDE_ID,
                TAG,
                KNOWN_ACTION,
                POLYPEPTIDE_NAME
            FROM CONNECTION
            JOIN TAG ON (TAG.TAG_ID = CONNECTION.TAG_ID)
            JOIN TARGET ON (TARGET.TARGET_ID = CONNECTION.TARGET_ID)
            LEFT JOIN POLYPEPTIDE ON (POLYPEPTIDE.TARGET_ID = TARGET.TARGET_ID)
            WHERE TAG = ? AND DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur8 = dbConnection.cursor()
    cur8.execute(query8,(target_type,drug['DRUG_ID']))

    for row in cur8.fetchall(): 
        aType = biolinkClass_dict[row['TAG']]
        targetKnownAction = row['KNOWN_ACTION']
        polypeptide_id = row['POLYPEPTIDE_ID']

        geneConnection = transformer.Connection(compound.id, transformer.PREDICATE, transformer.INVERSE_PREDICATE)    
        geneConnection.type = aType
 
        geneConnection.attributes.append(
                            transformer.Attribute(
                                    'known action',
                                    targetKnownAction,
                                    'known action'
                                    )
                                )

        get_connection_properties(transformer, info_name, row['CONNECTION_ID'], geneConnection)   # add attributes from CONNECTION_PROPERTY table
        get_connection_references(transformer, info_name, row['CONNECTION_ID'], geneConnection)   # add attributes from REFERENCE table
        connectionsDict[polypeptide_id] = geneConnection
        targetList.append(polypeptide_id)
    return targetList

    
#############################################################
#
#   Used by the Compound Producer to format the various names
#
#
def get_names(element, drug_id):
    query9 = """
            SELECT
                SYNONYM,
                LANGUAGE,
                CODER
            FROM SYNONYM
            LEFT JOIN LANGUAGE ON LANGUAGE.LANGUAGE_ID = SYNONYM.LANGUAGE_ID
            LEFT JOIN CODER ON CODER.CODER_ID = SYNONYM.CODER_ID
            WHERE DRUG_ID = ?
    """
    dbConnection = get_db() 
    cur9 = dbConnection.cursor()
    cur9.execute(query9,(drug_id,))

    for row in cur9.fetchall(): 
        name = row['SYNONYM']
        if row['LANGUAGE'] is not None:
            language = '[' + row['LANGUAGE'] + ']'
        else:
            language = ''

        coders = str(row['CODER']).split('/') 
        for code in coders:  
            source = code + language + '@DrugBank'
        #   add drug name from the drugs table
            notFound = True
            for nameObj in element.names_synonyms:
                if  nameObj.source == source:
                    if nameObj.synonyms == [] and source != 'DrugBank':
                        nameObj.synonyms.append(nameObj.name)
                        nameObj.name = None
                    nameObj.synonyms.append(name)
                    notFound = False
            if notFound:
                element.names_synonyms.append(
                    Names(
                        name = name,
                        synonyms = [],
                        source = source
                    ))
            



########################################################################
#
# Used by class DrugBankInteractionsTransformer
# => connection attributes (TAG -> name/type, VALUE -> value)
# 
#
def get_connection_properties(self, info_name, connectionId, geneConnection):
    query10 = """
            SELECT 
                TAG,
                KIND,
                VALUE,
                SOURCE
            FROM CONNECTION_PROPERTY
            JOIN PROPERTY ON (CONNECTION_PROPERTY.PROPERTY_ID = PROPERTY.PROPERTY_ID)
            JOIN TAG ON (TAG.TAG_ID = PROPERTY.TAG_ID)
            WHERE CONNECTION_PROPERTY.CONNECTION_ID = ?
            """
    dbConnection = get_db() 
    cur10 = dbConnection.cursor()
    cur10.execute(query10,(connectionId,))
    for row in cur10.fetchall(): 
        name = row['TAG']
        type = row['TAG']
        value= row['VALUE']

        geneConnection.attributes.append(
                self.Attribute(
                        name,
                        value,
                        type,
                        )
                    )


########################################################################
#
# Used by class DrugBankInteractionsTransformer
#
# For each connection obtain references:
#   article
#   attachment
#   link
#   textbook
#
def get_connection_references(self, info_name, connectionId, geneConnection):      
    query11 = """
            SELECT 
                REFERENCE_TYPE,
                PUBMED_ID,
                ISBN,
                CITATION,
                TITLE,
                URL
            FROM CONNECTION_REFERENCE
            JOIN REFERENCE ON (REFERENCE.REFERENCE_ID = CONNECTION_REFERENCE.REFERENCE_ID)
            JOIN REFERENCE_TYPE ON (REFERENCE_TYPE.REFERENCE_TYPE_ID = REFERENCE.REFERENCE_TYPE_ID)
            WHERE CONNECTION_REFERENCE.CONNECTION_ID = ?
        """
    dbConnection = get_db() 
    cur11 = dbConnection.cursor()
    cur11.execute(query11,(connectionId,))

    for row in cur11.fetchall(): 
        name = row['REFERENCE_TYPE']
        atype = 'biolink:Publication'
        url  = row['URL']
        value = None
        if (row['PUBMED_ID'] is not None):
            value = 'PMID:' + row['PUBMED_ID']
        elif (row['URL'] is not None):
            value = row['URL']
        if name is not None and value is not None:
            #name, value, type=None, value_type = None, url=None, description=None):
            geneConnection.attributes.append(
                self.Attribute(
                        name,
                        value,
                        atype,
                        url
                        )
            )



def get_connection_polypeptide_identifiers(polypeptideId, element, resource):

    resourceFieldName = ''
    protein_curie_prefix = ''
    if (resource == 'HUGO Gene Nomenclature Committee (HGNC)'):
        resourceFieldName = 'hgnc'
    elif (resource == 'UniProtKB'):
        resourceFieldName = 'uniprot'
        protein_curie_prefix = get_find_MoleProPrefix(resourceFieldName)


    query12 = """
            SELECT IDENTIFIER
            FROM POLYPEPTIDE_IDENTIFIER
            JOIN RESOURCE ON POLYPEPTIDE_IDENTIFIER.RESOURCE_ID = RESOURCE.RESOURCE_ID
            WHERE RESOURCE = ?
            AND POLYPEPTIDE_IDENTIFIER.POLYPEPTIDE_ID = ? 
            """
    dbConnection = get_db() 
    cur12 = dbConnection.cursor()
    cur12.execute(query12,(resource, polypeptideId,))
  
    for row in cur12.fetchall(): 
        if(row['IDENTIFIER'] is not None):
            iD = row['IDENTIFIER']
            if ':' in iD:
                element.id = iD 
            else:
                element.id = protein_curie_prefix + iD      # May Need CURIE
            element.identifiers = {resourceFieldName:element.id}
            

#################################################
#
# Used by class DrugBankInteractionsTransformer
#
def get_target_names(transformer, polypeptideId, element):
    query14 = """
        SELECT POLYPEPTIDE_NAME
        FROM POLYPEPTIDE
        WHERE POLYPEPTIDE.POLYPEPTIDE_ID = ?
    """
    dbConnection = get_db()     
    cur14 = dbConnection.cursor()
    cur14.execute(query14,(polypeptideId,))

    polypeptideName = None
    for row in cur14.fetchall(): 
        polypeptideName = row['POLYPEPTIDE_NAME']

    element.names_synonyms.append(
                    transformer.Names(
                        name = polypeptideName,
                        synonyms = []
                    )
    )


#################################################
#
# Used by class DrugBankInteractionsTransformer
# - synonyms are provided as tag value
#
def get_target_attributes(transformer, polypeptideId, element):
    query15 = """
        SELECT DISTINCT TAG, VALUE
        FROM POLYPEPTIDE_PROPERTY
        JOIN PROPERTY ON POLYPEPTIDE_PROPERTY.PROPERTY_ID = PROPERTY.PROPERTY_ID
        JOIN TAG ON PROPERTY.TAG_ID = TAG.TAG_ID
        WHERE POLYPEPTIDE_PROPERTY.POLYPEPTIDE_ID = ?
    """
    dbConnection = get_db()     
    cur15 = dbConnection.cursor()
    cur15.execute(query15,(polypeptideId,))

    for row in cur15.fetchall(): 
        name = row['TAG']
        aType= row['TAG']
        value= row['VALUE']
        if(name == "synonym"):
            element.names_synonyms[0].synonyms.append(value)
        else:
            if name != "go-classifier":
                element.attributes.append(
                            transformer.Attribute(
                                    name,
                                    value,
                                    aType
                                    )
        )



#######################################################################################################
#
# This function reads the spreadsheet downloaded from 
# https://docs.google.com/spreadsheets/d/1rCzl7Yec8fSa1hKOClxdm2ZomfvMpUODhYJVWj5DhBc/edit#gid=0
#
# The columns are:
# MolePro class	> Biolink class	> MolePro field name  > MolePro CURIE prefix > Biolink CURIE prefix
def get_prefix_mapping():
        sheet = []
        with open('data/prefixMap.csv', 'r') as data: 
            for line in csv.DictReader(data): 
                sheet.append(line)
        return sheet


########################################################################
# Lookup the required MoleProPrefix corresponding to the field name
# of a identifier
#
def get_find_MoleProPrefix(fieldname):
        for line in prefix_mapping:
            if (line['MolePro field name'] == fieldname):
                if line['MolePro CURIE prefix'] == '<none>' or line['MolePro CURIE prefix'] is None:
                    return ''
                else:
                    return str(line['MolePro CURIE prefix'])


prefix_mapping = get_prefix_mapping()   # load the spreadsheet of field name and prefixes
