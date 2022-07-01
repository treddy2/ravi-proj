import os
import stat
import tempfile

from google.cloud import storage, bigquery


def gcp_config():
    #storage_client = storage.Client.from_service_account_json('gcp-serviceaccounts/psapp-309910-key.json')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "gcp-serviceaccounts/psapp.json"
    #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_file


#def gcp_strg_client(key_file):
def gcp_strg_client():
    gcp_config()
    storage_client = storage.Client()
    return storage_client


def gcp_strg_bucket_list():
    z = []
    x = gcp_strg_client()
    bucket_list = x.list_buckets()
    for y in bucket_list:
        z.append(y.name)
    return z


def upload_files_gcp(source_files,profiles_bucket):
    b = []
    storage_client = gcp_strg_client()
    bucket = storage_client.bucket(profiles_bucket)
    for y in source_files:
        try:
            alterd_filename = altered_filename(y)
            blob = bucket.blob(alterd_filename)
            blob.upload_from_filename(y)
        except FileNotFoundError:
            print("File doesn't exist")
    blob_list = storage_client.list_blobs(profiles_bucket)
    for a in blob_list:
        b.append(a.name)
    return b



#Listing the screened files from the storage
def download_files_gcp(technologies,bucket_name):

    #destination_file_name = os.path.join("C:\\", "Ravindra", "Java", )
    destination_file_name = os.path.join(os.getcwd(),technologies)
    if not os.path.exists(destination_file_name):
        os.mkdir(destination_file_name)
    storage_client = gcp_strg_client()
    for files_list in storage_client.list_blobs(bucket_name):
        dest_filename = os.path.join(destination_file_name, files_list.name)
        files_list.download_to_filename(dest_filename)

def ddfle(bucket_name):
    filesselected = []
    temp_dir_name = tempfile.TemporaryDirectory(prefix="upload_files_", dir=os.getcwd())
    upld_files = os.path.join(temp_dir_name.name)
    destination_file_name = os.path.join(os.getcwd(), upld_files)
    storage_client = gcp_strg_client()
    for file_nme in storage_client.list_blobs(bucket_name):
        #print(file_nme)
        dest_filename = os.path.join(destination_file_name, file_nme.name)
        print(dest_filename)
        file_nme.download_to_filename(dest_filename)
        filesselected.append(dest_filename)
    print("return values--",filesselected)
    return filesselected

#ddfle("psapp_profiles")

def get_storage_files(staging_bucket):
    if not len(str(staging_bucket).strip()):
        return []
    storage_buckets_list = []
    storage_files_list = []
    storage_client = gcp_strg_client()
    for x in storage_client.list_buckets():
        storage_buckets_list.append(x.name)
    if staging_bucket in storage_buckets_list:
        for files_list in storage_client.list_blobs(staging_bucket):
            storage_files_list.append(files_list.name)
        return storage_files_list
    else:
        return []


def altered_filename(source_file):
    x = ""
    docx_format = source_file.endswith(".docx")
    pdf_format = source_file.endswith(".pdf")
    if docx_format is True or pdf_format is True:
        docx_list = source_file.split("/")
        x = docx_list[-1]
    return x


def query_stackoverflow():
    gcp_config()
    client = bigquery.Client()
    query_job = client.query(
        """
        SELECT
          CONCAT(
            'https://stackoverflow.com/questions/',
            CAST(id as STRING)) as url,
          view_count
        FROM `bigquery-public-data.stackoverflow.posts_questions`
        WHERE tags like '%google-bigquery%'
        ORDER BY view_count DESC
        LIMIT 10"""
    )

    results = query_job.result()  # Waits for job to complete.

    for row in results:
        print("{} : {} views".format(row.url, row.view_count))


"""
create table H_USER_TAB(FIRST_NAME varchar(70),LAST_NAME varchar(70),
MAIL_ID varchar(210) NOT NULL PRIMARY KEY,
H_PASSWORD varchar(70),H_ADDRESS varchar(210),
H_COUNTRY varchar(70),MOBILE_NUMBER varchar(70),
USER_ROLE varchar(50),CREATED_DATE varchar(70),MODIFIED_DATE varchar(70));"""


def ps_user_insrt():
    stg, bq = gcp_strg_client()
    schema = [
        bigquery.SchemaField("FIRST_NAME", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("LAST_NAME", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("MAIL_ID", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("H_PASSWORD", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("H_ADDRESS", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("H_COUNTRY", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("MOBILE_NUMBER", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("USER_ROLE", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("CREATED_DATE", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("MODIFIED_DATE", "STRING", mode="REQUIRED"),
    ]
    table = bigquery.Table("hcl-gcp-project.psapp.psapp_user_table", schema=schema)
    table = bq.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )


"""create table H_TECHNOLOGIES(TECH_NAME varchar(225) NOT NULL PRIMARY KEY,
TECH_SUBAREAS text,CREATED_DATE varchar(70),MODIFIED_DATE varchar(70));"""


def ps_tech_insrt():
    stg, bq = gcp_strg_client()
    schema = [
        bigquery.SchemaField("TECH_NAME", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("TECH_SUBAREAS", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("CREATED_DATE", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("MODIFIED_DATE", "STRING", mode="REQUIRED"),
    ]
    table = bigquery.Table("hcl-gcp-project.psapp.psapp_technologies_table", schema=schema)
    table = bq.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )


"""create table MNCS_COMPANIES(MNCS_TYPE varchar(225) NOT NULL PRIMARY KEY,
MNCS_NAME text,CREATED_DATE varchar(70),MODIFIED_DATE varchar(70));"""


def ps_mncs_insrt():
    stg, bq = gcp_strg_client()
    schema = [
        bigquery.SchemaField("MNCS_TYPE", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("MNCS_NAME", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("CREATED_DATE", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("MODIFIED_DATE", "STRING", mode="REQUIRED"),
    ]
    table = bigquery.Table("hcl-gcp-project.psapp.psapp_mncs_table", schema=schema)
    table = bq.create_table(table)  # Make an API request.
    print(
        "Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id)
    )

# ps_mncs_insrt()
# gcp_strg_upload_files(source_files)
