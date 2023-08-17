python -u script/extract_ids.py script/components/bindingdb.sql 
python script/components/bindingdb.py data/bindingdb/BindingDB-ID-inchikey.tsv data/pubchem/MolePro.PubChem.sqlite > data/bindingdb/BindingDB-ID.tsv
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-transformers'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-prefixes'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-structures "BindingBD ligand producer" data/bindingdb/BindingDB-ID.tsv'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-compounds'
sbt -mem 4096 'run data/bindingdb/MolePro.BindingDB.sqlite load-connections bindingdb data/bindingdb/BindingDB-ID.tsv "BindingBD binding transformer"'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
