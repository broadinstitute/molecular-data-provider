python -u script/extract_ids.py script/connections/hierarchy.sql
sbt -mem 32000 'run data/MoleProDB.sqlite load-hierarchy data/hierarchy/hierarchy-ID.tsv'
cp data/MoleProDB.sqlite data/backup/MoleProDB-hierarchy.sqlite
