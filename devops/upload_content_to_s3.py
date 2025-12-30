import boto3
import os
from botocore.exceptions import ClientError

# Configuration from Environment
key = os.environ.get("AWS_ACCESS_KEY_ID")
pwd = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3bucket = os.environ.get("AWS_S3_BUCKET")
region = os.environ.get("AWS_DEFAULT_REGION")

s3_client = boto3.client("s3", region_name=region, aws_access_key_id=key, aws_secret_access_key=pwd)

def upload_to_s3(local_directory, s3_folder_name):
    """
    local_directory: The path on the GitHub Runner (e.g., 'temp_dags/utils')
    s3_folder_name: The top-level folder name in your S3 bucket (e.g., 'utils')
    """
    if not os.path.exists(local_directory):
        print(f"Directory {local_directory} does not exist, skipping.")
        return

    for root, dirs, files in os.walk(local_directory):
        for file in files:
            local_path = os.path.join(root, file)
            
            # Calculate path relative to the specific folder we are processing
            # This handles subdirectories inside utils, sql, or plugins
            relative_path = os.path.relpath(local_path, local_directory)
            
            # Final key: folder_name + relative_path (e.g., utils/my_script.py)
            target_key = f"{s3_folder_name}/{relative_path}".replace("\\", "/")
            
            try:
                print(f"Uploading {local_path} to s3://{s3bucket}/{target_key}")
                s3_client.upload_file(local_path, s3bucket, target_key)
            except Exception as e:
                print(f"Error uploading {file}: {e}")

# --- EXECUTION ---

# 1. Upload DAGs (Files sitting directly inside temp_dags)
# We handle the root files separately so we don't accidentally recurse into subfolders here
if os.path.exists("temp_dags"):
    for item in os.listdir("temp_dags"):
        local_file = os.path.join("temp_dags", item)
        if os.path.isfile(local_file):
            print(f"Uploading DAG: {item}")
            s3_client.upload_file(local_file, s3bucket, f"dags/{item}")

# 2. Upload the individual folders to their own top-level paths in S3
upload_to_s3("temp_dags/utils", "utils")
upload_to_s3("temp_dags/sql", "sql")
upload_to_s3("temp_dags/plugins", "plugins")
