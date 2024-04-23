import sys
import sqlite3
import itertools

connection = sqlite3.connect("data/GtoPdb.sqlite", check_same_thread=False)

TARGET_TABLE = """
    CREATE TABLE TARGET (
        TYPE                        TEXT    NOT NULL, 
        FAMILY_ID                   INT     NOT NULL, 
        FAMILY_NAME                 TEXT    NOT NULL, 
        TARGET_ID                   INT     PRIMARY_KEY, 
        TARGET_NAME                 TEXT    NOT NULL,
        SUBUNIT_ID                  TEXT    NOT NULL, 
        SUBUNIT_NAME                TEXT    NOT NULL,
        TARGET_SYSTEMATIC_NAME      TEXT    NOT NULL, 
        TARGET_ABBREVIATED_NAME     TEXT    NOT NULL, 
        HGNC_ID                     INT     NOT NULL,  
        HGNC_SYMBOL                 TEXT    NOT NULL, 
        HGNC_NAME                   TEXT    NOT NULL, 
        HUMAN_GENETIC_LOCALISATION  TEXT    NOT NULL, 
        HUMAN_NUCLEOTIDE_REFSEQ     TEXT    NOT NULL,
        HUMAN_PROTEIN_REFSEQ        TEXT    NOT NULL,
        HUMAN_SWISSPROT             TEXT    NOT NULL, 
        HUMAN_ENTREZ_GENE           INT     NOT NULL,
        HUMAN_ENSEMBL_GENE          TEXT    NOT NULL, 
        RGD_ID                      INT     NOT NULL, 
        RGD_SYMBOL                  TEXT    NOT NULL, 
        RGD_NAME                    TEXT    NOT NULL, 
        RAT_GENETIC_LOCALISATION    TEXT    NOT NULL, 
        RAT_NUCLEOTIDE_REFSEQ       TEXT    NOT NULL, 
        RAT_PROTEIN_REFSEQ          TEXT    NOT NULL,
        RAT_SWISSPROT               TEXT    NOT NULL, 
        RAT_ENTREZ_GENE             TEXT    NOT NULL,
        RAT_EMSEMBL_GENE            TEXT    NOT NULL, 
        MGI_ID                      TEXT    NOT NULL, 
        MGI_SYMBOL                  TEXT    NOT NULL, 
        MGI_NAME                    TEXT    NOT NULL, 
        MOUSE_GENETIC_LOCALISATION  TEXT    NOT NULL, 
        MOUSE_NUCLEOTIDE_REFSEQ     TEXT    NOT NULL,
        MOUSE_PROTEIN_REFSEQ        TEXT    NOT NULL,
        MOUSE_SWISSPROT             TEXT    NOT NULL, 
        MOUSE_ENTREZ_GENE           TEXT    NOT NULL,
        MOUSE_ENSEMBL_GENE          TEXT    NOT NULL 
    );      
"""

TARGET_SYNONYM_TABLE = """
    CREATE TABLE TARGET_SYNONYM (
        SYNONYM_ID  INT PRIMARY_KEY,
        SYNONYM_NAME    TEXT    NOT NULL,
        TARGET_ID   INT REFERENCES TARGET(TARGET_ID)
    );
"""


def create_tables():
    cur = connection.cursor()
    cur.execute(TARGET_TABLE)
    cur.execute(TARGET_SYNONYM_TABLE)
    cur.close()
    connection.commit()


def insert_target(cur, type_target, family_id, family_name, target_id, target_name, subunit_ids, subunit_names, target_systematic_name,
                  target_abbreviated_name, hgnc_id, hgnc_symbol, hgnc_name, human_genetic_localisation,
                  human_nucleotide_refseq, human_protein_refseq, human_swissprot, human_entrez_gene, human_ensembl_gene, rgd_id, rgd_symbol,
                  rgd_name, rat_genetic_localisation, rat_nucleotide_refseq, rat_protein_refseq, rat_swissprot,
                  rat_entrez_gene, rat_ensembl_gene, mgi_id, mgi_symbol, mgi_name, mouse_genetic_localisation, mouse_nucleotide_refseq,
                  mouse_protein_refseq, mouse_swissprot, mouse_entrez_gene, mouse_ensembl_gene):
    statement = """
        INSERT INTO TARGET (TYPE, FAMILY_ID, FAMILY_NAME, TARGET_ID,TARGET_NAME, SUBUNIT_ID, SUBUNIT_NAME, TARGET_SYSTEMATIC_NAME,
        TARGET_ABBREVIATED_NAME, HGNC_ID, HGNC_SYMBOL, HGNC_NAME, HUMAN_GENETIC_LOCALISATION, HUMAN_NUCLEOTIDE_REFSEQ, 
        HUMAN_PROTEIN_REFSEQ, HUMAN_SWISSPROT, HUMAN_ENTREZ_GENE, HUMAN_ENSEMBL_GENE, RGD_ID, RGD_SYMBOL, RGD_NAME, 
        RAT_GENETIC_LOCALISATION, RAT_NUCLEOTIDE_REFSEQ, RAT_PROTEIN_REFSEQ, RAT_SWISSPROT, RAT_ENTREZ_GENE, RAT_EMSEMBL_GENE, MGI_ID, 
        MGI_SYMBOL, MGI_NAME, MOUSE_GENETIC_LOCALISATION, MOUSE_NUCLEOTIDE_REFSEQ, MOUSE_PROTEIN_REFSEQ, MOUSE_SWISSPROT, 
        MOUSE_ENTREZ_GENE, MOUSE_ENSEMBL_GENE)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """

    # Iterates over 2 lists and till all are exhausted, when the shorter list is exhausted, itertools.zip_longest yields a tuple with None value. 
    subunit_ids_list   = subunit_ids.split('|')
    subunit_names_list = subunit_names.split('|')
    for (subunit_id, subunit_name ) in itertools.zip_longest(subunit_ids_list, subunit_names_list):
        cur.execute(statement,
                    (type_target, family_id, family_name, target_id, target_name, subunit_id, subunit_name, target_systematic_name,
                    target_abbreviated_name, hgnc_id, hgnc_symbol, hgnc_name, human_genetic_localisation,
                    human_nucleotide_refseq, human_protein_refseq, human_swissprot, human_entrez_gene, human_ensembl_gene, rgd_id, rgd_symbol,
                    rgd_name, rat_genetic_localisation, rat_nucleotide_refseq, rat_protein_refseq, rat_swissprot,
                    rat_entrez_gene, rat_ensembl_gene, mgi_id, mgi_symbol, mgi_name, mouse_genetic_localisation, mouse_nucleotide_refseq,
                    mouse_protein_refseq, mouse_swissprot, mouse_entrez_gene, mouse_ensembl_gene))


def insert_target_synonym(cur, synonym_id, synonym_name, target_id):
    statement = """
        INSERT INTO TARGET_SYNONYM (SYNONYM_ID, SYNONYM_NAME, TARGET_ID) VALUES (?,?,?)
    """
    cur.execute(statement, (synonym_id, synonym_name, target_id))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX {}_{}_IDX ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    cur = connection.cursor()
    create_index(cur, 'TARGET', 'TARGET_NAME')
    create_index(cur, 'TARGET', 'TARGET_ID')
    create_index(cur, 'TARGET', 'HGNC_ID')
    create_index(cur, 'TARGET', 'HGNC_NAME')
    create_index(cur, 'TARGET', 'RGD_ID')
    create_index(cur, 'TARGET', 'RGD_NAME')
    create_index(cur, 'TARGET', 'MGI_ID')
    create_index(cur, 'TARGET', 'MGI_NAME')
    create_index(cur, 'TARGET_SYNONYM', 'TARGET_ID')
    create_index(cur, 'TARGET_SYNONYM', 'SYNONYM_NAME')
    cur.close()
    connection.commit()


def parse_ligands(filename):
    targets = {}
    #target_synonyms = {}
    synonym_id = 0
    meg_count = 0
    cur = connection.cursor()
    with open(filename, 'r', errors='ignore') as f:
        count = 0
        # to find columns of cells I need to split
        # split_list = []
        for line in f:
            # if line.rstrip() != '"Ligand id"\t"Name"\t"Species"\t"Type"\t"Approved"\t"Withdrawn"\t"Labelled"\t' \
            #                     '"Radioactive"\t"PubChem SID"\t"PubChem CID"\t"UniProt id"\t"IUPAC ' \
            #                     'name"\t"INN"\t"Synonyms"\t"SMILES"\t"InChIKey"\t"InChI"\t"GtoImmuPdb"\t"GtoMPdb"':
            #     print('ERROR: wrong ligand-file format')
            #     return
            if count <=1:  # we want to skip the first two lines of header in the tsv file
                count += 1
            else:
                row = line.split('\t')
                for i in range(len(row)):
                    row[i] = row[i].strip('"')
                # print(row)
                target_type = row[0]
                family_id = row[1]
                family_name = row[2]
                target_id = row[3]
                target_name = row[4]
                subunit_ids = row[5]
                subunit_names = row[6]
                target_systematic_name = row[7]
                target_abbreviated_name = row[8]
                synonyms = row[9]
                hgnc_id = row[10].split('|')[0]
                hgnc_symbol = row[11].split('|')[0]
                hgnc_name = row[12].split('|')[0]
                human_genetic_localisation = row[13].split('|')[0]
                human_nucleotide_refseq = row[14].split('|')[0]
                human_protein_refseq = row[15].split('|')[0]
                human_swissprot = row[16].split('|')[0]
                human_entrez_gene = row[17].split('|')[0]
                human_ensembl_gene = row[18].split('|')[0]
                rgd_id = row[19].split('|')[0]
                rgd_symbol = row[20].split('|')[0]
                rgd_name = row[21].split('|')[0]
                rat_genetic_localisation = row[22].split('|')[0]
                rat_nucleotide_refseq = row[23].split('|')[0]
                rat_protein_refseq = row[24].split('|')[0]
                rat_swissprot = row[25].split('|')[0]
                rat_entrez_gene = row[26].split('|')[0]
                rat_ensembl_gene = row[27].split('|')[0]
                mgi_id = row[28].split('|')[0]
                mgi_symbol = row[29].split('|')[0]
                mgi_name = row[30].split('|')[0]
                mouse_genetic_localisation = row[31].split('|')[0]
                mouse_nucleotide_refseq = row[32].split('|')[0]
                mouse_protein_refseq = row[33].split('|')[0]
                mouse_swissprot = row[34].split('|')[0]
                for x in row[35].strip().split('|'):
                    if not x.startswith("ENSMUSG"):
                        mouse_entrez_gene = x.strip('"')
                mouse_ensembl_gene = row[36].split('|')[0]

                insert_target(cur, target_type, family_id, family_name, target_id, target_name, subunit_ids, subunit_names,
                              target_systematic_name, target_abbreviated_name, hgnc_id, hgnc_symbol, hgnc_name,
                              human_genetic_localisation, human_nucleotide_refseq, human_protein_refseq,
                              human_swissprot, human_entrez_gene, human_ensembl_gene, rgd_id, rgd_symbol, rgd_name,
                              rat_genetic_localisation, rat_nucleotide_refseq, rat_protein_refseq, rat_swissprot,
                              rat_entrez_gene, rat_ensembl_gene, mgi_id, mgi_symbol, mgi_name, mouse_genetic_localisation,
                              mouse_nucleotide_refseq, mouse_protein_refseq, mouse_swissprot, mouse_entrez_gene, mouse_ensembl_gene)
                targets[target_name] = target_id
                #target_synonyms[target_id] = synonym.split('|')
                for syn_name in synonyms.split('|'):
                    synonym_id += 1
                    insert_target_synonym(cur, synonym_id, syn_name, target_id)

                # Check if everything was parsed correctly
                # if not (isinstance(int(family_id), int) and isinstance(int(target_id), int) and
                #         isinstance(int(hgnc_id), int) and isinstance(int(rgd_id), int) and
                #         isinstance(int(mouse_entrez_gene), int)):
                #     print('Error: Parsing of data is incorrect')
                #     print(row)
                #     if not isinstance(int(family_id), int):
                #         print('Family id is not an integer')
                #     elif not isinstance(int(target_id), int):
                #         print('Target id is not an integer')
                #     elif not isinstance(int(hgnc_id), int):
                #         print('HGNC id is not an integer')
                #     elif not isinstance(int(rgd_id), int):
                #         print('RGD id is not an integer')
                #     elif not isinstance(int(mouse_entrez_gene), int):
                #         print('Mouse entrez gene id is not an integer')
                
                if mouse_entrez_gene == '':
                    meg_count += 1
                # Because of value errors
                elif mouse_entrez_gene == 'ENSMUSG000000025':
                    print(row)
                elif not (isinstance(int(family_id), int) and isinstance(int(target_id), int) and
                        isinstance(int(mouse_entrez_gene), int)):
                    print('Error: Parsing of data is incorrect')
                    print(row)
                    if not isinstance(int(family_id), int):
                        print('Family id is not an integer')
                    elif not isinstance(int(target_id), int):
                        print('Target id is not an integer')
                    elif not isinstance(int(mouse_entrez_gene), int):
                        print('Mouse entrez gene id is not an integer')

    cur.close()
    connection.commit()
    print(meg_count)
    # print(target_synonyms)
    # split_list.sort()
    # print(split_list)


create_tables()
create_indexes()
parse_ligands('data/targets_and_families.tsv')
