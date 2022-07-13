#! /usr/bin/bash
source gcp-config.sh

#PROJECT_ID=hcl-gcp-project
#PROJECT_LOCATION=us-central1
#PROJECT_ZONE=us-central1-a
#REPOSITORY_NAME=hcl-proj-repo
#PROJECT_DESCRIPTION=HCL psapp Docker repository
#DOCKER_IMAGE_ID=psweb-app
#DOCKER_IMAGE_ID_VERSION=1.0.0
#PSAPP_GKE_CLUSTER_NAME=psweb-app-gke-cluster

#Delete the kuberneties cluster
gcloud container clusters delete $PSAPP_GKE_CLUSTER_NAME --zone=$PROJECT_ZONE
echo "Step -1 : Kuberneties cluster deleted"
#Delete the artifacts from the artifacts registry
gcloud artifacts docker images delete $PROJECT_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$DOCKER_IMAGE_ID
echo "Step -2 : Artifacts deleted "
docker images
docker rm $(docker stop $(docker ps -aq)) 
echo "Stopeed and Deleted all containers and images"
#docker rmi image


