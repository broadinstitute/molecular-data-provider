import sqlite3
import re

from transformers.transformer import Transformer
from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure
from openapi_server.models.gene_info import GeneInfo
from openapi_server.models.gene_info_identifiers import GeneInfoIdentifiers

# CURIE prefixes
PUBCHEM = 'CID:'

class RepurposingHubProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='compounds_transformer_info.json')


    inchikey_regex = re.compile('[A-Z]{14}-[A-Z]{10}-[A-Z]')


    def produce(self, controls):
        compound_list = []
        compounds = {}
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            for compound in self.find_compound(name):
                drug_id = compound[0]
                for sample in get_samples(drug_id):
                    sample_id = sample[1]
                    if sample_id not in compounds.keys():
                        compounds[sample_id]= self.compound_info(sample)
                        compound_list.append(compounds[sample_id])
                    compounds[sample_id].attributes.append(Attribute(name='query name', value=name,source=self.info.name))
        return compound_list


    def find_compound(self, name):
        if self.inchikey_regex.match(name) is not None:
            return find_compound_by_inchi_key(name)
        ids = find_compound_by_name(name)
        if len(ids) != 0:
            return ids
        else:
            return find_compound_by_synonym(name)


    def compound_info(self, sample):
        print(sample)
        drug_id = sample[0]
        sample_id = sample[1]
        smiles = sample[2]
        inchi_key = sample[3]
        pubchem_cid = PUBCHEM+str(sample[4]) if sample[4] != '' else None
        compound = get_compound(drug_id)[0]
        synonyms = get_synonyms(sample_id)
        compound_info = CompoundInfo(
            compound_id = pubchem_cid if pubchem_cid is not None else inchi_key,
            identifiers = CompoundInfoIdentifiers(
                pubchem = pubchem_cid
            ),
            structure = CompoundInfoStructure(
                smiles = smiles,
                inchikey = inchi_key,
                source = self.info.label
            ),
            names_synonyms = [Names(
                name = compound[1],
                synonyms = [synonym[1] for synonym in synonyms],
                source = 'Drug Repurposing Hub'
            )],
            attributes = [],
            source = self.info.name
        )
        return compound_info


class RepurposingHubTargets(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='targets_transformer_info.json')


    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            drugs = self.find_drug(compound)
            for drug in drugs:
                targets = get_targets(drug[0])
                for target in targets:
                    gene_id = target[1]
                    gene = genes.get(gene_id)
                    if gene is None:
                        gene = GeneInfo(
                            gene_id = gene_id,
                            identifiers = GeneInfoIdentifiers(hgnc=gene_id),
                            attributes = []
                        )
                        gene_list.append(gene)
                        genes[gene_id] = gene
                    gene.attributes.append(Attribute(name='target info', value='target of '+drug[1], source=self.info.name))
        return gene_list


    def find_drug(self, compound_info: CompoundInfo):
        if compound_info.structure is not None:
            if compound_info.structure.inchikey is not None:
                for drug in find_compound_by_inchi_key(compound_info.structure.inchikey):
                    return get_compound(drug[0])
        return []



connection = sqlite3.connect("RepurposingHub.sqlite", check_same_thread=False)


def find_compound_by_name(name):
    query = """
        SELECT DISTINCT DRUG_ID FROM DRUG
        WHERE PERT_INAME = ?
    """
    cur = connection.cursor()
    cur.execute(query,(name,))
    return cur.fetchall()


def find_compound_by_synonym(synonym):
    query = """
        SELECT DISTINCT DRUG_ID FROM NAME
        WHERE NAME = ?
    """
    cur = connection.cursor()
    cur.execute(query,(synonym,))
    return cur.fetchall()


def find_compound_by_pubchem_cid(id):
    query = """
        SELECT DISTINCT DRUG_ID FROM SAMPLE
        WHERE PUBCHEMCID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(id,))
    return cur.fetchall()


def find_compound_by_inchi_key(inchi_key):
    query = """
        SELECT DISTINCT DRUG_ID FROM SAMPLE
        WHERE INCHIKEY = ?
    """
    cur = connection.cursor()
    cur.execute(query,(inchi_key,))
    return cur.fetchall()


def get_compound(drug_id):
    query = """
        SELECT DRUG_ID, PERT_INAME FROM DRUG
        WHERE DRUG_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_id,))
    return cur.fetchall()


def get_samples(drug_id):
    query = """
        SELECT DRUG_ID, SAMPLE_ID, SMILES, INCHIKEY, PUBCHEMCID FROM SAMPLE
        WHERE DRUG_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_id,))
    return cur.fetchall()


def get_synonyms(sample_id):
    query = """
        SELECT SAMPLE_ID, NAME FROM NAME
        WHERE SAMPLE_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(sample_id,))
    return cur.fetchall()


def get_targets(drug_id):
    query = """
        SELECT FEATURE_NAME, FEATURE_XREF FROM FEATURE
        INNER JOIN FEATURE_MAP ON FEATURE.FEATURE_ID = FEATURE_MAP.FEATURE_ID
        WHERE FEATURE_TYPE = 'target' AND FEATURE_MAP.DRUG_ID = ?
    """
    cur = connection.cursor()
    cur.execute(query,(drug_id,))
    return cur.fetchall()
