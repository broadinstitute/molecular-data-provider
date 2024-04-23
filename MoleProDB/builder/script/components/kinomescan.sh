python -u script/extract_ids.py script/components/kinomescan.sql
sbt 'run data/kinomescan/MolePro.KINOMEscan.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/kinomescan/MolePro.KINOMEscan.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/kinomescan/MolePro.KINOMEscan.sqlite load-transformers'
sbt -mem 4096 'run data/kinomescan/MolePro.KINOMEscan.sqlite load-structures "KINOMEscan small-molecule-list producer" data/kinomescan/KinomeScan-inchikey.tsv'
sbt -mem 4096 'run data/kinomescan/MolePro.KINOMEscan.sqlite load-compounds'
sbt -mem 4096 'run data/kinomescan/MolePro.KINOMEscan.sqlite load-connections inchikey data/kinomescan/KinomeScan-inchikey.tsv "KINOMEscan activity transformer(Kd nMol threshold=10,percent control threshold=10)" uniprot'
sbt 'run data/kinomescan/MolePro.KINOMEscan.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
