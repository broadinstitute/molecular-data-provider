python script/extract_ids.py script/components/chebi.sql
sbt 'run data/chebi/MolePro.ChEBI.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/chebi/MolePro.ChEBI.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/chebi/MolePro.ChEBI.sqlite load-transformers'
sbt 'run data/chebi/MolePro.ChEBI.sqlite load-structures "ChEBI compound-list producer" data/chebi/ChEBI-inchikey.tsv'
sbt 'run data/chebi/MolePro.ChEBI.sqlite load-compounds'
sbt 'run data/chebi/MolePro.ChEBI.sqlite load-elements "ChEBI compound-list producer" data/chebi/ChEBI-no-struct-id.tsv chebi'
sbt 'run data/chebi/MolePro.ChEBI.sqlite add-connections inchikey data/chebi/ChEBI-inchikey.tsv "ChEBI relations transformer(direction=up)" chebi'
sbt 'run data/chebi/MolePro.ChEBI.sqlite add-connections chebi data/chebi/ChEBI-no-struct-id.tsv "ChEBI relations transformer(direction=up)" chebi'
