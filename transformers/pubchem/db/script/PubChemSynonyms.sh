sbt 'run syn-create-db'

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000001.ttl.gz
gunzip data/download/pc_synonym2compound_000001.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000001.ttl'
rm data/download/pc_synonym2compound_000001.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000002.ttl.gz
gunzip data/download/pc_synonym2compound_000002.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000002.ttl'
rm data/download/pc_synonym2compound_000002.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000003.ttl.gz
gunzip data/download/pc_synonym2compound_000003.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000003.ttl'
rm data/download/pc_synonym2compound_000003.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000004.ttl.gz
gunzip data/download/pc_synonym2compound_000004.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000004.ttl'
rm data/download/pc_synonym2compound_000004.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000005.ttl.gz
gunzip data/download/pc_synonym2compound_000005.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000005.ttl'
rm data/download/pc_synonym2compound_000005.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000006.ttl.gz
gunzip data/download/pc_synonym2compound_000006.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000006.ttl'
rm data/download/pc_synonym2compound_000006.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000007.ttl.gz
gunzip data/download/pc_synonym2compound_000007.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000007.ttl'
rm data/download/pc_synonym2compound_000007.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000008.ttl.gz
gunzip data/download/pc_synonym2compound_000008.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000008.ttl'
rm data/download/pc_synonym2compound_000008.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000009.ttl.gz
gunzip data/download/pc_synonym2compound_000009.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000009.ttl'
rm data/download/pc_synonym2compound_000009.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000010.ttl.gz
gunzip data/download/pc_synonym2compound_000010.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000010.ttl'
rm data/download/pc_synonym2compound_000010.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym2compound_000011.ttl.gz
gunzip data/download/pc_synonym2compound_000011.ttl.gz
sbt -mem 4096 'run syn-load-ids data/download/pc_synonym2compound_000011.ttl'
rm data/download/pc_synonym2compound_000011.ttl

cp data/PubChemSynonyms.sqlite data/PubChemSynonyms.cid.sqlite

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000001.ttl.gz
gunzip data/download/pc_synonym_type_000001.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000001.ttl'
rm data/download/pc_synonym_type_000001.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000002.ttl.gz
gunzip data/download/pc_synonym_type_000002.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000002.ttl'
rm data/download/pc_synonym_type_000002.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000003.ttl.gz
gunzip data/download/pc_synonym_type_000003.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000003.ttl'
rm data/download/pc_synonym_type_000003.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000004.ttl.gz
gunzip data/download/pc_synonym_type_000004.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000004.ttl'
rm data/download/pc_synonym_type_000004.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000005.ttl.gz
gunzip data/download/pc_synonym_type_000005.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000005.ttl'
rm data/download/pc_synonym_type_000005.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000006.ttl.gz
gunzip data/download/pc_synonym_type_000006.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000006.ttl'
rm data/download/pc_synonym_type_000006.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000007.ttl.gz
gunzip data/download/pc_synonym_type_000007.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000007.ttl'
rm data/download/pc_synonym_type_000007.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000008.ttl.gz
gunzip data/download/pc_synonym_type_000008.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000008.ttl'
rm data/download/pc_synonym_type_000008.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000009.ttl.gz
gunzip data/download/pc_synonym_type_000009.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000009.ttl'
rm data/download/pc_synonym_type_000009.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000010.ttl.gz
gunzip data/download/pc_synonym_type_000010.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000010.ttl'
rm data/download/pc_synonym_type_000010.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000011.ttl.gz
gunzip data/download/pc_synonym_type_000011.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000011.ttl'
rm data/download/pc_synonym_type_000011.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000012.ttl.gz
gunzip data/download/pc_synonym_type_000012.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000012.ttl'
rm data/download/pc_synonym_type_000012.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000013.ttl.gz
gunzip data/download/pc_synonym_type_000013.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000013.ttl'
rm data/download/pc_synonym_type_000013.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000014.ttl.gz
gunzip data/download/pc_synonym_type_000014.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000014.ttl'
rm data/download/pc_synonym_type_000014.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_type_000015.ttl.gz
gunzip data/download/pc_synonym_type_000015.ttl.gz
sbt -mem 4096 'run syn-load-types data/download/pc_synonym_type_000015.ttl'
rm data/download/pc_synonym_type_000015.ttl

cp data/PubChemSynonyms.sqlite data/PubChemSynonyms.types.sqlite

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000001.ttl.gz
gunzip data/download/pc_synonym_value_000001.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000001.ttl'
rm data/download/pc_synonym_value_000001.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000002.ttl.gz
gunzip data/download/pc_synonym_value_000002.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000002.ttl'
rm data/download/pc_synonym_value_000002.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000003.ttl.gz
gunzip data/download/pc_synonym_value_000003.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000003.ttl'
rm data/download/pc_synonym_value_000003.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000004.ttl.gz
gunzip data/download/pc_synonym_value_000004.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000004.ttl'
rm data/download/pc_synonym_value_000004.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000005.ttl.gz
gunzip data/download/pc_synonym_value_000005.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000005.ttl'
rm data/download/pc_synonym_value_000005.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000006.ttl.gz
gunzip data/download/pc_synonym_value_000006.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000006.ttl'
rm data/download/pc_synonym_value_000006.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000007.ttl.gz
gunzip data/download/pc_synonym_value_000007.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000007.ttl'
rm data/download/pc_synonym_value_000007.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000008.ttl.gz
gunzip data/download/pc_synonym_value_000008.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000008.ttl'
rm data/download/pc_synonym_value_000008.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000009.ttl.gz
gunzip data/download/pc_synonym_value_000009.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000009.ttl'
rm data/download/pc_synonym_value_000009.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000010.ttl.gz
gunzip data/download/pc_synonym_value_000010.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000010.ttl'
rm data/download/pc_synonym_value_000010.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000011.ttl.gz
gunzip data/download/pc_synonym_value_000011.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000011.ttl'
rm data/download/pc_synonym_value_000011.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000012.ttl.gz
gunzip data/download/pc_synonym_value_000012.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000012.ttl'
rm data/download/pc_synonym_value_000012.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000013.ttl.gz
gunzip data/download/pc_synonym_value_000013.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000013.ttl'
rm data/download/pc_synonym_value_000013.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000014.ttl.gz
gunzip data/download/pc_synonym_value_000014.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000014.ttl'
rm data/download/pc_synonym_value_000014.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000015.ttl.gz
gunzip data/download/pc_synonym_value_000015.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000015.ttl'
rm data/download/pc_synonym_value_000015.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000016.ttl.gz
gunzip data/download/pc_synonym_value_000016.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000016.ttl'
rm data/download/pc_synonym_value_000016.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000017.ttl.gz
gunzip data/download/pc_synonym_value_000017.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000017.ttl'
rm data/download/pc_synonym_value_000017.ttl

wget -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/synonym/pc_synonym_value_000018.ttl.gz
gunzip data/download/pc_synonym_value_000018.ttl.gz
sbt -mem 4096 'run syn-load-values data/download/pc_synonym_value_000018.ttl'
rm data/download/pc_synonym_value_000018.ttl

cp data/PubChemSynonyms.sqlite data/PubChemSynonyms.values.sqlite

sbt -mem 4096 'run syn-build-indexes'
