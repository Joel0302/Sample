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

directory = "temp_dags"
for filename in os.listdir(directory):
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



