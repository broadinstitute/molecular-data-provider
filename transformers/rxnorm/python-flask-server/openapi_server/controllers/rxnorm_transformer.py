import sqlite3

from transformers.transformer import Transformer
from openapi_server.models.element import Element
from openapi_server.models.names import Names
from openapi_server.models.connection import Connection
from openapi_server.models.attribute import Attribute


SOURCE = 'RxNorm'
RXNORM = 'RxNorm'
UNIISOURCE = 'UNII'

# because the connection is outside of the function, check_same_thread=False is needed.
connection = sqlite3.connect(
    "data/RXNORM+UNII.sqlite", check_same_thread=False)
# use actual column name instead of the numbers
connection.row_factory = sqlite3.Row


# RxNorm
# RxNorm provides normalized names for clinical drugs and links its names to many of the drug vocabularies commonly used in pharmacy management and drug interaction software,
# including those of First Databank, Micromedex, and Gold Standard Drug Database.
# By providing links between these vocabularies,
# RxNorm can mediate messages between systems not using the same software and vocabulary.
# RxNorm now includes the United States Pharmacopeia (USP) Compendial Nomenclature from the United States Pharmacopeial Convention.
# USP is a cumulative data set of all Active Pharmaceutical Ingredients (API).

# RxNorm is two things: a normalized naming system for generic and branded drugs;
# and a tool for supporting semantic interoperation between drug terminologies and pharmacy knowledge base systems.
#  The National Library of Medicine (NLM) produces RxNorm.

# Purpose of RxNorm
# Hospitals, pharmacies, and other organizations use computer systems to record and process drug information. Because these systems use many different sets of drug names, it can be difficult for one system to communicate with another. To address this challenge, RxNorm provides normalized names and unique identifiers for medicines and drugs. The goal of RxNorm is to allow computer systems to communicate drug-related information efficiently and unambiguously.

# Scope of RxNorm
# RxNorm contains the names of prescription and many over-the-counter drugs available in the United States. RxNorm includes generic and branded:

# 1. Clinical drugs - pharmaceutical products given to (or taken by) a patient with therapeutic intent
# 2. Drug packs - packs that contain multiple drugs, or drugs designed to be administered in a specified sequence
# Non-therapeutic radiopharmaceuticals, bulk powders, contrast media, food, dietary supplements, and medical devices are all out-of-scope for RxNorm. Medical devices include but are not limited to bandages and crutches.


class RxNormCompoundProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')

    def produce(self, controls):
        #print(controls)
        compound_list = []
        names = controls['compounds'].split(';')
    #   find drug data for each compound name that were submitted
        for name in names:
            name = name.strip()

            if name.startswith('UNII:'):
                for compound in self.find_compound_by_unii(name[5:]):
                    compound_list.append(compound)
            else:
                for compound in self.find_compound_by_name(name):
                    compound_list.append(compound)

        return compound_list

    def find_compound_by_name(self, name):
        """
            Find compound by a name
        """
        compounds = []
        # slect * is not a good practice rather than * distinct listing is better.

        query = """
        select
            distinct RXNCONSO.CODE

        from RXNCONSO
        join UNII on RXNCONSO.CODE = UNII.UNII
        where (RXNCONSO.STR = ? or UNII.PT = ? or UNII.INCHIKEY = ?)
        and UNII.INCHIKEY is not null
        and UNII.INCHIKEY != ''

        collate nocase;
        """
        cur = connection.execute(
            query, (name, name, name))  # in order to make the varible as a tuple of one explicitely.

        # TODO issue SQL query and collect results
        # for each hit (i.e., of the same drug name, an unlikely but possible occurrence)
        for row in cur.fetchall():
            id = "UNII:" + row['CODE']
            for compound in self.find_compound_by_unii(row['CODE']):
                compound.attributes.append(Attribute(
                    name='query name',
                    value=name,
                    provided_by=self.info.name,
                ))

            compounds.append(compound)

        return compounds

    def find_compound_by_unii(self, unii):
        """
            Find compound by a unii
        """
        # slect * is not a good practice rather than * distinct listing is better.
        id = "UNII:" + unii

        query = """
        select
            UNII.UNII,
            UNII.PT,
            UNII.RN,
            UNII.NCIT,
            UNII.PUBCHEM,
            UNII.INCHIKEY,
            UNII.SMILES,
            RXNCONSO.CODE
        from RXNCONSO
        join UNII on RXNCONSO.CODE = UNII.UNII
        where (UNII.UNII = ?)
        """
        cur = connection.execute(
            query, (unii,))  # in order to make the varible as a tuple of one explicitely.

        compound = Element(
            id=id,
            biolink_class='ChemicalSubstance',
            identifiers={'unii': unii},
            attributes=self.find_compound_attributes(unii),
            connections=[],
            source=self.info.name
        )

        # TODO issue SQL query and collect results
        # for each hit (i.e., of the same drug name, an unlikely but possible occurrence)
        for row in cur.fetchall():
            if (row['UNII'] == unii):
                compound.names_synonyms = [Names(name=row['PT'],
                                                 synonyms=[],
                                                 source=UNIISOURCE)]  # add names & synonyms from the database

                compound.identifiers = {
                    'unii': id,
                    'cas': 'CAS:' + row['RN'],
                    'ncit': 'NCIT:' + row['NCIT'],
                    'inchikey': row['INCHIKEY'],
                    'smiles': row['SMILES'],
                    'pubchem': 'CID:' + str(row['pubchem'])}

        return [compound]

    def find_compound_attributes(self, unii):
        """
            Find compound attribute
        """
        attributes = []
        # slect * is not a good practice rather than * distinct listing is better.

        query = """
        select
            UNII.UNII,
            UNII.MF,
            UNII.INGREDIENT_TYPE
        from UNII
        where (UNII.UNII = ?)
        """
        cur = connection.execute(
            query, (unii,))  # in order to make the varible as a tuple of one explicitely.

        for row in cur.fetchall():

            attribute = Attribute(
                name='molecular formula',
                value=row['MF'],
                type='molecular formula',
                provided_by=self.info.name,
                source=UNIISOURCE
            )
            attributes.append(attribute)
            attribute = Attribute(
                name='ingredient type',
                value=row['INGREDIENT_TYPE'],
                type='ingredient type',
                provided_by=self.info.name,
                source=UNIISOURCE
            )

            attributes.append(attribute)
        return attributes


# RxNorm


# https://www.nlm.nih.gov/research/umls/rxnorm/docs/appendix4.html
# RXNSAT spec sheet.

     
ttydict = {
    'SU':'substance',
    'IN':'ingredient',
    'SY':'synonym',
    'BN':'brand name',
    'PIN':'precise ingredient',
    'TMSY':'tall man lettering synonym',
    'SCD':'semantic clinical drug',
    'PSN':'prescribable name',
    'SBD':'semantic branded drug',
    'MIN':'multiple ingredients'
}

class RxNormDrugProducer(Transformer):

    variables = ['drugs']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/drugs_transformer_info.json')

    def produce(self, controls):
        #print(controls)
        drug_list = []
        names = controls['drugs'].split(';')
        # unii = con
    #   find drug data for each drug name that were submitted
        for name in names:
            name = name.strip()
            if name.startswith('RXCUI:'):
                for drug in self.find_drug_by_rxcui(name[6:]):
                    drug_list.append(drug)
            else:
                for drug in self.find_drug_by_name(name):
                    drug_list.append(drug)

        return drug_list

    def find_drug_by_name(self, name):
        """
            Find drug by a name
        """
        drugs = []
        # slect * is not a good practice rather than * distinct listing is better.

        query = """
        select
            distinct RXNCONSO.RXCUI
        from RXNCONSO
        where (RXNCONSO.STR = ?)

        collate nocase;
        """

        cur = connection.execute(
            query, (name,))  # in order to make the varible as a tuple of one explicitely.

        # TODO issue SQL query and collect results
        # for each hit (i.e., of the same drug name, an unlikely but possible occurrence)
        for row in cur.fetchall():
            id = "RXCUI:" + str(row['RXCUI'])
            for drug in self.find_drug_by_rxcui(row['RXCUI']):
                drug.attributes.append(Attribute(
                    name='query name',
                    value=name,
                    provided_by=self.info.name,
                ))

            drugs.append(drug)

        return drugs

    def find_drug_by_rxcui(self, rxcui):
        """
            Find drug by a rxcui
        """

        # slect * is not a good practice rather than * distinct listing is better.
        id = "RXCUI:" + str(rxcui)

        query = """
        select
            RXNCONSO.RXCUI,
            RXNCONSO.CODE
        from RXNCONSO

        where (RXNCONSO.RXCUI = ?)
        """

        cur = connection.execute(
            query, (rxcui, ))  # in order to make the varible as a tuple of one explicitely.
        drug = Element(
            id=id,
            biolink_class='Drug',
            identifiers={'rxnorm': id},
            attributes=self.find_drug_attributes(rxcui),
            names_synonyms=self.find_drug_synonyms(rxcui),
            connections=[],
            source=self.info.name
        )

        return [drug]

   

    def find_drug_attributes(self, rxcui):
        """
            Find drug attribute
        """
        attributes = []
        # slect * is not a good practice rather than * distinct listing is better.

        query = """
        select distinct
            RXNSAT.RXCUI,
            RXNSAT.ATN,
            RXNSAT.ATV

        from RXNSAT
        where (RXNSAT.RXCUI = ?)
        and RXNSAT.ATN != 'SPL_SET_ID'
        """
        cur = connection.execute(
            query, (rxcui,))  # in order to make the varible as a tuple of one explicitely.

        for row in cur.fetchall():
            attribute = Attribute(
                name=row['ATN'],
                value=row['ATV'],
                source=SOURCE,
                provided_by=self.info.name,
                type=row['ATN']
            )
            attributes.append(attribute)
        return attributes

    def find_drug_synonyms(self, rxcui):
        """
            Find drug synonyms
        """
        names_synonyms = []
        names_by_type = {}
        query = """
        select
            RXNCONSO.TTY,
            RXNCONSO.STR
        from RXNCONSO
        where RXNCONSO.RXCUI = ?
        """
        cur = connection.execute(
            query, (rxcui,))

        for row in cur.fetchall():
            
            name=row['STR']
            source=SOURCE
            type=ttydict[row['TTY']]
            if type not in names_by_type:
                name_synonyms = Names(
                    name = name,
                    synonyms = [],
                    source = type+'@'+source
                )
                names_by_type[type] = name_synonyms
                names_synonyms.append(name_synonyms)
            else:
                name_synonyms = names_by_type[type]
                name_synonyms.synonyms.append(name)
        return names_synonyms




reldict = {'AQ': 'Allowed qualifier',
           'CHD': 'has child relationship in a Metathesaurus source vocabulary',
           'DEL': 'Deleted concept',
           'PAR': 'has parent relationship in a Metathesaurus source vocabulary',
           'QB': 'can be qualified by.',
           'RB': 'has a broader relationship',
           'RL': 'the relationship is similar or "alike". the two concepts are similar or "alike". In the current edition of the Metathesaurus, most relationships with this attribute are mappings provided by a source, named in SAB and SL; hence concepts linked by this relationship may be synonymous, i.e. self-referential: CUI1 = CUI2. In previous releases, some MeSH Supplementary Concept relationships were represented in this way.',
           'RN': 'has a narrower relationship',
           'RO': 'has relationship other than synonymous, narrower, or broader',
           'RQ': 'related and possibly synonymous.',
           'RU': 'Related, unspecified',
           'SIB': 'has sibling relationship in a Metathesaurus source vocabulary.',
           'SY': 'source asserted synonymy.',
           'XR': 'Not related, no mapping',
           '': 'Empty relationship'}



class RxNormRelationTransformer(Transformer):
    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='info/relation_transformer_info.json')




    def map(self, collection, controls):
        substances = {}
        substance_list = []

        """
            Find drug rxcui relations
        """
        #print(collection)
        
        for element in collection:
            rxcui = element.identifiers['rxnorm']
            #print(rxcui)
            if rxcui.startswith('RXCUI:'):
                rxcui = rxcui[6:]


            for substance in self.find_drug(rxcui, element.id):
                if substance.id not in substances:
                    substances[substance.id] = substance
                    substance_list.append(substance)
                else:
                    substances[substance.id].connections.extend(substance.connections)

        return substance_list


    def find_drug(self, rxcui2, source_element_id):

        substance_list = []

        query = """
        SELECT
            RXNREL.RXCUI1,
            RXNREL.RXCUI2
        from RXNREL

        where RELA != 'has_tradename'
        and RELA != 'tradename_of'
        and RXNREL.RXCUI2 = ?
        """
        cur = connection.execute(
            query, (rxcui2, ))

        for row in cur.fetchall():
            rxcui1 = row['RXCUI1']

            if rxcui1 is not None:
            
                substance = Element(
                    id='RXCUI:' + str(rxcui1),
                    biolink_class='Drug',
                    identifiers={'rxnorm': 'RXCUI:' + str(rxcui1)},
                    connections=[],
                    source=self.info.name
                )
                substance_list.append(substance)

                connect = Connection(
                    source_element_id=source_element_id,
                    type=self.info.knowledge_map.predicates[0].predicate,
                    attributes=self.connection_attributes(rxcui1, rxcui2)
                )
                substance.connections.append(connect)

        return substance_list



    def connection_attributes(self, rxcui1, rxcui2):
        """
            connection attributes
        """
        attributes = []

        query = """
        SELECT
            RXNREL.RXCUI1,
            RXNREL.REL,
            RXNREL.RXCUI2,
            RXNREL.RELA
        from RXNREL

        where RXNREL.RXCUI1 = ? and RXNREL.RXCUI2 =?

        """
        cur = connection.execute(
            query, (rxcui1, rxcui2)) 

        for row in cur.fetchall():
       

            attribute = Attribute(
                name='rel',
                value=reldict[row['REL']],
                type='rel',
                source=SOURCE,
                provided_by=self.info.name
            )
            attributes.append(attribute)

            attribute = Attribute(
                name='rela',
                value=row['RELA'],
                type='rela',
                source=SOURCE,
                provided_by=self.info.name
            )
            attributes.append(attribute)

        return attributes
