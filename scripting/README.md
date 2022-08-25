# molepro-scripting-dev


## examples of usage

```
from molepro.transformers import * 
from molepro.server import elements
import molepro.save as save

x = pubchem_compound_list_producer(compound=['bortezomib','aspirin'])
y = drugbank_target_genes_transformer(x)
z = cmap_compound_to_gene_transformer(x, score_threshold = 99, maximum_number = 10)
w = union(y,z)

print("Found "+str(z.size)+ " genes via CMAP")
print("Found "+str(w.size)+ " genes in total")

for element in elements(y):
    print(element.biolink_class + ": " + element.id)
    for attribute in element.attributes:
        if attribute.original_attribute_name in ('gene-name','molecular-weight'):
            print("  "+attribute.original_attribute_name+": "+attribute.value)

save.names(w, 'examples/names.tsv')
save.identifiers(w, 'examples/ids.tsv')
save.attributes(w, 'examples/attributes.tsv')
save.connections(w, 'examples/connections.tsv')
```


```
from molepro.transformers import * 
from molepro.server import elements
import molepro.save as save

u = compound_producer(elements=['ibuprofen','aspirin'])
v = transform_compound_to_disease(u)
for element in elements(v):
    for connection in element.connections:
        print(connection.source_element_id, connection.biolink_predicate, element.biolink_class + ": " + element.id, sep='\t')
```

## generate API model classes

```
java -jar ../../../openapi-generator/openapi-generator-cli-5.2.0.jar generate -i molecular_data_provider.yml -g python-flask -o molepro --model-package classes --global-property models
```
