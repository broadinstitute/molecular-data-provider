import os
import sys
import sqlite3


def count(file, rel, connection, query):
    cur = connection.cursor()
    cur.execute(query)
    for row in cur.fetchall():
        print(file, rel, row['transformer'],row['count'], sep='\t')

def count_identifiers(file, connection):
    query = """
    select transformer, count(distinct list_element_id) as count
    from List_Element_Identifier
    join Source on List_Element_Identifier.source_id = Source.source_id
    group by Source.transformer
    order by transformer;
    """
    count(file, 'List_Element', connection, query)

def count_connections(file, connection):
    query = """
    select transformer, count(connection_id) as count
    from Connection
    join Source on Connection.source_id = Source.source_id
    group by Source.transformer
    order by transformer;
    """
    count(file, 'Connection', connection, query)


def db_dontent(file, db_file):
    connection = sqlite3.connect(db_file, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    count_identifiers(file, connection)
    count_connections(file, connection)
    connection.close()


def main():
    for dir in sorted(os.listdir(sys.argv[1])):
        dir = os.path.join(sys.argv[1], dir)
        if os.path.isdir(dir):
            #print(dir)
            for file in os.listdir(dir):
                if file.startswith('MolePro') and file.endswith('.sqlite'):
                    db_file = os.path.join(dir, file)
                    if file.count('.') == 2:
                        db_dontent(file, db_file)


if __name__ == "__main__":
    main()
