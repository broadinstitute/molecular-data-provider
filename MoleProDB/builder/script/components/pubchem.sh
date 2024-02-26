python -u script/extract_ids.py script/components/pubchem.sql
sbt 'run data/pubchem/MolePro.PubChem.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/pubchem/MolePro.PubChem.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/pubchem/MolePro.PubChem.sqlite load-transformers'
sbt 'run data/pubchem/MolePro.PubChem.sqlite load-prefixes'
sbt -mem 4096 'run data/pubchem/MolePro.PubChem.sqlite load-structures "Pubchem compound-list producer" data/pubchem/PubChem-CID.tsv'
sbt 'run data/pubchem/MolePro.PubChem.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
