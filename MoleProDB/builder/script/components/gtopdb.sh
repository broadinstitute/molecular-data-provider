python -u script/extract_ids.py script/components/gtopdb.sql
sbt 'run data/gtopdb/MolePro.GtoPdb.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/gtopdb/MolePro.GtoPdb.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/gtopdb/MolePro.GtoPdb.sqlite load-transformers'
sbt 'run data/gtopdb/MolePro.GtoPdb.sqlite load-structures "GtoPdb compound-list producer" data/gtopdb/GtoPdb-id.tsv'
sbt 'run data/gtopdb/MolePro.GtoPdb.sqlite load-compounds'
sbt 'run data/gtopdb/MolePro.GtoPdb.sqlite load-connections gtopdb data/gtopdb/GtoPdb-id.tsv "GtoPdb target transformer" hgnc'
sbt 'run data/gtopdb/MolePro.GtoPdb.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
