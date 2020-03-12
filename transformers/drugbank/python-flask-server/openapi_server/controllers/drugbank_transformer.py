import sqlite3

from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.gene_info import GeneInfo
from openapi_server.models.gene_info_identifiers import GeneInfoIdentifiers
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure

# CURIE prefixes
DRUGBANK = 'DrugBank:'
PUBCHEM = 'CID:'
CHEMBL = 'ChEMBL:'
CHEBI = 'CHEBI:'

class DrugBankProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='drugs_transformer_info.json')


    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            for drug in find_drug(name):
                compound_info = get_drug(drug)
                compound_info.source = self.info.name
                compound_info.attributes = [Attribute(name='query name', value=name,source=self.info.name)]
                compound_list.append(compound_info)
        return compound_list

class DrugBankTargetTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='targets_transformer_info.json')


    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            drug = self.find_drug(compound)
            if drug is not None:
                targets = get_targets(drug[0])
                for target in targets:
                    gene_id = target[0]
                    gene = genes.get(gene_id)
                    if gene is None:
                        gene = GeneInfo(
                            gene_id = gene_id,
                            identifiers = GeneInfoIdentifiers(hgnc=gene_id),
                            attributes = []
                        )
                        gene_list.append(gene)
                        genes[gene_id] = gene
                    gene.attributes.append(Attribute(name='target of '+drug[2], value=target[1],source=self.info.name))
        return gene_list


    def find_drug(self, compound_info: CompoundInfo):
        if compound_info.identifiers is not None:
            if compound_info.identifiers.drugbank is not None:
                drug_bank_id = de_prefix(DRUGBANK,compound_info.identifiers.drugbank)
                for drug in find_drug_by_name(drug_bank_id):
                    return drug
            if compound_info.identifiers.pubchem is not None:
                cid = de_prefix(PUBCHEM, compound_info.identifiers.pubchem)
                for drug in find_drug_by_identifier(cid, 'PubChem Compound'):
                    return drug
        return None


class DrugBankInhibitorsTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='inhibitors_transformer_info.json')


    def map(self, gene_list, controls):
        compound_list = []
        compounds = {}
        for gene in gene_list:
            if gene.identifiers is not None and gene.identifiers.hgnc is not None:
                gene_id = gene.identifiers.hgnc
                inhibitors = get_inhibitors(gene_id)
                for inhibitor in inhibitors:
                    drug_bank_id = inhibitor[1]
                    actions = ' ['+inhibitor[3]+']' if inhibitor[3] is not None else ''
                    compound = compounds.get(drug_bank_id)
                    if compound is None:
                        compound = get_drug(inhibitor)
                        compound.source = self.info.name
                        compound_list.append(compound)
                        compounds[drug_bank_id] = compound
                    compound.attributes.append(Attribute(name='target', value=gene_id+actions,source=self.info.name))
        return compound_list



connection = sqlite3.connect("DrugBank.sqlite", check_same_thread=False)


def find_drug_by_name(drug_name):
    query = """
        SELECT DISTINCT DRUG_ID, DRUG_BANK_ID, DRUG_NAME FROM DRUG
        WHERE DRUG_BANK_ID = ? OR DRUG_NAME = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_name,drug_name))
    return cur.fetchall()


def find_drug_by_synonym(synonym):
    query = """
        SELECT DISTINCT DRUG.DRUG_ID, DRUG_BANK_ID, DRUG_NAME FROM DRUG
        INNER JOIN SYNONYM ON SYNONYM.DRUG_ID = DRUG.DRUG_ID
        WHERE SYNONYM.SYNONYM = ?
    """
    cur = connection.cursor()
    cur.execute(query,(synonym,))
    return cur.fetchall()


def find_drug_by_identifier(identifier, source = None):
    query = """
        SELECT DISTINCT DRUG.DRUG_ID, DRUG_BANK_ID, DRUG_NAME FROM DRUG
        INNER JOIN IDENTIFIER ON IDENTIFIER.DRUG_ID = DRUG.DRUG_ID
        WHERE IDENTIFIER.IDENTIFIER = ?
    """
    params = (identifier,)
    if source is not None:
        query = query + " AND IDENTIFIER.SOURCE = ?"
        params = (identifier,source)
    cur = connection.cursor()
    cur.execute(query, params)
    return cur.fetchall()


def find_drug(name):
    if name.startswith(DRUGBANK):
        return find_drug_by_name(name[9:])
    drugs = find_drug_by_name(name)
    if len(drugs) == 0:
        drugs = find_drug_by_synonym(name)
    if len(drugs) == 0:
        drugs = find_drug_by_identifier(name)
    return drugs


def get_synonyms(drug_id):
    query = """
        SELECT SYNONYM FROM SYNONYM WHERE DRUG_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_id,))
    return [synonym[0] for synonym in cur.fetchall()]


def get_identifiers(drug_id):
    query = """
        SELECT IDENTIFIER, SOURCE FROM IDENTIFIER WHERE DRUG_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_id,))
    identifiers = {}
    for row in cur.fetchall():
        identifiers[row[1]] = row[0]
    return identifiers


def prefix(prefix, value):
    return prefix + value if value is not None else None

def de_prefix(prefix, value):
    return value[len(prefix):] if value.startswith(prefix) else value

def get_drug(row):
    drug_id = row[0]
    drug_bank_id = prefix(DRUGBANK,row[1])
    drug_name = row[2]
    synonyms = get_synonyms(drug_id)
    identifiers = get_identifiers(drug_id)
    compound_id = 'CID:'+identifiers['PubChem Compound'] if 'PubChem Compound' in identifiers else drug_bank_id

    return CompoundInfo(
        compound_id = compound_id,
        identifiers = CompoundInfoIdentifiers(
            drugbank = drug_bank_id,
            pubchem = prefix(PUBCHEM,identifiers.get('PubChem Compound')),
            chembl = prefix(CHEMBL,identifiers.get('ChEMBL')),
            chebi = prefix(CHEBI,identifiers.get('ChEBI'))
        ),
        names_synonyms = [Names(
            name = drug_name,
            synonyms = synonyms,
            source = 'DrugBank',
            url = 'https://www.drugbank.ca/drugs/'+row[1]
        )],
        structure = CompoundInfoStructure(
            smiles = identifiers.get('SMILES'),
            inchi = identifiers.get('InChI'),
            inchikey = identifiers.get('InChIKey'),
            source = 'DrugBank'
        ),
        attributes = []
    )


def get_targets(drug_id):
    query = """
        SELECT TARGET.GENE_ID, TARGET_MAP.ACTIONS FROM TARGET
        INNER JOIN TARGET_MAP ON TARGET.TARGET_ID = TARGET_MAP.TARGET_ID
        WHERE TARGET_MAP.DRUG_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_id,))
    return cur.fetchall()


def get_inhibitors(gene_id):
    query = """
        SELECT DISTINCT DRUG.DRUG_ID, DRUG.DRUG_BANK_ID, DRUG.DRUG_NAME, TARGET_MAP.ACTIONS FROM DRUG
        INNER JOIN TARGET_MAP ON DRUG.DRUG_ID = TARGET_MAP.DRUG_ID
        INNER JOIN TARGET     ON TARGET.TARGET_ID = TARGET_MAP.TARGET_ID
        WHERE TARGET.GENE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(gene_id,))
    return cur.fetchall()

