python -u script/extract_ids.py script/elements/node_norm_gene.sql
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/BiGG-entrez.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/ChEMBL-gene-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/CMAP-NCBIGeneId.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/CTD-geneID.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/DGIdb-gene-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/DrugBank-gene-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/GtoPdb-gene-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/hmdb/UniProt2Entrez.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/MSigDB-gene-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/Pharos-gene-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/RepHub-gene-id.tsv id'
sbt 'run data/MoleProDB.sqlite load-elements "SRI node normalizer producer" data/nn/UniProt-gene-id.tsv id'
cp data/MoleProDB.sqlite data/backup/MoleProDB-genes.sqlite
