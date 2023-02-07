from molepro.transformers import * 
from molepro.server import elements
from molepro.server import set_base_url
import molepro.save as save

set_base_url('http://localhost:9200/molecular_data_provider')

genes = ['BLVRB','CAND1','AHCY','XPO1','MCM6','RETSAT','AP3B2','IPO9','TIMM44','CAND2','KPNA4','USP9X','LRPPRC','GAPDH']

gene_list_from_pull_down = gene_producer(genes)
connections = moleprodb_connections_transformer(gene_list_from_pull_down, predicate='biolink:affects')
print(connections)
