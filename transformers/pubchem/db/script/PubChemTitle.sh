wget -nv -P data/download/ ftp://ftp.ncbi.nlm.nih.gov/pubchem/Compound/Extras/CID-Title.gz
gunzip data/download/CID-Title.gz
sbt -mem 4096 'run load-titles data/db/PubChem.title.sqlite data/download/CID-Title'
rm data/download/CID-Title
