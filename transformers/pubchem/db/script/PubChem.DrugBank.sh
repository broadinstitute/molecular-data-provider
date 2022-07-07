sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/DrugBank-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/DrugBank-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/DrugBank-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.drugbank.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
