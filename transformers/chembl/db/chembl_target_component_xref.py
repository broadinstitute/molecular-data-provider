import requests
import sqlite3
import json
from time import sleep

CHEMBL_TARGETS_URL = 'https://www.ebi.ac.uk/chembl/api/data/target.json?limit=200'

connection = sqlite3.connect("data/ChEMBL.target.xref.sqlite", check_same_thread=False)

loaded_components = set()


def create_target_xref_table():
    sql = """
        CREATE TABLE target_xref (
            target_chembl_id  TEXT  NOT NULL,
            xref_id           TEXT,
            xref_name         TEXT,
            xref_src          TEXT
        )
    """
    connection.execute(sql)
    connection.commit()


def insert_target_xref(cur, target_chembl_id, xref_id, xref_name, xref_src):
    statement = """
        INSERT INTO target_xref(target_chembl_id, xref_id, xref_name, xref_src)
        VALUES (?,?,?,?);
    """
    cur.execute(statement,(target_chembl_id, xref_id, xref_name, xref_src))


def create_component_table():
    sql = """
        CREATE TABLE component (
            target_chembl_id  TEXT  NOT NULL,
            component_id      INT   NOT NULL
        )
    """
    connection.execute(sql)
    connection.commit()


def insert_component(cur, target_chembl_id, component_id):
    statement = """
        INSERT INTO component(target_chembl_id, component_id)
        VALUES (?,?);
    """
    cur.execute(statement,(target_chembl_id, component_id))


def create_component_xref_table():
    sql = """
        CREATE TABLE component_xref (
            component_id  INT  NOT NULL,
            xref_id       TEXT,
            xref_name     TEXT,
            xref_src_db   TEXT
        )
    """
    connection.execute(sql)
    connection.commit()


def insert_component_xref(cur, component_id, xref_id, xref_name, xref_src_db):
    statement = """
        INSERT INTO component_xref(component_id, xref_id, xref_name, xref_src_db)
        VALUES (?,?,?,?);
    """
    cur.execute(statement,(component_id, xref_id, xref_name, xref_src_db))


def load_cross_references(cur, target_chembl_id, xrefs):
    for xref in xrefs:
        insert_target_xref(cur, target_chembl_id, xref['xref_id'], xref['xref_name'], xref['xref_src'])

# Add more target types
# SINGLE PROTEIN
# PROTEIN FAMILY
# PROTEIN COMPLEX GROUP
# PROTEIN COMPLEX
# CHIMERIC PROTEIN
# SELECTIVITY GROUP
# PROTEIN NUCLEIC-ACID COMPLEX
# NUCLEIC-ACID
# PROTEIN-PROTEIN INTERACTION
def load_component_xrefs(cur, target):
    gene_target_tuple=('SINGLE PROTEIN','PROTEIN FAMILY','PROTEIN COMPLEX GROUP','PROTEIN COMPLEX','CHIMERIC PROTEIN','SELECTIVITY GROUP','PROTEIN NUCLEIC-ACID COMPLEX','NUCLEIC-ACID','PROTEIN-PROTEIN INTERACTION')
    if target['target_type'] in gene_target_tuple :
        target_chembl_id = target['target_chembl_id']
        for component in target['target_components']:
            component_id = component['component_id']
            insert_component(cur, target_chembl_id, component_id)
            if component_id not in loaded_components:
                loaded_components.add(component_id)
                if 'target_component_xrefs' in component:
                    for xref in component['target_component_xrefs']:
                        insert_component_xref(cur, component_id, xref['xref_id'], xref['xref_name'], xref['xref_src_db'])


def main():
    create_target_xref_table()
    create_component_table()
    create_component_xref_table()
    
    response = requests.get(CHEMBL_TARGETS_URL).json()
    while True:
        cur = connection.cursor()
        for target in response['targets']:
            if 'cross_references' in target:
                load_cross_references(cur, target['target_chembl_id'], target['cross_references'])
            if 'target_components' in target:
                load_component_xrefs(cur, target)
        if response['page_meta']['next'] is None:
            break
        cur.close()
        connection.commit()
        sleep(10)
        print(response['page_meta']['next'])
        response = requests.get('https://www.ebi.ac.uk'+response['page_meta']['next']).json()
    connection.close()


if __name__ == '__main__':
    main()
