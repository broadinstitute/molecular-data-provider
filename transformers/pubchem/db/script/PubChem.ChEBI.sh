sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/ChEBI-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/ChEBI-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.ChEBI.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
