python -u script/extract_ids.py script/elements/node_norm_protein.sql
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/BindingDB-protein-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/ChEMBL-protein-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/DrugBank-protein-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/HMDB-uniprot-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/STITCH-ensembl.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/probe-miner-uniprot-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/UniProt-uniprot-id.tsv id'
cp data/MoleProDB.sqlite data/backup/MoleProDB-proteins.sqlite
