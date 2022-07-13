#! /usr/bin/bash
source gcp-config.sh

# docker build --tag hcl-webapp:1.0.0 . # 1.uncomment the line if you want to build docker image

# docker run --name hcl-webapp -p 8000:8000 hcl-webapp:1.0.0 # 2.uncomment the line if you want to build docker image

# Note : Cloud Build API should be enabled and Artifact Registry API


# Project Constants
#PROJECT_ID=hcl-gcp-project
#PROJECT_LOCATION=us-central1
#PROJECT_ZONE=us-central1-c
#REPOSITORY_NAME=hcl-proj-repo
#PROJECT_DESCRIPTION=profilescreen-application
#DOCKER_IMAGE_ID=psweb-app
#DOCKER_IMAGE_ID_VERSION=1.0.0
#PSAPP_GKE_CLUSTER_NAME=psweb-app-gke-cluster

#1) Note: enable  artifactregistry.googleapis.com and cloud buil API
#create artifact
#you will store your container in Artifact Registry and deploy it to your cluster from the registry. Run the following command to create a repository named hello-repo in the same region as your cluster:
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create $REPOSITORY_NAME --project=$PROJECT_ID --repository-format=docker --location=$PROJECT_LOCATION --description=$PROJECT_DESCRIPTION
echo "Step - 1 : Artifacts created successfully {Artifact Name : $REPOSITORY_NAME}"
#Build your container image using Cloud Build, which is similar to running docker build and docker push, but the build happens on Google Cloud:
gcloud builds submit --tag $PROJECT_LOCATION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$DOCKER_IMAGE_ID .
echo "Step - 2 : Image created in Google cloud successfully using cloud build"
#  ========or use below===========
# 2) Note: enable container registry API
#Create docker image and then push code to the container registry
docker build -t gcr.io/$PROJECT_ID/$DOCKER_IMAGE_ID:$DOCKER_IMAGE_ID_VERSION .
echo "Step - 3 : Docker image created in local repository using Docker"
docker run --publish 8080:8080 $DOCKER_IMAGE_ID:$DOCKER_IMAGE_ID_VERSION
echo "Step - 4 : Image running in the container"
gcloud services enable containerregistry.googleapis.com
gcloud auth configure-docker
echo "Step - 5 : Successfully enabled container-registry API and authenticated to docker configure"
docker push gcr.io/$PROJECT_ID/$DOCKER_IMAGE_ID:$DOCKER_IMAGE_ID_VERSION
echo "Step - 6 : Successsfully pushed image to google-cloud-container registry"
gcloud container clusters create $PSAPP_GKE_CLUSTER_NAME --num-nodes 3 --zone $PROJECT_ZONE
echo "Step - 7 : Successfully Kuberneties Cluster created"
kubectl apply -f deployment.yaml
echo "Step - 8 : Successfully deployed the application in Kuberneties Cluster"
kubectl apply -f service.yaml
echo "Step - 9 : services are defined and ready to access application"
kubectl get services
echo "Step - 10 : Services enabled, copy the external-Ip and preview deployed application in Browser"






