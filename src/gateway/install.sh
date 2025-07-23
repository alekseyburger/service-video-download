#! /bin/bash

docker build . --tag  $DOCKER_ACCOUNT/gateway:latest
docker push  $DOCKER_ACCOUNT/gateway:latest

[ ! -d "./manifests.tmp" ] &&  mkdir ./manifests.tmp/
yaml_list=`ls manifests/`
echo $yaml_list
for file in $yaml_list; do
    envsubst <"./manifests/${file}" >"./manifests.tmp/${file}"
done

kubectl apply -f ./manifests.tmp/
kubectl scale deployment --replicas=1 gateway
