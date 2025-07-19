#! /bin/bash

docker build . --tag  "$DOCKER_ACCOUNT/notification:latest"
docker push  "$DOCKER_ACCOUNT/notification:latest"
kubectl apply -f ./manifests/
kubectl scale deployment --replicas=1 notification
