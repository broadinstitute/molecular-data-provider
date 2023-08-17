python -u script/extract_ids.py script/components/stitch.sql 
sbt 'run data/stitch/MolePro.STITCH.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/stitch/MolePro.STITCH.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/stitch/MolePro.STITCH.sqlite load-transformers'
sbt 'run data/stitch/MolePro.STITCH.sqlite load-prefixes'
sbt 'run data/stitch/MolePro.STITCH.sqlite load-structures "Pubchem compound-list producer" data/stitch/STITCH-CID.tsv'
cp data/stitch/MolePro.STITCH.sqlite data/stitch/MolePro.STITCH.structures.sqlite
sbt 'run data/stitch/MolePro.STITCH.sqlite load-compounds'
sbt -mem 4096 'run data/stitch/MolePro.STITCH.sqlite load-elements "SRI node normalizer producer" data/stitch/STITCH-ensembl.tsv ensembl'
sbt -mem 4096 'run data/stitch/MolePro.STITCH.sqlite load-connections pubchem data/stitch/STITCH-CID.tsv "STITCH link transformer(score_threshold=700, limit=500)" ensembl'
sbt 'run data/stitch/MolePro.STITCH.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
