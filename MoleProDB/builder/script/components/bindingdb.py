import sqlite3
import sys

db_connection = sqlite3.connect(sys.argv[2], check_same_thread=False) 
db_connection.row_factory = sqlite3.Row

def found(line):
    query = """
        select structure_id
        from Chem_Structure
        where inchikey = ?
    
    """
    cur = db_connection.cursor()
    cur.execute(query, (line, ))
    for row in cur.fetchall():
        return True
    return False


def main():
    with open(sys.argv[1]) as input:
        input.readline() # skip header
        for line in input:
            row = line.strip().split('\t')
            if found(row[1]):
                print(row[0])


if __name__ == '__main__':
    main()
