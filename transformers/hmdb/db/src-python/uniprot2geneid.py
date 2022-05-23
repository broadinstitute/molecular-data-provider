import requests
import sqlite3


BATCH_SIZE = 32

connection = sqlite3.connect("../data/HMDB.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


def get_uniprot_ids():
    query = """
        SELECT UNIPROT_ID
        FROM PROTEIN
    """
    cur = connection.cursor()
    cur.execute(query)
    return cur.fetchall()


def uniprot_to_gene_id(batch):
    url = 'https://nodenormalization-sri.renci.org/get_normalized_nodes?'
    url = url+'&'.join(['curie=UniProtKB:'+uniprot for uniprot in batch])
    response = requests.get(url)
    for uniprot_id, entry in response.json().items():
        if entry is not None and 'id' in entry:
            if uniprot_id.startswith('UniProtKB:') and entry['id']['identifier'].startswith('NCBIGene:'):
                print(uniprot_id[10:], entry['id']['identifier'], sep='\t', flush=True)


def main():
    batch = []
    for row in get_uniprot_ids():
        batch.append(row['UNIPROT_ID'])
        if len(batch) >= 32:
            uniprot_to_gene_id(batch)
            batch = []
    if len(batch) > 0:
        uniprot_to_gene_id(batch)


if __name__ == "__main__":
    main()