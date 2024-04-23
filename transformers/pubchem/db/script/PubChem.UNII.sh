sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/UNII-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/UNII-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/UNII-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.UNII.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
