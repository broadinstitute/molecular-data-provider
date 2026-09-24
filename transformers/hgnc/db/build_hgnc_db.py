import sqlite3
import sys
import pandas as pd

connection_source = None

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
            rna_central_id           INT,
            lncipedia                TEXT,
            gtrnadb                  TEXT,
            agr                      TEXT,
            mane_select              TEXT,
            gencc                    TEXT
        );

        CREATE TABLE version (
            version    TEXT
        );
    '''
    cur = connection_source.cursor()
    cur.executescript(statement)


def validate_columns(df):
    # Get column names from the SQLite database
    cur = connection_source.cursor()
    cur.execute("PRAGMA table_info(hgnc);")
    db_columns = [row[1] for row in cur.fetchall()]  # Extract column names from the schema
    cur.close()

    # Get column names from the DataFrame
    df_columns = df.columns.tolist()

    # Compare columns
    missing_in_db = [col for col in df_columns if col not in db_columns]
    missing_in_df = [col for col in db_columns if col not in df_columns]

    if missing_in_db:
        print("Columns in DataFrame but missing in database:", missing_in_db, file=sys.stderr)
    if missing_in_df:
        print("Columns in database but missing in DataFrame:", missing_in_df, file=sys.stderr)
    if missing_in_db or missing_in_df:
        print("Column mismatch between DataFrame and database schema.", file=sys.stderr)
        sys.exit(1)

def insert_version(version):
    statement = """
        INSERT INTO version (version) VALUES (?);
    """
    cur = connection_source.cursor()
    cur.execute(statement, (version,))
    cur.close()


def build_database(folder):
    insert_version(folder)
    df = pd.read_csv(f'data/{folder}/hgnc_complete_set_{folder}.txt', sep="\t", low_memory=False)
    print('gene count:', len(df))
    validate_columns(df)
    df.to_sql("hgnc", connection_source, if_exists=DO_IF_EXISTS, index=False, chunksize=CHUNK_SIZE)
    print("hgnc_complete_set loaded into database.")


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


def main():
    global connection_source
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        connection_source = sqlite3.connect(f"data/{folder}/HGNC.sqlite", check_same_thread=False)
        connection_source.row_factory = sqlite3.Row
        create_database()
        build_database(folder)
        create_indexes()
        connection_source.commit()
        connection_source.close()
    else:
        print("Please provide the folder path as an argument.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
