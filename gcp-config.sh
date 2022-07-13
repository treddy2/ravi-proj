# GCP Project Constants Initialization
PROJECT_ID=hcl-gcp-project
PROJECT_LOCATION=us-central1
PROJECT_ZONE=us-central1-c

#CloudBuild Repository Name and Description
REPOSITORY_NAME=hcl-proj-repo
PROJECT_DESCRIPTION=profilescreen-application

#Docker image name
DOCKER_IMAGE_ID=psweb-app
#Docker image tagged-id
DOCKER_IMAGE_ID_VERSION=1.0.0

#Kubernetes cluster name
PSAPP_GKE_CLUSTER_NAME=psweb-app-gke-cluster

#CLoud SQL Initialization
#Database setup
DB_SQL_INSTANCE=hcl-sql-db
DB_SQL_VERSION=MYSQL_5_7
DB_SQL_CPU=2
DB_SQL_MEMORY=4GB
DB_SQL_RT_PWD=ravindra123
#USER ROLE
DB_SQL_USERNAME=ravindra
DB_SQL_USER_PWD=ravindra
# Patching operation, Add network to interact with any http request from web-applications
DB_SQL_AUTH_NETWORK=0.0.0.0/0
