import sqlite3


connection = sqlite3.connect("data/rxnorm.sqlite", check_same_thread=False)

primary_rxcui_map = {}


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


DRUG_MAP_TABLE = """
    CREATE TABLE DRUG_MAP (
        PRIMARY_RXCUI  INT  NOT NULL,
        RXCUI          INT  NOT NULL
    )
"""


def create_tables():
    cur = connection.cursor()
    cur.execute(RXNCONSO_TABLE)
    cur.execute(RXNREL_TABLE)
    cur.execute(RXNSAT_TABLE)
    cur.execute(UNII_TABLE)
    cur.close()
    connection.commit()


def create_drug_table():
    cur = connection.cursor()
    cur.execute(DRUG_MAP_TABLE)
    create_index(cur, 'DRUG_MAP', 'PRIMARY_RXCUI')
    create_index(cur, 'DRUG_MAP', 'RXCUI')
    cur.close()


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


def insert_drug(cur, primary_rxcui, rxcui):
    statement = """
        INSERT INTO DRUG_MAP (PRIMARY_RXCUI, RXCUI) VALUES (?, ?)
    """
    if rxcui not in primary_rxcui_map:
        primary_rxcui_map[rxcui] = {primary_rxcui}
        cur.execute(statement, (primary_rxcui, rxcui))
    elif primary_rxcui not in primary_rxcui_map[rxcui]:
        primary_rxcui_map[rxcui].add(primary_rxcui)
        print("WARN: duplicate RXCUI "+str(rxcui)+",  PRIMARY_RXCUI = "+str(primary_rxcui_map[rxcui]))
        cur.execute(statement, (primary_rxcui, rxcui))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX IDX_{}_{} ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    print("create_indexes")
    cur = connection.cursor()
    create_index(cur, 'UNII', 'PT')
    create_index(cur, 'UNII', 'RXCUI')
    create_index(cur, 'UNII', 'UNII')
    create_index(cur, 'UNII', 'RN')
    create_index(cur, 'UNII', 'NCIT')
    create_index(cur, 'UNII', 'INCHIKEY')
    create_index(cur, 'UNII', 'MF')
    create_index(cur, 'RXNCONSO', 'CODE')
    create_index(cur, 'RXNCONSO', 'RXCUI')
    create_index(cur, 'RXNCONSO', 'STR')
    create_index(cur, 'RXNCONSO', 'TTY')
    create_index(cur, 'RXNREL', 'RXCUI1')
    create_index(cur, 'RXNREL', 'RXCUI2')
    create_index(cur, 'RXNREL', 'RELA')
    create_index(cur, 'RXNSAT', 'RXCUI')
    cur.close()
    connection.commit()


def parse_rxnconso(filename):
    print("parse_rxnconso")
    cur = connection.cursor()
    with open(filename, 'r') as f:
        for line in f:
            row = line.split('|')
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


def parse_rxnrel(filename):
    print("parse_rxnrel")
    cur = connection.cursor()
    with open(filename, 'r') as f:
        for line in f:
            row = line.split('|')
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


def parse_rxnsat(filename):
    print("parse_rxnsat")
    cur = connection.cursor()
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            row = line.split('|')
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


def parse_unii(filename):
    print("parse_unii")
    cur = connection.cursor()
    with open(filename, 'r', encoding='utf-8') as f:
        # skip header line
        f.readline()
        for line in f:
            row = line.split('\t')
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


def load_rxcui(tty):
    query = """
    SELECT DISTINCT RXCUI FROM RXNCONSO WHERE TTY = ?
    """
    cur = connection.execute(query, (tty,))
    return cur.fetchall()


def save_precise_ingredients():
    query = """
        SELECT DISTINCT RXNREL.RXCUI1 AS PRIMARY_RXCUI, RXNREL.RXCUI2 AS RXCUI
        FROM RXNCONSO AS RXNCONSO1
        JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = 'IN' AND RELA = 'form_of'
        JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY = 'PIN'
        WHERE PRIMARY_RXCUI = ?
    """
    print("precise_ingredients")
    save(query, 'IN' )
    print("precise_ingredients done")


def save_multiple_ingredients():
    query = """
        SELECT DISTINCT RXNREL.RXCUI1 AS PRIMARY_RXCUI, RXNREL.RXCUI2 AS RXCUI
        FROM RXNCONSO AS RXNCONSO1
        JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = 'MIN' AND RELA = 'has_ingredients'
        JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY = 'SCD'
        WHERE (RXCUI1 != 2591374 OR RXCUI2 != 1115991)
        AND PRIMARY_RXCUI = ?
    """
    print("multiple_ingredients")
    save(query, 'MIN')
    print("multiple_ingredients done")


def save_drug_component():
    query = """
        SELECT DISTINCT RXNREL.RXCUI1 AS PRIMARY_RXCUI, RXNREL.RXCUI2 AS RXCUI
        FROM RXNCONSO AS RXNCONSO1
        JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = 'IN' AND RELA = 'has_ingredient'
        JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY = 'SCDC'
        WHERE PRIMARY_RXCUI = ?
    """
    print("drug_component")
    save(query, 'IN')
    print("drug_component done")


def save_clinical_drug():
    query = """
        SELECT DISTINCT RXNREL.RXCUI1 AS SRC_RXCUI, RXNREL.RXCUI2 AS RXCUI
        FROM RXNCONSO AS RXNCONSO1
        JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = 'SCDC' AND RXNREL.RELA = 'consists_of'
        JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY = 'SCD'
        LEFT JOIN RXNREL AS RXNREL2 ON RXNREL2.RXCUI2 = RXNCONSO2.RXCUI AND RXNREL2.RELA = 'has_ingredients'
        WHERE RXNREL2.RELA IS NULL AND SRC_RXCUI = ?
    """
    print("clinical_drug")
    save(query, 'SCDC', map_rxcui = True)
    print("clinical_drug done")


def save_drug_form():
    query = """
        SELECT DISTINCT RXNREL.RXCUI1 AS SRC_RXCUI, RXNREL.RXCUI2 AS RXCUI
        FROM RXNCONSO AS RXNCONSO1
        JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = 'SCD' AND RELA = 'inverse_isa'
        JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY IN ('SCDG','SCDF')
        WHERE SRC_RXCUI = ?
    """
    print("drug_form")
    save(query, 'SCD', map_rxcui = True)
    print("drug_form done")


def save_branded_drugs():
    for tty1, tty2 in [('SCD','SBD'),('SCDG','SBDG'),('SCDF','SBDF')]:
        query = """
            SELECT DISTINCT RXNREL.RXCUI1 AS SRC_RXCUI, RXNREL.RXCUI2 AS RXCUI
            FROM RXNCONSO AS RXNCONSO1
            JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = '{}' AND RELA = 'tradename_of'
            JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY = '{}'
            WHERE SRC_RXCUI = ?
        """.format(tty1, tty2)
        print("branded_drug ({})".format(tty2))
        save(query, tty1, map_rxcui = True)
        print("branded_drug ({}) done".format(tty2))


def save_branded_components():
    query = """
        SELECT DISTINCT RXNREL.RXCUI1 AS SRC_RXCUI, RXNREL.RXCUI2 AS RXCUI
        FROM RXNCONSO AS RXNCONSO1
        JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = 'SBD' AND RELA = 'constitutes'
        JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY = 'SBDC'
        WHERE SRC_RXCUI = ?
    """
    print("branded_components")
    save(query, 'SBD', map_rxcui = True)
    print("branded_components done")


def save_branded_names():
    query = """
        SELECT DISTINCT RXNREL.RXCUI1 AS SRC_RXCUI, RXNREL.RXCUI2 AS RXCUI
        FROM RXNCONSO AS RXNCONSO1
        JOIN RXNREL ON RXNREL.RXCUI1 = RXNCONSO1.RXCUI AND RXNCONSO1.TTY = 'SBDF' AND RELA = 'ingredient_of'
        JOIN RXNCONSO AS RXNCONSO2 ON RXNCONSO2.RXCUI = RXNREL.RXCUI2 and RXNCONSO2.TTY = 'BN'
        WHERE SRC_RXCUI = ?
    """
    print("drug_names")
    save(query, 'SBDF', map_rxcui = True)
    print("drug_names done")


def save(query, tty, map_rxcui = False):
    cur1 = connection.cursor()
    i = 0
    for rxcui in load_rxcui(tty):
        cur = connection.execute(query, (rxcui[0],))
        i = i + 1
        if i % 100 == 0:
            print('.', end = ' ', flush = True)
        if i % 1000 == 0:
            print(i)
        for row in cur.fetchall():
            primary_rxcui = row[0]
            if map_rxcui:
                primary_rxcuis = primary_rxcui_map.get(primary_rxcui)
                if primary_rxcuis is not None:
                    for primary_rxcui in primary_rxcuis:
                        insert_drug(cur1, primary_rxcui, row[1])
                else:
                    print('WARN: cannot map {}'.format(rxcui))
            else:
                insert_drug(cur1, primary_rxcui, row[1])
    connection.commit()


def main():
    create_tables()
    parse_rxnconso('data/RXNCONSO.RRF')
    parse_rxnrel('data/RXNREL.RRF')
    parse_rxnsat('data/RXNSAT.RRF')
    parse_unii('data/UNII_Records.txt')
    create_indexes()

    create_drug_table()
    save_precise_ingredients()
    save_multiple_ingredients()
    save_drug_component()
    save_clinical_drug()
    save_drug_form()
    save_branded_drugs()
    save_branded_components()
    save_branded_names()
    connection.close()

if __name__ == '__main__':
    main()

