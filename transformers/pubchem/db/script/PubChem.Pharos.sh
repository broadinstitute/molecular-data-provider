sbt -mem 4096 "run load-compounds-cid data/PubChem.sqlite data/src/Pharos-CID.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/Pharos-drugnames.txt"
sbt -mem 4096 "run load-compounds-name data/PubChem.sqlite data/src/Pharos-names.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.Pharos.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
