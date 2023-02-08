sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/ChEMBL-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/ChEMBL-drug-inchikey.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/ChEMBL-metabolite-inchikey.txt"
#sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/ChEMBL-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.ChEMBL.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
