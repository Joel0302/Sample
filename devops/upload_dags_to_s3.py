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

# Deletion part
delete_list_path = "./delete_list.txt"
if os.path.exists(delete_list_path):
    with open(delete_list_path, "r") as f:
        #cleaning up empty spaces and newline characters
        delete_targets = []  
        for line in f:
            cleaned_line = line.strip()
            if cleaned_line:
                delete_targets.append(cleaned_line)
        for target in delete_targets:
            #Remove the 'retd_' marker from the path segments to find the real S3 path
            parts = target.split('/')
            clean_path = "/".join([p.replace('retd_', '') for p in parts])
            if not clean_path.startswith('dags/'):
                clean_path = f"dags/{clean_path}"
            #Is it a folder or a single file / If there's no dot in the last part, it's a folder
            is_folder = "." not in parts[-1]
            if is_folder:
                #dags/sql/sfmc -> dags/sql/sfmc/
                folder_prefix = clean_path if clean_path.endswith('/') else f"{clean_path}/"                
                print(f"Action: Wiping Directory -> {folder_prefix}")                
                #List all objects in that folder
                response = s3_client.list_objects_v2(Bucket=s3bucket, Prefix=folder_prefix)                
                if 'Contents' in response:
                    delete_keys = [{'Key': obj['Key']} for obj in response['Contents']]
                    s3_client.delete_objects(Bucket=s3bucket, Delete={'Objects': delete_keys})
                    print(f"Successfully cleared contents of: {folder_prefix}")
                else:
                    print(f"Folder {folder_prefix} is already empty")
            else:
                # Example: dags/sql/sfmc/file.sql -> deletes just that file
                print(f"Action: Deleting Single File -> {clean_path}")
                try:
                    s3_client.delete_object(Bucket=s3bucket, Key=clean_path)
                except Exception as e:
                    print(f"Error deleting file {clean_path}: {e}")

#Root DAGs (temp_dags/) 
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
