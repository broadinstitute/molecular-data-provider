#!/bin/bash

set -e

kubectl apply -f namespace.yaml

if [ $PLATERS == "all" ]
then
    platers_list=`ls -l translator-ops/config/sri/plater/ | awk '{print $NF}' | awk -F"." '{print $1}' | sed 's/^.......//' | awk NF | awk '(NR>1)'`
    echo "The following platers will be deployed: $platers_list"
    for plater in $platers_list
    do
        echo "------ Install/Delete Plater $plater beginning ------"
        values_file="plater-$plater.yaml"
        cp translator-ops/config/sri/plater/$values_file ./
        cp translator-ops/ops/sri/plater/deploy/image-value.yaml ./
        
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
            echo "helm install $plater"
            helm upgrade --install -n sri -f $values_file -f image-value.yaml $plater .
            echo "------ Install Plater $plater end ------"
        else
            echo "helm delete $plater"
            helm delete -n sri $plater
            echo "------ Delete Plater $plater end ------"
        fi
    done
else
    echo "------ Install/Delete Plater $PLATERS beginning ------"
    values_file="plater-$PLATERS.yaml"
    cp translator-ops/config/sri/plater/$values_file ./
    cp translator-ops/ops/sri/plater/deploy/image-value.yaml ./
    
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
        echo "helm install $PLATERS"
        helm upgrade --install -n sri -f $values_file -f image-value.yaml $PLATERS .
        echo "------ Install Plater $PLATERS end ------"
    else
        echo "helm delete $PLATERS"
        helm delete -n sri $PLATERS
        echo "------ Delete Plater $PLATERS end ------"
    fi
fi