python -u script/extract_ids.py script/components/hmdb.sql
sbt 'run data/hmdb/MolePro.HMDB.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/hmdb/MolePro.HMDB.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/hmdb/MolePro.HMDB.sqlite load-transformers'
sbt 'run data/hmdb/MolePro.HMDB.sqlite load-prefixes'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-structures "HMDB metabolite producer" data/hmdb/HMDB-id.tsv'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-compounds'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-connections hmdb data/hmdb/HMDB-id.tsv "HMDB target proteins transformer" uniprot'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-connections hmdb data/hmdb/HMDB-id.tsv "HMDB target genes transformer" entrez'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-elements "SRI node normalizer producer" data/hmdb/HMDB-term-id.tsv'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-elements "SRI node normalizer producer" data/hmdb/HMDB-OMIM.tsv omim'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite add-connections hmdb data/hmdb/HMDB-id.tsv "HMDB disorders transformer" id'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-connections hmdb data/hmdb/HMDB-id.tsv "HMDB locations transformer" id'
sbt -mem 2028 'run data/hmdb/MolePro.HMDB.sqlite load-connections hmdb data/hmdb/HMDB-id.tsv "HMDB pathways transformer" id'
sbt 'run data/hmdb/MolePro.HMDB.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
