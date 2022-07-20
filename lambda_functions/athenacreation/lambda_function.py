"""
  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  @author maheshb
"""

import json
import boto3
import os
import time
import re
from botocore.exceptions import ClientError
import cfnresponse

# environment variables
database = os.environ["athenadb"]
s3_regex = r"(?i)s3://S3_BUCKET/(.*\w+)"


def create_prefix(bucket_name, path_to_folder):
    try:
        print("creating prefix : {0}".format(path_to_folder))
        s3 = boto3.client("s3")
        bucket_name = bucket_name
        directory_name = path_to_folder
        s3.put_object(Bucket=bucket_name, Key=(directory_name + "/"))
    except Exception as e:
        print(str(e))


def check_folder_exists(bucket_name, path_to_folder):
    try:
        s3 = boto3.client("s3")
        res = s3.list_objects_v2(Bucket=bucket_name, Prefix=path_to_folder)
        return "Contents" in res
    except ClientError as e:
        # Logic to handle errors.
        pass
    return False


def emptyS3Bucket(bucket_name):
    s3 = boto3.resource('s3')
    s3_bucket = s3.Bucket(bucket_name)
    bucket_versioning = s3.BucketVersioning(bucket_name)
    if bucket_versioning.status == 'Enabled':
        s3_bucket.object_versions.delete()
    else:
        s3_bucket.objects.all().delete()

def CreateAthenaTables():
    outbucketname = os.environ["outputbucket"]
    print("creating athena tables....")
    ath = boto3.client("athena")
    with open("athenaTablesViews.sql", "r") as f:
        content = f.read()
        prefixes = re.findall(s3_regex, content)
        # print (prefixes)
        for prefix in prefixes:
            if not check_folder_exists(outbucketname, prefix):
                create_prefix(outbucketname, prefix)
        queries = content.split(";")
        for query in queries:
            query = query.replace("S3_BUCKET", outbucketname)
            # print(query)
            # ath.start_query_execution(QueryString=query,QueryExecutionContext={'Database': database},ResultConfiguration={'OutputLocation': 's3://'+outbucketname+'/queries/'})
            result = ath.start_query_execution(
                QueryString=query,
                QueryExecutionContext={"Database": database},
                ResultConfiguration={
                    "OutputLocation": "s3://" + outbucketname + "/queries/"
                },
            )
            queryid = result["QueryExecutionId"]
            i = 0
            time.sleep(3)
            while i < 3:
                athres = ath.get_query_execution(QueryExecutionId=queryid)
                if athres["QueryExecution"]["Status"]["State"] == "SUCCEEDED":
                    break
                time.sleep(3)
                i = i + 1


def copyCSVFiles():
    outbucketname = os.environ["outputbucket"]
    print("uploading csv files...")
    client = boto3.client("s3")
    client.upload_file(
        "rds_instance_type.csv", outbucketname, "instancelookup/rds_instance_type.csv"
    )
    client.upload_file(
        "wqf_estimate_default.csv",
        outbucketname,
        "wqfestimatedefault/wqf_estimate_default.csv",
    )
    client.upload_file("wqf_2nd_values.csv", outbucketname, "wqf2/wqf_2nd_values.csv")
    client.upload_file("url.csv", outbucketname, "documenturls/url.csv")
    client.upload_file("oracle_internal.csv", outbucketname, "oracleinternal/oracle_internal.csv")


def lambda_handler(event, context):
    print(event)
    try:
        if event["RequestType"] == "Create":
            copyCSVFiles()
            CreateAthenaTables()
        if event["RequestType"] == "Delete":
            sctinputbucket = os.environ["sctinputbucket"]
            outbucketname = os.environ["outputbucket"]
            emptyS3Bucket(sctinputbucket)
            emptyS3Bucket(outbucketname)

    except Exception as e:
        print(e)
    responseValue = "Processed"
    responseData = {}
    responseData["Data"] = responseValue
    cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData)
