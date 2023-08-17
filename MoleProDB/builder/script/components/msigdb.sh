python -u script/extract_ids.py script/components/msigdb.sql
sbt 'run data/msigdb/MolePro.MSigDB.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/msigdb/MolePro.MSigDB.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/msigdb/MolePro.MSigDB.sqlite load-transformers'
sbt -mem 4096 'run data/msigdb/MolePro.MSigDB.sqlite load-elements "SRI node normalizer producer" data/msigdb/MSigDB-gene-id.tsv id'
sbt -mem 4096 'run data/msigdb/MolePro.MSigDB.sqlite load-connections entrez data/msigdb/MSigDB-gene-id.tsv "MSigDB pathways transformer" msigdb'
sbt 'run data/msigdb/MolePro.MSigDB.sqlite exec ../schema/MoleProPostLoadIndexes.sql'