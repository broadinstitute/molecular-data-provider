python -u script/extract_ids.py script/elements/node_norm_disease.sql
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/HMDB-OMIM.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/hmdb/HMDB-term-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/DrugCentral-SNOMED.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/ChEMBL-disease-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/CTD-disease-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/RepHub-disease-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/SIDER-UMLS.tsv id'
cp data/MoleProDB.sqlite data/backup/MoleProDB-diseases.sqlite
