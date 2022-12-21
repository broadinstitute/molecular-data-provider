sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/GtoPdb-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/GtoPdb-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/GtoPdb-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.GtoPdb.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
