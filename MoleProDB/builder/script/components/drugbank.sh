python -u script/extract_ids.py script/components/drugbank.sql
sbt 'run data/drugbank/MolePro.DrugBank.sqlite exec ../schema/MoleProSchema.sql'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite exec ../schema/MoleProPreLoadIndexes.sql'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-transformers'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-structures "DrugBank compound-list producer" data/drugbank/DrugBank-compound-id.tsv'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-compounds'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-elements "DrugBank molecule-list producer" data/drugbank/DrugBank-id.tsv drugbank'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank target genes transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank enzyme genes transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank transporter genes transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank carrier genes transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank target proteins transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank enzyme proteins transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank transporter proteins transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite load-connections drugbank data/drugbank/DrugBank-id.tsv "DrugBank carrier proteins transformer" id'
sbt 'run data/drugbank/MolePro.DrugBank.sqlite exec ../schema/MoleProPostLoadIndexes.sql'
