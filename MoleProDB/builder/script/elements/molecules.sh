python -u script/extract_ids.py script/elements/molecules.sql
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank molecule-list producer" data/drugbank/MolePro.DrugBank.sqlite drugbank'
sbt -mem 4096 'run data/MoleProDB.sqlite load-elements "ChEMBL compound-list producer" data/nn/ChEMBL-molecule-id.tsv chembl'
sbt -mem 4096 'run data/MoleProDB.sqlite load-elements "ChEBI compound-list producer" data/nn/ChEBI-no-struct-id.tsv chebi'
sbt -mem 4096 'run data/MoleProDB.sqlite load-elements "CTD compound-list producer" data/ctd/CTD-chem-MeSH-ID.tsv pubchem,mesh'
sbt -mem 4096 'run data/MoleProDB.sqlite load-elements "PharmGKB compound-list producer" data/pharmgkb/PharmGKB-ID.tsv pubchem,inchi'
cp data/MoleProDB.sqlite data/backup/MoleProDB-molecules.sqlite
