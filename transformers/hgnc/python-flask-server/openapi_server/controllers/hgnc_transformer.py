import sqlite3

from transformers.transformer import Producer

connection = sqlite3.connect("data/HGNC.sqlite", check_same_thread=False)
connection.row_factory = sqlite3.Row

class HgncGeneProducer(Producer):

    variables = ['gene']

    def __init__(self, definition_file='info/hgnc_transformer_info.json'):
        super().__init__(self.variables, definition_file)


    def update_transformer_info(self, info):
        info.knowledge_map.nodes[self.biolink_class('Gene')].count = get_gene_count()


    def find_names(self, name):
        if self.has_prefix('hgnc', name, self.OUTPUT_CLASS):
            return find_gene('hgnc_id', name)
        elif self.has_prefix('entrez', name, self.OUTPUT_CLASS):
            entrez_id = self.de_prefix('entrez', name, self.OUTPUT_CLASS)
            return find_gene('entrez_id', entrez_id)
        elif self.has_prefix('ensembl', name, self.OUTPUT_CLASS):
            ensembl_gene_id = self.de_prefix('ensembl', name, self.OUTPUT_CLASS)
            return find_gene('ensembl_gene_id', ensembl_gene_id)
        else:
            genes = find_gene('symbol', name)
            if genes is not None and len(genes) > 0:
                return genes
            return find_gene('name', name)


    def create_element(self, hgnc_id):
        row = get_gene(hgnc_id)
        if row is None:
            return None
        biolink_class = self.biolink_class(self.OUTPUT_CLASS)
        identifiers = self.identifiers(hgnc_id, row)
        names = self.names(row)
        attributes = self.attributes(row)
        element = self.Element(hgnc_id, biolink_class, identifiers, names, attributes)
        return element


    def identifiers(self, hgnc_id, row):
        identifiers = {'hgnc': hgnc_id}
        if row['entrez_id'] is not None:
            identifiers['entrez'] = self.add_prefix('entrez', row['entrez_id'])
        if row['ensembl_gene_id'] is not None:
            identifiers['ensembl'] = self.add_prefix('ensembl', row['ensembl_gene_id'])
        if row['omim_id'] is not None:
            identifiers['mim'] = self.add_prefix('mim', row['omim_id'])
        return identifiers


    def names(self, row):
        name = row['name']
        synonyms = []
        if row['alias_name'] is not None:
            synonyms = row['alias_name'].split('|')
        if row['prev_name'] is not None:
            synonyms.extend(row['prev_name'].split('|'))
        names = self.Names(name, synonyms)

        symbol = row['symbol']
        synonyms = []
        if row['alias_symbol'] is not None:
            synonyms = row['alias_symbol'].split('|')
        if row['prev_symbol'] is not None:
            synonyms.extend(row['prev_symbol'].split('|'))
        symbols = self.Names(symbol, synonyms, 'symbol')
 
        return [names, symbols]


    def attributes(self, row):
        attributes = []
        if row['symbol'] is not None:
            attributes.append(self.Attribute('symbol',row['symbol'],'biolink:symbol'))
        for attr in ['locus_group','locus_type','location','gene_group']:
            if row[attr] is not None:
                attributes.append(self.Attribute(attr,row[attr]))
        return attributes


def find_gene(column_name, value):
    query = '''
        select hgnc_id
        from hgnc
        where {} = ?
    '''.format(column_name)
    cur = connection.cursor()
    cur.execute(query,(value,))
    return [row['hgnc_id'] for row in cur.fetchall()]


def get_gene(hgnc_id):
    query = '''
        select 
            hgnc_id, symbol, name, locus_group, locus_type, location,
            alias_symbol, alias_name, prev_symbol, prev_name, gene_group,
            entrez_id, ensembl_gene_id, omim_id
        from hgnc
        where hgnc_id = ?
    '''
    cur = connection.cursor()
    cur.execute(query,(hgnc_id,))
    for row in cur.fetchall():
        return row
    return None


def get_gene_count():
    query = '''
        select count(hgnc_id) as count from hgnc
    '''
    cur = connection.cursor()
    cur.execute(query)
    for row in cur.fetchall():
        return row['count']
    return -1
