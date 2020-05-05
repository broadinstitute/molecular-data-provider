import sys
import sqlite3
import requests


connection = sqlite3.connect("data/RepurposingHub.sqlite", check_same_thread=False)


DRUG_TABLE = """
    CREATE TABLE DRUG (
        DRUG_ID    INT   PRIMARY_KEY,
        PERT_INAME TEXT  NOT NULL COLLATE NOCASE
    );
"""


FEATURE_TABLE = """
    CREATE TABLE FEATURE (
        FEATURE_ID    INT   PRIMARY_KEY,
        FEATURE_TYPE  TEXT  NOT NULL,
        FEATURE_NAME  TEXT  NOT NULL COLLATE NOCASE,
        FEATURE_XREF  TEXT
    );
"""


FEATURE_MAP_TABLE = """
    CREATE TABLE FEATURE_MAP (
        MAP_ID      INT  PRIMARY_KEY,
        DRUG_ID     INT  REFERENCES DRUG(DRUG_ID),
        FEATURE_ID  INT  REFERENCES FEATURE(FEATURE_ID)
    );
"""


SAMPLE_TABLE = """
    CREATE TABLE SAMPLE (
        SAMPLE_ID     INT   PRIMARY_KEY,
        DRUG_ID       INT   REFERENCES DRUG(DRUG_ID),
        BROAD_CPD_ID  TEXT  NOT NULL,
        SMILES        TEXT  NOT NULL,
        INCHIKEY      TEXT  NOT NULL,
        PUBCHEMCID    INT
    );
"""


NAME_TABLE = """
    CREATE TABLE NAME (
        NAME_ID    INT   PRIMARY_KEY,
        SAMPLE_ID  INT   REFERENCES SAMPLE(SAMPLE_ID),
        DRUG_ID    INT   REFERENCES DRUG(DRUG_ID),
        NAME       TEXT  NOT NULL
    );
"""


def create_tables():
    cur = connection.cursor()
    cur.execute(DRUG_TABLE)
    cur.execute(FEATURE_TABLE)
    cur.execute(FEATURE_MAP_TABLE)
    cur.execute(SAMPLE_TABLE)
    cur.execute(NAME_TABLE)
    cur.close()
    connection.commit()


feature_types = ['','clinical_phase','moa','target','disease_area','indication']


def insert_drug(cur, drug_id, pert_iname):
    statement = """
        INSERT INTO DRUG (DRUG_ID, PERT_INAME) VALUES (?,?)
    """
    cur.execute(statement,(drug_id, pert_iname))


def insert_feature(cur, feature_id, feature_type, feature_name, feature_xref=None):
    statement = """
        INSERT INTO FEATURE (FEATURE_ID, FEATURE_TYPE, FEATURE_NAME, FEATURE_XREF) VALUES (?,?,?,?)
    """
    cur.execute(statement,(feature_id, feature_type, feature_name, feature_xref))


def insert_feature_map(cur, map_id, drug_id, feature_id):
    statement = """
        INSERT INTO FEATURE_MAP (MAP_ID, DRUG_ID, FEATURE_ID) VALUES (?,?,?)
    """
    cur.execute(statement,(map_id, drug_id, feature_id))


def insert_sample(cur, sample_id, drug_id, broad_cpd_id, smiles, inchikey, pubchem_cid):
    statement = """
        INSERT INTO SAMPLE (SAMPLE_ID, DRUG_ID, BROAD_CPD_ID, SMILES, INCHIKEY, PUBCHEMCID) VALUES (?,?,?,?,?,?)
    """
    cur.execute(statement,(sample_id, drug_id, broad_cpd_id, smiles, inchikey, pubchem_cid))


def insert_name(cur, name_id, sample_id, drug_id, name):
    statement = """
        INSERT INTO NAME (NAME_ID, SAMPLE_ID, DRUG_ID, NAME) VALUES (?,?,?,?)
    """
    cur.execute(statement,(name_id, sample_id, drug_id, name))


def create_index(cur, table, column):
    statement = """
        CREATE INDEX {}_{}_IDX ON {}({});
    """
    cur.execute(statement.format(table, column, table, column))


def create_indexes():
    cur = connection.cursor()
    create_index(cur, 'DRUG', 'PERT_INAME')
    create_index(cur, 'FEATURE', 'FEATURE_NAME')
    create_index(cur, 'FEATURE', 'FEATURE_TYPE')
    create_index(cur, 'FEATURE_MAP', 'DRUG_ID')
    create_index(cur, 'FEATURE_MAP', 'FEATURE_ID')
    create_index(cur, 'NAME', 'NAME')
    create_index(cur, 'NAME', 'DRUG_ID')
    create_index(cur, 'NAME', 'SAMPLE_ID')
    create_index(cur, 'SAMPLE', 'DRUG_ID')
    create_index(cur, 'SAMPLE', 'INCHIKEY')
    create_index(cur, 'SAMPLE', 'PUBCHEMCID')
    cur.close()
    connection.commit()


def parse_drugs(filename):
    drugs = {}
    features = {}
    cur = connection.cursor()
    first_row = True
    drug_id = 0
    feature_id = 0
    map_id = 0
    with open(filename,'r') as f:
        for line in f:
            if not line.startswith('!'):
                if first_row:
                    first_row = False
                    print(line)
                    if line.rstrip() != 'pert_iname\tclinical_phase\tmoa\ttarget\tdisease_area\tindication':
                        print('ERROR: wrong drug-file format')
                        return
                else:
                    drug_id = drug_id + 1
                    row = line.split('\t')
                    pert_iname = row[0]
                    insert_drug(cur, drug_id, pert_iname)
                    drugs[pert_iname] = drug_id
                    for i in range(1,6):
                        feature_names = row[i].rstrip().split('|') if row[i].rstrip() != '' else []
                        for feature_name in feature_names:
                            feature_type = feature_types[i]
                            fid = features.get(feature_type+'#'+feature_name)
                            if fid is None:
                                feature_id = feature_id + 1
                                feature_xref = get_xref(feature_type, feature_name)
                                insert_feature(cur, feature_id, feature_type, feature_name, feature_xref)
                                features[feature_type+'#'+feature_name] = feature_id
                                fid = feature_id
                            map_id = map_id + 1
                            insert_feature_map(cur, map_id, drug_id, fid)
    cur.close()
    connection.commit()
    return drugs


def get_xref(feature_type, feature_name):
    if feature_type == 'target':
        return get_gene_id(feature_name)
    return None


gene_ids = {}

def get_gene_id(gene_symbol):
    gene_id = gene_ids.get(gene_symbol)
    if gene_id is None:
        url = 'https://translator.broadinstitute.org/molecular_data_provider/transform'
        controls = [{'name':'gene symbols', 'value':gene_symbol}]
        query = {'name':'HGNC gene-list producer', 'controls':controls}
        gene_list = requests.post(url, json=query).json()
        if gene_list['size'] > 0:
            url = 'https://translator.broadinstitute.org/molecular_data_provider/gene/list/'+gene_list['id']
            gene_list = requests.get(url).json()
            print(gene_list)
            gene_id = gene_list['elements'][0]['gene_id']
            gene_ids[gene_symbol] = gene_id
    return gene_id


def parse_samples(filename, drugs):
    samples = {}
    names = set()
    cur = connection.cursor()
    sample_id = 0
    name_id = 0
    first_row = True
    with open(filename,'r') as f:
        for line in f:
            if not line.startswith('!'):
                if first_row:
                    first_row = False
                    if line.rstrip() != 'broad_id\tpert_iname\tqc_incompatible\tpurity\tvendor\tcatalog_no\tvendor_name\texpected_mass\tsmiles\tInChIKey\tpubchem_cid\tdeprecated_broad_id':
                        print('ERROR: wrong drug-file format')
                        return
                else:
                    row = line.split('\t')
                    broad_cpd_id = row[0][0:13]
                    pert_iname = row[1]
                    drug_id = drugs[pert_iname]
                    smiles = row[8]
                    inchikey = row[9]
                    pubchem_cid = row[10]
                    sid = samples.get(inchikey)
                    if sid is None:
                        sample_id = sample_id + 1
                        insert_sample(cur, sample_id, drug_id, broad_cpd_id, smiles, inchikey, pubchem_cid)
                        samples[inchikey] = sample_id
                        sid = sample_id
                    name = row[6]
                    if name != '' and name not in names:
                        name_id = name_id + 1
                        insert_name(cur, name_id, sid, drug_id, name)
                        names.add(name)
    cur.close()
    connection.commit()


def main():
    create_tables()
    drugs = parse_drugs(sys.argv[1])
    parse_samples(sys.argv[2], drugs)
    create_indexes()
    connection.close()


if __name__ == '__main__':
    main()

