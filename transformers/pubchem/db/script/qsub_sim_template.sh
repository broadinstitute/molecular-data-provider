#!/bin/bash

#$ -cwd
#$ -j y
#$ -l h_vmem=5g
#$ -l h_rt=8:00:00
#$ -o data/sim_script/qsub_{000}.log

source /broad/software/scripts/useuse
reuse Java-1.8
reuse SBT
mkdir data/tmp/{000}
sbt -Djline.terminal=none "run sim-create-db data/tmp/{000}/PubChemSimilarity_{000}.sqlite" 

>>wget -nv -P data/tmp/{000} https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/compound/nbr2d/{file}.gz
>>gunzip data/tmp/{000}/{file}.gz
>>java -Xmx4g -cp target/scala-2.12/pubchem-db-assembly-2.4.0.jar org.broadinstitute.translator.parser.pubchem.PubChem sim-load-neighbors data/tmp/{000}/PubChemSimilarity_{000}.sqlite data/tmp/{000}/{file}
>>rm data/tmp/{000}/{file}

java -Xmx4g -cp target/scala-2.12/pubchem-db-assembly-2.4.0.jar org.broadinstitute.translator.parser.pubchem.PubChem sim-build-indexes data/tmp/{000}/PubChemSimilarity_{000}.sqlite
cp data/tmp/{000}/PubChemSimilarity_{000}.sqlite data/db/similarity/PubChemSimilarity_{000}.sqlite

