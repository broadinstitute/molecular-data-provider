import sqlite3


connection_src = sqlite3.connect("data/BindingDBsrc.sqlite", check_same_thread=False)
connection_src.row_factory = sqlite3.Row

connection = sqlite3.connect("data/BindingDB.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row


# Tables

LIGAND = 'LIGAND'
LIGAND_NAME = 'LIGAND_NAME'
TARGET_CHAIN = 'TARGET_CHAIN'
PDB = 'PDB_MAP'
TARGET = 'TARGET'
TARGET_CHAIN_MAP = 'TARGET_CHAIN_MAP'
BINDING = 'BINDING'


# Columns

LIGAND_SRC_COLUMNS = [
    '[BindingDB MonomerID]',
    '[Ligand SMILES]',
    '[Ligand InChI]',
    '[Ligand InChI Key]',
    '[Link to Ligand in BindingDB]',
    '[PubChem CID]',
    '[PubChem SID]',
    '[ChEBI ID of Ligand]',
    '[ChEMBL ID of Ligand]',
    '[DrugBank ID of Ligand]',
    '[IUPHAR_GRAC ID of Ligand]',
    '[KEGG ID of Ligand]',
    '[ZINC ID of Ligand]',
    '[BindingDB Ligand Name]'
]


LIGAND_ID_PRIMAY_KEY = 'Ligand_ID'

LIGAND_NAME_COLUMN = 'Ligand_Name'


LIGAND_COLUMNS = [
    LIGAND_ID_PRIMAY_KEY,
    'SMILES',
    'InChI',
    'InChI_Key',
    'Ligand_Link',
    'PubChem_CID',
    'PubChem_SID',
    'ChEBI_ID',
    'ChEMBL_ID',
    'DrugBank_ID',
    'IUPHAR_GRAC_ID',
    'KEGG_ID',
    'ZINC_ID',
    LIGAND_NAME_COLUMN
]


TARGET_CHAIN_SRC_COLUMNS = [
    'PDB ID(s) of Target Chain{}',
    'BindingDB Target Chain  Sequence{}',
    'UniProt (SwissProt) Recommended Name of Target Chain{}',
    'UniProt (SwissProt) Entry Name of Target Chain{}',
    'UniProt (SwissProt) Primary ID of Target Chain{}',
    'UniProt (TrEMBL) Submitted Name of Target Chain{}',
    'UniProt (TrEMBL) Entry Name of Target Chain{}',
    'UniProt (TrEMBL) Primary ID of Target Chain{}'
]


TARGET_CHAIN_PRIMAY_KEY = 'Target_Chain_ID'

TARGET_CHAIN_COLUMNS = [
    'PDB_ID',
    'Sequence',
    'UniProt_Name',
    'UniProt_Entry_Name',
    'UniProt_ID',
    'TrEMBL_Submitted_Name',
    'TrEMBL_Entry_Name',
    'TrEMBL_ID'
]


PDB_ID = 'PDB_ID'

PDB_COLUMNS = [
    'PDB_map_id',
    TARGET_CHAIN_PRIMAY_KEY,
    PDB_ID
]


TARGET_SRC_COLUMNS = [
    'Number of Protein Chains in Target (>1 implies a multichain complex)',
    'Target Name Assigned by Curator or DataSource',
    'Target Source Organism According to Curator or DataSource',
    'Link to Target in BindingDB'
]


TARGET_ID_PRIMAY_KEY = 'Target_ID'

TARGET_COLUMNS = [
    TARGET_ID_PRIMAY_KEY,
    'Number_of_Chains',
    'Target_Name',
    'Target_Organism',
    'Target_Link'
]


BINDING_SRC_COLUMNS = [
    'BindingDB Reactant_set_id',
    'Ki (nM)',
    'IC50 (nM)',
    'Kd (nM)',
    'EC50 (nM)',
    'kon (M-1-s-1)',
    'koff (s-1)',
    'pH',
    'Temp (C)',
    'Curation/DataSource',
    'Article DOI',
    'PMID',
    'PubChem AID',
    'Patent Number',
    'Authors',
    'Institution',
    'Link to Ligand-Target Pair in BindingDB',
    'PDB ID(s) for Ligand-Target Complex'
]


BINDING_ID_PRIMAY_KEY = 'BindingDB_ID'

BINDING_COLUMNS = [
    BINDING_ID_PRIMAY_KEY,
    LIGAND_ID_PRIMAY_KEY,
    TARGET_ID_PRIMAY_KEY,
    'Ki',
    'IC50',
    'Kd',
    'EC50',
    'kon',
    'koff',
    'pH',
    'Temperature',
    'Curation_DataSource',
    'Article_DOI',
    'PMID',
    'PubChem_AID',
    'Patent_Number',
    'Authors',
    'Institution',
    'Binding_Link',
    'PDB_IDs'
]


def create_table(table_name, primary_key, colums, int_columns = 0):
    colums = ',\n  '.join([column + (' INT' if i < int_columns else ' TEXT') for (i,column) in enumerate(colums)])
    sql = """
    CREATE TABLE {} (
        {} INTEGER PRIMARY KEY ASC,
        {}
    )
    """.format(table_name, primary_key, colums)
    cur = connection.cursor()
    cur.execute(sql)
    connection.commit()


def create_map_table(table_name, parent__id, value, mapped_type):
    sql = """
    CREATE TABLE {} (
        {} INT,
        {} {}
    )
    """.format(table_name, parent__id, value, mapped_type)
    cur = connection.cursor()
    cur.execute(sql)
    connection.commit()


def src_db_query(src_columns, db_columns):
    columns = [src_column + ' AS ' + column for (src_column, column) in zip(src_columns, db_columns)]
    query = 'SELECT\n  ' + ',\n\t\t'.join(columns) + '\nFROM binding_db' 
    cur = connection_src.cursor()
    cur.execute(query)
    return cur.fetchall()


def ligand_query():
    return src_db_query(LIGAND_SRC_COLUMNS, LIGAND_COLUMNS)


def bindings_query():
    query = 'SELECT * FROM binding_db'
    cur = connection_src.cursor()
    cur.execute(query)
    return cur.fetchall()


def insert_row(cur, table, columns, row):
    values = [row[column] for column in columns]
    sql = """
    INSERT INTO {} ({})
    VALUES ({})
    """.format(table, ', '.join(columns), ', '.join(['?' for column in columns]))
    cur.execute(sql, values)


def insert_ligand(cur, row):
    insert_row(cur, LIGAND, LIGAND_COLUMNS[:-1], row)


def insert_ligand_names(cur, ligand_id, names):
    for name in names.split('::'):
        values = {
            LIGAND_ID_PRIMAY_KEY: ligand_id,
            LIGAND_NAME_COLUMN: name
        }
        insert_row(cur, LIGAND_NAME, values.keys(), values)


def insert_pdb_ids(cur, target_chain_id, pdb):
    for pdb_id in pdb:
        row = {TARGET_CHAIN_PRIMAY_KEY: target_chain_id, PDB_ID: pdb_id}
        insert_row(cur, PDB, PDB_COLUMNS[1:], row)


def insert_chain(cur, target_chain_id, row):
    row_dict = dict(row)
    row_dict[TARGET_CHAIN_PRIMAY_KEY] = target_chain_id
    columns = [TARGET_CHAIN_PRIMAY_KEY, *TARGET_CHAIN_COLUMNS[1:]]
    insert_row(cur, TARGET_CHAIN, columns, row_dict)


def insert_target(cur, target_id, target_row):
    target_row[TARGET_ID_PRIMAY_KEY] = target_id
    insert_row(cur, TARGET, TARGET_COLUMNS, target_row)


def insert_target_map(cur, target_id, chain_id):
    target_map = {
        TARGET_ID_PRIMAY_KEY : target_id,
        TARGET_CHAIN_PRIMAY_KEY: chain_id
    }
    insert_row(cur, TARGET_CHAIN_MAP, target_map.keys(), target_map)


def insert_binding(cur, ligand_id, target_id, row):
    binding_row = {column : row[src_column] for (src_column, column) in zip(BINDING_SRC_COLUMNS[1:], BINDING_COLUMNS[3:])}
    binding_row[BINDING_ID_PRIMAY_KEY] = int(row[BINDING_SRC_COLUMNS[0]])
    binding_row[LIGAND_ID_PRIMAY_KEY] = ligand_id
    binding_row[TARGET_ID_PRIMAY_KEY] = target_id
    insert_row(cur, BINDING, BINDING_COLUMNS, binding_row)


def get_chain_row(row, i):
    chain_index = '.'+str(i) if i > 0 else ''
    return { 
        column : row[src_column.format(chain_index)]
            for (src_column, column) in zip(TARGET_CHAIN_SRC_COLUMNS, TARGET_CHAIN_COLUMNS)
    }


def load_ligands():
    create_table(LIGAND, LIGAND_COLUMNS[0], LIGAND_COLUMNS[1:-1])
    create_map_table(LIGAND_NAME, LIGAND_ID_PRIMAY_KEY, LIGAND_NAME_COLUMN, mapped_type='TEXT COLLATE NOCASE')
    ligands = set()
    cur = connection.cursor()
    for row in ligand_query():
        ligand_id = row[LIGAND_ID_PRIMAY_KEY]
        if ligand_id not in ligands:
            insert_ligand(cur, row)
            insert_ligand_names(cur, ligand_id, row[LIGAND_NAME_COLUMN])
            ligands.add(ligand_id)
            if len(ligands) % 10000 == 0:
                connection.commit()
                print(len(ligands))
    connection.commit()
    cur.close()
    print('loaded ' + str(len(ligands)) + ' ligands')


def load_chains(cur, row, all_chains):
    chain_idxs = []
    for i in range(0,13):
        chain_row = get_chain_row(row, i)
        pdb_id = chain_row['PDB_ID']
        sequence = chain_row['Sequence']
        uniprot_id = chain_row['UniProt_ID']
        trembl_id = chain_row['TrEMBL_ID']
        if pdb_id or sequence or uniprot_id or trembl_id:
            pdb = pdb_id.split(',') if pdb_id is not None else []
            key = (sequence, tuple(pdb), uniprot_id, trembl_id)
            if key not in all_chains:
                target_chain_id = len(all_chains) + 1
                all_chains[key] = target_chain_id
                insert_pdb_ids(cur, target_chain_id, pdb)
                insert_chain(cur, target_chain_id, chain_row)
                chain_idxs.append(target_chain_id)
            else:
                chain_idxs.append(all_chains[key])
    chain_idxs.sort()
    return chain_idxs


def load_target(cur, row, all_targets, chain_ids):
    target_row = {column : row[src_column] for (src_column, column) in zip(TARGET_SRC_COLUMNS, TARGET_COLUMNS[1:])}
    key = (target_row['Target_Name'], target_row['Target_Organism'], tuple(chain_ids))
    if key not in all_targets:
        target_id = len(all_targets) + 1
        insert_target(cur, target_id, target_row)
        all_targets[key] = target_id
        for chain_id in chain_ids:
            insert_target_map(cur, target_id, chain_id)
    else:
        target_id = all_targets[key]
    return target_id


def load_bindings():

    create_map_table(PDB, TARGET_CHAIN_PRIMAY_KEY, PDB_ID, 'TEXT')
    create_table(TARGET_CHAIN, TARGET_CHAIN_PRIMAY_KEY, TARGET_CHAIN_COLUMNS[1:])
    create_map_table(TARGET_CHAIN_MAP, TARGET_ID_PRIMAY_KEY, TARGET_CHAIN_PRIMAY_KEY, 'INT')
    create_table(TARGET, TARGET_COLUMNS[0], TARGET_COLUMNS[1:], int_columns = 1)
    create_table(BINDING, BINDING_COLUMNS[0], BINDING_COLUMNS[1:], int_columns = 2)

    all_chains = {}
    all_targets = {}
    cur = connection.cursor()
    i = 0

    for row in bindings_query():
        ligand_id = row['BindingDB MonomerID']
        chain_count = int(row['Number of Protein Chains in Target (>1 implies a multichain complex)'])
        target_chain_ids = load_chains(cur, row, all_chains)
        target_id = load_target(cur, row, all_targets, target_chain_ids)
        insert_binding(cur, ligand_id, target_id, row)

        if i < 1000 and chain_count != len(target_chain_ids):
            print('missmatch chain count @ {}; {} != {}'.format(i, chain_count, target_chain_ids))
        if i % 10000 == 0:
            print(i)
            connection.commit()
        i = i + 1
    connection.commit()
    cur.close()

    print('loaded ' + str(len(all_chains)) + ' chains')        
    print('loaded ' + str(len(all_targets)) + ' targets')        
    print('loaded ' + str(i) + ' bindings')        


def create_index(table, column, colate=None):
    print('index',table, column)
    colate_nocase = 'COLLATE NOCASE' if colate == 'NOCASE' else ''
    stmt = """
        CREATE INDEX {}_{}_idx 
        ON {} ({} {});    
    """.format(table, column, table, column, colate_nocase)
    cur = connection.cursor()
    cur.executescript(stmt)
    cur.close()


def create_indexes():
    create_index(LIGAND, 'InChI_Key')
    create_index(LIGAND, 'PubChem_CID')

    create_index(LIGAND_NAME, LIGAND_ID_PRIMAY_KEY)
    create_index(LIGAND_NAME, LIGAND_NAME_COLUMN, colate='NOCASE')

    create_index(BINDING, LIGAND_ID_PRIMAY_KEY)
    create_index(BINDING, TARGET_ID_PRIMAY_KEY)

    create_index(PDB, TARGET_CHAIN_PRIMAY_KEY)
    create_index(PDB, PDB_ID)

    create_index(TARGET_CHAIN, 'UniProt_ID')
    create_index(TARGET_CHAIN, 'TrEMBL_ID')

    create_index(TARGET_CHAIN_MAP, TARGET_ID_PRIMAY_KEY)
    create_index(TARGET_CHAIN_MAP, TARGET_CHAIN_PRIMAY_KEY)


def main():
    load_ligands()
    load_bindings()
    create_indexes()
    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()
