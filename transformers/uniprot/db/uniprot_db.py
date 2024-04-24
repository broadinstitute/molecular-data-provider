import sqlite3

connection = sqlite3.connect("data/UniProt.sqlite", check_same_thread=False)


def create_protein_table():
    sql = """
        CREATE TABLE PROTEIN (
            UNIPROT_AC TEXT PRIMARY_KEY,
            UNIPROT_ID TEXT,
            PROTEIN_NAME TEXT NOT NULL COLLATE NOCASE,
            PROTEIN_LENGTH INT
        )
    """
    connection.execute(sql)
    connection.commit()


def insert_protein(cur, uniprot_ac, uniprot_id, name, length):
    statement = """
        INSERT INTO PROTEIN (UNIPROT_AC, UNIPROT_ID, PROTEIN_NAME, PROTEIN_LENGTH) VALUES (?,?,?,?)
    """
    cur.execute(statement,(uniprot_ac, uniprot_id, name, length))


def create_synonym_table():
    sql = """
        CREATE TABLE SYNONYM (
            UNIPROT_AC TEXT,
            SYNONYM TEXT NOT NULL COLLATE NOCASE
        )
    """
    connection.execute(sql)
    connection.commit()


def insert_synonym(cur, uniprot_ac, synonym):
    statement = """
        INSERT INTO SYNONYM (UNIPROT_AC, SYNONYM) VALUES (?,?)
    """
    cur.execute(statement,(uniprot_ac, synonym))


def create_xref_table():
    sql = """
        CREATE TABLE XREF (
            UNIPROT_AC TEXT,
            XREF_TYPE  NOT NULL,
            XREF NOT NULL
        )
    """
    connection.execute(sql)
    connection.commit()


def insert_xref(cur, uniprot_ac, xref_type, xref):
    statement = """
        INSERT INTO XREF (UNIPROT_AC, XREF_TYPE, XREF) VALUES (?,?,?)
    """
    cur.execute(statement,(uniprot_ac, xref_type, xref))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX {}_{}_IDX ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    cur = connection.cursor()
    create_index(cur, 'PROTEIN', 'UNIPROT_ID')
    create_index(cur, 'PROTEIN', 'PROTEIN_NAME')
    create_index(cur, 'SYNONYM', 'UNIPROT_AC')
    create_index(cur, 'SYNONYM', 'SYNONYM')
    create_index(cur, 'XREF', 'UNIPROT_AC')
    create_index(cur, 'XREF', 'XREF')
    cur.close()
    connection.commit()


def create_tables():
    create_protein_table()
    create_synonym_table()
    create_xref_table()


def load_proteins(filename):
    first_row = True
    cur = connection.cursor()
    with open(filename,'r') as f:
        for line in f:
            if first_row:
                if line.rstrip().lower() != 'Entry\tEntry name\tProtein names\tLength'.lower():
                    print('ERROR: wrong protein-file format')
                    print('"'+line.rstrip()+'"')
                    return
                first_row = False
            else:
                row = line.split('\t')
                entry = row[0]
                entry_name = row[1]
                names = row[2].split('(')
                protein_name = get_protein_name(names)
                synonyms = get_synonyms(names)
                length = int(row[3])
                insert_protein(cur, entry, entry_name, protein_name, length)
                # do not save synonyms - incorrectly handled nested parenteses
                #for synonym in synonyms:
                #    insert_synonym(cur, entry, synonym)
    cur.close()
    connection.commit()


def get_protein_name(names):
    return names[0].strip()


def get_synonyms(names):
    #todo - handle nested parenteses
    synonyms = []
    for name in names:
        if ')' in name:
            synonyms.append(name.split(')')[0])
    return synonyms


def load_xrefs(filename):
    cur = connection.cursor()
    with open(filename,'r') as f:
        for line in f:
            row = line.rstrip().split('\t')
            entry = row[0]
            # removes "-1", "-2", etc from protein name
            if "-" in entry: 
                index = int(entry.rfind("-"))
                entry = entry[:index]
            xref_type = row[1]
            xref = row[2]
            if xref_type.startswith("Ensembl") and "." in xref:
                index = int(xref.rfind("."))
                xref = xref[:index]
            insert_xref(cur, entry, xref_type, xref)
    cur.close()
    connection.commit()


def main():
    create_tables()
    load_proteins("data/uniprot-human-names.tab")
    load_xrefs("data/HUMAN_9606_idmapping.dat")
    create_indexes()


if __name__ == '__main__':
    main()