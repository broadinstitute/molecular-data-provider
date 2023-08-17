python script/extract_ids.py script/elements/molecules.sql
sbt 'run data/MoleProDB.sqlite load-elements "DrugBank molecule-list producer" data/nn/DrugBank-molecule-id.tsv drugbank'
sbt 'run data/MoleProDB.sqlite load-elements "ChEMBL compound-list producer" data/nn/ChEMBL-molecule-id.tsv chembl'
sbt 'run data/MoleProDB.sqlite load-elements "ChEBI compound-list producer" data/nn/ChEBI-no-struct-id.tsv chebi'
cp data/MoleProDB.sqlite data/backup/MoleProDB-molecules.sqlite
