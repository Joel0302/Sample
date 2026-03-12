from posixpath import dirname
import boto3
import os
import sys

from botocore.exceptions import ClientError


sys.path.append(os.path.join(os.path.dirname(__file__), "../temp_dags"))
# Creating S3 Resource From the Session.
#print(os.environ)
key = os.environ.get("AWS_ACCESS_KEY_ID")
pwd = os.environ.get("AWS_SECRET_ACCESS_KEY")
s3bucket = os.environ.get("AWS_S3_BUCKET")
#print(key)
s3_client = boto3.client("s3", region_name="us-east-1", aws_access_key_id=key, aws_secret_access_key=pwd)

# Deletion part
delete_list_path = "./delete_list.txt"
if os.path.exists(delete_list_path):
    with open(delete_list_path, "r") as f:
        delete_targets = [line.strip() for line in f if line.strip()]        
        for target in delete_targets:
            #Remove the 'retd_' marker from the path segments to find the real S3 path
            parts = target.strip().split('/')
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
                    delete_keys = [{'Key': obj['Key']} for obj in response['Contents']] + [{'Key': folder_prefix}]
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

directory = "temp_dags"
for filename in os.listdir(directory):
    if filename.startswith("retd_"):
            continue
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)
        try:
            response = s3_client.upload_file(f, s3bucket, "dags/" + filename)
        except ClientError as e:
            print(e)
        except FileNotFoundError as e:
            print(e)
directory = "temp_dags/utils"
for filename in os.listdir(directory):
    if filename.startswith("retd_"):
            continue
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)
        try:
            response = s3_client.upload_file(f, s3bucket, "dags/utils/" + filename)
        except ClientError as e:
            print(e)
        except FileNotFoundError as e:
            print(e)

directory = "temp_dags/sql"
for root,dirname,filename in os.walk(directory):
    for file in filename:
        if file.startswith("retd_"):
            continue
        print(root)
        print(dirname)
        print(file)
        f = os.path.join(root, file)
         # checking if it is a file
        if os.path.isfile(f):
            print(f)
        try:
            filekey=f.replace(directory,"")
            print(filekey)
            response = s3_client.upload_file(f, s3bucket, "dags/sql" +filekey)
        except ClientError as e:
            print(e)
        except FileNotFoundError as e:
            print(e)

#for filename in os.listdir(directory):
#    f = os.path.join(directory, filename)
    # checking if it is a file
#if os.path.isfile(f):
#        print(f)
#        try:
#            response = s3_client.upload_file(f, s3bucket, "dags/sql/" + filename)
#        except ClientError as e:
#            print(e)
#        except FileNotFoundError as e:
#            print(e)

#for root,d_names,f_names in os.walk(path):#
	#for f in f_names:



