python script/extract_ids.py script/components/uniprot.sql 
sbt 'run data/uniprot/MolePro.UniProt.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/uniprot/MolePro.UniProt.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/uniprot/MolePro.UniProt.sqlite load-transformers'
sbt 'run data/uniprot/MolePro.UniProt.sqlite load-prefixes'
sbt -mem 4096 'run data/uniprot/MolePro.UniProt.sqlite load-elements "UniProt protein-list producer" data/uniprot/UniProtKB.tsv'
sbt -mem 4096 'run data/uniprot/MolePro.UniProt.sqlite load-connections uniprot data/uniprot/UniProtKB.tsv "UniProt protein to gene transformer" id'
