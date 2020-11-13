import sys
import sqlite3

# connection = sqlite3.connect("C:/Users/michelle/PycharmProjects/GuideToPharmacology/Ligands.db",
#                              check_same_thread=False)

connection = sqlite3.connect("C:/Users/michelle/Documents/GitHub/scb-kp-dev/transformers/gtopdb/python-flask-server/data/GtoPdb.db",
                             check_same_thread=False)

# place holder for file directory, what does check_same_thread do?
# Need to remove quotation marks most likely

LIGAND_TABLE = """
    CREATE TABLE LIGAND (
        LIGAND_ID   INT     PRIMARY_KEY, 
        NAME        TEXT    NOT NULL, 
        SPECIES     TEXT    NOT NULL, 
        TYPE        TEXT    NOT NULL, 
        APPROVED    TEXT    NOT NULL, 
        WITHDRAWN   TEXT    NOT NULL, 
        LABELLED    TEXT    NOT NULL, 
        RADIOACTIVE TEXT    NOT NULL, 
        PUBCHEMSID  INT     NOT NULL, 
        PUBCHEMCID  INT     NOT NULL, 
        UNIPROT_ID  TEXT    NOT NULL, 
        IUPAC       TEXT    NOT NULL, 
        INN         TEXT    NOT NULL, 
        SMILES      TEXT    NOT NULL, 
        INCHIKEY    TEXT    NOT NULL, 
        INCHI       TEXT    NOT NULL
    );
"""
# Is the synonym id the primary key?
LIGAND_SYNONYM_TABLE = """
    CREATE TABLE LIGAND_SYNONYM (
        SYNONYM_ID      INT     PRIMARY_KEY,
        SYNONYM_NAME    TEXT    NOT NULL,
        LIGAND_ID       INT     REFERENCES LIGAND(LIGAND_ID)
    );
"""


def create_tables():
    cur = connection.cursor()
    cur.execute(LIGAND_TABLE)
    cur.execute(LIGAND_SYNONYM_TABLE)
    cur.close()
    connection.commit()


def insert_ligand(cur, ligand_id, name, species, type, approved, withdrawn, labelled, radioactive, pubchem_sid,
                  pubchem_cid, uniprot_id, iupac_name, inn, smiles, inchikey, inchi):
    # Double check format of statement
    statement = """
        INSERT INTO LIGAND (LIGAND_ID, NAME, SPECIES, TYPE, APPROVED, WITHDRAWN, LABELLED, RADIOACTIVE, PUBCHEMSID,
        PUBCHEMCID, UNIPROT_ID, IUPAC, INN, SMILES, INCHIKEY, INCHI)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cur.execute(statement, (ligand_id, name, species, type, approved, withdrawn, labelled, radioactive, pubchem_sid,
                            pubchem_cid, uniprot_id, iupac_name, inn, smiles, inchikey, inchi))


def insert_ligand_synonym(cur, synonym_id, synonym_name, ligand_id):
    statement = """
        INSERT INTO LIGAND_SYNONYM (SYNONYM_ID, SYNONYM_NAME, LIGAND_ID) VALUES (?,?,?)
    """
    cur.execute(statement, (synonym_id, synonym_name, ligand_id))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX {}_{}_IDX ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    cur = connection.cursor()
    create_index(cur, 'LIGAND', 'NAME')
    create_index(cur, 'LIGAND', 'LIGAND_ID')
    create_index(cur, 'LIGAND', 'PUBCHEMSID')
    create_index(cur, 'LIGAND', 'PUBCHEMCID')
    create_index(cur, 'LIGAND', 'UNIPROT_ID')
    create_index(cur, 'LIGAND', 'IUPAC')
    create_index(cur, 'LIGAND', 'INN')
    create_index(cur, 'LIGAND', 'INCHIKEY')
    create_index(cur, 'LIGAND', 'INCHI')
    create_index(cur, 'LIGAND_SYNONYM', 'LIGAND_ID')
    create_index(cur, 'LIGAND_SYNONYM', 'SYNONYM_NAME')
    cur.close()
    connection.commit()


def parse_ligands(filename):
    ligands = {}
    ligand_synonyms = {}
    synonym_id = 0
    cur = connection.cursor()
    # would we have an our own numbers to refer to the ligands other than ligand_id
    # had to add errors='ignore' when switching laptops, not sure why this error happened
    with open(filename, 'r', errors='ignore') as f:
        count = 1
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
                ligand_id = row[0]
                name = row[1]
                species = row[2]
                type = row[3]
                approved = row[4]
                withdrawn = row[5]
                labelled = row[6]
                radioactive = row[7]
                pubchem_sid = row[8]
                pubchem_cid = row[9]
                uniprot_id = row[10]
                iupac_name = row[11]
                inn = row[12]
                synonym = row[13]
                smiles = row[14]
                inchikey = row[15]
                inchi = row[16]
                insert_ligand(cur, ligand_id, name, species, type, approved, withdrawn, labelled, radioactive,
                              pubchem_sid, pubchem_cid, uniprot_id, iupac_name, inn, smiles, inchikey, inchi)
                # not sure if this the correct structure for the dictionary we want in this case,
                # are there other dictionaries that are needed? one to get synonyms?
                ligands[name] = ligand_id
                ligand_synonyms[ligand_id] = synonym.split('|')
                for syn_name in synonym.split('|'):
                    if syn_name != '':
                        synonym_id += 1
                        insert_ligand_synonym(cur, synonym_id, syn_name, ligand_id)

                # Create code that checks that the parsing function separated columns correctly by double checking that
                # ligand id, pubchem SID, and pubchem CID are all integers and InchI is in the proper format
                # Ask why if works with inch in the elif
                if ligand_id == '':
                    print(row)
                elif pubchem_cid == '' or pubchem_sid == '' or inchi == '':
                    pass
                elif not (isinstance(int(ligand_id), int) and isinstance(int(pubchem_cid), int) and
                          isinstance(int(pubchem_sid), int) and "InChI=" in inchi):
                    print('Error: Parsing of data is incorrect')
                    if not isinstance(int(ligand_id), int):
                        print('Ligand id is not an integer:', ligand_id)
                    elif not isinstance(int(pubchem_cid), int):
                        print('Pubchem cid is not an integer:', pubchem_cid)
                    elif not isinstance(int(pubchem_sid), int):
                        print('Pubchem sid is not an integer:', pubchem_sid)
                    else:
                        print('InChI not in proper format:', inchi)

    # Is it okay for pubchem cid and sid to be blank? What should we do about the last two columns that appear in the
    # spreadsheet but not in the documentation?

    cur.close()
    connection.commit()


create_tables()
create_indexes()
parse_ligands('C:/Users/michelle/PycharmProjects/GuideToPharmacology/ligands.tsv')
