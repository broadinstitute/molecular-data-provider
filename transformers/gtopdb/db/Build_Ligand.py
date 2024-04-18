import sys
import sqlite3

connection = sqlite3.connect("data/GtoPdb.sqlite", check_same_thread=False)

LIGAND_TABLE = """
    CREATE TABLE LIGAND (
        LIGAND_ID                   INT     PRIMARY_KEY, 
        NAME                        TEXT    NOT NULL, 
        SPECIES                     TEXT    NOT NULL, 
        TYPE                        TEXT    NOT NULL, 
        APPROVED                    TEXT    NOT NULL, 
        WITHDRAWN                   TEXT    NOT NULL, 
        LABELLED                    TEXT    NOT NULL, 
        RADIOACTIVE                 TEXT    NOT NULL, 
        PUBCHEM_SID                 INT     NOT NULL, 
        PUBCHEM_CID                 INT     NOT NULL, 
        UNIPROT_ID                  TEXT    NOT NULL,
        ENSEMBL_ID                  TEXT    NOT NULL,
        LIGAND_SUBUNIT_ID           TEXT    NOT NULL,
        LIGAND_SUBUNIT_NAME         TEXT    NOT NULL,
        LIGAND_SUBUNIT_UNIPROT_ID   TEXT    NOT NULL,
        LIGAND_SUBUNIT_ENSEMBL_ID   TEXT    NOT NULL,
        IUPAC_NAME                  TEXT    NOT NULL, 
        INN                         TEXT    NOT NULL, 
        SMILES                      TEXT    NOT NULL, 
        INCHIKEY                    TEXT    NOT NULL, 
        INCHI                       TEXT    NOT NULL, 
        GTOIMMUPDB                  TEXT    NOT NULL,
        GTOMPDB                     TEXT    NOT NULL,
        ANTIBACTERIAL               TEXT    NOT NULL
    );
"""

LIGAND_SYNONYM_TABLE = """
    CREATE TABLE LIGAND_SYNONYM (
        SYNONYM_ID      INT     PRIMARY_KEY,
        SYNONYM_NAME    TEXT    NOT NULL,
        NAME_TYPE       TEXT    NOT NULL,
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
                  pubchem_cid, uniprot_id, ensembl_id, ligand_subunit_id, ligand_subunit_name, ligand_subunit_uniprot_id, 
                  ligand_subunit_ensembl_id, iupac_name, inn, smiles, inchikey, inchi, gtoimmupdb, gtompdb, antibacterial):
    statement = """
        INSERT INTO LIGAND (LIGAND_ID, NAME, SPECIES, TYPE, APPROVED, WITHDRAWN, LABELLED, RADIOACTIVE, PUBCHEM_SID,
        PUBCHEM_CID, UNIPROT_ID, ENSEMBL_ID, LIGAND_SUBUNIT_ID, LIGAND_SUBUNIT_NAME, LIGAND_SUBUNIT_UNIPROT_ID,
        LIGAND_SUBUNIT_ENSEMBL_ID, IUPAC_NAME, INN, SMILES, INCHIKEY, INCHI, GTOIMMUPDB, GTOMPDB, ANTIBACTERIAL)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cur.execute(statement, (ligand_id, name, species, type, approved, withdrawn, labelled, radioactive, pubchem_sid,
                  pubchem_cid, uniprot_id, ensembl_id, ligand_subunit_id, ligand_subunit_name, ligand_subunit_uniprot_id, 
                  ligand_subunit_ensembl_id, iupac_name, inn, smiles, inchikey, inchi, gtoimmupdb, gtompdb, antibacterial))


def insert_ligand_synonym(cur, synonym_id, synonym_name, ligand_id, name_type):
    statement = """
        INSERT INTO LIGAND_SYNONYM (SYNONYM_ID, SYNONYM_NAME, LIGAND_ID, NAME_TYPE) VALUES (?,?,?,?)
    """
    cur.execute(statement, (synonym_id, synonym_name, ligand_id, name_type))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX {}_{}_IDX ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    cur = connection.cursor()
    create_index(cur, 'LIGAND', 'NAME')
    create_index(cur, 'LIGAND', 'LIGAND_ID')
    create_index(cur, 'LIGAND', 'PUBCHEM_SID')
    create_index(cur, 'LIGAND', 'PUBCHEM_CID')
    create_index(cur, 'LIGAND', 'UNIPROT_ID')
    create_index(cur, 'LIGAND', 'IUPAC_NAME')
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
    with open(filename, 'r', errors='ignore') as f:
        count = 0
        for line in f:
            if count <=1:   # we want to skip the first two lines of header in the tsv file
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
                ensembl_id = row[11]
                ligand_subunit_id = row[12]
                ligand_subunit_name = row[13] 
                ligand_subunit_uniprot_id = row[14] 
                ligand_subunit_ensembl_id = row[15]
                iupac_name = row[16]
                inn = row[17]
                synonym = row[18]
                smiles = row[19]
                inchikey = row[20]
                inchi = row[21]
                gtoimmupdb = row[22]
                gtompdb = row[23]
                antibacterial = row[24][:-2]
                insert_ligand(cur, ligand_id, name, species, type, approved, withdrawn, labelled, radioactive, pubchem_sid,
                  pubchem_cid, uniprot_id, ensembl_id, ligand_subunit_id, ligand_subunit_name, ligand_subunit_uniprot_id, 
                  ligand_subunit_ensembl_id, iupac_name, inn, smiles, inchikey, inchi, gtoimmupdb, gtompdb, antibacterial)
                ligands[name] = ligand_id
                ligand_synonyms[ligand_id] = synonym.split('|')
                for syn_name in synonym.split('|'):
                    if syn_name != '':
                        synonym_id += 1
                        insert_ligand_synonym(cur, synonym_id, syn_name, ligand_id, 'Common Name')

                # Create code that checks that the parsing function separated columns correctly by double checking that
                # ligand id, pubchem SID, and pubchem CID are all integers and InchI is in the proper format
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
    
    parse_ligand_id_mapping('data/ligand_id_mapping.tsv', synonym_id)

    cur.close()
    connection.commit()

def parse_ligand_id_mapping(filename, synonym_id):
    cur = connection.cursor()
    with open(filename, 'r', errors='ignore') as f:
        count = 0


        for line in f:
            if count <=1:   # we want to skip the first two lines of header in the tsv file
                count += 1
            else:
                row = line.split('\t')
                for i in range(len(row)):
                    row[i] = row[i].strip('"')
                ligand_id = row[0]
                name = row[1]
                iupac = row[10]
                inn   = row[11]
                if iupac != '':
                    synonym_id += 1
                    insert_ligand_synonym(cur, synonym_id, iupac, ligand_id, 'IUPAC')
                if inn != '':
                    synonym_id += 1
                    insert_ligand_synonym(cur, synonym_id, inn, ligand_id, 'INN')



    cur.close()
    connection.commit()




create_tables()
create_indexes()
parse_ligands('data/ligands.tsv')

