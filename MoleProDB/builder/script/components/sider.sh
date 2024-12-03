python script/extract_ids.py script/components/sider.sql 
sbt 'run data/sider/MolePro.SIDER.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/sider/MolePro.SIDER.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/sider/MolePro.SIDER.sqlite load-transformers'
sbt 'run data/sider/MolePro.SIDER.sqlite load-prefixes'
sbt 'run data/sider/MolePro.SIDER.sqlite load-structures "Pubchem compound-list producer" data/sider/SIDER-CID.tsv'
sbt 'run data/sider/MolePro.SIDER.sqlite load-compounds'
sbt 'run data/sider/MolePro.SIDER.sqlite load-elements "SIDER drug producer" data/sider/SIDER-CID.tsv pubchem'
sbt -mem 4096 'run data/sider/MolePro.SIDER.sqlite load-elements "SRI node normalizer producer" data/sider/SIDER-UMLS.tsv umls'
sbt -mem 16384 'run data/sider/MolePro.SIDER.sqlite load-connections pubchem data/sider/SIDER-CID.tsv "SIDER side effect transformer" umls'
sbt -mem 4096 'run data/sider/MolePro.SIDER.sqlite load-connections pubchem data/sider/SIDER-CID.tsv "SIDER indication transformer" umls'
sbt 'run data/sider/MolePro.SIDER.sqlite exec ../schema/MoleProPostLoadIndexes.sql'