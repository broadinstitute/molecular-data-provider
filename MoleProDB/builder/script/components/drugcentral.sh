python -u script/extract_ids.py script/components/drugcentral.sql
sbt 'run data/drugcentral/MolePro.DrugCentral.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/drugcentral/MolePro.DrugCentral.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/drugcentral/MolePro.DrugCentral.sqlite load-transformers'
sbt -mem 4096 'run data/drugcentral/MolePro.DrugCentral.sqlite load-structures "DrugCentral compounds producer" data/drugcentral/DrugCentral-ID.tsv'
sbt 'run data/drugcentral/MolePro.DrugCentral.sqlite load-compounds'
sbt -mem 4096 'run data/drugcentral/MolePro.DrugCentral.sqlite load-elements "SRI node normalizer producer(category=Disease,category=PhenotypicFeature)" data/drugcentral/DrugCentral-SNOMED.tsv snomed'
sbt -mem 4096 'run data/drugcentral/MolePro.DrugCentral.sqlite add-connections snomed data/drugcentral/DrugCentral-SNOMED.tsv "DrugCentral indications transformer" drugcentral'
sbt 'run data/drugcentral/MolePro.DrugCentral.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
