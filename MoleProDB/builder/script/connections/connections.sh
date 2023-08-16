sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "BiGG gene_reaction transformer" data/bigg/MolePro.BiGG.sqlite bigg'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections bigg    "BiGG genes transformer"         data/bigg/MolePro.BiGG.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections bigg    "BiGG reactions transformer"     data/bigg/MolePro.BiGG.sqlite bigg'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL activities transformer"  data/chembl/MolePro.ChEMBL.sqlite uniprot,chembl'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL gene target transformer" data/chembl/MolePro.ChEMBL.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL indication transformer"  data/chembl/MolePro.ChEMBL.sqlite mesh'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL mechanism transformer"   data/chembl/MolePro.ChEMBL.sqlite uniprot,chembl'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL metabolite transformer"  data/chembl/MolePro.ChEMBL.sqlite chembl'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CMAP compound-to-compound expander" data/cmap/MolePro.CMAP.sqlite pubchem'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CMAP compound-to-gene transformer"  data/cmap/MolePro.CMAP.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "CMAP gene-to-gene expander"         data/cmap/MolePro.CMAP.sqlite entrez'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD disease associations transformer"   data/ctd/MolePro.CTD.sqlite omim,mesh'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD gene interactions transformer"      data/ctd/MolePro.CTD.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD go associations transformer"        data/ctd/MolePro.CTD.sqlite go'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD pathway associations transformer"   data/ctd/MolePro.CTD.sqlite kegg,reactome'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD phenotype interactions transformer" data/ctd/MolePro.CTD.sqlite go'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTRP compound-list expander"          data/ctrp/MolePro.CTRP.sqlite entrez'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "DGIdb target transformer"             data/dgidb/MolePro.DGIdb.sqlite entrez'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections snomed  "DrugCentral indications transformer"  data/drugcentral/MolePro.DrugCentral.sqlite drugcentral'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections gtopdb  "GtoPdb target transformer"            data/gtopdb/MolePro.GtoPdb.sqlite hgnc'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB disorders transformer"       data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB locations transformer"       data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB pathways transformer"        data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB target genes transformer"    data/hmdb/MolePro.HMDB.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB target proteins transformer" data/hmdb/MolePro.HMDB.sqlite uniprot'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "MSigDB pathways transformer"      data/msigdb/MolePro.MSigDB.sqlite'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "Pharos target genes transformer"  data/pharos/MolePro.Pharos.sqlite entrez'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections inchikey "ProbeMiner chemical interactions transformer" data/probe-miner/MolePro.ProbeMiner.sqlite uniprot'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections inchikey "Repurposing Hub indication transformer" data/rephub/MolePro.RepHub.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections inchikey "Repurposing Hub target transformer"     data/rephub/MolePro.RepHub.sqlite hgnc'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections unii     "RxNorm active ingredient transformer" data/rxnorm/MolePro.RxNorm.sqlite rxnorm'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections rxnorm   "RxNorm components transformer"        data/rxnorm/MolePro.RxNorm.sqlite rxnorm'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "SIDER indication transformer"  data/sider/MolePro.SIDER.sqlite umls'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "SIDER side effect transformer" data/sider/MolePro.SIDER.sqlite umls'

sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "STITCH link transformer" data/stitch/MolePro.STITCH.sqlite ensembl'

