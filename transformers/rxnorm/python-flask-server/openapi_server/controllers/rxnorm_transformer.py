import sqlite3
import re

from transformers.transformer import Transformer, Producer

UNIISOURCE = 'UNII'

inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


connection = sqlite3.connect("data/rxnorm.sqlite", check_same_thread=False)
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


class UniiProducer(Producer):
    variables = ['ingredient']

    def __init__(self, definition_file='info/unii_transformer_info.json'):
        super().__init__(self.variables, definition_file)


    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('ChemicalEntity')].count = unii_count()


    def find_names(self, name):
    #   find drug data for each compound name that were submitted
        if self.has_prefix('unii', name, self.OUTPUT_CLASS):
            return self.find_compound_by_unii(self.de_prefix('unii', name, self.OUTPUT_CLASS))
        else:
            return self.find_compound_by_name(name)


    def create_element(self, unii):
        compound = self.get_compound(unii)
        identifiers = self.get_compound_identifiers(compound)
        element = self.Element(
            id=identifiers['unii'],
            biolink_class = self.determine_biolink_class(identifiers),
            identifiers = identifiers,
            names_synonyms = self.get_compound_names(unii, compound),
            attributes = self.get_compound_attributes(compound),
        )
        return element


    def determine_biolink_class(self, identifiers):
        if 'inchikey' in identifiers and inchikey_regex.match(identifiers['inchikey']) is not None:
            return self.biolink_class('SmallMolecule')
        return self.biolink_class('ChemicalEntity')


    def find_compound_by_name(self, name):
        """
            Find compound by a name
        """
        query = """
        select distinct UNII
        from RXNCONSO
        join UNII on RXNCONSO.CODE = UNII.UNII
        where RXNCONSO.STR = ? collate nocase
        and RXNCONSO.TTY = 'SU'
        
        union

        select distinct UNII
        from UNII
        where UNII.PT = ? collate nocase
        """
        cur = connection.execute(
            query, (name,name))  # in order to make the varible as a tuple of one explicitely.
        return [row['UNII'] for row in cur.fetchall()]


    def find_compound_by_unii(self, unii):
        """
            Find compound by a unii
        """
        query = """
        select
            distinct UNII
        from UNII
        where UNII.UNII = ?
        """
        cur = connection.execute(
            query, (unii,))  # in order to make the varible as a tuple of one explicitely.
        return [row['UNII'] for row in cur.fetchall()]


    def get_compound(self, unii):
        """
            Find compound by a unii
        """
        query = """
        select
            UNII,
            PT,
            RN,
            NCIT,
            PUBCHEM,
            NCBI,
            INCHIKEY,
            SMILES,
            MF,
            INGREDIENT_TYPE
        from UNII
        where UNII = ?
        """
        cur = connection.execute(
            query, (unii,))  # in order to make the varible as a tuple of one explicitely.
        compound = None
        for row in cur.fetchall():
            compound = row
        return compound 


    def get_compound_identifiers(self, row):
        identifiers = {}
        identifiers['unii'] = self.add_prefix('unii',row['UNII'])
        if row['inchikey'] is not None and row['inchikey'] != '':
            identifiers['inchikey'] = row['INCHIKEY']
        if row['RN'] is not None and row['RN'] != '':
            identifiers['cas'] = self.add_prefix('cas',row['RN'],'compound')
        if row['PUBCHEM'] is not None and row['PUBCHEM'] != '':
            identifiers['pubchem'] = self.add_prefix('pubchem',row['PUBCHEM'],'compound')
        if row['NCIT'] is not None and row['NCIT'] != '':
            identifiers['nci_thesaurus'] = self.add_prefix('nci_thesaurus',row['NCIT'],'compound')
        if row['SMILES'] is not None and row['SMILES'] != '':
            identifiers['smiles'] = row['SMILES']
        return identifiers


    def get_compound_names(self, unii, compound):
        """
            Find compound by a name
        """
        query = """
        select
            LAT,
            TTY,
            STR
        from RXNCONSO
        where RXCUI in (
            select distinct RXNCONSO.RXCUI
            from RXNCONSO
            join UNII on RXNCONSO.CODE = UNII.UNII
            where UNII.UNII = ?
            and RXNCONSO.TTY = 'SU'
            and UNII.INCHIKEY is not null
            and UNII.INCHIKEY != ''
            and SUPPRESS = 'N'
            )
        """
        cur = connection.execute(
            query, (unii,))  # in order to make the varible as a tuple of one explicitely.

        ingredient = None
        ingredient_synonyms = []
        synonyms = []
        for row in cur.fetchall():
            tty = row['TTY']
            if tty == 'PIN':
                if ingredient is None:
                    ingredient = row['STR']
                else:
                    ingredient_synonyms.append(ingredient)
                    ingredient = row['STR']
            elif tty == 'IN':
                if ingredient is None:
                    ingredient = row['STR']
                else:
                    ingredient_synonyms.append(row['STR'])
            else:
                synonyms.append(row['STR'])
        names = [self.Names(name = compound['PT'], name_source = UNIISOURCE)]
        if ingredient is not None:
            self.Names(name = ingredient, synonyms = ingredient_synonyms, type = 'ingredient')
        if len(synonyms) > 0:
            self.Names(name = None, synonyms = synonyms, type = 'synonym')
        
        return names


    def get_compound_attributes(self, row):
        """
            Find compound attribute
        """
        attributes = []
        if row['MF'] is not None and row['MF'] != '':
            attribute = self.Attribute(
                name='MF',
                value=str(row['MF']),
                type='molecular formula'
            )
            attribute.attribute_source = UNIISOURCE
            attributes.append(attribute)
        if row['INGREDIENT_TYPE'] is not None and row['INGREDIENT_TYPE'] != '':
            attribute = self.Attribute(
                name='INGREDIENT_TYPE',
                value=str(row['INGREDIENT_TYPE']),
                type='ingredient type'
            )
            attribute.attribute_source = UNIISOURCE
            attributes.append(attribute)
        if row['NCBI'] is not None and row['NCBI'] != '':
            attribute = self.Attribute(
                name='NCBI',
                value='NCBITaxon:'+str(row['NCBI']),
                type='biolink:in_taxon'
            )
            attribute.attribute_source = UNIISOURCE
            attributes.append(attribute)
        return attributes


class RxNormCompoundProducer(UniiProducer):

    variables = ['compound']

    def __init__(self):
        super().__init__(definition_file='info/molecules_transformer_info.json')


    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = compound_count()


    def find_names(self, name):
    #   find drug data for each compound name that were submitted
        if inchikey_regex.match(name) is not None:
            return self.find_compound_by_inchikey(name)
        else:
            return super().find_names(name)


    def create_element(self, unii):
        element = super().create_element(unii)
        if 'inchikey' in element.identifiers and inchikey_regex.match(element.identifiers['inchikey']) is not None:
            return element
        return None


    def find_compound_by_inchikey(self, unii):
        """
            Find compound by a inchikey
        """
        query = """
        select
            distinct UNII
        from UNII
        where UNII.INCHIKEY = ?
        and UNII.INCHIKEY is not null
        and UNII.INCHIKEY != '';
        """
        cur = connection.execute(
            query, (unii,))  # in order to make the varible as a tuple of one explicitely.
        return [row['UNII'] for row in cur.fetchall()]


# RxNorm


# https://www.nlm.nih.gov/research/umls/rxnorm/docs/appendix4.html
# RXNSAT spec sheet.

     
ttydict = {
    'BN':'brand name',
    'BPCK':'brand name pack',
    'DP': 'DP',
    'GPCK':'generic pack',
    'IN':'ingredient',
    'MIN':'multiple ingredients',
    'MTH_RXN_DP': 'MTH_RXN_DP',
    'PIN':'precise ingredient',
    'PSN':'prescribable name',
    'PT': 'PT',
    'SBD':'semantic branded drug',
    'SBDC':'semantic branded drug component',
    'SBDF':'semantic branded drug form',
    'SBDG':'semantic branded drug form group',
    'SCD':'semantic clinical drug',
    'SCDC':'semantic clinical drug component',
    'SCDF':'semantic clinical drug form',
    'SCDG':'semantic clinical drug form group',
    'SU':'substance',
    'SY':'synonym',
    'TMSY':'tall man lettering synonym',
}

class RxNormDrugProducer(Producer):

    variables = ['drug']

    def __init__(self, definition_file='info/drugs_transformer_info.json'):
        super().__init__(self.variables, definition_file)


    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('Drug')].count = drug_count()


    def find_names(self, name):
    #   find drug data for each drug name that were submitted
        if self.has_prefix('rxnorm', name, self.OUTPUT_CLASS):
            return self.get_primary_rxcui(self.de_prefix('rxnorm', name, self.OUTPUT_CLASS))
        else:
            return self.find_drug_by_name(name)


    def find_drug_by_name(self, name):
        """
            Find drug by a name
        """
        query = """
        select
            distinct RXNCONSO.RXCUI
        from RXNCONSO
        where (RXNCONSO.STR = ?)

        collate nocase;
        """
        cur = connection.execute(
            query, (name,))  # in order to make the varible as a tuple of one explicitely.
        rxcuis = set()
        for row in cur.fetchall():
            for rxcui in self.get_primary_rxcui(row['RXCUI']):
                rxcuis.add(rxcui)
        return rxcuis


    def get_primary_rxcui(self, rxcui):
        primary_rxcuis = self.find_primary_rxcui(rxcui)
        if len(primary_rxcuis) == 0:
            primary_rxcuis = self.find_mapped_rxcui(rxcui)
        if len(primary_rxcuis) == 0:
            primary_rxcuis = self.find_any_rxcui(rxcui)
        return primary_rxcuis


    def find_primary_rxcui(self, rxcui):
        """
            Find primary_rxcui
        """
        query = """
        select
            distinct PRIMARY_RXCUI
        from DRUG_MAP

        where PRIMARY_RXCUI = ?
        """
        cur = connection.execute(query, (rxcui, ))
        return [row['PRIMARY_RXCUI'] for row in cur.fetchall()]


    def find_mapped_rxcui(self, rxcui):
        """
            Find primary_rxcui
        """
        query = """
        select
            distinct PRIMARY_RXCUI
        from DRUG_MAP

        where RXCUI = ?
        """
        cur = connection.execute(query, (rxcui, ))
        return [row['PRIMARY_RXCUI'] for row in cur.fetchall()]


    def find_any_rxcui(self, rxcui):
        """
            Find drug by a rxcui
        """
        query = """
        select
            distinct RXNCONSO.RXCUI
        from RXNCONSO

        where (RXNCONSO.RXCUI = ?)
        """

        cur = connection.execute(
            query, (rxcui, ))  # in order to make the varible as a tuple of one explicitely.
        return [row['RXCUI'] for row in cur.fetchall()]


    def create_element(self, rxcui):
        element_id = self.add_prefix('rxnorm', rxcui)
        rxcuis = self.get_rxcuis(rxcui)
        identifiers = {
            'rxnorm': element_id, 
            'rxcui': [self.add_prefix('rxnorm', rxcui) for rxcui in rxcuis]
        }
        element = self.Element(
            id = element_id,
            biolink_class = self.biolink_class('Drug'),
            identifiers = identifiers,
            names_synonyms = self.find_drug_synonyms(rxcuis),
            attributes = self.find_drug_attributes(rxcui)
        )
        return element


    def get_rxcuis(self, rxcui):
        query = """
        select RXCUI
        from DRUG_MAP
        where PRIMARY_RXCUI = ?
        """
        rxcuis = [rxcui]
        cur = connection.execute(query, (rxcui, ))
        for row in cur.fetchall():
            rxcuis.append(row['RXCUI'])
        return rxcuis


    def find_drug_attributes(self, rxcui):
        """
            Find drug attribute
        """
        attributes = []

        query = """
            select distinct RXNCONSO.RXCUI, RXNCONSO.STR
            from DRUG_MAP
            join RXNREL on RXNREL.RXCUI1 = DRUG_MAP.RXCUI
            join RXNCONSO on RXNCONSO.RXCUI = RXNREL.RXCUI2
            where RXNCONSO.TTY = 'DF'
            and RXNREL.RELA = 'dose_form_of'
            and DRUG_MAP.PRIMARY_RXCUI = ?
        """

        cur = connection.execute(query, (rxcui,))

        for row in cur.fetchall():
            attribute = self.Attribute(
                name = 'dose_form',
                value = self.add_prefix('rxnorm', row['RXCUI']),
                description = row['STR']
            )
            attributes.append(attribute)
        return attributes


    def find_drug_synonyms(self, rxcuis):
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
        for rxcui in rxcuis:
            cur = connection.execute(query, (rxcui,))

            synonyms = set()
            synonym_type = None
            for row in cur.fetchall():
                name=row['STR']
                type=ttydict.get(row['TTY'])
                if type is not None:
                    if row['TTY'] in {'SY','TMSY','DP','MTH_RXN_DP','PT'}:
                        synonyms.add(name)
                    else:
                        synonym_type = type
                        if type not in names_by_type:
                            name_synonyms = self.Names(
                                name = name,
                                synonyms = set(),
                                type = type
                            )
                            names_by_type[type] = name_synonyms
                            names_synonyms.append(name_synonyms)
                        else:
                            name_synonyms = names_by_type[type]
                            if name_synonyms.name is not None:
                                name_synonyms.synonyms.add(name_synonyms.name)
                                name_synonyms.name = None
                            name_synonyms.synonyms.add(name)
            if synonym_type is None:
                if len(synonyms) > 0:
                    name = None
                    if len(synonyms) == 1:
                        name = synonyms.pop()
                    names_synonyms.append(self.Names(name = name, synonyms = synonyms))
            else:
                names_by_type[synonym_type].synonyms.update(synonyms)
        for names_synonym in names_synonyms:
            names_synonym.synonyms = sorted(list(names_synonym.synonyms))
        return names_synonyms


    def create_connection(self, source_element_id):
        infores = self.Attribute(
            'biolink:primary_knowledge_source',
            'infores:rxnorm',
            value_type='biolink:InformationResource'
        )
        infores.attribute_source = 'infores:molepro'
        return self.Connection(
            source_element_id = source_element_id,
            predicate = self.PREDICATE,
            inv_predicate = self.INVERSE_PREDICATE,
            attributes = [infores]
        )


class RxNormIngredientTransformer(RxNormDrugProducer):
    variables = []


    def __init__(self):
        super().__init__(definition_file='info/ingredient_transformer_info.json')


    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('ChemicalEntity')].count = unii_count()
        info.knowledge_map.nodes[self.biolink_class('Drug')].count = drug_count()
        info.knowledge_map.nodes[self.biolink_class('SmallMolecule')].count = compound_count()
        info.knowledge_map.edges[0].count = ingredients_count('SmallMolecule')
        info.knowledge_map.edges[1].count = ingredients_count('ChemicalEntity') - info.knowledge_map.edges[0].count


    def map(self, collection, controls):
        drug_list = []
        drugs = {}
        for src_element in collection:
            ingredient_id = src_element.id
            unii = self.de_prefix('unii',src_element.identifiers.get('unii'))
            for rxcui in self.find_drug_by_unii(unii):
                if rxcui not in drugs:
                    element = self.create_element(rxcui)
                    drug_list.append(element)
                    drugs[rxcui] = element
                element = drugs[rxcui]
                element.connections.append(self.create_connection(ingredient_id))
                for mixture_rxcui in self.get_components(rxcui):
                    if mixture_rxcui not in drugs:
                        element = self.create_element(mixture_rxcui)
                        drug_list.append(element)
                        drugs[mixture_rxcui] = element
                    element = drugs[mixture_rxcui]
                    element.connections.append(self.create_connection(ingredient_id))
        return drug_list


    def find_drug_by_unii(self, unii):
        """
            Find drug by a unii
        """
        query = """
        select distinct RXNCONSO.RXCUI, DRUG_MAP.PRIMARY_RXCUI
        from RXNCONSO
        left join DRUG_MAP on DRUG_MAP.RXCUI = RXNCONSO.RXCUI
        where RXNCONSO.CODE = ?
        and RXNCONSO.TTY = 'SU'
        """

        cur = connection.execute(
            query, (unii, ))  # in order to make the varible as a tuple of one explicitely.
        return [row['RXCUI'] for row in cur.fetchall()]


    def get_components(self, primary_rxcui):
        query = """
        select RXCUI2
        from RXNREL
        join RXNCONSO ON RXNCONSO.RXCUI = RXNREL.RXCUI2
        where RXCUI1 = ?
        and RELA = 'has_part'
        and TTY = 'MIN';
        """
        cur = connection.execute(query, (primary_rxcui, ))
        return [row['RXCUI2'] for row in cur.fetchall()]


class RxNormComponentTransformer(RxNormDrugProducer):

    variables = []


    def __init__(self):
        super().__init__(definition_file='info/component_transformer_info.json')


    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('Drug')].count = drug_count()
        info.knowledge_map.edges[0].count = component_count()


    def map(self, collection, controls):
        drug_list = []
        drugs = {}
        for src_element in collection:
            for primary_rxcui in self.get_rxnorm_rxcui(src_element):
                for component_rxcui in self.get_components(primary_rxcui):
                    if component_rxcui not in drugs:
                        element = self.create_element(component_rxcui)
                        drug_list.append(element)
                        drugs[component_rxcui] = element
                    element = drugs[component_rxcui]
                    element.connections.append(self.create_connection(src_element.id))
        return drug_list


    def get_rxnorm_rxcui(self, element):
        source_rxcui = element.identifiers.get('rxnorm')
        if source_rxcui is not None:
            primary_rxcuis = self.get_primary_rxcui(self.de_prefix('rxnorm', source_rxcui))
            if primary_rxcuis is not None:
                return primary_rxcuis
        return []

   
    def get_components(self, primary_rxcui):
        query = """
        select RXCUI2
        from RXNREL
        join RXNCONSO ON RXNCONSO.RXCUI = RXNREL.RXCUI2
        where RXCUI1 = ?
        and RELA = 'part_of'
        and TTY = 'IN';
        """
        cur = connection.execute(query, (primary_rxcui, ))
        return [row['RXCUI2'] for row in cur.fetchall()]


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
        select
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
            
                substance = self.Element(
                    id='RXCUI:' + str(rxcui1),
                    biolink_class='Drug',
                    identifiers={'rxnorm': 'RXCUI:' + str(rxcui1)}
                )
                substance_list.append(substance)

                connect = self.Connection(
                    source_element_id=source_element_id,
                    predicate=self.PREDICATE,
                    inv_predicate=self.INVERSE_PREDICATE,
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
        select
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
       

            attribute = self.Attribute(
                name='rel',
                value=reldict[row['REL']],
                type='rel'
            )
            attributes.append(attribute)

            attribute = self.Attribute(
                name='rela',
                value=row['RELA'],
                type='rela'
            )
            attributes.append(attribute)

        return attributes


def compound_count():
    query = """
    select count(distinct UNII.UNII) as COUNT
    from RXNCONSO
    join UNII on RXNCONSO.CODE = UNII.UNII
    where RXNCONSO.TTY = 'SU'
    and UNII.INCHIKEY is not null
    and UNII.INCHIKEY != ''
    """
    ctn = count(query)
    print('compound_count = ',ctn)
    return ctn


def drug_count():
    query = """
    select count(distinct RXCUI) as COUNT
    from RXNCONSO
    """
    ctn = count(query)
    print('drug_count = ',ctn)
    return ctn


def unii_count():
    query = """
    select count(UNII) as COUNT
    from UNII
    """
    ctn = count(query)
    print('unii_count = ',ctn)
    return ctn


def ingredients_count(biolink_class):
    has_structure = "and UNII.INCHIKEY != ''"
    has_no_structure = ""
    query = """
    select count(distinct RXNCONSO.RXCUI) as COUNT
    from RXNCONSO
    join UNII on RXNCONSO.CODE = UNII.UNII
    where RXNCONSO.TTY = 'SU'
     {}
    """.format(has_structure if biolink_class == 'SmallMolecule' else has_no_structure)
    ctn = count(query)
    print(biolink_class, 'count = ',ctn)
    return ctn


def component_count():
    query = """
        select count(*) as COUNT
        from RXNREL
        join RXNCONSO on RXNCONSO.RXCUI = RXNREL.RXCUI2
        where RELA = 'part_of'
        and TTY = 'IN'
    """
    ctn = count(query)
    print('componens count = ',ctn)
    return ctn


def count(query):
    cur = connection.cursor()
    cur.execute(query)
    count = -1
    for row in cur.fetchall():
        count = row['COUNT']
    return count


