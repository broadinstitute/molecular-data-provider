python -u script/extract_ids.py script/components/probeminer.sql
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite load-transformers'
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite load-prefixes'
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite load-structures "ProbeMiner compound-list producer" data/probeminer/probe-miner-id.tsv'
cp data/probeminer/MolePro.ProbeMiner.sqlite data/probeminer/MolePro.ProbeMiner.compounds.sqlite
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite load-compounds'
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite load-elements "SRI node normalizer producer" data/probeminer/probe-miner-uniprot-id.tsv uniprot'
cp data/probeminer/MolePro.ProbeMiner.sqlite data/probeminer/MolePro.ProbeMiner.elements.sqlite
sbt -mem 4096 'run data/probeminer/MolePro.ProbeMiner.sqlite add-connections inchikey data/probeminer/probe-miner-id.tsv "ProbeMiner chemical interactions transformer" uniprot'
sbt 'run data/probeminer/MolePro.ProbeMiner.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
