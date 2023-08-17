python script/extract_ids.py script/components/bindingdb.sql 
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-transformers'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-structures "BindingBD ligand producer" data/bindingdb/BindingDB-ID.tsv'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-compounds'
sbt 'run data/bindingdb/MolePro.BindingDB.sqlite load-connections bindingdb data/bindingdb/BindingDB-ID.tsv "BindingBD binding transformer"'
