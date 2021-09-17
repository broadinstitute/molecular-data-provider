#!/bin/bash

export $(egrep -v '^#' .env)

sed -i.bak \
    -e "s/DOCKER_VERSION_VALUE/${BUILD_VERSION}/g" \
    deployment.yaml
rm deployment.yaml.bak

sed -i.bak \
    -e "s/NODE_NORMALIZER_HOSTNAME_VALUE/${NODE_NORMALIZER_HOSTNAME}/g" \
    -e "s/NODE_NORMALIZER_ALB_TAG_VALUE/${NODE_NORMALIZER_ALB_TAG}/g" \
    -e "s/NODE_NORMALIZER_ALB_SG_VALUE/${NODE_NORMALIZER_ALB_SG}/g" \
    -e "s/ENVIRONMENT_TAG_VALUE/${ENVIRONMENT_TAG}/g" \
    ingress.yaml
rm ingress.yaml.bak

kubectl apply -f namespace.yaml
kubectl apply -f deployment.yaml
kubectl apply -f services.yaml
kubectl apply -f ingress.yaml