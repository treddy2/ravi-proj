#!/bin/bash

gcloud sql connect myinstance --user=ravindra --password=ravindra

mysql -uravindra -p-h 35.239.29.23 --ssl-ca=ssl/server-ca.pem --ssl-cert=ssl/client-cert.pem --ssl-key=ssl/client-key.pem 


