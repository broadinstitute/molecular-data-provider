import requests
from collections import defaultdict

from transformers.transformer import Transformer

from openapi_server.models.names import Names
from openapi_server.models.attribute import Attribute
from openapi_server.models.element import Element
from openapi_server.models.connection import Connection

SOURCE = 'ChEMBL'

# CURIE prefixes
CHEMBL = 'ChEMBL:'
ENSEMBL = 'ENSEMBL:'

# attribute types
MOA = 'MI:2044' # mechanism of action
ACTION = 'NCIT:C1708' # Agent: Chemical Viewed Functionally
REFERENCE = 'NCIT:C25641' # reference

# URLs
CHEMBL_NAME_URL = 'https://www.ebi.ac.uk/chembl/api/data/molecule?pref_name__exact={}&format=json'
CHEMBL_ID_URL = 'https://www.ebi.ac.uk/chembl/api/data/molecule/{}?format=json'
CHEMBL_INCHIKEY = 'https://www.ebi.ac.uk/chembl/api/data/molecule?molecule_structures__standard_inchi_key__exact={}&format=json'
CHEMBL_MOA = 'https://www.ebi.ac.uk/chembl/api/data/mechanism?molecule_chembl_id__exact={}&format=json'
CHEMBL_TARGET = 'https://www.ebi.ac.uk/chembl/api/data/target.json?target_chembl_id__exact={}'

#Biolink class
GENE = 'Gene'
CHEMICAL_SUBSTANCE = 'ChemicalSubstance'


class ChemblProducer(Transformer):

    variables = ['compounds']

    def __init__(self):
        super().__init__(self.variables, definition_file='info/molecules_transformer_info.json')


    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            if name.upper().startswith('CHEMBL'):
                compound_list.append(self.find_compound_by_id(name))
            for compound in self.find_compound_by_name(name):
                compound_list.append(compound)
        return compound_list


    def find_compound_by_name(self, name):
        """
            Find compound by a name
        """
        compounds = []
        molecules = requests.get(CHEMBL_NAME_URL.format(name.upper())).json()
        for molecule in molecules['molecules']:
            compounds.append(self.get_compound(molecule, name))
        return compounds


    def find_compound_by_id(self, id):
        """
            Find compound by a ChEMBL id
        """
        chembl_id = id
        if chembl_id.upper().startswith('CHEMBL:'):
            chembl_id = chembl_id[7:]
        print(chembl_id)
        molecule = requests.get(CHEMBL_ID_URL.format(chembl_id.upper())).json()
        return self.get_compound(molecule, id)


    def get_compound(self, molecule, name):
        id = molecule['molecule_chembl_id']
        compound_id = CHEMBL + id
        identifiers = {
            'chembl': compound_id,
            'smiles':  molecule['molecule_structures']['canonical_smiles'],
            'inchi': molecule['molecule_structures']['standard_inchi'],
            'inchikey': molecule['molecule_structures']['standard_inchi_key'],
        }
        compound = Element(
            id = compound_id,
            biolink_class = CHEMICAL_SUBSTANCE,
            identifiers = identifiers,
            names_synonyms = self.get_names_synonyms(id, molecule['pref_name'], molecule['molecule_synonyms']),
            attributes = [
                Attribute(name='query name', value=name,source=self.info.name),
                Attribute(name='structure source', value=SOURCE,source=self.info.name)
            ],
            connections = [],
            source = self.info.name
        )
        return compound


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
        super().__init__(self.variables, definition_file='info/targets_transformer_info.json')


    def map(self, compound_list, controls):
        gene_list = []
        genes = {}
        for compound in compound_list:
            targets = self.get_targets(compound)
            for target in targets:
                gene_id = ENSEMBL+target['gene_id']
                gene = genes.get(gene_id)
                if gene is None:
                    gene = Element(
                        id=gene_id,
                        biolink_class=GENE,
                        identifiers = {'ensembl':[gene_id]},
                        connections=[],
                        attributes = [],
                        source = self.info.name
                    )
                    gene_list.append(gene)
                    genes[gene_id] = gene
                gene.connections.append(target['connection'])
        return gene_list


    def get_targets(self, compound):
        target_list = []
        chembl_id = self.get_chembl_id(compound)
        if chembl_id is not None:
            moa = requests.get(CHEMBL_MOA.format(chembl_id)).json()
            while True:
                for mechanism in moa['mechanisms']:
                    connection = self.create_connection(compound, mechanism)
                    target_id = mechanism['target_chembl_id']
                    targets = requests.get(CHEMBL_TARGET.format(target_id)).json()
                    for target in targets['targets']:
                        if target['target_type'] == 'SINGLE PROTEIN' or target['target_type'] == 'PROTEIN FAMILY':
                            for component in target['target_components']:
                                gene_id = self.get_gene_id(component)
                                if gene_id is not None:
                                    target_list.append({'gene_id':gene_id, 'connection': connection})
                if moa['page_meta']['next'] is None:
                    break
                moa = requests.get('https://www.ebi.ac.uk'+moa['page_meta']['next']).json()

        return target_list


    def create_connection(self, compound, mechanism):
        connection = Connection(
            source_element_id=compound.id,
            type = self.info.knowledge_map.predicates[0].predicate,
            attributes=[]
        )
        action = mechanism['action_type']
        if action is not None:
            connection.attributes.append(
                Attribute(
                    name='action_type',
                    value=action,
                    type=ACTION,
                    source=SOURCE,
                    url=None,
                    provided_by=self.info.name
                )
            )
        moa = mechanism['mechanism_of_action']
        if moa is not None:
            connection.attributes.append(
                Attribute(
                    name='mechanism_of_action',
                    value=moa,
                    type=MOA,
                    source=SOURCE,
                    url=None,
                    provided_by=self.info.name
                )
            )
        for reference in mechanism['mechanism_refs']:
            connection.attributes.append(
                Attribute(
                    name=reference['ref_type'],
                    value=reference['ref_id'],
                    type=REFERENCE,
                    source=SOURCE,
                    url=reference['ref_url'],
                    provided_by=self.info.name
                )
            )
        return connection



    def get_chembl_id(self, compound):
        if 'chembl' in compound.identifiers and compound.identifiers['chembl'] is not None:
            if compound.identifiers['chembl'].upper().startswith('CHEMBL:'):
                return compound.identifiers['chembl'][7:]
            return compound.identifiers['chembl']
        if 'inchikey' in compound.identifiers and compound.identifiers['inchikey'] is not None:
            molecules = requests.get(CHEMBL_INCHIKEY.format(compound.identifiers['inchikey'])).json()
            if len(molecules['molecules']) == 1:
                for molecule in molecules['molecules']:
                    return molecule['molecule_chembl_id']
            else:
                print("WARNING: multiple molecules for an InChI key: ",CHEMBL_INCHIKEY.format(compound.structure.inchikey))
        return None


    def get_gene_id(self, component):
        for xref in component['target_component_xrefs']:
            if xref['xref_src_db'] == 'EnsemblGene':
                return xref['xref_id']
        return None