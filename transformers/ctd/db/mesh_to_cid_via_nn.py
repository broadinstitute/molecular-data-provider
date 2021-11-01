# Outputs two files, one without node normalizer results and one with nn results

import pandas as pd
# Read in and format the file for translating CTD IDs to PubChem CIDs
fname = "pcsubstance_result.txt"
cpd_df = pd.read_csv(fname, sep="\t", header=None)
# Keep only the rows that start with SID
cpd_df = cpd_df[['SID:' in x for x in cpd_df[0]]]

sid_list = []
cid_list = []
ctd_list = []
entry_list = cpd_df[0].tolist()


for entry in entry_list:

    sid_index = -1
    cid_index = -1
    ctd_index = -1

    indexes = [sid_index, cid_index, ctd_index]

    # Find the index where each of the types of names begins
    if "SID:" in entry:
        sid_index = entry.find("SID:") #would return -1 if not found
    if "CID:" in entry:
        cid_index = entry.find("CID:")
    if "Comparative Toxicogenomics Database (CTD):" in entry:
        ctd_index = entry.find("Comparative Toxicogenomics Database (CTD):")

    if sid_index != -1:
        if cid_index != -1:
            sid_list.append(entry[sid_index:cid_index])
        else:
            sid_list.append(entry[sid_index:ctd_index])
    else:
        sid_list.append("")

    if cid_index != -1:
        cid_list.append(entry[(cid_index + 5):ctd_index])
    else:
        cid_list.append("")

    if ctd_index != -1:
        ctd_list.append(entry[(ctd_index + 43):])
    else:
        ctd_list.append("")


formatted_cid_list = ["CID:" + x if x != "" else x for x in cid_list]
dict = {'PubChem CID': formatted_cid_list, 'CTD MeSH': ctd_list}
new_df = pd.DataFrame(dict)

new_df.to_csv('mesh_to_pubchemCID.tsv', sep='\t', index=False)


# Use node normalizer to fill in missing values
import json
import requests

mesh_index_list = []
mesh_list = []

for i in range(len(formatted_cid_list)):
    if formatted_cid_list[i] == "":
        mesh = "MESH:" + ctd_list[i]
        mesh_list.append(mesh)
        mesh_index_list.append(i)

query_dict = {}
query_dict['curies'] = mesh_list
result = requests.post('https://nodenormalization-sri.renci.org/get_normalized_nodes',
                       json=query_dict)

for i in range(len(mesh_list)):

    cid_from_nn = ""
    if result.status_code == 200 and result.json()[mesh_list[i]] != None and 'id' in result.json()[
        mesh_list[i]] and 'identifier' in result.json()[mesh_list[i]]['id']:
        if result.json()[mesh_list[i]]['id']['identifier'].startswith("PUBCHEM.COMPOUND:"):
            cid_from_nn = result.json()[mesh_list[i]]['id']['identifier']
            cid_from_nn = "CID:" + cid_from_nn[17:]
            formatted_cid_list[mesh_index_list[i]] = cid_from_nn
    else:
        if result.status_code == 200 and result.json()[mesh_list[i]] != None and 'equivalent_identifiers' in \
                result.json()[mesh_list[i]]:
            for identifier_dict in result.json()[mesh_list[i]]['equivalent_identifiers']:
                if identifier_dict['identifier'].startswith("PUBCHEM.COMPOUND:"):
                    cid_from_nn = identifier_dict['identifier']
                    cid_from_nn = "CID:" + cid_from_nn[17:]
                    formatted_cid_list[mesh_index_list[i]] = cid_from_nn
                    break  # break out of for loop because we want to use the first pubchem curie returned


for i in range(len(ctd_list)):
    if ctd_list[i] != "":
        ctd_list[i] = ctd_list[i][5:]
dict = {'PubChem_CID': formatted_cid_list, 'ChemicalID': ctd_list}
final_df = pd.DataFrame(dict)
final_df.to_csv('mesh_to_pubchemCID_w_nn.tsv', sep='\t', index=False)

