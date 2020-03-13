from contextlib import closing
import requests

from openapi_server.models.gene_info import GeneInfo
from openapi_server.models.gene_info_identifiers import GeneInfoIdentifiers
from openapi_server.models.attribute import Attribute

from transformers.transformer import Transformer

LIGAND_URL = 'https://pharos.nih.gov/idg/api/v1/ligands/search?q={}&top=100&skip=0'


target_map = {}

class PharosExpander(Transformer):

    variables = []


    def __init__(self):
        super().__init__(self.variables)


    def map(self, collection, controls):
        gene_list = []
        genes = {}
        for compound in collection:
            try:
                targets = self.find_targets(compound)
                for target in targets:
                    gene_info = self.get_gene_info(target, gene_list, genes)
                    value = self.compound_name(compound) + ' ('+target['source']
                    if target['action'] != '':
                        value = value + ':'+target['action']
                    value = value + ')'
                    gene_info.attributes.append(
                        Attribute(
                            name = 'is affected by',
                            value = value,
                            source = self.info.name
                        )
                    )
            except:
                print('failed to find targets for '+compound.id)
        return gene_list


    def compound_name(self, compound):
        if compound.names_synonyms is not None:
            for name in compound.names_synonyms:
                if name.name is not None:
                    return name.name
        return compound.compound_id


    def find_targets(self, compound):
        targets = []
        cid = self.get_cid(compound)
        ligand_urls = self.find_ligand(cid)
        for url in ligand_urls:
            with closing(requests.get(url)) as response_obj:
                response = response_obj.json()
                if self.has_cid(response, cid):
                    for link in response['links']:
                        if link['kind'] == 'ix.idg.models.Target':
                            target = self.get_target(link)
                            if target is not None:
                                targets.append(target)
        return targets


    def get_cid(self, compound):
        if compound.identifiers.pubchem is None:
            return None
        id = compound.identifiers.pubchem
        if id.startswith('CID:'):
            id = id[4:]
        return 'CID'+id


    def find_ligand(self, cid):
        ligands = []
        if cid is not None:
            url = LIGAND_URL.format(cid)
            with closing(requests.get(url)) as response:
                for cpd in response.json()['content']:
                    if cpd['kind'] == 'ix.idg.models.Ligand':
                        ligands.append(cpd['self'])
        return ligands


    def has_cid(self, ligand, cid):
        for synonym in ligand['synonyms']:
            if synonym['term'] == cid:
                return True
        return False


    def get_target(self, link):
        target_id = self.get_target_id(link['href'])
        if target_id is None:
            return None
        primary_source = 'Pharos'
        action = ''
        for property in link['properties']:
            if property['label'] == 'Ligand Activity Source':
                primary_source = property['term']
            if property['label'] == 'Pharmalogical Action':
                action = property['term']

        target = {'target':target_id, 'action': action, 'source': primary_source}
        return target


    def get_target_id(self, href):
        if href in target_map:
            return target_map[href]
        url = href+'?view=full'
        with closing(requests.get(url)) as response_obj:
            response = response_obj.json()
            target = {'gene_symbol': response.get('gene')}
            for synonym in response['synonyms']:
                if synonym['label'] == 'Entrez Gene':
                    target['gene_id']='NCBIGene:'+synonym['term']
                    target_map[href] = target
                    return target
        return None


    def get_gene_info(self, target, gene_list, genes):
        gene_id = target['target']['gene_id']
        if gene_id in genes:
            return genes
        gene_info = GeneInfo(
            gene_id = gene_id,
            identifiers = GeneInfoIdentifiers(entrez=gene_id),
            source = self.info.name,
            attributes = []
        )
        gene_list.append(gene_info)
        return gene_info

