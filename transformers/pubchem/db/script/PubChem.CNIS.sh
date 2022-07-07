sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/CNIS-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/CNIS-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/CNIS-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.CNIS.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
