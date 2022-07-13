#! /usr/bin/bash
source gcp-config.sh

# Enable sqladmin.googleapis.com
gcloud services enable sqladmin.googleapis.com

echo "Step - 1 : sqladmin API enabled successfully"

gcloud sql instances create $DB_SQL_INSTANCE --database-version=$DB_SQL_VERSION --cpu=$DB_SQL_CPU --memory=$DB_SQL_MEMORY --region=$PROJECT_LOCATION --root-password=$DB_SQL_RT_PWD

echo "Step - 2 : Cloud sql instane created successfully"

gcloud sql users create $DB_SQL_USERNAME --instance=$DB_SQL_INSTANCE --password=$DB_SQL_USER_PWD

echo "Step - 3 : Cloud sql user name and password created"

gcloud sql instances patch $DB_SQL_INSTANCE --authorized-networks=$DB_SQL_AUTH_NETWORK

echo "Step - 4 : Network hadd been added to the sql instance, Now application can access Cloud SQL"

#gcloud sql instances describe $DB_SQL_INSTANCE





    

