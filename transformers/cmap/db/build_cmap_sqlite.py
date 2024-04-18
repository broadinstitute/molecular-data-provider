import pandas as pd
import requests
import sqlite3

from collections import OrderedDict
from contextlib import closing


CMAP_URL = 'https://s3.amazonaws.com/macchiato.clue.io/builds/touchstone/v1.1/arfs/{}/pert_id_summary.gct'

connection = sqlite3.connect("data/cmap.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

nocase='NOCASE'

COMPOUND_TABLE = """
    CREATE TABLE COMPOUND (
    pert_id     TEXT  PRIMARY KEY,
    pert_type   TEXT  NOT NULL,
    pert_iname  TEXT  NOT NULL,
    pert_class  TEXT  NOT NULL,
    xref_id     TEXT  NOT NULL,
    cmap_name   TEXT  NOT NULL,
    smiles      TEXT  NOT NULL,
    inchi_key   TEXT  NOT NULL,
    aliases     TEXT  DEFAULT NULL
    );
    """


MOA_TABLE = """
    CREATE TABLE MOA (
    moa_id   INTEGER PRIMARY KEY,
    pert_id  TEXT    NOT NULL,
    target   TEXT    DEFAULT NULL,
    moa      TEXT    DEFAULT NULL,
    UNIQUE (pert_id, target, moa)
    );
"""


GENE_TABLE = """
    CREATE TABLE GENE (
    pert_id        TEXT  PRIMARY KEY,
    pert_type      TEXT  NOT NULL,
    pert_iname     TEXT  NOT NULL,
    pert_class     TEXT  NOT NULL,
    xref_id        TEXT  NOT NULL,
    gene_id        INT   NOT NULL,
    gene_symbol    TEXT  NOT NULL,
    ensembl_id     TEXT  DEFAULT NULL,
    gene_title     TEXT  NOT NULL,
    gene_type      TEXT  NOT NULL,
    src            TEXT  NOT NULL,
    feature_space  TEXT  NOT NULL
    );
"""


CMAP_SCORE_TABLE = """
    CREATE TABLE CMAP_SCORE (
    pert_id_1    TEXT  NOT NULL,
    pert_id_2    TEXT  NOT NULL,
    cmap_score  REAL NOT NULL,
    UNIQUE (pert_id_1, pert_id_2)
    );
"""


def insert_compound(cur, pert_id, pert_type, pert_iname, pert_class, xref_id, cmap_name, smiles, inchi_key, aliases):
    statement = """
        INSERT INTO COMPOUND (pert_id, pert_type, pert_iname, pert_class, xref_id, cmap_name, smiles, inchi_key, aliases) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(statement, (pert_id, pert_type, pert_iname, pert_class, xref_id, cmap_name, smiles, inchi_key, aliases))


def insert_moa(cur, pert_id, target, moa):
    statement = """
        INSERT INTO MOA (pert_id, target, moa) 
        VALUES (?, ?, ?)
    """
    cur.execute(statement, (pert_id, target, moa))


def insert_gene(cur, pert_id, pert_type, pert_iname, pert_class, xref_id, gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space):
    statement = """
        INSERT INTO GENE (pert_id, pert_type, pert_iname, pert_class, xref_id, gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(statement, (pert_id, pert_type, pert_iname, pert_class, xref_id, gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space))


def insert_score(cur, pert_id_1, pert_id_2, cmap_score):
    statement = """
        INSERT INTO CMAP_SCORE (pert_id_1, pert_id_2, cmap_score) 
        VALUES (?, ?, ?)
    """
    cur.execute(statement, (pert_id_1, pert_id_2, cmap_score))


def create_tables():
    cur = connection.cursor()
    cur.execute(COMPOUND_TABLE)
    cur.execute(MOA_TABLE)
    cur.execute(GENE_TABLE)
    cur.execute(CMAP_SCORE_TABLE)
    cur.close()
    connection.commit()


def load_pert_ids():
    pert_ids = OrderedDict()
    with open("data/CMAP_pert_ids.txt",'r') as f:
        header = f.readline()
        if header.strip() != 'pert_type\tpert_id\tpert_iname\tclass\tID':
            print('expected "{}"'.format(header.strip()))
            print('found "{}"'.format('pert_type\tpert_id\tpert_iname\tclass\tID'))
            raise Exception('CMAP_pert_ids.txt: wrong file format')
        for line in f:
            row = line.strip().split('\t')
            pert_type = row[0]
            pert_id = row[1]
            pert_iname = row[2]
            pert_class = row[3]
            id = row[4]
            if pert_type == 'trt_kd' or pert_type == 'trt_cp':
                pert_ids[pert_id] = (pert_type, pert_iname, pert_class, id)
    return pert_ids


def load_compounds(pert_ids):
    df = pd.read_csv('data/compoundinfo_beta.txt', sep="\t", header=0, dtype=str)
    cur = connection.cursor()
    loaded = set()
    n = 0
    for i, row in df.iterrows():
        pert_id = row['pert_id']
        if pert_id in pert_ids:
            (pert_type, pert_iname, pert_class, xref_id) = pert_ids[pert_id]
            pert_id = row['pert_id']
            cmap_name = row['cmap_name']
            target = row['target']
            moa = row['moa']
            smiles = row['canonical_smiles']
            inchi_key = row['inchi_key']
            aliases = row['compound_aliases']
            if pert_id not in loaded:
                insert_compound(cur, pert_id, pert_type, pert_iname, pert_class, xref_id, cmap_name, smiles, inchi_key, aliases)
                n = n + 1
                loaded.add(pert_id)
            if not pd.isnull(target) or not pd.isnull(moa):
                insert_moa(cur, pert_id, target, moa)
    connection.commit()
    cur.close()
    print('loaded {} pert_ids'.format(n))


def load_genes(pert_ids):
    # collect genes
    df = pd.read_csv('data/geneinfo_beta.txt', sep="\t", header=0, dtype=str)
    cur = connection.cursor()
    genes = {}
    for i, row in df.iterrows():
        gene_id = row['gene_id']
        gene_symbol = row['gene_symbol']
        ensembl_id = row['ensembl_id']
        gene_title = row['gene_title']
        gene_type = row['gene_type']
        src = row['src']
        feature_space = row['feature_space']
        genes[gene_id] = (gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space)
    print('loaded {} genes'.format(len(genes)))

    # save genes
    n = 0
    for (pert_id, (pert_type, pert_iname, pert_class, xref_id)) in pert_ids.items():
        if xref_id.startswith('NCBIGene:'):
            gene_id = xref_id[9:]
            if gene_id in genes:
                (gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space) = genes[gene_id]
            else:
                (gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space) = load_hgnc(xref_id)
            n = n + 1
            insert_gene(cur, pert_id, pert_type, pert_iname, pert_class, xref_id, 
                        gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space)
    connection.commit()
    cur.close()
    print('loaded {} pert_ids'.format(n))
        

def load_hgnc(xref_id):
    base_url = 'https://translator.broadinstitute.org/hgnc/genes'
    controls = {'controls': [{'name':'gene', 'value': xref_id}]}
    gene_id = ''
    gene_symbol = ''
    ensembl_id = ''
    gene_title = ''
    gene_type = ''
    src = ''
    feature_space = ''
    response = requests.post(base_url+'/transform', json=controls)
    if response.status_code != 200:
        print('Call to HGNC transformer failed', xref_id, ':', response.json())
    else:
        json_response = response.json()
        if len(json_response) > 0 and 'identifiers' in json_response[0] and 'names_synonyms' in json_response[0]:
            identifiers = json_response[0]['identifiers']
            if 'entrez' in identifiers and identifiers['entrez'].startswith('NCBIGene:'):
                gene_id = identifiers['entrez'][9:]
            if 'ensembl' in identifiers and identifiers['ensembl'].startswith('ENSEMBL:'):
                ensembl_id = identifiers['ensembl'][8:]
            names_synonyms = json_response[0]['names_synonyms']
            for name in names_synonyms:
                if name.get('name_type') == 'symbol':
                    gene_symbol = name['name']
                elif gene_title == '':
                    gene_title = name['name']
        else:
            print('  No results in HGNC transformer', xref_id, ':', len(json_response))
    
    return (gene_id, gene_symbol, ensembl_id, gene_title, gene_type, src, feature_space) 


def load_scores(pert_ids, threshold):
    # load scores
    cur = connection.cursor()
    n = 0
    for pert_id_1 in pert_ids:
        url = CMAP_URL.format(pert_id_1)
        with closing(requests.get(url)) as response:
            if response.status_code == 200:
                row_no = 0
                for line in response.iter_lines():
                    if row_no >= 3:
                        row = line.decode().strip().split('\t')
                        pert_id_2 = row[0]
                        cmap_score = float(row[1])
                        if pert_id_2 in pert_ids and abs(cmap_score) >= threshold:
                            insert_score(cur, pert_id_1, pert_id_2, cmap_score)
                    row_no = row_no + 1
                n = n + 1
                if n % 10 == 0:
                    print(n,'/',len(pert_ids))
                    connection.commit()
    connection.commit()
    cur.close()
    print('loaded scores for {} pert_ids'.format(n))


def create_index(table, column, column2=None, colate=None):
    print(table, column, column2 if column2 else '')
    colate_nocase = 'COLLATE ' + nocase if colate == nocase else ''
    index_name = column
    columns = column
    if column2 is not None:
        index_name = column + '_' + column2
        columns = column + ', ' + column2
    stmt = """
        CREATE INDEX {}_{}_idx 
        ON {} ({} {});    
    """.format(table, index_name, table, columns, colate_nocase)
    cur = connection.cursor()
    cur.executescript(stmt)
    cur.close()


def create_indexes():
    create_index('COMPOUND','pert_iname', colate = nocase)
    create_index('COMPOUND','cmap_name', colate = nocase)
    create_index('COMPOUND','aliases', colate = nocase)
    create_index('COMPOUND','xref_id', colate = nocase)
    create_index('COMPOUND','inchi_key')

    create_index('GENE','gene_id')
    create_index('GENE','xref_id', colate = nocase)
    
    create_index('CMAP_SCORE','pert_id_1')
    create_index('CMAP_SCORE','pert_id_1', 'cmap_score')
    
    create_index('MOA','pert_id')


def main():
    create_tables()
    pert_ids = load_pert_ids()
    print('loaded {} compounds'.format(len(pert_ids)))
    load_compounds(pert_ids)
    load_genes(pert_ids)
    load_scores(pert_ids, 90.0)
    create_indexes()


if __name__ == '__main__':
    main()
