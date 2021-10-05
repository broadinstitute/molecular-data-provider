#!/bin/bash

set -e

kubectl apply -f namespace.yaml

if [ $TRANSFORMERS == "all" ]
then
    transformers_list=`ls -l translator-ops/config/molepro/transformers/ | awk '{print $NF}' | awk -F"." '{print $1}' | sed 's/^.......//' | awk NF | awk '(NR>1)'`
    echo "The following transformers will be deployed: $transformers_list"
    for transformer in $transformers_list
    do
        echo "------ Install/Delete Transformer $transformer beginning ------"
        values_file="molepro-$transformer.yaml"
        cp translator-ops/config/molepro/$values_file ./
        # update domain to translator ci domain
        sed -i.bak 's/automat.renci.org/automat.ci.transltr.io/g' $values_file
        rm $values_file.bak
        
        if [ $LOAD_DATA == "no" ]
        then
            echo "install in no data load mode"
            sed -i.bak '/dataUrl/d' $values_file
            rm $values_file.bak
        fi
        
        if [ $ACTION == "install" ]
        then
            echo "helm install $transformer"
            helm upgrade --install -n molepro -f $values_file $transformer .
            echo "------ Install Plater $transformer end ------"
        else
            echo "helm delete $plater"
            helm delete -n molepro $transformer
            echo "------ Delete Plater $transformer end ------"
        fi
    done
else
    echo "------ Install/Delete Transformer $TRANSFORMERS beginning ------"
    values_file="molepro-$TRANSFORMERS.yaml"
    cp translator-ops/config/molepro/$values_file ./
    # update domain to translator ci domain
    sed -i.bak 's/automat.renci.org/automat.ci.transltr.io/g' $values_file
    rm $values_file.bak
    
    if [ $LOAD_DATA == "no" ]
    then
        echo "install in no data load mode"
        sed -i.bak '/dataUrl/d' $values_file
        rm $values_file.bak
    fi
    
    if [ $ACTION == "install" ]
    then
        echo "helm install $TRANSFORMERS"
        helm upgrade --install -n molepro -f $values_file $TRANSFORMERS .
        echo "------ Install Plater $PLATERS end ------"
    else
        echo "helm delete $TRANSFORMERS"
        helm delete -n molepro $TRANSFORMERS
        echo "------ Delete Plater $TRANSFORMERS end ------"
    fi
fi