import sqlite3
import requests
import pandas as pd

connection = sqlite3.connect("data/CTD.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def get_chemicals():
    query = """
        SELECT
        ChemicalName,
        ChemicalID,
        PubChem_CID
        FROM chemicals_w_PubchemCID
        WHERE PubChem_CID is not null
    """
    cur = connection.execute(query)
    return cur.fetchall()


def get_current_cids():
    cids = {}
    for row in get_chemicals():
        cids[row['ChemicalName']] = row['PubChem_CID']
    return cids


def mesh_to_cid():
    for row in get_chemicals():
        #print(row['ChemicalID'], row['PubChem_CID'],row['ChemicalName'])
        name = row['ChemicalName']
        current_cid = row['PubChem_CID'] if row['PubChem_CID'] is not None else ''
        base_url = 'https://molepro.broadinstitute.org/molecular_data_provider'
        query = [name]
        with requests.post(base_url+'/compound/by_name', json=query) as id_response_obj:
            response = id_response_obj.json()
            ids = ['']
            if response['size'] > 0:
                #print('  ', response['id'])
                with requests.get(base_url+'/collection/'+response['id']) as elements_obj:
                    collection = elements_obj.json()
                    ids = [element['id'] for element in collection['elements']]
            cid = ids[0] if ids[0].startswith('CID') else ''
            print(row['ChemicalID'], current_cid, cid, ','.join(ids[1:]), sep='\t')


def mesh_to_cid_df():
    df = pd.read_csv('data/CTD_chemicals.tsv', sep="\t", header=0, dtype=str)
    current_cids = get_current_cids()
    base_url = 'https://molepro.broadinstitute.org/molecular_data_provider'
    print('PubChem_CID\tChemicalID');
    for row_index, row in df.iterrows():
        #if row_index < 500:
            name = row[0]
            mesh = row[1][5:]
            #print(row[0],row[1][5:],sep='\t')
            query = [name]
            with requests.post(base_url+'/compound/by_name', json=query) as id_response_obj:
                response = id_response_obj.json()
                ids = ['']
                if response['size'] == 1:
                    #print('  ', response['id'])
                    with requests.get(base_url+'/collection/'+response['id']+'?cache=no') as elements_obj:
                        collection = elements_obj.json()
                        ids = [element['id'] for element in collection['elements']]
                if response['size'] == 1:
                    #print('  ', response['id'])
                    if mesh in current_cids:
                        ids = [current_cids[mesh]]
                        #print('old CID  ', response['id'])
                cid = ids[0] if ids[0].startswith('CID') else ''
                print(cid, mesh, sep='\t')


def main():
    mesh_to_cid_df()


if __name__ == "__main__":
    main()