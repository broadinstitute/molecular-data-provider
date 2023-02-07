from molepro.transformers import * 
from molepro.server import elements

compound = 'glucose'

compound_list = compound_producer(compound)
reactions = bigg_reactions_transformer(compound_list)
for element in elements(reactions):
    print(element.id, element.names_synonyms[0].name)
