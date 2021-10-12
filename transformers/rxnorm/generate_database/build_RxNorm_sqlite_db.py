import sys
import sqlite3
import requests


connection = sqlite3.connect("data/RXNORM+UNII.sqlite", check_same_thread=False)


RXNCONSO_TABLE = """
    CREATE TABLE RXNCONSO (
    RXCUI    INT  NOT NULL,
    LAT      TEXT NOT NULL,
    TS       TEXT DEFAULT NULL,
    LUI      TEXT DEFAULT NULL,
    STT      TEXT DEFAULT NULL,
    SUI      TEXT DEFAULT NULL,
    ISPREF   TEXT DEFAULT NULL,
    RXAUI    INT  NOT NULL,
    SAUI     INT  DEFAULT NULL,
    SCUI     INT  DEFAULT NULL,
    SDUI     TEXT DEFAULT NULL,
    SAB      TEXT NOT NULL,
    TTY      TEXT NOT NULL,
    CODE     TEXT NOT NULL,
    STR      TEXT NOT NULL
                  COLLATE NOCASE,
    SRL      TEXT DEFAULT NULL,
    SUPPRESS TEXT DEFAULT NULL,
    CVF      INT  DEFAULT NULL
    );
"""


RXNREL_TABLE = """
    CREATE TABLE RXNREL (
    RXCUI1   INT DEFAULT NULL,
    RXAUI1   INT  DEFAULT NULL,
    STYPE1   TEXT DEFAULT NULL,
    REL      TEXT DEFAULT NULL,
    RXCUI2   INT DEFAULT NULL,
    RXAUI2   INT  DEFAULT NULL,
    STYPE2   TEXT DEFAULT NULL,
    RELA     TEXT DEFAULT NULL,
    RUI      TEXT DEFAULT NULL,
    SRUI     TEXT DEFAULT NULL,
    SAB      TEXT NOT NULL,
    SL       TEXT DEFAULT NULL,
    DIR      TEXT DEFAULT NULL,
    RG       TEXT DEFAULT NULL,
    SUPPRESS TEXT DEFAULT NULL,
    CVF      INT  DEFAULT NULL
    );
"""


RXNSAT_TABLE = """
    CREATE TABLE RXNSAT (
    RXCUI    INT  DEFAULT NULL,
    LUI      TEXT DEFAULT NULL,
    SUI      TEXT DEFAULT NULL,
    RXAUI    INT  DEFAULT NULL,
    STYPE    TEXT DEFAULT NULL,
    CODE     INT  DEFAULT NULL,
    ATUI     TEXT DEFAULT NULL,
    SATUI    TEXT DEFAULT NULL,
    ATN      TEXT NOT NULL,
    SAB      TEXT NOT NULL,
    ATV      TEXT DEFAULT NULL,
    SUPPRESS TEXT DEFAULT NULL,
    CVF      INT  DEFAULT NULL
    );
"""


UNII_TABLE = """
    CREATE TABLE UNII (
    UNII            TEXT DEFAULT NULL,
    PT              TEXT DEFAULT NULL 
                         COLLATE NOCASE,
    RN              TEXT DEFAULT NULL,
    EC              TEXT DEFAULT NULL,
    NCIT            TEXT DEFAULT NULL,
    RXCUI           INT  DEFAULT NULL,
    PUBCHEM         INT  DEFAULT NULL,
    ITIS            INT  DEFAULT NULL,
    NCBI            INT  DEFAULT NULL,
    PLANTS          TEXT DEFAULT NULL,
    GRIN            INT  DEFAULT NULL,
    MPNS            TEXT DEFAULT NULL,
    INN_ID          INT  DEFAULT NULL,
    MF              TEXT DEFAULT NULL,
    INCHIKEY        TEXT DEFAULT NULL,
    SMILES          TEXT DEFAULT NULL,
    INGREDIENT_TYPE TEXT DEFAULT NULL
    );
"""

# CREATE INDEX IDX_UNII_PT ON UNII (
#     PT
# );


def create_tables():
    cur = connection.cursor()
    cur.execute(RXNCONSO_TABLE)
    cur.execute(RXNREL_TABLE)
    cur.execute(RXNSAT_TABLE)
    cur.execute(UNII_TABLE)
    cur.close()
    connection.commit()


# feature_types = ['','clinical_phase','moa','target','disease_area','indication']


def insert_rxnconso(cur, rxcui, lat, ts, lui, stt, sui, ispref, rxaui, saui, scui, sdui, sab, tty, code, str, srl, suppress, cvf):
    statement = """
        INSERT INTO RXNCONSO (RXCUI, LAT, TS, LUI, STT, SUI, ISPREF, RXAUI, SAUI, SCUI, SDUI, SAB, TTY, CODE, STR, SRL, SUPPRESS, CVF) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cur.execute(statement, (rxcui, lat, ts, lui, stt, sui, ispref, rxaui,
                            saui, scui, sdui, sab, tty, code, str, srl, suppress, cvf))


def insert_rxnrel(cur, rxcui1, rxaui1, stype1, rel, rxcui2, rxaui2, stype2, rela, rui, srui, sab, sl, dir, rg, suppress, cvf):
    statement = """
        INSERT INTO RXNREL (RXCUI1, RXAUI1, STYPE1, REL, RXCUI2, RXAUI2, STYPE2, RELA, RUI, SRUI, SAB, SL, DIR, RG, SUPPRESS, CVF) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(statement, (rxcui1, rxaui1, stype1, rel, rxcui2, rxaui2,
                            stype2, rela, rui, srui, sab, sl, dir, rg, suppress, cvf))


def insert_rxnsat(cur, rxcui, lui, sui, rxaui, stype, code, atui, satui, atn, sab, atv, suppress, cvf):
    statement = """
        INSERT INTO RXNSAT (RXCUI, LUI, SUI, RXAUI, STYPE, CODE, ATUI, SATUI, ATN, SAB, ATV, SUPPRESS, CVF) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(statement, (rxcui, lui, sui, rxaui, stype, code,
                            atui, satui, atn, sab, atv, suppress, cvf))


def insert_unii(cur, unii, pt, rn, ec, ncit, rxcui, pubchem, itis, ncbi, plants, grin, mpns, inn_id, mf, inchikey, smiles, ingredient_type):
    statement = """
        INSERT INTO UNII (UNII, PT, RN, EC, NCIT, RXCUI, PUBCHEM, ITIS, NCBI, PLANTS, GRIN, MPNS, INN_ID, MF, INCHIKEY, SMILES, INGREDIENT_TYPE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?)
    """
    cur.execute(statement, (unii, pt, rn, ec, ncit, rxcui, pubchem, itis, ncbi, plants,
                            grin, mpns, inn_id, mf, inchikey, smiles, ingredient_type.rstrip('\n')))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX IDX_{}_{} ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    cur = connection.cursor()
    create_index(cur, 'UNII', 'PT')
    create_index(cur, 'UNII', 'RXCUI')
    create_index(cur, 'UNII', 'UNII')
    create_index(cur, 'UNII', 'RN')
    create_index(cur, 'UNII', 'NCIT')
    create_index(cur, 'UNII', 'INCHIKEY')
    create_index(cur, 'UNII', 'MF')
    create_index(cur, 'RXNCONSO', 'CODE')
    create_index(cur, 'RXNCONSO', 'STR')
    create_index(cur, 'RXNREL', 'RXCUI1')
    create_index(cur, 'RXNREL', 'RXCUI2')
    create_index(cur, 'RXNSAT', 'RXCUI')
    cur.close()
    connection.commit()


def parse_rxnconso(filename):
    cur = connection.cursor()
    with open(filename, 'r') as f:
        for line in f:
            row = line.split('|')
            # print(row)
            a0 = row[0]
            a1 = row[1]
            a2 = row[2]
            a3 = row[3]
            a4 = row[4]
            a5 = row[5]
            a6 = row[6]
            a7 = row[7]
            a8 = row[8]
            a9 = row[9]
            a10 = row[10]
            a11 = row[11]
            a12 = row[12]
            a13 = row[13]
            a14 = row[14]
            a15 = row[15]
            a16 = row[16]
            a17 = row[17]

            insert_rxnconso(cur, a0, a1, a2, a3, a4, a5, a6, a7,
                            a8, a9, a10, a11, a12, a13, a14, a15, a16, a17)

    cur.close()
    connection.commit()
    # return rxnconso


def parse_rxnrel(filename):
    cur = connection.cursor()
    with open(filename, 'r') as f:
        for line in f:
            row = line.split('|')
            # print(row)
            a0 = row[0]
            a1 = row[1]
            a2 = row[2]
            a3 = row[3]
            a4 = row[4]
            a5 = row[5]
            a6 = row[6]
            a7 = row[7]
            a8 = row[8]
            a9 = row[9]
            a10 = row[10]
            a11 = row[11]
            a12 = row[12]
            a13 = row[13]
            a14 = row[14]
            a15 = row[15]

            insert_rxnrel(cur, a0, a1, a2, a3, a4, a5, a6, a7,
                          a8, a9, a10, a11, a12, a13, a14, a15)

    cur.close()
    connection.commit()
    # return rxnrel


def parse_rxnsat(filename):
    cur = connection.cursor()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            row = line.split('|')
            # print(row)
            a0 = row[0]
            a1 = row[1]
            a2 = row[2]
            a3 = row[3]
            a4 = row[4]
            a5 = row[5]
            a6 = row[6]
            a7 = row[7]
            a8 = row[8]
            a9 = row[9]
            a10 = row[10]
            a11 = row[11]
            a12 = row[12]

            insert_rxnsat(cur, a0, a1, a2, a3, a4, a5,
                          a6, a7, a8, a9, a10, a11, a12)

    cur.close()
    connection.commit()
    # return rxnsat


def parse_unii(filename):
    cur = connection.cursor()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            row = line.split('\t')
            # print(row)
            a0 = row[0]
            a1 = row[1]
            a2 = row[2]
            a3 = row[3]
            a4 = row[4]
            a5 = row[5]
            a6 = row[6]
            a7 = row[7]
            a8 = row[8]
            a9 = row[9]
            a10 = row[10]
            a11 = row[11]
            a12 = row[12]
            a13 = row[13]
            a14 = row[14]
            a15 = row[15]
            a16 = row[16]

            insert_unii(cur, a0, a1, a2, a3, a4, a5, a6, a7, a8,
                        a9, a10, a11, a12, a13, a14, a15, a16)

    cur.close()
    connection.commit()


def main():
    create_tables()
    rxnconso = parse_rxnconso('data/RXNCONSO.RRF')
    rxnrel = parse_rxnrel('data/RXNREL.RRF')
    rxnsat = parse_rxnsat('data/RXNSAT.RRF')
    unii = parse_unii('data/UNII_Records_18Aug2020.txt')
    create_indexes()
    connection.close()


if __name__ == '__main__':
    main()
