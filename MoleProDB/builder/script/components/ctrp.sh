python -u script/extract_ids.py script/components/ctrp.sql
sbt 'run data/ctrp/MolePro.CTRP.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/ctrp/MolePro.CTRP.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/ctrp/MolePro.CTRP.sqlite load-transformers'
sbt 'run data/ctrp/MolePro.CTRP.sqlite load-prefixes'
sbt 'run data/ctrp/MolePro.CTRP.sqlite load-structures "Pubchem compound-list producer" data/ctrp/CTRP-CID.tsv'
sbt 'run data/ctrp/MolePro.CTRP.sqlite load-compounds'
sbt 'run data/ctrp/MolePro.CTRP.sqlite add-connections pubchem data/ctrp/CTRP-CID.tsv "CTRP compound-list expander(maximum FDR=0.1, disease context=pan-cancer (all lines), maximum number=0)" pubchem'
sbt 'run data/ctrp/MolePro.CTRP.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
