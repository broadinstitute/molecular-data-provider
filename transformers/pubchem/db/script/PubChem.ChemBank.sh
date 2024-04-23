sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/ChemBank-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/ChemBank-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.ChemBank.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
