import sys
import sqlite3


def save(src_db, statement, dest_file):
    print('"',src_db,'"\t"',dest_file,'"', sep='')
    connection = sqlite3.connect(src_db, check_same_thread=False)
    with connection:
        cur = connection.cursor()
        cur.execute(statement)
        with open(dest_file,'w') as output:
            output.write('id\n')
            for row in cur.fetchall():
                output.write(str(row[0])+'\n')


def exec(sql_file):
    statement = ''
    with open(sql_file,'r') as f:
        for line in f:
            if line.startswith('-->'):
                row = line[3:].rstrip().split('>>>')
                src_db = row[0].strip()
                dest_file = row[1].strip()
            else:
                statement = statement + line.rstrip()
            if statement.endswith(';'):
                save(src_db, statement, dest_file)
                statement = ''
                src_db = None
                dest_file = None


def main():
    exec(sys.argv[1])


if __name__ == "__main__":
    main()
