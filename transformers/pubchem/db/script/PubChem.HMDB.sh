sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/HMDB-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/HMDB-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/HMDB-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.HMDB.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
