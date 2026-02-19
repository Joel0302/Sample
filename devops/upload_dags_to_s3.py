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
            print(f"  --> Deleted folder contents: {prefix}")

# --- SECTION 1: DYNAMIC DELETIONS ---
delete_list_path = "./delete_list.txt"

if os.path.exists(delete_list_path):
    with open(delete_list_path, "r") as f:
        # Use set() to avoid duplicate API calls if multiple files in one folder are marked
        delete_targets = set(line.strip() for line in f if line.strip())

        for target in delete_targets:
            parts = target.split('/')
            # Clean the path for S3 (remove all retd_ markers)
            clean_path = "/".join([p.replace('retd_', '') for p in parts])
            
            if not clean_path.startswith('dags/'):
                clean_path = f"dags/{clean_path}"

            # CHECK: If 'retd_' is in any part of the folder structure
            # OR if the target doesn't look like a file (no dot)
            is_folder_deletion = any(p.startswith('retd_') for p in parts[:-1]) or "." not in parts[-1]

            if is_folder_deletion:
                # If folder was 'sql/retd_omni/file.sql', prefix becomes 'dags/sql/omni/'
                prefix = clean_path if is_folder_deletion and "." not in parts[-1] else "/".join(clean_path.split('/')[:-1]) + "/"
                print(f"Action: Deleting ENTIRE Folder -> {prefix}")
                delete_s3_prefix(s3bucket, prefix)
            else:
                print(f"Action: Deleting Single File -> {clean_path}")
                try:
                    s3_client.delete_object(Bucket=s3bucket, Key=clean_path)
                except Exception as e:
                    print(f"Error: {e}")
        '''
        for target in delete_targets:
            # 1. Clean the path: Remove 'retd_' from any part of the path string
            # e.g., 'sql/retd_omni/file.sql' -> ['sql', 'omni', 'file.sql']
            parts = target.split('/')
            clean_parts = [p.replace('retd_', '') for p in parts]
            clean_path = "/".join(clean_parts)
            
            # 2. Ensure S3 Root: Prepend 'dags/' if missing
            if not clean_path.startswith('dags/'):
                clean_path = f"dags/{clean_path}"

            # 3. Logic: Determine if we delete a specific file or a whole folder
            # If 'retd_' was in a folder name (any part except the last) OR no extension exists
            is_folder = any(p.startswith('retd_') for p in parts[:-1]) or "." not in os.path.basename(target)

            if is_folder:
                prefix = clean_path if clean_path.endswith('/') else f"{clean_path}/"
                print(f"Action: Deleting Folder Prefix -> {prefix}")
                delete_s3_prefix(s3bucket, prefix)
            else:
                print(f"Action: Deleting Single File -> {clean_path}")
                try:
                    s3_client.delete_object(Bucket=s3bucket, Key=clean_path)
                except Exception as e:
                    print(f"  --> Error: {clean_path} not found or: {e}")
        '''   
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
