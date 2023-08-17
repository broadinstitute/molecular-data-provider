python -u script/extract_ids.py script/components/ctd.sql 
sbt 'run data/ctd/MolePro.CTD.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/ctd/MolePro.CTD.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/ctd/MolePro.CTD.sqlite load-transformers'
sbt 'run data/ctd/MolePro.CTD.sqlite load-prefixes'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-structures "Pubchem compound-list producer" data/ctd/CTD-chem-CID.tsv'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-structures "CTD compound-list producer" data/ctd/CTD-chem-CID.tsv'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-compounds'
cp data/ctd/MolePro.CTD.sqlite data/ctd/MolePro.CTD.compounds.sqlite
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-elements "CTD compound-list producer" data/ctd/CTD-chem-MeSH-ID.tsv pubchem,mesh'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-elements "SRI node normalizer producer(category=Disease,category=PhenotypicFeature)" data/ctd/CTD-disease-ID.tsv id'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-elements "SRI node normalizer producer(category=Gene)" data/ctd/CTD-gene-ID.tsv entrez'
cp data/ctd/MolePro.CTD.sqlite data/ctd/MolePro.CTD.entities.sqlite
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite add-connections mesh data/ctd/CTD-gene-int-ID.tsv "CTD gene interactions transformer" entrez'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite add-connections mesh data/ctd/CTD-chem-MeSH-ID.tsv "CTD disease associations transformer" omim,mesh'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-connections mesh data/ctd/CTD-chem-MeSH-ID.tsv "CTD go associations transformer" go'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-connections mesh data/ctd/CTD-chem-MeSH-ID.tsv "CTD pathway associations transformer" id'
sbt -mem 4096 'run data/ctd/MolePro.CTD.sqlite load-connections mesh data/ctd/CTD-chem-MeSH-ID.tsv "CTD phenotype interactions transformer" go'
sbt 'run data/ctd/MolePro.CTD.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
