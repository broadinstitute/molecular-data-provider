import requests
from contextlib import closing
from time import sleep

import xml.etree.ElementTree as ET

from transformers.transformer import Transformer
from openapi_server.models.compound_info import CompoundInfo
from openapi_server.models.compound_info_identifiers import CompoundInfoIdentifiers
from openapi_server.models.attribute import Attribute
from openapi_server.models.compound_info_structure import CompoundInfoStructure

X_Throttling_Control = 0

def x_throttling_control(header):
    max_percent = 0
    status = header.split(',')
    max_percent = max(max_percent, percent(status[0]))
    max_percent = max(max_percent, percent(status[1]))
    max_percent = max(max_percent, percent(status[2])/10.0)
    X_Throttling_Control = max_percent * 0.01


def percent(status):
    percent = status.split('(')[1]
    percent = percent.split('%')[0]
    return int(percent)


class PubChemProducer(Transformer):

    variables = ['compounds']


    def __init__(self):
        super().__init__(self.variables)


    def produce(self, controls):
        compound_list = []
        names = controls['compounds'].split(';')
        for name in names:
            name = name.strip()
            cids = self.find_compound(name)
            if len(cids) == 0:
                compound_list.append(CompoundInfo(attributes=[Attribute(name='query name', value=name,source=self.info.name)]))
            for cid in cids:
                structure = self.get_structure(cid)
                compound = CompoundInfo(
                    compound_id = 'CID:'+str(cid),
                    identifiers = CompoundInfoIdentifiers(
                        pubchem='CID:'+str(cid)
                    ),
                    structure = structure,
                    attributes = [
                        Attribute(name='query name', value=name,source=self.info.name)
                    ],
                    source = self.info.name
                )
                compound_list.append(compound)
            sleep(X_Throttling_Control) # PubChem only allows 5 requests per second
        return compound_list


    def find_compound(self, name):
        if (name.startswith('CID:')):
            return [name[4:]]
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/cids/JSON'
        query = 'name='+name
        with closing(requests.post(url, data=query)) as response_obj:
            try:
                x_throttling_control(response_obj.headers['X-Throttling-Control'])
            except:
                pass
            response = response_obj.json()
            if 'IdentifierList' in response:
                if 'CID' in response['IdentifierList']:
                    return response['IdentifierList']['CID']
            return []


    def get_structure(self, cid):
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/property/IsomericSMILES,InChI,InChIKey/JSON'
        url = url.format(cid)
        with closing(requests.get(url)) as response_obj:
            try:
                x_throttling_control(response_obj.headers['X-Throttling-Control'])
            except:
                pass
            response = response_obj.json()
            if 'PropertyTable' in response:
                if 'Properties' in response['PropertyTable']:
                    for property in response['PropertyTable']['Properties']:
                        if str(cid) == str(property.get('CID')):
                            return CompoundInfoStructure(
                                smiles = property['IsomericSMILES'],
                                inchi = property['InChI'],
                                inchikey = property['InChIKey'],
                                source = 'PubChem'
                            )
        return None
