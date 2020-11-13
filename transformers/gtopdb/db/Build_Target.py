import sys
import sqlite3

# connection = sqlite3.connect("C:/Users/michelle/PycharmProjects/GuideToPharmacology/Ligands.db",
#                              check_same_thread=False)

connection = sqlite3.connect("C:/Users/michelle/Documents/GitHub/scb-kp-dev/transformers/gtopdb/python-flask-server/data/GtoPdb.db",
                             check_same_thread=False)

# DO I NEED TO DIVIDE UP HUMAN NUCLEOTIDE REFSEQ, HUMAN PROTEIN REFSEQ, RGC SYMBOL, RAT NUCLEOTIDE REFSEQ
# RAT SWISSPROT, RAT ENTREZ GENE, MGI SYMBOL, MGI NAME, MOUSE GENETIC LOCALISATION (SEMICOLONS), MOUSE PROTEIN REFSEQ,
# MOUSE SWISSPROT, AND MOUSE ENTREZ GENE (AND ANY OTHER COLUMNS I MISSED WITH MULTIPLE ENTRIES)
# FOR MGI ID, IS THERE A NEED FOR EACH CELL TO HAVE MGI:
# THERE'S AN AND IN THE HUMAN GENETIC LOCALISATION COLUMN
TARGET_TABLE = """
    CREATE TABLE TARGET (
        TYPE                        TEXT    NOT NULL, 
        FAMILY_ID                   INT     NOT NULL, 
        FAMILY_NAME                 TEXT    NOT NULL, 
        TARGET_ID                   INT     PRIMARY_KEY, 
        TARGET_NAME                 TEXT    NOT NULL,
        SUBUNITS                    TEXT    NOT NULL, 
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
        RGD_ID                      INT     NOT NULL, 
        RGD_SYMBOL                  TEXT    NOT NULL, 
        RGD_NAME                    TEXT    NOT NULL, 
        RAT_GENETIC_LOCALISATION    TEXT    NOT NULL, 
        RAT_NUCLEOTIDE_REFSEQ       TEXT    NOT NULL, 
        RAT_PROTEIN_REFSEQ          TEXT    NOT NULL,
        RAT_SWISSPROT               TEXT    NOT NULL, 
        RAT_ENTREZ_GENE             TEXT    NOT NULL, 
        MGI_ID                      TEXT    NOT NULL, 
        MGI_SYMBOL                  TEXT    NOT NULL, 
        MGI_NAME                    TEXT    NOT NULL, 
        MOUSE_GENETIC_LOCALISATION  TEXT    NOT NULL, 
        MOUSE_NUCLEOTIDE_REFSEQ     TEXT    NOT NULL,
        MOUSE_PROTEIN_REFSEQ        TEXT    NOT NULL,
        MOUSE_SWISSPROT             TEXT    NOT NULL, 
        MOUSE_ENTREZ_GENE           TEXT    NOT NULL 
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


def insert_target(cur, type_target, family_id, family_name, target_id, target_name, subunits, target_systematic_name,
                  target_abbreviated_name, hgnc_id, hgnc_symbol, hgnc_name, human_genetic_localisation,
                  human_nucleotide_refseq, human_protein_refseq, human_swissprot, human_entrez_gene, rgd_id, rgd_symbol,
                  rgd_name, rat_genetic_localisation, rat_nucleotide_refseq, rat_protein_refseq, rat_swissprot,
                  rat_entrez_gene, mgi_id, mgi_symbol, mgi_name, mouse_genetic_localisation, mouse_nucleotide_refseq,
                  mouse_protein_refseq, mouse_swissprot, mouse_entrez_gene):
    statement = """
        INSERT INTO TARGET (TYPE, FAMILY_ID, FAMILY_NAME, TARGET_ID,TARGET_NAME, SUBUNITS, TARGET_SYSTEMATIC_NAME,
        TARGET_ABBREVIATED_NAME, HGNC_ID, HGNC_SYMBOL, HGNC_NAME, HUMAN_GENETIC_LOCALISATION, HUMAN_NUCLEOTIDE_REFSEQ, 
        HUMAN_PROTEIN_REFSEQ, HUMAN_SWISSPROT, HUMAN_ENTREZ_GENE, RGD_ID, RGD_SYMBOL, RGD_NAME, 
        RAT_GENETIC_LOCALISATION, RAT_NUCLEOTIDE_REFSEQ, RAT_PROTEIN_REFSEQ, RAT_SWISSPROT, RAT_ENTREZ_GENE, MGI_ID, 
        MGI_SYMBOL, MGI_NAME, MOUSE_GENETIC_LOCALISATION, MOUSE_NUCLEOTIDE_REFSEQ, MOUSE_PROTEIN_REFSEQ,MOUSE_SWISSPROT, 
        MOUSE_ENTREZ_GENE)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cur.execute(statement,
                (type_target, family_id, family_name, target_id, target_name, subunits, target_systematic_name,
                 target_abbreviated_name, hgnc_id, hgnc_symbol, hgnc_name, human_genetic_localisation,
                 human_nucleotide_refseq, human_protein_refseq, human_swissprot, human_entrez_gene, rgd_id, rgd_symbol,
                 rgd_name, rat_genetic_localisation, rat_nucleotide_refseq, rat_protein_refseq, rat_swissprot,
                 rat_entrez_gene, mgi_id, mgi_symbol, mgi_name, mouse_genetic_localisation, mouse_nucleotide_refseq,
                 mouse_protein_refseq, mouse_swissprot, mouse_entrez_gene))


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
    target_synonyms = {}
    synonym_id = 0
    meg_count = 0
    cur = connection.cursor()
    # would we have an our own numbers to refer to the ligands other than ligand_id
    # had to add errors='ignore' when switching laptops, not sure why this error happened
    with open(filename, 'r', errors='ignore') as f:
        count = 1
        # to find columns of cells I need to split
        # split_list = []
        for line in f:
            # if line.rstrip() != '"Ligand id"\t"Name"\t"Species"\t"Type"\t"Approved"\t"Withdrawn"\t"Labelled"\t' \
            #                     '"Radioactive"\t"PubChem SID"\t"PubChem CID"\t"UniProt id"\t"IUPAC ' \
            #                     'name"\t"INN"\t"Synonyms"\t"SMILES"\t"InChIKey"\t"InChI"\t"GtoImmuPdb"\t"GtoMPdb"':
            #     print('ERROR: wrong ligand-file format')
            #     return
            if count == 1:
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
                subunits = row[5]
                target_systematic_name = row[6]
                target_abbreviated_name = row[7]
                synonym = row[8]
                hgnc_id = row[9].split('|')[0]
                hgnc_symbol = row[10].split('|')[0]
                hgnc_name = row[11].split('|')[0]
                human_genetic_localisation = row[12].split('|')[0]
                human_nucleotide_refseq = row[13].split('|')[0]
                human_protein_refseq = row[14].split('|')[0]
                human_swissprot = row[15].split('|')[0]
                human_entrez_gene = row[16].split('|')[0]
                rgd_id = row[17].split('|')[0]
                rgd_symbol = row[18].split('|')[0]
                rgd_name = row[19].split('|')[0]
                rat_genetic_localisation = row[20].split('|')[0]
                rat_nucleotide_refseq = row[21].split('|')[0]
                rat_protein_refseq = row[22].split('|')[0]
                rat_swissprot = row[23].split('|')[0]
                rat_entrez_gene = row[24].split('|')[0]
                mgi_id = row[25].split('|')[0]
                mgi_symbol = row[26].split('|')[0]
                mgi_name = row[27].split('|')[0]
                mouse_genetic_localisation = row[28].split('|')[0]
                mouse_nucleotide_refseq = row[29].split('|')[0]
                mouse_protein_refseq = row[30].split('|')[0]
                mouse_swissprot = row[31].split('|')[0]
                for x in row[32].strip().split('|'):
                    if not x.startswith("ENSMUSG"):
                        mouse_entrez_gene = x.strip('"')
                # ^ To take away additional " and \n at the end of the line
                # Should I create loops to separate other columns that have cells with multiple inputs
                # make a list of indexes/columns that need to be split to make if statement
                # for cell in row:
                #     if '|' in cell and not (row.index(cell) in split_list):
                #         split_list.append(row.index(cell))

                insert_target(cur, target_type, family_id, family_name, target_id, target_name, subunits,
                              target_systematic_name, target_abbreviated_name, hgnc_id, hgnc_symbol, hgnc_name,
                              human_genetic_localisation, human_nucleotide_refseq, human_protein_refseq,
                              human_swissprot, human_entrez_gene, rgd_id, rgd_symbol, rgd_name,
                              rat_genetic_localisation, rat_nucleotide_refseq, rat_protein_refseq, rat_swissprot,
                              rat_entrez_gene, mgi_id, mgi_symbol, mgi_name, mouse_genetic_localisation,
                              mouse_nucleotide_refseq, mouse_protein_refseq, mouse_swissprot, mouse_entrez_gene)
                # not sure if this the correct structure for the dictionary we want in this case,
                # are there other dictionaries that are needed? one to get synonyms?
                targets[target_name] = target_id
                target_synonyms[target_id] = synonym.split('|')
                for syn_name in synonym.split('|'):
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
parse_ligands('C:/Users/michelle/PycharmProjects/GuideToPharmacology/targets_and_families.tsv')
