import sys
import sqlite3

# connection = sqlite3.connect("C:/Users/michelle/PycharmProjects/GuideToPharmacology/Ligands.db",
#                              check_same_thread=False)

connection = sqlite3.connect("C:/Users/michelle/Documents/GitHub/scb-kp-dev/transformers/gtopdb/python-flask-server/data/GtoPdb.db",
                             check_same_thread=False)

INTERACTION_TABLE = """
    CREATE TABLE INTERACTION (
        INTERACTION_ID                  INT     PRIMARY_KEY,
        TARGET_ID                       INT     NOT NULL, 
        TARGET_SPECIES                  TEXT    NOT NULL, 
        LIGAND_ID                       INT     NOT NULL,
        TYPE                            TEXT    NOT NULL, 
        ACTION                          TEXT    NOT NULL, 
        ACTION_COMMENT                  TEXT    NOT NULL, 
        SELECTIVITY                     TEXT    NOT NULL, 
        ENDOGENOUS                      TEXT    NOT NULL, 
        PRIMARY_TARGET                  TEXT    NOT NULL,
        CONCENTRATION_RANGE             TEXT    NOT NULL, 
        AFFINITY_UNITS                  TEXT    NOT NULL, 
        AFFINITY_HIGH                   INT     NOT NULL, 
        AFFINITY_MEDIAN                 INT     NOT NULL, 
        AFFINITY_LOW                    INT     NOT NULL, 
        ORIGINAL_AFFINITY_UNITS         TEXT    NOT NULL,
        ORIGINAL_AFFINITY_LOW_NM        INT     NOT NULL,
        ORIGINAL_AFFINITY_MEDIAN_NM     INT     NOT NULL,
        ORIGINAL_AFFINITY_HIGH_NM       INT     NOT NULL,
        ORIGINAL_AFFINITY_RELATION      TEXT    NOT NULL, 
        ASSAY_DESCRIPTION               TEXT    NOT NULL,
        RECEPTOR_SITE                   TEXT    NOT NULL, 
        LIGAND_CONTEXT                  TEXT    NOT NULL, 
        PUBMED_ID                       INT     NOT NULL    
    );      
"""


def create_tables():
    cur = connection.cursor()
    cur.execute(INTERACTION_TABLE)
    cur.close()
    connection.commit()


def insert_interaction(cur, interaction_id, target_id, target_species, ligand_id, type, action,
                       action_comment, selectivity, endogenous, primary_target, concentration_range, affinity_units,
                       affinity_high, affinity_median, affinity_low, original_affinity_units, original_affinity_low_nm,
                       original_affinity_median_nm, original_affinity_high_nm, original_affinity_relation,
                       assay_description, receptor_site, ligand_context, pubmed_id):
    statement = """
        INSERT INTO INTERACTION (INTERACTION_ID,TARGET_ID, TARGET_SPECIES, LIGAND_ID, TYPE, ACTION, ACTION_COMMENT, 
        SELECTIVITY, ENDOGENOUS, PRIMARY_TARGET, CONCENTRATION_RANGE, AFFINITY_UNITS, AFFINITY_HIGH, AFFINITY_MEDIAN, 
        AFFINITY_LOW, ORIGINAL_AFFINITY_UNITS, ORIGINAL_AFFINITY_LOW_NM, ORIGINAL_AFFINITY_MEDIAN_NM, 
        ORIGINAL_AFFINITY_HIGH_NM, ORIGINAL_AFFINITY_RELATION, ASSAY_DESCRIPTION, RECEPTOR_SITE, LIGAND_CONTEXT, 
        PUBMED_ID)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cur.execute(statement, (interaction_id, target_id, target_species, ligand_id, type, action,
                            action_comment, selectivity, endogenous, primary_target, concentration_range,
                            affinity_units,
                            affinity_high, affinity_median, affinity_low, original_affinity_units,
                            original_affinity_low_nm,
                            original_affinity_median_nm, original_affinity_high_nm, original_affinity_relation,
                            assay_description, receptor_site, ligand_context, pubmed_id))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX {}_{}_IDX ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    cur = connection.cursor()
    create_index(cur, 'INTERACTION', 'TARGET_ID')
    create_index(cur, 'INTERACTION', 'LIGAND_ID')
    create_index(cur, 'INTERACTION', 'INTERACTION_ID')
    create_index(cur, 'INTERACTION', 'PUBMED_ID')
    cur.close()
    connection.commit()


def parse_ligands(filename):
    # Are there any dictionaries I should make?
    cur = connection.cursor()
    # had to add errors='ignore' when switching laptops, not sure why this error happened
    with open(filename, 'r', errors='ignore') as f:
        count = 1
        # missing_info = 0
        interaction_id = 0
        for line in f:
            # if line.rstrip() != '"Ligand id"\t"Name"\t"Species"\t"Type"\t"Approved"\t"Withdrawn"\t"Labelled"\t' \
            #                     '"Radioactive"\t"PubChem SID"\t"PubChem CID"\t"UniProt id"\t"IUPAC ' \
            #                     'name"\t"INN"\t"Synonyms"\t"SMILES"\t"InChIKey"\t"InChI"\t"GtoImmuPdb"\t"GtoMPdb"':
            #     print('ERROR: wrong ligand-file format')
            #     return
            row = line.split('\t')
            if count == 1:
                count += 1
            # elif not (len(row) == 37):
            #     missing_info += 1
            else:
                for i in range(len(row)):
                    row[i] = row[i].strip('"')
                    row[i] = row[i].strip('\n')
                # print(row)
                # print(len(row))
                if len(row) == 37:
                    interaction_id += 1
                    target_id = row[1]
                    target_species = row[11]
                    ligand_id = row[13]
                    type = row[17]
                    action = row[18]
                    action_comment = row[19]
                    selectivity = row[20]
                    endogenous = row[21]
                    primary_target = row[22]
                    concentration_range = row[23]
                    affinity_units = row[24]
                    affinity_high = row[25]
                    affinity_median = row[26]
                    affinity_low = row[27]
                    original_affinity_units = row[28]
                    original_affinity_low_nm = row[29]
                    original_affinity_median_nm = row[30]
                    original_affinity_high_nm = row[31]
                    original_affinity_relation = row[32]
                    assay_description = row[33]
                    receptor_site = row[34]
                    ligand_context = row[35]
                    pubmed_id = row[36]
                    split_pubmed_id = row[36].split('|')[0]
                    if not (ligand_id == '' or target_id == ''):
                        insert_interaction(cur, interaction_id, target_id, target_species, ligand_id, type, action,
                                           action_comment, selectivity, endogenous, primary_target,
                                           concentration_range, affinity_units,
                                           affinity_high, affinity_median, affinity_low, original_affinity_units,
                                           original_affinity_low_nm,
                                           original_affinity_median_nm, original_affinity_high_nm,
                                           original_affinity_relation,
                                           assay_description, receptor_site, ligand_context, pubmed_id)
                        if pubmed_id == '':
                            pass
                        elif not (isinstance(int(ligand_id), int) and isinstance(int(target_id), int) and
                                  isinstance(int(split_pubmed_id), int)):
                            print('Error: Parsing of data is incorrect')
                            print(row)
                            if not isinstance(int(ligand_id), int):
                                print('Ligand id is not an integer')
                            elif not isinstance(int(target_id), int):
                                print('Target id is not an integer')
                            elif not isinstance(int(split_pubmed_id), int):
                                print('Pubmed id is not an integer')

    # print(missing_info)
    # print(odd)
    cur.close()
    connection.commit()


create_tables()
create_indexes()
parse_ligands('C:/Users/michelle/PycharmProjects/GuideToPharmacology/interactions.tsv')
