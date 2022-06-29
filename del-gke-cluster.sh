#! /usr/bin/bash
kubectl delete service hcl-psapp-server
gcloud container clusters delete hcl-psapp-cluster --zone=us-west1-a
docker images
#docker rmi image
