python -u script/extract_ids.py script/connections/hierarchy.sql
sbt -mem 4096 'run data/MoleProDB.sqlite load-hierarchy data/hierarchy/hierarchy-ID.tsv'
cp data/MoleProDB.sqlite data/backup/MoleProDB-hierarchy.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
cp data/MoleProDB.sqlite data/backup/
