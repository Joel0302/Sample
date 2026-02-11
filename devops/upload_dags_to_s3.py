from posixpath import dirname
import boto3
import os
import sys
from botocore.exceptions import ClientError

sys.path.append(os.path.join(os.path.dirname(__file__), "../temp_dags"))

key = os.environ.get("AWS_ACCESS_KEY_ID")
pwd = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3bucket = os.environ.get("AWS_S3_BUCKET")

s3_client = boto3.client("s3", region_name="us-east-1", aws_access_key_id=key, aws_secret_access_key=pwd)

# --- UPLOAD SECTION ---

directory = "temp_dags"
for filename in os.listdir(directory):
    # SKIP delete_list and retd_ files
    if filename == "delete_list.txt" or filename.startswith("retd_"):
        continue
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        try:
            s3_client.upload_file(f, s3bucket, "dags/" + filename)
            print(f"Uploaded: {filename}")
        except Exception as e:
            print(e)

directory = "temp_dags/utils"
if os.path.exists(directory):
    for filename in os.listdir(directory):
        # SKIP retd_ files
        if filename.startswith("retd_"):
            continue
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            try:
                s3_client.upload_file(f, s3bucket, "dags/utils/" + filename)
                print(f"Uploaded: utils/{filename}")
            except Exception as e:
                print(e)

directory = "temp_dags/sql"
if os.path.exists(directory):
    for root, sub_dirs, filenames in os.walk(directory):
        for file in filenames:
            # SKIP retd_ files
            if file.startswith("retd_"):
                continue
            f = os.path.join(root, file)
            try:
                filekey = f.replace(directory, "")
                s3_client.upload_file(f, s3bucket, "dags/sql" + filekey)
                print(f"Uploaded: sql{filekey}")
            except Exception as e:
                print(e)

# --- DELETE SECTION ---

delete_list = "temp_dags/delete_list.txt"
if os.path.exists(delete_list):
    print("Processing deletions...")
    with open(delete_list, "r") as f:
        for line in f:
            target_key = line.strip()
            if target_key:
                try:
                    s3_client.delete_object(Bucket=s3bucket, Key=target_key)
                    print(f"Deleted from S3: {target_key}")
                except Exception as e:
                    print(f"Delete failed for {target_key}: {e}")
