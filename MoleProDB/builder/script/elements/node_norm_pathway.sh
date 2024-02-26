python -u script/extract_ids.py script/elements/node_norm_pathway.sql
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/CTD-GO.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/CTD-pathways.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/MSigDB-GO.tsv id'
cp data/MoleProDB.sqlite data/backup/MoleProDB-pathways.sqlite
