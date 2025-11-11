import sqlite3
import json
import sys

# ETL process to read the SQL dump file and insert the data into the SQLite database
def  etl_dgidb(sqlite_conn, sql_dump_file):
    sqlite_cursor = sqlite_conn.cursor()
    # Read and process the sql dump file
    with open(sql_dump_file, "r") as dump_file:
        #value = None
        sql_insert = None
        sql = None
        start_copy = False
        count_of_columns = 0
        table = ''
        table_exclude_list = ['delayed_jobs','drug_alias_blacklists','drug_claim_approval_ratings', 'drug_claim_approval_ratings',
        'drug_claim_attributes','gene_aliases_sources','gene_claim_categories','gene_categories_genes',
        'gene_claims','gene_claim_aliases','gene_claim_attributes',
        'gene_claim_categories_gene_claims','interaction_claims', 'interaction_claim_attributes',
        'interaction_claim_links','interaction_claim_types_interaction_claims', 'interaction_claims_publications']
         #List of tables to be excluded from data INSERTion
        ##### List all tables in SQL dump file:
        # 'delayed_jobs','drug_alias_blacklists','drugs','drug_aliases','drug_applications' ,'drug_approval_ratings','drug_attributes','drug_attributes_sources','drug_claims',
        # 'source_trust_levels','sources','drug_claim_approval_ratings','drug_claim_aliases','drug_claim_attributes','genes','gene_aliases' ,'gene_aliases_sources', 
        # 'gene_attributes','gene_attributes_sources','gene_claim_categories','gene_categories_genes','gene_claims','gene_claim_aliases','gene_claim_attributes',
        # 'gene_claim_categories_gene_claims','interactions','interaction_attributes','interaction_attributes_sources','interaction_claims','interaction_claim_attributes',
        # 'interaction_claim_links','interaction_claim_types','interaction_claim_types_interaction_claims','publications','interaction_claims_publications','interaction_types_interactions',
        # 'interactions_publications','interactions_sources', 'source_types','source_types_sources' 
        additonal_columns = {
             "drug_aliases": (", field_name", field_name)
        }


        print(table_exclude_list)
        for line in dump_file:
                # Convert PostgreSQL SQL to SQLite SQL
                if 'COPY public.' in line:
                    table = (line.split('public.'))[1].split(' (')[0]
                    print('TABLE ===>', '"'+table+'"', table in table_exclude_list)
                    start_copy = True
                    additonal_column = ('', None)
                    additonal_column_count = 0
                    if table in additonal_columns:
                        additonal_column = additonal_columns[table]
                        additonal_column_count = 1
                    sql_insert = "INSERT INTO " + table + "(" + (line.split('('))[1].split(')')[0] + additonal_column[0] + ") "              
                    count_of_columns = len((line.split('('))[1].split(')')[0].split(',')) + additonal_column_count
                    count_of_rows = 0
                elif '\\.' in line:                             # end of table data lines
                    sql_insert = None                           # reset (clear) the INSERT sql
                    start_copy == False 
                    sqlite_conn.commit()
                    print('      ===> ', table, 'Rows:', count_of_rows)
                elif start_copy == True and '--' not in line:   # Read a line of table data
                    values_tuple = values_into_list(line, additonal_column)
                    value_string = values_tuple[1]
                    values = values_tuple[0]
                    count_of_values = len(values)               # table data
                    if value_string is not None and sql_insert is not None:
                        sql = sql_insert + " VALUES(" + value_string + ")"
                
                # Execute in SQLite
                    if sql is not None and not (table in table_exclude_list):
                        if count_of_columns == count_of_values:
                            try:
                                    sqlite_cursor.execute(sql, values)
                                    count_of_rows += 1
                            except sqlite3.IntegrityError as e:
                                    print("Error: ", e, sql)
                    if count_of_rows % 1000 == 0:
                        sqlite_conn.commit() 
        sqlite_conn.commit()


#######################################################
# Read the table values from the database dump file
def values_into_list(line, additonal_column):
    cleaned_line = line.strip()             # remove spurious white space and newline
    value_list = cleaned_line.split('\t')
    value_string = None
    for i in range(len(value_list)):
        if value_string is None:
            value_string = '?'      # set up binding placeholders in the SQL query
        else:
            value_string += ',?'    # set up binding placeholders in the SQL query
        if value_list[i] == '\\N':
            value_list[i] = None
    (field_name, field_function) = additonal_column
    if field_function is not None and value_string is not None:
        value_string += ',?'
        value_list.append(field_function(value_list))
    return value_list,value_string


def field_name(row):
    if len(row) >= 3:
        alias = row[2]
        if ':' in alias:
            prefix = alias.split(':')[0]
            if prefix in dgidb_prefix_map:
                return dgidb_prefix_map[prefix]['field_name']
    return None

     

# Create tables in SQLite database
def create_tables(db_connection):
    cursor = db_connection.cursor()
    # drugs
    cursor.execute('''CREATE TABLE drugs (
                        id              TEXT NOT NULL PRIMARY KEY,
                        name            TEXT NOT NULL COLLATE NOCASE,
                        approved        TEXT,
                        immunotherapy   TEXT,
                        anti_neoplastic TEXT,
                        concept_id      TEXT)''')

    # drug_aliases
    cursor.execute('''CREATE TABLE drug_aliases (
                        id         TEXT PRIMARY KEY,
                        drug_id    TEXT,
                        alias      TEXT COLLATE NOCASE,
                        field_name TEXT)''')
    
    # drug_approval_ratings
    cursor.execute('''CREATE TABLE drug_approval_ratings (
                        id        TEXT PRIMARY KEY,
                        rating    TEXT,
                        drug_id   TEXT,
                        source_id TEXT); ''')

    # drug attributes
    cursor.execute('''CREATE TABLE drug_attributes (
                        id      TEXT PRIMARY KEY,
                        drug_id TEXT,
                        name    TEXT,
                        value   TEXT)''')

    # drug_attributes_sources
    cursor.execute('''CREATE TABLE drug_attributes_sources (
                        drug_attribute_id TEXT NOT NULL,
                        source_id  TEXT NOT NULL,
                        CONSTRAINT drug_attributes_sources_pkey PRIMARY KEY (
                        drug_attribute_id,
                        source_id))''')

    # drug_applications
    cursor.execute('''CREATE TABLE drug_applications (
                        id      TEXT PRIMARY KEY,
                        app_no  TEXT,
                        drug_id TEXT)''')

    # drug_claims
    cursor.execute('''CREATE TABLE drug_claims (
                        id           TEXT PRIMARY KEY,
                        name         TEXT NOT NULL COLLATE NOCASE,
                        nomenclature TEXT,
                        source_id    TEXT,
                        drug_id      TEXT)''')

    # drug_claim_aliases
    cursor.execute('''CREATE TABLE drug_claim_aliases (
                        id            TEXT PRIMARY KEY,
                        drug_claim_id TEXT NOT NULL COLLATE NOCASE,
                        alias         TEXT,
                        nomenclature  TEXT)''')

    # genes
    cursor.execute('''CREATE TABLE genes (
                        id         TEXT PRIMARY KEY,
                        name       TEXT,
                        long_name  TEXT,
                        concept_id TEXT) ''')

    #gene_aliases
    cursor.execute('''CREATE TABLE gene_aliases (
                        id      TEXT PRIMARY KEY,
                        gene_id TEXT,
                        alias   TEXT) ''')

    # gene_attributes
    cursor.execute('''CREATE TABLE gene_attributes (
                        id      TEXT PRIMARY KEY,
                        gene_id TEXT,
                        name    TEXT,
                        value   TEXT)''')

    # gene_attributes_sources
    cursor.execute('''CREATE TABLE gene_attributes_sources (
                        gene_attribute_id TEXT,
                        source_id         TEXT)''')

    # interactions
    cursor.execute('''CREATE TABLE interactions (
                        id               TEXT PRIMARY KEY,
                        drug_id          TEXT,
                        gene_id          TEXT,
                        score            DOUBLE,
                        drug_specificity DOUBLE,
                        gene_specificity DOUBLE,
                        evidence_score   INTEGER)''')
    
    # interaction_attributes
    cursor.execute('''CREATE TABLE interaction_attributes (
                        id             TEXT PRIMARY KEY,
                        interaction_id TEXT,
                        name           TEXT,
                        value          TEXT)''')

    # interaction_attributes_sources
    cursor.execute('''CREATE TABLE interaction_attributes_sources (
                        interaction_attribute_id TEXT NOT NULL,
                        source_id                TEXT NOT NULL,
                        CONSTRAINT interaction_attributes_sources_pkey PRIMARY KEY (
                                                interaction_attribute_id,
                                                source_id))''')

    # interactions_sources
    cursor.execute('''CREATE TABLE interactions_sources (
                        interaction_id TEXT NOT NULL,
                        source_id      TEXT NOT NULL)''')

    # interaction_claim_types
    cursor.execute('''CREATE TABLE interaction_claim_types (
                        id             TEXT PRIMARY KEY,
                        type           TEXT,
                        directionality TEXT,
                        definition     TEXT,
                        reference      TEXT)''')

    # interaction_types_interactions
    cursor.execute('''CREATE TABLE interaction_types_interactions (
                        interaction_claim_type_id TEXT NOT NULL,
                        interaction_id            TEXT NOT NULL)''')


    # interactions_publications
    cursor.execute('''CREATE TABLE interactions_publications (
                        interaction_id TEXT,
                        publication_id TEXT) ''')

    # publications
    cursor.execute('''CREATE TABLE publications (
                        id         TEXT PRIMARY KEY,
                        pmid       INTEGER,
                        citation   TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP)''')

    # sources
    cursor.execute('''CREATE TABLE sources (
                            id                                 TEXT PRIMARY KEY,
                            source_db_name                     TEXT,
                            source_db_version                  TEXT,
                            citation                           TEXT,
                            base_url                           TEXT,
                            site_url                           TEXT,
                            full_name                          TEXT,
                            gene_claims_count                  INTEGER                   DEFAULT 0,
                            drug_claims_count                  INTEGER                   DEFAULT 0,
                            interaction_claims_count           INTEGER                   DEFAULT 0,
                            interaction_claims_in_groups_count INTEGER                   DEFAULT 0,
                            gene_claims_in_groups_count        INTEGER                   DEFAULT 0,
                            drug_claims_in_groups_count        INTEGER                   DEFAULT 0,
                            source_trust_level_id              TEXT,
                            license                            TEXT,
                            license_link                       TEXT,
                            citation_short                     TEXT,
                            pmid                               TEXT,
                            pmcid                              TEXT,
                            doi                                TEXT)''')

    #source_trust_levels
    cursor.execute('''CREATE TABLE source_trust_levels (
                        id    TEXT PRIMARY KEY,
                        level TEXT)''')

    #source_types
    cursor.execute('''CREATE TABLE source_types (
                        id           TEXT PRIMARY KEY,
                        type         TEXT,
                        display_name TEXT)''')

    #source_types_sources
    cursor.execute('''CREATE TABLE source_types_sources (
                        source_id      TEXT,
                        source_type_id TEXT)''')
    cursor.execute('''CREATE INDEX  index_source_types_source_id ON source_types_sources(source_id)''')

    db_connection.commit()


# Create indexes in SQLite database
def create_indexes(db_connection):
    print('Creating indexes')
    cursor = db_connection.cursor()
    cursor.execute('''CREATE INDEX index_drugs_name ON drugs(name COLLATE NOCASE)''')
    cursor.execute('''CREATE INDEX index_drugs_concept_id ON drugs(concept_id)''')
    cursor.execute('''CREATE INDEX index_drug_aliases_drug_id ON drug_aliases (drug_id)''')    
    cursor.execute('''CREATE INDEX index_drug_aliases_alias ON drug_aliases (alias COLLATE NOCASE)''')   
    cursor.execute('''CREATE INDEX index_drug_aliases_filed_name ON drug_aliases (alias COLLATE NOCASE, field_name)''')   
    cursor.execute('''CREATE INDEX index_drug_approval_drug_id ON drug_approval_ratings (drug_id)''')  
    cursor.execute('''CREATE INDEX index_drug_attributes_drug_id ON drug_attributes (drug_id)''')
    cursor.execute('''CREATE INDEX index_drug_attributes_name ON drug_attributes (name)''')
    cursor.execute('''CREATE INDEX index_drug_attributes_value ON drug_attributes (value)''')
    cursor.execute('''CREATE INDEX index_drug_attributes_sources_id ON drug_attributes_sources(drug_attribute_id)''')
    cursor.execute('''CREATE INDEX index_drug_attributes_sources_source_id ON drug_attributes_sources(source_id)''')
    cursor.execute('''CREATE INDEX index_drug_applications_drug_id ON drug_applications (drug_id)''')
    cursor.execute('''CREATE INDEX index_drug_claims_drug_id ON drug_claims (drug_id)''')
    cursor.execute('''CREATE INDEX index_drug_claims_name ON drug_claims(name COLLATE NOCASE)''')
    cursor.execute('''CREATE INDEX index_drug_claim_aliases_drug_id ON drug_claim_aliases (drug_claim_id)''')
    cursor.execute('''CREATE INDEX index_drug_claim_alias ON drug_claim_aliases(alias COLLATE NOCASE)''')
    cursor.execute('''CREATE INDEX index_gene_concept_id ON genes (concept_id) ''')
    cursor.execute('''CREATE INDEX index_gene_name ON genes(name) ''')
    cursor.execute('''CREATE INDEX index_gene_long_name ON genes(long_name) ''')
    cursor.execute('''CREATE INDEX index_gene_alias_gene_id ON gene_aliases(gene_id) ''')
    cursor.execute('''CREATE INDEX index_gene_aliases_alias ON gene_aliases(alias) ''')
    cursor.execute('''CREATE INDEX index_gene_attributes_gene_id ON gene_attributes(gene_id)''')
    cursor.execute('''CREATE INDEX index_gene_attributes_name ON gene_attributes(name)''')
    cursor.execute('''CREATE INDEX index_gene_attributes_value ON gene_attributes(value)''')
    cursor.execute('''CREATE INDEX index_gene_attribute_sources_id ON gene_attributes_sources(gene_attribute_id)''')
    cursor.execute('''CREATE INDEX index_interactions_drugs_id ON interactions(drug_id)''')   
    cursor.execute('''CREATE INDEX index_interactions_gene_id ON interactions(gene_id)''') 
    cursor.execute('''CREATE INDEX index_interaction_attributes ON interaction_attributes(interaction_id)''')
    cursor.execute('''CREATE INDEX index_interaction_attr_src_id ON interaction_attributes_sources(interaction_attribute_id)''')
    cursor.execute('''CREATE INDEX index_interactions_sources_interaction_id ON interactions_sources(interaction_id)''')
    cursor.execute('''CREATE INDEX index_interactions_sources_src_id ON interactions_sources(source_id)''')
    cursor.execute('''CREATE INDEX index_interaction_types_interaction_id ON interaction_types_interactions(interaction_id)''')
    cursor.execute('''CREATE INDEX index_interaction_types_interactions_src_id ON interaction_types_interactions(interaction_claim_type_id)''')
    cursor.execute('''CREATE INDEX index_interactions_pub_int_id ON interactions_publications(interaction_id)''')
    cursor.execute('''CREATE INDEX index_interactions_pub_pub_id ON interactions_publications(publication_id)''')
    db_connection.commit()


def load_dgidb_prefix_mapping():
    with open("data/DGIdb_prefixes.json") as json_file:
        return json.load(json_file)


dgidb_prefix_map = load_dgidb_prefix_mapping() 


def main():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sys.argv[2])
    create_tables(sqlite_conn)
    sql_dump_file = sys.argv[1]
    etl_dgidb(sqlite_conn, sql_dump_file)
    create_indexes(sqlite_conn)
    sqlite_conn.close()


if __name__ == '__main__':
    main()