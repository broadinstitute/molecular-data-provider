import sys
import sqlite3

connection = sqlite3.connect("data/GtoPdb.sqlite", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

INTERACTION_TABLE = """
    CREATE TABLE INTERACTION (
        INTERACTION_ID                  INT     NOT NULL,
        TARGET                          TEXT    NOT NULL,
        TARGET_ID                       INT     NOT NULL, 
        TARGET_SUBUNIT_ID               INT     NOT NULL,
        TARGET_GENE_SYMBOL              TEXT    NOT NULL,
        TARGET_UNIPROT_ID               INT     NOT NULL,
        TARGET_ENSEMBL_GENE_ID          TEXT    NOT NULL,
       -- TARGET_LIGAND                   TEXT    NOT NULL,
       -- TARGET_LIGAND_ID                INT     NOT NULL,
       -- TARGET_LIGAND_SUBUNIT_ID        INT     NOT NULL,
       -- TARGET_LIGAND_GENE_SYMBOL       TEXT    NOT NULL,
       -- TARGET_LIGAND_UNIPROT_ID        TEXT    NOT NULL,
       -- TARGET_LIGAND_ENSEMBL_GENE_ID   TEXT    NOT NULL,
        TARGET_LIGAND_PUBCHEM_SID       TEXT    NOT NULL,
        TARGET_SPECIES                  TEXT    NOT NULL, 
        LIGAND_ID                       INT     NOT NULL,
        LIGAND                          TEXT    NOT NULL,
        LIGAND_TYPE                     TEXT    NOT NULL,
        LIGAND_SUBUNIT_ID               INT     NOT NULL,
        LIGAND_GENE_SYMBOL              TEXT    NOT NULL,
        LIGAND_SPECIES                  TEXT    NOT NULL,
        LIGAND_PUBCHEM_SID              TEXT    NOT NULL,
        APPROVED                        TEXT    NOT NULL,
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


def insert_interaction(cur, interaction_id, target, target_id, target_subunit_id, target_gene_symbol, target_uniprot_id, target_ensembl_gene_id, target_ligand_pubchem_sid, target_species, 
                    ligand_id, ligand, ligand_type, ligand_subunit_id, ligand_gene_symbol, ligand_species, ligand_pubchem_sid, approved, type, action,
                    action_comment, selectivity, endogenous, primary_target, concentration_range, affinity_units,
                       affinity_high, affinity_median, affinity_low, original_affinity_units, original_affinity_low_nm,
                       original_affinity_median_nm, original_affinity_high_nm, original_affinity_relation,
                       assay_description, receptor_site, ligand_context, pubmed_id):
    statement = """
        INSERT INTO INTERACTION (INTERACTION_ID, TARGET, TARGET_ID, TARGET_SUBUNIT_ID, TARGET_GENE_SYMBOL, TARGET_UNIPROT_ID,
        TARGET_ENSEMBL_GENE_ID, TARGET_LIGAND_PUBCHEM_SID, TARGET_SPECIES, LIGAND_ID, LIGAND, LIGAND_TYPE, LIGAND_SUBUNIT_ID, LIGAND_GENE_SYMBOL, LIGAND_SPECIES, LIGAND_PUBCHEM_SID, APPROVED,
        TYPE, ACTION, ACTION_COMMENT, SELECTIVITY, ENDOGENOUS, PRIMARY_TARGET, CONCENTRATION_RANGE, AFFINITY_UNITS, AFFINITY_HIGH, AFFINITY_MEDIAN, AFFINITY_LOW, ORIGINAL_AFFINITY_UNITS, ORIGINAL_AFFINITY_LOW_NM, ORIGINAL_AFFINITY_MEDIAN_NM, ORIGINAL_AFFINITY_HIGH_NM, ORIGINAL_AFFINITY_RELATION, ASSAY_DESCRIPTION, RECEPTOR_SITE, 
        LIGAND_CONTEXT, PUBMED_ID)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    cur.execute(statement, (interaction_id, target, target_id, target_subunit_id, target_gene_symbol, target_uniprot_id, target_ensembl_gene_id, target_ligand_pubchem_sid, target_species, 
                    ligand_id, ligand, ligand_type, ligand_subunit_id, ligand_gene_symbol, ligand_species, ligand_pubchem_sid, approved, type, action,
                    action_comment, selectivity, endogenous, primary_target, concentration_range, affinity_units,
                    affinity_high, affinity_median, affinity_low, original_affinity_units, original_affinity_low_nm,
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
    cur = connection.cursor()
    with open(filename, 'r', errors='ignore') as f:
        count = 0
        interaction_id = 0
        for line in f:
            row = line.split('\t')
            if count == 0 or count == 1:
                count += 1
            else:
                for i in range(len(row)):
                    row[i] = row[i].strip('"')
                    row[i] = row[i].strip('\n')
                if len(row) == 42 and (len(row[0]) > 0 or len(row[6]) > 0):
                    interaction_id += 1
                    target             = {len(row[0]) > 0: row[0], len(row[6]) > 0: row[6]}.get(True, '') 
                    target_id          = {len(row[1]) > 0: row[1], len(row[7]) > 0: row[7]}.get(True, '') 
                    target_subunit_id  = {len(row[2]) > 0: row[2], len(row[8]) > 0: row[8]}.get(True, '') 
                    target_gene_symbol = {len(row[3]) > 0: row[3], len(row[9]) > 0: row[9]}.get(True, '') 
                    target_uniprot_id  = {len(row[4]) > 0: row[4], len(row[10]) > 0: row[10]}.get(True, '')
                    target_ensembl_gene_id = {len(row[5]) > 0: row[5], len(row[11]) > 0: row[11]}.get(True, '')
                    target_ligand_pubchem_sid = row[12] 
                    target_species = row[13]
                    ligand_id = row[14] 
                    ligand = row[15] 
                    ligand_type = row[16] 
                    ligand_subunit_id = row[17] 
                    ligand_gene_symbol = row[18] 
                    ligand_species = row[19] 
                    ligand_pubchem_sid = row[20]
                    approved = row[21]
                    type = row[22]
                    action = row[23]
                    action_comment = row[24]
                    selectivity = row[25]
                    endogenous = row[26]
                    primary_target = row[27]
                    concentration_range = row[28]
                    affinity_units = row[29]
                    affinity_high = row[30]
                    affinity_median = row[31]
                    affinity_low = row[32]
                    original_affinity_units = row[33]
                    original_affinity_low_nm = row[34]
                    original_affinity_median_nm = row[35]
                    original_affinity_high_nm = row[36]
                    original_affinity_relation = row[37]
                    assay_description = row[38]
                    receptor_site = row[39]
                    ligand_context = row[40]
                    pubmed_id = row[41].strip('"')
                    split_pubmed_id = row[41].split('|')[0]
                    if not (ligand_id == '' or target_id == ''):
                        insert_interaction(cur, interaction_id, target, target_id, target_subunit_id, target_gene_symbol, target_uniprot_id, target_ensembl_gene_id, target_ligand_pubchem_sid, target_species, 
                                ligand_id, ligand, ligand_type, ligand_subunit_id, ligand_gene_symbol, ligand_species, ligand_pubchem_sid, approved, type, action,
                                action_comment, selectivity, endogenous, primary_target, concentration_range, affinity_units,
                                affinity_high, affinity_median, affinity_low, original_affinity_units, original_affinity_low_nm,
                                original_affinity_median_nm, original_affinity_high_nm, original_affinity_relation,
                                assay_description, receptor_site, ligand_context, pubmed_id)
                        # print(ligand_id)
                        # if pubmed_id == '':
                        #     pass
                        # elif not (isinstance(int(ligand_id), int) and isinstance(int(target_id), int) and
                        #           isinstance(int(split_pubmed_id), int)):
                        #     print('Error: Parsing of data is incorrect')
                        #     print(row)
                        #     if not isinstance(int(ligand_id), int):
                        #         print('Ligand id is not an integer')
                        #     elif not isinstance(int(target_id), int):
                        #         print('Target id is not an integer')
                        #     elif not isinstance(int(split_pubmed_id), int):
                        #         print('Pubmed id is not an integer')

    cur.close()
    connection.commit()


create_tables()
create_indexes()
parse_ligands("data/interactions.tsv")
