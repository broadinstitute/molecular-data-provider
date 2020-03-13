import requests
from collections import defaultdict

from transformers.transformer import Transformer

from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure
from openapi_server.models.gene_info import GeneInfo
from openapi_server.models.gene_info_identifiers import GeneInfoIdentifiers

# CURIE prefixes
CHEMBL = 'ChEMBL:'

CHEMBL_NAME_URL = 'https://www.ebi.ac.uk/chembl/api/data/molecule?pref_name__exact={}&format=json'
CHEMBL_INCHIKEY = 'https://www.ebi.ac.uk/chembl/api/data/molecule?molecule_structures__standard_inchi_key__exact={}&format=json'
CHEMBL_MOA = 'https://www.ebi.ac.uk/chembl/api/data/mechanism?molecule_chembl_id__exact={}&format=json'
CHEMBL_TARGET = 'https://www.ebi.ac.uk/chembl/api/data/target.json?target_chembl_id__exact={}'


class ChemblProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='molecules_transformer_info.json')


    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            for compound_info in self.find_compound_by_name(name):
                compound_list.append(compound_info)
        return compound_list


    def find_compound_by_name(self, name):
        """
            Find compound by a name
        """
        compounds = []
        molecules = requests.get(CHEMBL_NAME_URL.format(name.upper())).json()
        for molecule in molecules['molecules']:
            id = molecule['molecule_chembl_id']
            compound_id = CHEMBL + id
            smiles = molecule['molecule_structures']['canonical_smiles']
            compound_info = CompoundInfo(
                compound_id = compound_id,
                identifiers = CompoundInfoIdentifiers(
                    chembl = compound_id
                ),
                names_synonyms = self.get_names_synonyms(id, molecule['pref_name'], molecule['molecule_synonyms']),
                structure = CompoundInfoStructure(
                    smiles = molecule['molecule_structures']['canonical_smiles'],
                    inchi = molecule['molecule_structures']['standard_inchi'],
                    inchikey = molecule['molecule_structures']['standard_inchi_key'],
                    source = 'ChEMBL'
                ),
                attributes = [Attribute(name='query name', value=name,source=self.info.name)],
                source = self.info.name
            )
            compounds.append(compound_info)
        return compounds


    def get_names_synonyms(self, id, pref_name, molecule_synonyms):
        """
            Build names and synonyms list
        """
        synonyms = defaultdict(list)
        for molecule_synonym in molecule_synonyms:
            if molecule_synonym['syn_type'] is None:
                synonyms['ChEMBL'].append(molecule_synonym['molecule_synonym'])
            else:
                synonyms[molecule_synonym['syn_type']].append(molecule_synonym['molecule_synonym'])
        names_synonyms = []
        names_synonyms.append(
            Names(
                name =pref_name,
                source = 'ChEMBL',
                synonyms = synonyms['ChEMBL'],
                url = 'https://www.ebi.ac.uk/chembl/compound_report_card/'+id
            )
        ),
        for syn_type, syn_list in synonyms.items():
            if syn_type != 'ChEMBL':
                names_synonyms.append(
                    Names(
                        name = syn_list[0] if len(syn_list) == 1 else  None,
                        synonyms = syn_list if len(syn_list) > 1 else  None,
                        source = syn_type+'@ChEMBL',
                    )
                )
        return names_synonyms


class ChemblTargetTransformer(Transformer):

    variables = []

    def __init__(self):
        super().__init__(self.variables, definition_file='targets_transformer_info.json')


    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            targets = self.get_targets(compound)
            for target in targets:
                gene_id = 'ENSEMBL:'+target['gene_id']
                gene = genes.get(gene_id)
                if gene is None:
                    gene = GeneInfo(
                        gene_id = gene_id,
                        identifiers = GeneInfoIdentifiers(ensembl=[gene_id]),
                        attributes = []
                    )
                    gene_list.append(gene)
                    genes[gene_id] = gene
                gene.attributes.append(
                    Attribute(
                        name='mechanism of action',
                        value='target of '+compound.compound_id+' ('+target['action']+')',
                        source=self.info.name
                        )
                    )

        return gene_list


    def get_targets(self, compound):
        target_list = []
        chembl_id = self.get_chembl_id(compound)
        if chembl_id is not None:
            moa = requests.get(CHEMBL_MOA.format(chembl_id)).json()
            while True:
                for mechanism in moa['mechanisms']:
                    action = mechanism['action_type']
                    target_id = mechanism['target_chembl_id']
                    print(CHEMBL_TARGET.format(target_id))
                    targets = requests.get(CHEMBL_TARGET.format(target_id)).json()
                    for target in targets['targets']:
                        if target['target_type'] == 'SINGLE PROTEIN' or target['target_type'] == 'PROTEIN FAMILY':
                            for component in target['target_components']:
                                gene_id = self.get_gene_id(component)
                                if gene_id is not None:
                                    target_list.append({'gene_id':gene_id, 'action': action})
                if moa['page_meta']['next'] is None:
                    break
                moa = requests.get('https://www.ebi.ac.uk'+moa['page_meta']['next']).json()

        return target_list


    def get_chembl_id(self, compound):
        if compound.identifiers.chembl is not None:
            if compound.identifiers.chembl.upper().startswith('CHEMBL:'):
                return compound.identifiers.chembl[7:]
            return compound.identifiers.chembl
        if compound.structure is not None and compound.structure.inchikey is not None:
            molecules = requests.get(CHEMBL_INCHIKEY.format(compound.structure.inchikey)).json()
            if len(molecules['molecules']) == 1:
                for molecule in molecules['molecules']:
                    return molecule['molecule_chembl_id']
            else:
                print(CHEMBL_INCHIKEY.format(compound.structure.inchikey))
        return None


    def get_gene_id(self, component):
        for xref in component['target_component_xrefs']:
            if xref['xref_src_db'] == 'EnsemblGene':
                return xref['xref_id']
        return None