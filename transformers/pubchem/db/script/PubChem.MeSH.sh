sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/MeSH-CID.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.MeSH.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
