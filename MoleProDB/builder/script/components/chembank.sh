python -u script/extract_ids.py script/components/chembank.sql
sbt 'run data/moleprodb/chembank/MolePro.ChemBank.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/moleprodb/chembank/MolePro.ChemBank.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/moleprodb/chembank/MolePro.ChemBank.sqlite load-transformers'
sbt 'run data/moleprodb/chembank/MolePro.ChemBank.sqlite load-prefixes'
sbt 'run data/moleprodb/chembank/MolePro.ChemBank.sqlite load-structures "ChemBank compound-list producer" data/moleprodb/chembank/ChemBank-ID.tsv'
sbt 'run data/moleprodb/chembank/MolePro.ChemBank.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
