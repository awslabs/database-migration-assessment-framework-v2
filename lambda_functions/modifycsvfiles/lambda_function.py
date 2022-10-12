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
import os.path
import csv
import time
import zipfile
import io
import os
from urllib.parse import unquote
import logging
import re


logger = logging.getLogger()
logger.setLevel(logging.INFO)

AGGREGATED_SUMMARY_HEADER = [
    "Timestamp",
    "database",
    "schema",
    "Server Ip",
    "Name",
    "Description",
    "Schema name",
    "Target",
    "Code object conversion %",
    "Storage object conversion %",
    "Syntax Elements conversion %",
    "Conversion Complexity",
    "customerName",
    "BatchName",
]


def validate_files(aggregated_data, files_list):
    csvReader = csv.DictReader(aggregated_data)
    valid = True
    logger.info("Checking if folders exist as per the aggregated csv file.")
    for row in csvReader:
        parent_folder = row["Name"]
        schema_name = row["Schema name"]
        schema_folder = os.path.join(parent_folder, schema_name)

        if parent_folder in files_list and schema_folder in files_list:
            logger.info(
                "{0} folder exist".format(os.path.join(parent_folder, schema_folder))
            )
        else:
            logger.error(
                "{0} folder doesn't exist".format(
                    os.path.join(parent_folder, schema_folder)
                )
            )
            valid = False
    return valid


def lambda_handler(event, context):
    client = boto3.client("s3")
    lambdaclient = boto3.client("lambda")
    s3_resource = boto3.resource("s3")
    sqs_client = boto3.client("sqs")
    sts_client = boto3.client("sts")
    sns_client = boto3.client("sns")

    ## get environment variables
    # zipqueueurl = os.environ["zipqueue"]
    snstopicarn = os.environ["snstopictounsubscribe"]
    csvqueueurl = os.environ["csvqueue"]
    outputbucket = os.environ["outbucket"]

    # stsres = sts_client.get_caller_identity()
    # queue = sqs_client.get_queue_url(QueueName='testqueue',QueueOwnerAWSAccountId=str(stsres['Account']))
    # queueurl = queue['QueueUrl']

    logger.info(event)
    flag = False

    mesg = json.loads(event["Records"][0]["Sns"]["Message"])

    inbucket = mesg["Records"][0]["s3"]["bucket"]["name"]
    key = unquote(mesg["Records"][0]["s3"]["object"]["key"])
    logger.info(inbucket)
    logger.info(key)
    dirname = os.path.splitext(key)[0]

    try:
        obj = client.get_object(Bucket=inbucket, Key=key)
        zipFileName = os.path.split(key)[-1]
        baseNameWithoutExtension = os.path.splitext(zipFileName)[0]
        splitZipFileName = baseNameWithoutExtension.split("_")
        if len(splitZipFileName) == 1:
            logger.error(
                "Unable to process file. File : {0} do not follow the naming conventions (customerName_BatchName.zip)".format(
                    key
                )
            )
            return None
        customerName = splitZipFileName[0]
        BatchName = "".join(splitZipFileName[1:])

        putObjects = []
        with io.BytesIO(obj["Body"].read()) as tf:
            # rewind the file
            tf.seek(0)
            # Read the file as a zipfile and process the members
            with zipfile.ZipFile(tf, mode="r") as zipf:

                files_list = []
                for file in zipf.infolist():
                    fileName = file.filename
                    if ".DS_Store" in fileName or "__MACOSX" in fileName:
                        continue
                    files_list.append(fileName.strip("/"))

                if "Aggregated_report.csv" not in files_list:
                    logger.error(
                        "Unable to process file. File : {0}. It do not have zip Aggregated_report.csv file.".format(
                            key
                        )
                    )
                    return None

                data = zipf.read("Aggregated_report.csv").decode("utf-8").splitlines()
                if not validate_files(data, files_list):
                    logger.error("Failed to process file. File : {0}.".format(key))
                    return None

                for file in zipf.infolist():
                    fileName = file.filename
                    logger.info(fileName)
                    if ".DS_Store" in fileName or "__MACOSX" in fileName:
                        continue
                    putFile = client.put_object(
                        Bucket=inbucket,
                        Key=dirname + "/" + fileName,
                        Body=zipf.read(file),
                    )
                    putObjects.append(putFile)
                    # print(putFile)
        # Delete zip file after unzip
        if len(putObjects) > 0:
            if "dmaf" in key:
                bucket = s3_resource.Bucket(inbucket)
                bucket.objects.filter(Prefix=key.split(".")[0] + "/").delete()
                deletedObj = client.delete_object(Bucket=inbucket, Key=key)
                return
            else:
                deletedObj = client.delete_object(Bucket=inbucket, Key=key)
            logger.info("deleted file:")
            logger.info(deletedObj)
    except Exception as e:
        logger.error(e)
        logger.error(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, inbucket
            )
        )
        raise e

    files = []
    paginator = client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=inbucket, Prefix=dirname)
    logger.info(pages)
    for page in pages:
        logger.info(page)
        for obj in page["Contents"]:
            if "Aggregated_report.csv" in obj["Key"]:
                s3_object = s3_resource.Object(inbucket, obj["Key"])
                data = s3_object.get()["Body"].read().decode("utf-8").splitlines()
                tmp_file_name = "/tmp/Aggregated_report_" + dirname + ".csv"
                keyDir = os.path.split(obj["Key"])[0]
                modifyAggregatedFile(
                    data, tmp_file_name, inbucket, keyDir, customerName, BatchName
                )
                client.upload_file(
                    tmp_file_name,
                    outputbucket,
                    "aggregated/Aggregated_report_" + dirname + ".csv",
                )
            if "Csv-report_Summary.csv" in obj["Key"]:
                files.append(obj["Key"])
    logger.info(len(files))
    csvfiles = [files[x : x + 100] for x in range(0, len(files), 100)]
    for i in range(len(csvfiles)):
        param = {"zipfile": dirname, "csvfile": csvfiles[i]}
        p = json.dumps(param)
        response = sqs_client.send_message(QueueUrl=csvqueueurl, MessageBody=p)


def modifyAggregatedFile(data, tmp_file, Bucket, dirname, customerName, BatchName):
    headers = ["Server Ip", "Name", "Description", "Schema name"]
    ConversionHeaders = [
        "Code object conversion %",
        "Storage object conversion %",
        "Syntax Elements conversion %",
        "Conversion Complexity",
    ]

    newRows = []

    csvReader = csv.DictReader(data)
    allHeaderKeys = csvReader.fieldnames
    Targets = []
    for headerName in allHeaderKeys:
        hArray = headerName.split("% for")
        if len(hArray) > 1:
            targetName = hArray[-1].strip().strip('"')
            if targetName not in Targets:
                Targets.append(targetName)
    for row in csvReader:
        # database, tmpschema = getDatabaseName(row, Bucket, dirname)
        tmphost = row["Server IP address and port"]
        schema = row["Schema name"].split(".")[-1]
        database = row.get("Database name", "")
        if database == "":
            database = row["Schema name"].split(".")[0]
        for target in Targets:
            checkTargetHeader = '{0} for "{1}"'.format(ConversionHeaders[0], target)
            if checkTargetHeader in row:
                newRow = dict()
                newRow["Timestamp"] = int(round(time.time(), 0))
                newRow["Target"] = target
                newRow["database"] = database
                newRow["schema"] = schema
                newRow["customerName"] = customerName
                newRow["BatchName"] = BatchName

                for key in headers:

                    if key == "Server Ip":
                        newRow[key] = tmphost
                    else:
                        newRow[key] = row[key]

                for header in ConversionHeaders:
                    conversionHeader = '{0} for "{1}"'.format(header, target)
                    newRow[header] = row[conversionHeader]
                newRows.append(newRow)

    newDirName = os.path.dirname(tmp_file)
    if not os.path.exists(newDirName):
        os.makedirs(newDirName)
    with open(tmp_file, "w") as f:
        csvWriter = csv.DictWriter(f, fieldnames=AGGREGATED_SUMMARY_HEADER)
        csvWriter.writeheader()
        csvWriter.writerows(newRows)
