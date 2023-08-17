sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "BiGG gene_reaction transformer" data/bigg/MolePro.BiGG.sqlite bigg'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections bigg    "BiGG genes transformer"         data/bigg/MolePro.BiGG.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections bigg    "BiGG reactions transformer"     data/bigg/MolePro.BiGG.sqlite bigg'
cp data/MoleProDB.sqlite data/backup/MoleProDB-bigg-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections bindingdb "BindingBD binding transformer" data/bindingdb/MolePro.BindingDB.sqlite uniprot'
cp data/MoleProDB.sqlite data/backup/MoleProDB-bindingdb-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chebi "ChEBI relations transformer" data/chebi/MolePro.ChEBI.sqlite chebi'
cp data/MoleProDB.sqlite data/backup/MoleProDB-chebi-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL activities transformer"  data/chembl/MolePro.ChEMBL.sqlite uniprot,chembl'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL gene target transformer" data/chembl/MolePro.ChEMBL.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL indication transformer"  data/chembl/MolePro.ChEMBL.sqlite mesh'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL mechanism transformer"   data/chembl/MolePro.ChEMBL.sqlite uniprot,chembl'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "ChEMBL metabolite transformer"  data/chembl/MolePro.ChEMBL.sqlite chembl'
cp data/MoleProDB.sqlite data/backup/MoleProDB-chembl-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CMAP compound-to-compound expander" data/cmap/MolePro.CMAP.sqlite pubchem'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CMAP compound-to-gene transformer"  data/cmap/MolePro.CMAP.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "CMAP gene-to-gene expander"         data/cmap/MolePro.CMAP.sqlite entrez'
cp data/MoleProDB.sqlite data/backup/MoleProDB-cmap-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD disease associations transformer"   data/ctd/MolePro.CTD.sqlite omim,mesh'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD gene interactions transformer"      data/ctd/MolePro.CTD.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD go associations transformer"        data/ctd/MolePro.CTD.sqlite go'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD pathway associations transformer"   data/ctd/MolePro.CTD.sqlite kegg,reactome'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTD phenotype interactions transformer" data/ctd/MolePro.CTD.sqlite go'
cp data/MoleProDB.sqlite data/backup/MoleProDB-ctd-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "CTRP compound-list expander"          data/ctrp/MolePro.CTRP.sqlite entrez'
cp data/MoleProDB.sqlite data/backup/MoleProDB-ctrp-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections chembl  "DGIdb target transformer"             data/dgidb/MolePro.DGIdb.sqlite entrez'
cp data/MoleProDB.sqlite data/backup/MoleProDB-dgidb-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections snomed  "DrugCentral indications transformer"  data/drugcentral/MolePro.DrugCentral.sqlite drugcentral'
cp data/MoleProDB.sqlite data/backup/MoleProDB-drugcentral-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections gtopdb  "GtoPdb target transformer"            data/gtopdb/MolePro.GtoPdb.sqlite hgnc'
cp data/MoleProDB.sqlite data/backup/MoleProDB-gtopdb-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB disorders transformer"       data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB locations transformer"       data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB pathways transformer"        data/hmdb/MolePro.HMDB.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB target genes transformer"    data/hmdb/MolePro.HMDB.sqlite entrez'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections hmdb    "HMDB target proteins transformer" data/hmdb/MolePro.HMDB.sqlite uniprot'
cp data/MoleProDB.sqlite data/backup/MoleProDB-hmdb-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "MSigDB pathways transformer"      data/msigdb/MolePro.MSigDB.sqlite'
cp data/MoleProDB.sqlite data/backup/MoleProDB-msigdb-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "PharmGKB relations transformer"             data/pharmgkb/MolePro.PharmGKB.sqlite entrez,pharmgkb'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections entrez  "PharmGKB automated annotations transformer" data/pharmgkb/MolePro.PharmGKB.sqlite entrez,pharmgkb'
cp data/MoleProDB.sqlite data/backup/MoleProDB-pharmgkb-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "Pharos target genes transformer"  data/pharos/MolePro.Pharos.sqlite entrez'
cp data/MoleProDB.sqlite data/backup/MoleProDB-pharos-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections inchikey "ProbeMiner chemical interactions transformer" data/probeminer/MolePro.ProbeMiner.sqlite uniprot'
cp data/MoleProDB.sqlite data/backup/MoleProDB-probe-miner-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections inchikey "Repurposing Hub indication transformer" data/rephub/MolePro.RepHub.sqlite'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections inchikey "Repurposing Hub target transformer"     data/rephub/MolePro.RepHub.sqlite hgnc'
cp data/MoleProDB.sqlite data/backup/MoleProDB-rephub-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections unii     "RxNorm active ingredient transformer" data/rxnorm/MolePro.RxNorm.sqlite rxnorm'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections rxnorm   "RxNorm components transformer"        data/rxnorm/MolePro.RxNorm.sqlite rxnorm'
cp data/MoleProDB.sqlite data/backup/MoleProDB-rxnorm-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "SIDER indication transformer"  data/sider/MolePro.SIDER.sqlite umls'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "SIDER side effect transformer" data/sider/MolePro.SIDER.sqlite umls'
cp data/MoleProDB.sqlite data/backup/MoleProDB-sider-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections pubchem "STITCH link transformer" data/stitch/MolePro.STITCH.sqlite ensembl'
cp data/MoleProDB.sqlite data/backup/MoleProDB-stitch-con.sqlite
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections uniprot "UniProt protein to gene transformer" data/uniprot/MolePro.UniProt.sqlite hgnc'
cp data/MoleProDB.sqlite data/backup/MoleProDB-connections.sqlite
