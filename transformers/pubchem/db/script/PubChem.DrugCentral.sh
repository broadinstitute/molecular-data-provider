sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/DrugCentral-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/DrugCentral-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.DrugCentral.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
