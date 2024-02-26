sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank target genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank enzyme genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank transporter genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank carrier genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
#
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank target proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank enzyme proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank transporter proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-elements "DrugBank carrier proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
#
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank target genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank enzyme genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank transporter genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank carrier genes transformer" data/drugbank/MolePro.DrugBank.sqlite hgnc'
#
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank target proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank enzyme proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank transporter proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
sbt -mem 4096 'run data/MoleProDB.sqlite merge-connections drugbank "DrugBank carrier proteins transformer" data/drugbank/MolePro.DrugBank.sqlite uniprot'
cp data/MoleProDB.sqlite data/backup/MoleProDB-drugbank-con.sqlite