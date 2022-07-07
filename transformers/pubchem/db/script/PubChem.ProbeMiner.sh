sbt -mem 4096 "run load-compounds-inchikey data/PubChem.sqlite data/src/ProbeMiner-inchikey.txt"
cp data/PubChem.sqlite data/tmp/backup/PubChem.ProbeMiner.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
