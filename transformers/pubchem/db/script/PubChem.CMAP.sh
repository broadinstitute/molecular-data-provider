sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/CMAP-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/CMAP-names.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.CMAP.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
