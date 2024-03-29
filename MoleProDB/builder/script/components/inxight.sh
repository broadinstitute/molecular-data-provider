python -u script/extract_ids.py script/components/inxight.sql
sbt 'run data/inxight/MolePro.InxightDrugs.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/inxight/MolePro.InxightDrugs.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/inxight/MolePro.InxightDrugs.sqlite load-transformers'
sbt 'run data/inxight/MolePro.InxightDrugs.sqlite load-prefixes'
sbt -mem 4096 'run data/inxight/MolePro.InxightDrugs.sqlite load-structures "Inxight:Drugs substance-list producer" data/inxight/InxightDrugs-UNII-chem.tsv'
sbt 'run data/inxight/MolePro.InxightDrugs.sqlite load-compounds'
sbt 'run data/inxight/MolePro.InxightDrugs.sqlite load-elements "Inxight:Drugs substance-list producer" data/inxight/InxightDrugs-UNII.tsv unii'
sbt -mem 4096 'run data/inxight/MolePro.InxightDrugs.sqlite add-connections unii data/inxight/InxightDrugs-UNII-chem.tsv "Inxight:Drugs relationship transformer" unii'
sbt -mem 4096 'run data/inxight/MolePro.InxightDrugs.sqlite add-connections unii data/inxight/InxightDrugs-UNII.tsv "Inxight:Drugs relationship transformer" unii'
sbt 'run data/inxight/MolePro.InxightDrugs.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
