sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/DGIdb-names.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.DGIdb.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
