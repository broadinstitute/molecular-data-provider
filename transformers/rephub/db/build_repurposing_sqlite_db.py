import sys
import sqlite3
import requests
import json
from contextlib import closing

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
        FEATURE_XREF  TEXT,
        PRIMARY_NAME  TEXT, 
        FEATURE_ACTION TEXT
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


def insert_feature(cur, feature_id, feature_type, feature_name, feature_xref=None, primary_name=None, feature_action=None):
    statement = """
        INSERT INTO FEATURE (FEATURE_ID, FEATURE_TYPE, FEATURE_NAME, FEATURE_XREF, PRIMARY_NAME, FEATURE_ACTION) VALUES (?,?,?,?,?,?)
    """
    cur.execute(statement,(feature_id, feature_type, feature_name, feature_xref, primary_name, feature_action))


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
                                xref_primary = get_xref(feature_type, feature_name) # returns [id, primary_name, feature_action] 
                                if xref_primary == None:
                                    feature_xref = None
                                    primary_name = None
                                    feature_action = None
                                else:
                                    if isinstance(xref_primary, list):
                                        feature_xref = xref_primary[0]
                                        primary_name = xref_primary[1]
                                        feature_action = xref_primary[2]
                                    # gene ids
                                    else:
                                        feature_xref = xref_primary
                                        primary_name = None
                                        if feature_type == 'indication':
                                            feature_action = 'indication for'
                                        elif feature_type == 'target':
                                            feature_action= 'affects'
                                        else:
                                            feature_action = None
                                insert_feature(cur, feature_id, feature_type, feature_name, feature_xref, primary_name, feature_action)
                                features[feature_type+'#'+feature_name] = feature_id
                                fid = feature_id
                            map_id = map_id + 1
                            insert_feature_map(cur, map_id, drug_id, fid)
    cur.close()
    connection.commit()
    return drugs

def format_feature_name(feature_name):
    # make sure that disease names composed of 2 or more words are in the proper format 
    if ' ' in feature_name:
        result=''
        for word in feature_name.split():
        # remove 's from disease names to reduce errors in query  
            if word.endswith("'s"):
                result+= word[:-2]+' '
        # remove plural from types of infections
            elif "infections"== word:
                result+= 'infection'+' '
        # remove abbreviations 
            elif '(' in word:
                pass
            else:
                result+= word+' '
        result= "'"+result[:-1]+"'"
    else:
        result= "'"+feature_name+"'"
    return result

def format_hpo_query(feature_name):
    url= 'https://hpo.jax.org/api/hpo/search/?q='
    disease_name=''
    if ' ' in feature_name:
        for word in feature_name.split():
            disease_name+=word
            disease_name+='%20'
        disease_name= disease_name[:-3]
    else:
        disease_name= feature_name
    result= url+disease_name
    return result

no_xref= []
def get_xref(feature_type, feature_name):
    if feature_type == 'target':
        return get_gene_id(feature_name)
    if feature_type == 'indication':
        # use mydisease.info to obtain mondo id for disease name
        if get_mondo(feature_name) != None:
            return get_mondo(feature_name)
        # check if feature name is phenotype found in HPO
        elif get_hpo(feature_name) != None:
            return get_hpo(feature_name)
        # rest should be found in .txt file
        elif find_indications(feature_name) != None:
            return find_indications(feature_name)
        else: 
            no_xref.append(feature_name)

        
            



# uses hpo.jax.org to obtain HP id for phenotypes, returns none if feature name is not in HPO
def get_hpo(feature_name):
    result= []
    try:
        query= format_hpo_query(feature_name)
        with closing(requests.get(query)) as response_obj:
            # checks if the query returned anything
            if len(response_obj.json()['terms']) != 0:
                for disease in response_obj.json()['terms']:
                    if disease['name'].lower() == feature_name:
                        result.append(disease['id'])
                        result.append(None)
                        result.append('indication for') 
                        return result
                    # remove possible plurals
                    elif disease['name'].lower() == feature_name[:-1]:
                        result.append(disease['id'])
                        result.append(None)
                        result.append('indication for')
                        return result
                    # check synonyms
                    elif disease['synonym'] != None:
                        if disease['synonym'].lower() == feature_name:
                            result.append(disease['id'])
                            result.append(disease['name'].lower())
                            result.append('indication for')
                            return result
                        # remove possible plurals
                        elif disease['synonym'].lower() == feature_name[:-1]:
                            result.append(disease['id'])
                            result.append(disease['name'].lower())
                            result.append('indication for')
                            return result
            else:
                return None
    except:
        return None

# uses my disease.info to obtain mondo id and returns None if id is not found for a disease 
def get_mondo(feature_name):
    result=[]
    try:
        disease_name= format_feature_name(feature_name)
        query = {'q': disease_name, 'scopes': 'mondo.label'}
        url= 'http://mydisease.info/v1/query'

        with closing(requests.post(url, query)) as response_obj:
            for disease_info in response_obj.json():
                if disease_name[1:-1].lower() == disease_info['mondo']['label'].lower(): 
                    result.append(response_obj.json()[0]['mondo']['mondo'])
                    result.append(None)
                    result.append('indication for')
                    return result 
                # take out quotation marks for disease name with 2+ words
                elif disease_name[1:-1].lower()+ ' (disease)' == disease_info['mondo']['label'].lower(): 
                    result.append(response_obj.json()[0]['mondo']['mondo'])
                    result.append(None)
                    result.append('indication for')
                    return result 
                # check list of synonyms
                elif len(disease_info['mondo']['synonym']['exact']) != 0 or disease_info['mondo']['synonym']['exact'] != None:
                    for synonym in disease_info['mondo']['synonym']['exact']:
                        if disease_name[1:-1].lower() == synonym.lower():
                            result.append(response_obj.json()[0]['mondo']['mondo'])
                            result.append(response_obj.json()[0]['mondo']['label'])
                            result.append('indication for')
                            return result 
                        elif disease_name[1:-1].lower()+ ' (disease)'== synonym.lower():
                            result.append(response_obj.json()[0]['mondo']['mondo'])
                            result.append(response_obj.json()[0]['mondo']['label'])
                            result.append('indication for')
                            return result 
            return None

    except:
        return None
        


gene_ids = {}

no_gene_id=[]
def get_gene_id(gene_symbol):
    try:
        gene_id = gene_ids.get(gene_symbol)
        if gene_id is None:
            url = 'https://translator.broadinstitute.org/molecular_data_provider/transform'
            controls = [{'name':'genes', 'value':gene_symbol}]
            query = {'name':'HGNC gene-list producer', 'controls':controls}
            gene_list = requests.post(url, json=query).json()
            if gene_list['size'] > 0:
                url = 'https://translator.broadinstitute.org/molecular_data_provider/collection/'+gene_list['id']+'?cache=no'
                with closing(requests.get(url)) as response_obj:
                    gene_list=response_obj.json()
                    gene_id = gene_list['elements'][0]['id']
                    gene_ids[gene_symbol] = gene_id
        return gene_id
    except:
        no_gene_id.append(gene_symbol)
        return None


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
                    print(line)
                    if line.rstrip() != 'broad_id\tpert_iname\tqc_incompatible\tpurity\tvendor\tcatalog_no\tvendor_name\texpected_mass\tsmiles\tInChIKey\tpubchem_cid\tdeprecated_broad_id':
                        print('ERROR: wrong drug-file format')
                        return
                else:
                    row = line.split('\t')
                    broad_cpd_id = row[0][0:13]
                    pert_iname = row[1]
                    drug_id = drugs[pert_iname]
                    smiles = row[8].strip('"')
                    if ' |' in smiles:
                        smiles = smiles[0:smiles.index(' |')]
                    inchikey = row[9]
                    if inchikey.startswith('"InChI='):
                        inchikey = inchi_key(drug_id, inchikey.strip('"'))
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

no_inchikey= []
def inchi_key(drug_id, inchi):
    url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchi/property/InChIKey/JSON'
    payload = {'inchi':inchi}
    with closing(requests.post(url,data=payload)) as response_obj:
        response= response_obj.json()
        if 'PropertyTable' in response and 'InChIKey' in response['PropertyTable']['Properties'][0]:
            return response['PropertyTable']['Properties'][0]['InChIKey']
        print(str(drug_id)+'\t'+inchi)
        return inchi

def find_indications(feature_name):
    filename= 'data/repurposing_indications.txt'
    first_row = True
    with open(filename,'r') as f:
        for line in f:
            if not line.startswith('!'):
                if first_row:
                    first_row = False
                    if line.rstrip() != 'disease_name\tx_ref\tprimary_name\tfeature_action':
                        print('ERROR: wrong drug-file format')
                        return
                else:
                    row =  line.split('\t')
                    disease_name =  row[0]
                    x_ref = row[1]
                    primary_name = row[2]
                    feature_action = row[3]
                    if feature_name == disease_name:
                        result= [x_ref, primary_name, feature_action]
                        return result
        return None

def main():
    create_tables()
    drugs = parse_drugs('data/repurposing_drugs_20200324.txt')
    parse_samples('data/repurposing_samples_20200324.txt', drugs)
    create_indexes()
    connection.close()
    print('There are '+str(len(no_xref))+' diseases that have not been matched to a MONDO ID or HP ID')
    print(no_xref)
    print('There are '+str(len(no_gene_id))+' without a gene id')
    print(no_gene_id)

if __name__ == '__main__':
    main()

