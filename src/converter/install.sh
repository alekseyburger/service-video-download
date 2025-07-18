#! /bin/bash

docker build . --tag  $DOCKER_ACCOUNT/converter:latest
docker push  $DOCKER_ACCOUNT/converter:latest
kubectl apply -f ./manifests/
kubectl scale deployment --replicas=1 converter
