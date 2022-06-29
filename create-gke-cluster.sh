#! /usr/bin/bash

# create a project
#gcloud projects create PROJECT_ID

#set the project
#gcloud config set project PROJECT_ID

#gcloud auth list
echo "Please authenticate!"

#gcloud config set project hcl-gcp-project
#gcloud config set compute/zone  us-west1-a
#gcloud config set compute/region us-west1

#Clone the  Project from the git repository
#git clone https://github.com/reponame/revi.git
#cd Project root repositroy

export PROJECT_ID=hcl-gcp-project
#Create Docker Images
echo "=============================================="
echo "Step - 2 : Crete Docker Image"
docker build -t gcr.io/${PROJECT_ID}/hcl-psapp:1.0.0 .
echo "Please continue by clicking on autherization button"
echo "Docker image created successfully"
echo "=============================================="
echo "              "
echo "=============================================="
echo "Step - 3 Enable and authentiacte the Container Registry"
gcloud services enable containerregistry.googleapis.com
gcloud auth configure-docker
echo "Enabled and authenticate the Container registry successfully"
echo "=============================================="
echo "              "
echo "=============================================="
echo "Step - 4 : Pushing images to Container Registry"
docker push gcr.io/${PROJECT_ID}/hcl-psapp:1.0.0
echo "Image pushed to containter registry successfully"
echo "=============================================="
echo "              "
echo "=============================================="
echo "Step - 5 : Create Kuberneties Cluster"
gcloud container clusters create hcl-psapp-cluster --num-nodes=1 --zone=us-west1-a
echo "Cluster is being creted Please wait........."
echo "Kuberneties cluster is created Successfully"
echo "=============================================="
echo "              "
echo "Step - 6 : Get the authentication credentials to interact with cluster"
gcloud container clusters get-credentials hcl-psapp-cluster --zone=us-west1-a
echo "Kubectl - configured successfully to use the cluster"
echo "=============================================="
echo "              "
echo "=============================================="
echo "Step - 7 : Create a deployment"
kubectl create deployment hcl-psapp-server --image=gcr.io/${PROJECT_ID}/hcl-psapp:1.0.0
echo "Deployement created successfully"
echo "=============================================="
echo "              "
echo "=============================================="
echo "Step - 8 : Expose the deployment"
kubectl expose deployment hcl-psapp-server --type LoadBalancer --port 80 --target-port 8080
echo "Application exposed successfully"
echo "============================================="
echo "              "
echo "============================================="
echo "Step - 9 :Inspect and view the application"
kubectl get pods
echo "Nodes are listed successfully "
echo "             "
echo "Copy the External IP Address and paste in browser"
kubectl get service hcl-psapp-server


