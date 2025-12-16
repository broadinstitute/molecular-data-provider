import sqlite3

connection = sqlite3.connect('testDB.sqlite')
connection.row_factory = sqlite3.Row


create_table_drugs_a = """
CREATE TABLE drugs_A (
    id                 STRING (100, 100) PRIMARY KEY
                                         NOT NULL,
    name               TEXT              NOT NULL,
    fda_approved       BOOLEAN,
    immunotherapy      BOOLEAN,
    anti_neoplastic    BOOLEAN,
    chembl_id          CHAR,
    chembl_molecule_id INTEGER
);
"""

create_chembl_index_drugs_a = """
CREATE INDEX drugs_A_chembl_id_index ON drugs_A (chembl_id);
"""

create_table_drugs_b = """
CREATE TABLE drugs_B (
    id                 TEXT PRIMARY KEY,
    name               TEXT              NOT NULL,
    fda_approved       BOOLEAN,
    immunotherapy      BOOLEAN,
    anti_neoplastic    BOOLEAN,
    chembl_id          CHAR,
    chembl_molecule_id INTEGER
);
"""

create_chembl_index_drugs_b = """
CREATE INDEX drugs_B_chembl_id_index ON drugs_B (chembl_id);
"""


create_table_drugs_aliases = """
CREATE TABLE drug_aliases (
    id      TEXT PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    drug_id TEXT,
    alias   TEXT COLLATE NOCASE
);
"""

create_index_drugs_aliases = """
CREATE INDEX drug_aliases_alias_index ON drug_aliases (drug_id);
"""


query_a = """
explain query plan 
SELECT * FROM drugs_A as drugs
JOIN drug_aliases ON drugs.id = drug_aliases.drug_id
WHERE chembl_id = "123124124Dfcbfgjd";
"""

query_b = """
explain query plan 
SELECT * FROM drugs_B as drugs
JOIN drug_aliases ON drugs.id = drug_aliases.drug_id
WHERE chembl_id = "123124124Dfcbfgjd";
"""

cursor = connection.cursor()
cursor.execute(create_table_drugs_a)
cursor.execute(create_chembl_index_drugs_a)
cursor.execute(create_table_drugs_b)
cursor.execute(create_chembl_index_drugs_b)
cursor.execute(create_table_drugs_aliases)
cursor.execute(create_index_drugs_aliases)
cursor.execute(query_a)
for row in cursor.fetchall():
    print(row['detail'])

print('-----------------')
cursor.execute(query_b)
for row in cursor.fetchall():
    print(row['detail'])
