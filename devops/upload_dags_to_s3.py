from posixpath import dirname
import boto3
import os
import sys
from botocore.exceptions import ClientError

# Credentials from Environment Variables
key = os.environ.get("AWS_ACCESS_KEY_ID")
pwd = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3bucket = os.environ.get("AWS_S3_BUCKET")

# Initialize S3 Client
s3_client = boto3.client("s3", region_name="us-east-1", aws_access_key_id=key, aws_secret_access_key=pwd)

def delete_s3_prefix(bucket, prefix):
    """Deletes all objects in S3 starting with the given prefix (folder)."""
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    for page in pages:
        if 'Contents' in page:
            delete_keys = [{'Key': obj['Key']} for obj in page['Contents']]
            s3_client.delete_objects(Bucket=bucket, Delete={'Objects': delete_keys})
            print(f"Deleted folder contents: {prefix}")

# --- SECTION 1: DELETIONS (Run this FIRST) ---
delete_list_path = "./delete_list.txt"

if os.path.exists(delete_list_path):
    with open(delete_list_path, "r") as f:
        # Use set() to avoid deleting the same thing twice
        delete_targets = set(line.strip() for line in f if line.strip())
        
        for target in delete_targets:
            # LOGIC: If target has a dot in the filename, it's a file. Otherwise, it's a folder.
            if "." in os.path.basename(target):
                print(f"Deleting file: {target}")
                try:
                    s3_client.delete_object(Bucket=s3bucket, Key=target)
                except Exception as e:
                    print(f"File {target} not found or error: {e}")
            else:
                # It's a folder: ensure it ends with / for S3 prefix matching
                prefix = target if target.endswith('/') else target + '/'
                print(f"Deleting folder prefix: {prefix}")
                delete_s3_prefix(s3bucket, prefix)

# --- SECTION 2: UPLOADS ---

# 1. Root DAGs (temp_dags/)
directory = "temp_dags"
if os.path.exists(directory):
    for filename in os.listdir(directory):
        if filename.startswith("retd_"):
            continue
            
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            try:
                print(f"Uploading root file: {f}")
                s3_client.upload_file(f, s3bucket, "dags/" + filename)
            except Exception as e:
                print(f"Error uploading {filename}: {e}")

# 2. Utils (temp_dags/utils/)
directory = "temp_dags/utils"
if os.path.exists(directory):
    for filename in os.listdir(directory):
        if filename.startswith("retd_"):
            continue
            
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            try:
                print(f"Uploading utils file: {f}")
                s3_client.upload_file(f, s3bucket, "dags/utils/" + filename)
            except Exception as e:
                print(f"Error uploading {filename}: {e}")

# 3. SQL (temp_dags/sql/ - Recursive)
directory = "temp_dags/sql"
if os.path.exists(directory):
    for root, sub_dirs, filenames in os.walk(directory):
        for file in filenames:
            if file.startswith("retd_"):
                continue
                
            f = os.path.join(root, file)
            try:
                # This logic correctly maps temp_dags/sql/folder/file -> dags/sql/folder/file
                filekey = f.replace("temp_dags/sql/", "") # Added / to avoid double slashes
                print(f"Uploading sql file: {f} to Key: dags/sql/{filekey}")
                s3_client.upload_file(f, s3bucket, "dags/sql/" + filekey)
            except Exception as e:
                print(f"Error uploading {file}: {e}")
