sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/RepHub-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/RepHub-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/RepHub-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.RepHub.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
