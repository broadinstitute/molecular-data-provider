sbt 'run data/MoleProDB.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/MoleProDB.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/MoleProDB.sqlite load-transformers'
sbt 'run data/MoleProDB.sqlite load-prefixes'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "Pubchem compound-list producer" data/pubchem/MolePro.PubChem.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-pubchem.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "Pubchem compound-list producer" data/sider/MolePro.SIDER.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-sider.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "Pubchem compound-list producer" data/stitch/MolePro.STITCH.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-stitch.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "ChEMBL compound-list producer" data/chembl/MolePro.ChEMBL.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-chembl.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "ChEBI compound-list producer" data/chebi/MolePro.ChEBI.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-chebi.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "HMDB metabolite producer" data/hmdb/MolePro.HMDB.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-hmdb.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "DrugBank compound-list producer" data/drugbank/MolePro.DrugBank.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-drugbank.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "DrugCentral compounds producer" data/drugcentral/MolePro.DrugCentral.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-drugcentral.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "GtoPdb compound-list producer" data/gtopdb/MolePro.GtoPdb.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-gtopdb.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "ChemBank compound-list producer" data/chembank/MolePro.ChemBank.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-chembank.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "Repurposing Hub compound-list producer" data/rephub/MolePro.RepHub.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-rephub.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "ProbeMiner compound-list producer" data/probe-miner/MolePro.ProbeMiner.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-probe.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "DGIdb compound-list producer" data/dgidb/MolePro.DGIdb.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-dgidb.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "BiGG compound-list producer" data/bigg/MolePro.BiGG.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-bigg.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "RxNorm compound-list producer" data/rxnorm/MolePro.RxNorm.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-rxnorm.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "Pubchem compound-list producer" data/ctd/MolePro.CTD.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-ctd.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "BindingBD ligand producer" data/bindingdb/MolePro.BindingDB.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-bindingdb.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-structures "SRI node normalizer producer" data/ctd/MolePro.CTD.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-structures.sqlite

sbt -mem 4096 'run data/MoleProDB.sqlite load-compounds'
cp data/MoleProDB.sqlite data/backup/MoleProDB-compounds.sqlite
