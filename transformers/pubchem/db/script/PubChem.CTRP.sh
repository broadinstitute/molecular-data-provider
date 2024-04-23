sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/CTRP1-CID.txt"
sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/CTRP2-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/CTRP1-names.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/CTRP2-names.txt"
sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/CTRP2-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.CTRP.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
