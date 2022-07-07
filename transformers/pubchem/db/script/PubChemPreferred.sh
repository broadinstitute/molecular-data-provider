sbt -mem 4096 "run get-preferred-cids data/PubChem.sqlite data/db/PubChemPreferredCID.sqlite"
cp data/PubChem.sqlite data/tmp/backup/PubChem.Preferred.sqlite
cp data/PubChem.sqlite data/db/PubChem.sqlite
