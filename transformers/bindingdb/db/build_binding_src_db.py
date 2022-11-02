import sqlite3

import pandas as pd

CHUNK_SIZE = 10000

connection_src = sqlite3.connect("data/BindingDBsrc.sqlite", check_same_thread=False)


def main():
    df = pd.read_csv('data/BindingDB_All.tsv', sep="\t", header=0, dtype=str, error_bad_lines=False)
    print('loaded binding_db')
    df.to_sql('binding_db', connection_src, index=False, chunksize=CHUNK_SIZE)
    print('saved binding_db')


if __name__ == "__main__":
    main()
