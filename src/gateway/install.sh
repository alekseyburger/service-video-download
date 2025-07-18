#! /bin/bash

docker build . --tag  $DOCKER_ACCOUNT/gateway:latest
docker push  $DOCKER_ACCOUNT/gateway:latest
kubectl apply -f ./manifests/
kubectl scale deployment --replicas=1 gateway
