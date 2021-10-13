import sys

def main():
    schema = {}
    table = []
    table_header = None
    with open(sys.argv[1]) as input:
        for line in input:
            if line.startswith('CREATE TABLE'):
                if table_header is not None:
                    schema[table_header] = table
                table_header = line
                table = []
            table.append(line.rstrip())
        schema[table_header] = table

    for key in sorted(schema.keys()):
        for line in schema[key]:
            print(line)

if __name__ == '__main__':
    main()
