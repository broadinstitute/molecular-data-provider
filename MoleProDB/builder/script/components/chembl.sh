python -u script/extract_ids.py script/components/chembl_ids.sql 
sbt 'run data/chembl/MolePro.ChEMBL.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/chembl/MolePro.ChEMBL.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/chembl/MolePro.ChEMBL.sqlite load-transformers'
sbt 'run data/chembl/MolePro.ChEMBL.sqlite load-prefixes'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/ChEMBL-ID.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/Pharos-ChEMBL_ID.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/ChEBI-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/ChemBank-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/DrugBank-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/DrugCentral-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/GtoPdb-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/HMDB-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/ProbeMiner-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/PubChem-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/RepHub-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-structures "ChEMBL compound-list producer" data/chembl/UNII-inchikey.tsv'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-compounds'
cp data/chembl/MolePro.ChEMBL.sqlite data/chembl/MolePro.ChEMBL.compounds.sqlite
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-elements "ChEMBL compound-list producer" data/chembl/ChEMBL-ID.tsv chembl'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-elements "SRI node normalizer producer(category=Gene)" data/chembl/ChEMBL-gene-id.tsv ensembl'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-elements "SRI node normalizer producer(category=Disease,category=PhenotypicFeature)" data/chembl/ChEMBL-disease-id.tsv mesh'
cp data/chembl/MolePro.ChEMBL.sqlite data/chembl/MolePro.ChEMBL.elements.sqlite
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite add-connections chembl data/chembl/ChEMBL-ID.tsv "ChEMBL metabolite transformer" chembl'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite add-connections chembl data/chembl/ChEMBL-ID.tsv "ChEMBL gene target transformer" ensembl'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-connections chembl data/chembl/ChEMBL-ID.tsv "ChEMBL indication transformer" mesh'
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-connections chembl data/chembl/ChEMBL-ID.tsv "ChEMBL mechanism transformer" chembl'
cp data/chembl/MolePro.ChEMBL.sqlite data/chembl/MolePro.ChEMBL.activities.sqlite
sbt -mem 4096 'run data/chembl/MolePro.ChEMBL.sqlite load-connections chembl data/chembl/ChEMBL-ID.tsv "ChEMBL activities transformer" chembl'
cp data/chembl/MolePro.ChEMBL.sqlite data/chembl/MolePro.ChEMBL.preIndexes.sqlite
sbt 'run data/chembl/MolePro.ChEMBL.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
