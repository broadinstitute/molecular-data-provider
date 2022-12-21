sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/Inxight-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.Inxight.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
