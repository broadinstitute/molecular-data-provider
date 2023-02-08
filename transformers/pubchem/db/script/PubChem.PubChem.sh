#sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/PubChem-prev-CID.txt"
sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/PubChem-log-CID.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.PubChem.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
