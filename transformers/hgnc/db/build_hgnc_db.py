import sqlite3
import pandas as pd

connection_source = sqlite3.connect("data/HGNC.sqlite", check_same_thread=False)
connection_source.row_factory = sqlite3.Row

CHUNK_SIZE = 25000
DO_IF_EXISTS = 'append'
nocase='NOCASE'


def create_database():
    statement = '''
        CREATE TABLE hgnc (
            hgnc_id                  TEXT  PRIMARY KEY,
            symbol                   TEXT,
            name                     TEXT,
            locus_group              TEXT,
            locus_type               TEXT,
            status                   TEXT,
            location                 TEXT,
            location_sortable        TEXT,
            alias_symbol             TEXT,
            alias_name               TEXT,
            prev_symbol              TEXT,
            prev_name                TEXT,
            gene_group               TEXT,
            gene_group_id            TEXT,
            date_approved_reserved   TEXT,
            date_symbol_changed      TEXT,
            date_name_changed        TEXT,
            date_modified            TEXT,
            entrez_id                INT,
            ensembl_gene_id          TEXT,
            vega_id                  TEXT,
            ucsc_id                  TEXT,
            ena                      TEXT,
            refseq_accession         TEXT,
            ccds_id                  TEXT,
            uniprot_ids              TEXT,
            pubmed_id                TEXT,
            mgd_id                   TEXT,
            rgd_id                   TEXT,
            lsdb                     TEXT,
            cosmic                   TEXT,
            omim_id                  TEXT,
            mirbase                  TEXT,
            homeodb                  INT,
            snornabase               TEXT,
            bioparadigms_slc         TEXT,
            orphanet                 INT,
            [pseudogene.org]         TEXT,
            horde_id                 TEXT,
            merops                   TEXT,
            imgt                     TEXT,
            iuphar                   TEXT,
            kznf_gene_catalog        INT,
            [mamit-trnadb]           INT,
            cd                       TEXT,
            lncrnadb                 TEXT,
            enzyme_id                TEXT,
            intermediate_filament_db TEXT,
            rna_central_ids          INT,
            lncipedia                TEXT,
            gtrnadb                  TEXT,
            agr                      TEXT,
            mane_select              TEXT,
            gencc                    TEXT
        );
    '''
    cur = connection_source.cursor()
    cur.executescript(statement)


def build_database():
    df = pd.read_csv('data/hgnc_complete_set_2023-01-01.txt', sep="\t", low_memory=False)
    print(len(df))
    df.to_sql("hgnc", connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    print("hgnc_complete_set")


def create_index(table, column, colate=None):
    colate_nocase = 'COLLATE ' + nocase if colate == nocase else ''
    statement = """
        CREATE INDEX {}_{}_idx 
        ON {} ({} {});    
    """.format(table, column,table, column, colate_nocase)
    cur = connection_source.cursor()
    cur.executescript(statement)
    cur.close()


def create_indexes():
    create_index('hgnc', 'symbol', colate=nocase)
    create_index('hgnc', 'name', colate=nocase)
    create_index('hgnc', 'entrez_id')
    create_index('hgnc', 'ensembl_gene_id')


if __name__ == "__main__":
    create_database()
    build_database()
    create_indexes()
