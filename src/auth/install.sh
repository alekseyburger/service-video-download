#! /bin/bash

docker build . --tag  $DOCKER_ACCOUNT/auth:latest
docker push  $DOCKER_ACCOUNT/auth:latest
kubectl apply -f ./manifests/
kubectl scale deployment --replicas=1 auth
