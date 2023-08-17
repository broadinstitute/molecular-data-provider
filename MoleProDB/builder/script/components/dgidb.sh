python -u script/extract_ids.py script/components/dgidb.sql
sbt 'run data/dgidb/MolePro.DGIdb.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/dgidb/MolePro.DGIdb.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/dgidb/MolePro.DGIdb.sqlite load-transformers'
sbt 'run data/dgidb/MolePro.DGIdb.sqlite load-structures "ChEMBL compound-list producer" data/dgidb/DGIdb-chembl-id.tsv'
sbt 'run data/dgidb/MolePro.DGIdb.sqlite load-structures "DGIdb compound-list producer" data/dgidb/DGIdb-name.tsv'
sbt 'run data/dgidb/MolePro.DGIdb.sqlite load-compounds'
sbt 'run data/dgidb/MolePro.DGIdb.sqlite load-connections chembl data/dgidb/DGIdb-chembl-id.tsv "DGIdb target transformer" id'
sbt 'run data/dgidb/MolePro.DGIdb.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
