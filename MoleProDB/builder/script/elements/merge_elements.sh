sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "BiGG gene_reaction transformer" data/bigg/MolePro.BiGG.sqlite bigg'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "BiGG genes transformer" data/bigg/MolePro.BiGG.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "BiGG reactions transformer" data/bigg/MolePro.BiGG.sqlite bigg'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "ChEMBL activities transformer" data/chembl/MolePro.ChEMBL.sqlite uniprot,chembl'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "ChEMBL gene target transformer" data/chembl/MolePro.ChEMBL.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "ChEMBL indication transformer" data/chembl/MolePro.ChEMBL.sqlite mesh'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "ChEMBL mechanism transformer" data/chembl/MolePro.ChEMBL.sqlite uniprot,chembl'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "ChEMBL metabolite transformer" data/chembl/MolePro.ChEMBL.sqlite chembl'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CMAP compound-to-compound expander" data/cmap/MolePro.CMAP.sqlite pubchem'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CMAP compound-to-gene transformer"  data/cmap/MolePro.CMAP.sqlite entrez'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CTD disease associations transformer"   data/ctd/MolePro.CTD.sqlite omim,mesh'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CTD gene interactions transformer"      data/ctd/MolePro.CTD.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CTD go associations transformer"        data/ctd/MolePro.CTD.sqlite go'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CTD pathway associations transformer"   data/ctd/MolePro.CTD.sqlite kegg,reactome'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CTD phenotype interactions transformer" data/ctd/MolePro.CTD.sqlite go'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "CTRP compound-list expander"        data/ctrp/MolePro.CTRP.sqlite entrez'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DGIdb target transformer" data/dgidb/MolePro.DGIdb.sqlite entrez'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugCentral indications transformer" data/drugcentral/MolePro.DrugCentral.sqlite drugcentral'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "GtoPdb target transformer" data/gtopdb/MolePro.GtoPdb.sqlite hgnc'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "HMDB disorders transformer" data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "HMDB locations transformer" data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "HMDB pathways transformer" data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "HMDB target genes transformer" data/hmdb/MolePro.HMDB.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "HMDB target proteins transformer" data/hmdb/MolePro.HMDB.sqlite uniprot'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "MSigDB pathways transformer" data/msigdb/MolePro.MSigDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "Pharos target genes transformer" data/pharos/MolePro.Pharos.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "ProbeMiner chemical interactions transformer" data/probe-miner/MolePro.ProbeMiner.sqlite uniprot'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "Repurposing Hub indication transformer" data/rephub/MolePro.RepHub.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "Repurposing Hub target transformer" data/rephub/MolePro.RepHub.sqlite hgnc'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "RxNorm drug-list producer"            data/rxnorm/MolePro.RxNorm.sqlite rxnorm'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "RxNorm active ingredient transformer" data/rxnorm/MolePro.RxNorm.sqlite rxnorm'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "RxNorm components transformer"        data/rxnorm/MolePro.RxNorm.sqlite rxnorm'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "UNII ingredient-list producer"        data/rxnorm/MolePro.RxNorm.sqlite pubchem,unii'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "SIDER drug producer"           data/sider/MolePro.SIDER.sqlite pubchem'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "SIDER indication transformer"  data/sider/MolePro.SIDER.sqlite umls'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "SIDER side effect transformer" data/sider/MolePro.SIDER.sqlite umls'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "STITCH link transformer" data/stitch/MolePro.STITCH.sqlite ensembl'

