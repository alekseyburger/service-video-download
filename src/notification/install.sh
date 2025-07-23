#! /bin/bash

docker build . --tag  "$DOCKER_ACCOUNT/notification:latest"
docker push  "$DOCKER_ACCOUNT/notification:latest"
cd ./manifests/
envsubst <notification-deploy.yaml | kubectl apply -f -
kubectl scale deployment --replicas=1 notification
