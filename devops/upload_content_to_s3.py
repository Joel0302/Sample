import boto3
import os
import sys
from botocore.exceptions import ClientError

# Configuration from Environment
key = os.environ.get("AWS_ACCESS_KEY_ID")
pwd = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3bucket = os.environ.get("AWS_S3_BUCKET")
region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

s3_client = boto3.client("s3", region_name=region, aws_access_key_id=key, aws_secret_access_key=pwd)

def upload_folder(directory, s3_prefix):
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist, skipping.")
        return

    # For dags (top level) and utils
    if s3_prefix != "dags/sql/":
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                target_key = s3_prefix + filename
                try:
                    print(f"Uploading {f} to {target_key}")
                    s3_client.upload_file(f, s3bucket, target_key)
                except Exception as e:
                    print(f"Error: {e}")
    
    # For SQL (handles subdirectories)
    else:
        for root, dirs, files in os.walk(directory):
            for file in files:
                f = os.path.join(root, file)
                # Calculate relative path to maintain folder structure in S3
                relative_path = os.path.relpath(f, directory)
                target_key = s3_prefix + relative_path
                try:
                    print(f"Uploading {f} to {target_key}")
                    s3_client.upload_file(f, s3bucket, target_key)
                except Exception as e:
                    print(f"Error: {e}")

# 1. Upload DAGs from root of temp_dags
upload_folder("temp_dags", "dags/")

# 2. Upload Utils
upload_folder("temp_dags/utils", "utils/")

# 3. Upload SQL (preserving structure)
upload_folder("temp_dags/sql", "sql/")

upload_folder("temp_dags/plugins", "plugins/")
