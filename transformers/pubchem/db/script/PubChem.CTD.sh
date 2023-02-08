sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/CTD-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/CTD-names.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.CTD.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
