import sys
import sqlite3

connection = sqlite3.connect("chebi.sqlite", check_same_thread=False)

def exec(sql_file):
    cur = connection.cursor()
    statement = ''
    with open(sql_file,'r') as f:
        for line in f:
            statement = statement + line.rstrip()
            if statement.endswith(';'):
                cur.execute(statement)
                statement = ''
    cur.close()
    connection.commit()

def main():
    sql_files = sys.argv[1]
    with connection:
        with open(sql_files,'r') as f:
            for sql_file in f:
                print(sql_file.rstrip())
                exec(sql_file.rstrip())

if __name__ == '__main__':
    main()
