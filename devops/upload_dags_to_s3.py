from posixpath import dirname
import boto3
import os
import sys
from botocore.exceptions import ClientError

# Add temp_dags to path if needed for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../temp_dags"))

# Credentials from Environment Variables
key = os.environ.get("AWS_ACCESS_KEY_ID")
pwd = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3bucket = os.environ.get("AWS_S3_BUCKET")

# Initialize S3 Client
s3_client = boto3.client("s3", region_name="us-east-1", aws_access_key_id=key, aws_secret_access_key=pwd)

# --- SECTION 1: UPLOADS ---

# 1. Root DAGs (temp_dags/)
directory = "temp_dags"
if os.path.exists(directory):
    for filename in os.listdir(directory):
        # We skip retd_ files so the 'marker' isn't uploaded as a new file
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
                # Calculate S3 key by removing the local temp path
                filekey = f.replace("temp_dags/sql", "")
                print(f"Uploading sql file: {f} to Key: dags/sql{filekey}")
                s3_client.upload_file(f, s3bucket, "dags/sql" + filekey)
            except Exception as e:
                print(f"Error uploading {file}: {e}")

def delete_s3_prefix(bucket, prefix):
    """Deletes all objects in S3 starting with the given prefix (folder)."""
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    for page in pages:
        if 'Contents' in page:
            delete_keys = [{'Key': obj['Key']} for obj in page['Contents']]
            s3_client.delete_objects(Bucket=bucket, Delete={'Objects': delete_keys})
            print(f"Deleted batch of files from: {prefix}")

# --- UPDATED DELETION PROCESS ---
if os.path.exists(delete_list_path):
    with open(delete_list_path, "r") as f:
        delete_targets = set(line.strip() for line in f if line.strip())
        
        for target in delete_targets:
            # If it looks like a file (has an extension), delete normally
            if "." in os.path.basename(target):
                s3_client.delete_object(Bucket=s3bucket, Key=target)
            else:
                # If it's a folder, delete everything inside
                # Ensure folder prefix ends with /
                folder_prefix = target if target.endswith('/') else target + '/'
                delete_s3_prefix(s3bucket, folder_prefix)
'''
delete_list_path = "./delete_list.txt" 
if os.path.exists(delete_list_path):
    print("--- Starting S3 Deletion Process ---")
    with open(delete_list_path, "r") as f:
        # Using set() to avoid deleting the same file twice if it appeared multiple times
        delete_keys = set(line.strip() for line in f if line.strip())
        
        for target_key in delete_keys:
            try:
                # This deletes the specific file key from S3
                s3_client.delete_object(Bucket=s3bucket, Key=target_key)
                print(f"Successfully deleted from S3: {target_key}")
            except Exception as e:
                print(f"Delete failed for {target_key}: {e}")                

# --- SECTION 2: DELETIONS ---
delete_list_path = "./delete_list.txt"
if os.path.exists(delete_list_path):
    print("--- Starting S3 Deletion Process ---")
    with open(delete_list_path, "r") as f:
        for line in f:
            target_key = line.strip()
            if target_key:
                try:
                    s3_client.delete_object(Bucket=s3bucket, Key=target_key)
                    print(f"Successfully deleted from S3: {target_key}")
                except Exception as e:
                    print(f"Delete failed for {target_key}: {e}")
else:
    print("No delete_list.txt found. Skipping deletions.")
'''

