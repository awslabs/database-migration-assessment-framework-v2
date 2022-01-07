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

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
            logger.error ("Unable to process file. File : {0} do not follow the naming conventions (customerName_BatchName.zip)".format(key))
            return None
        customerName = splitZipFileName[0]
        BatchName = "".join(splitZipFileName[1:])

        putObjects = []
        with io.BytesIO(obj["Body"].read()) as tf:
            # rewind the file
            tf.seek(0)
            # Read the file as a zipfile and process the members
            with zipfile.ZipFile(tf, mode="r") as zipf:
                for file in zipf.infolist():
                    fileName = file.filename
                    logger.info(fileName)
                    if ".DS_Store" in fileName or "__MACOSX" in fileName:
                        continue
                    if ".sql" in fileName:
                        putFile = client.put_object(
                            Bucket=inbucket,
                            Key="Inputfile/" + fileName,
                            Body=zipf.read(file),
                        )
                        putObjects.append(putFile)
                    elif "wqf" in fileName:
                        putFile = client.put_object(
                            Bucket=inbucket,
                            Key="Inputfile/wqfweightage/" + fileName,
                            Body=zipf.read(file),
                        )
                        putObjects.append(putFile)
                    elif "Complexity" in fileName:
                        putFile = client.put_object(
                            Bucket=inbucket,
                            Key="Inputfile/complexityweightage/" + fileName,
                            Body=zipf.read(file),
                        )
                        putObjects.append(putFile)
                    elif "rds" in fileName:
                        putFile = client.put_object(
                            Bucket=inbucket,
                            Key="Inputfile/rdsinfo/" + fileName,
                            Body=zipf.read(file),
                        )
                        putObjects.append(putFile)
                    elif "coderanges" in fileName:
                        putFile = client.put_object(
                            Bucket=inbucket,
                            Key="Inputfile/actioncodes/" + fileName,
                            Body=zipf.read(file),
                        )
                        putObjects.append(putFile)
                    elif "sct" in fileName:
                        putFile = client.put_object(
                            Bucket=inbucket,
                            Key="Inputfile/sctactioncodes/" + fileName,
                            Body=zipf.read(file),
                        )
                        putObjects.append(putFile)
                    else:
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
                modifyAggregatedFile(data, tmp_file_name, inbucket, keyDir,customerName,BatchName)
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


def getDatabaseName(row, inbucket, dirname):
    logger.info("_______________________________")
    logger.info("{0} {1} {2}".format(str(row), inbucket, dirname))
    client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    newPaginator = client.get_paginator("list_objects_v2")
    newDir = os.path.join(dirname, row["Name"],row["Schema name"])
    logger.info(newDir)
    pages = newPaginator.paginate(Bucket=inbucket, Prefix=newDir)
    database = ""
    schema = ""
    logger.info(pages)
    for page in pages:
        logger.info(page)
        logger.info("_______________________________")
        for obj in page["Contents"]:
            if "Csv-report_Summary.csv" in obj["Key"]:
                s3_object1 = s3_resource.Object(inbucket, obj["Key"])
                data1 = s3_object1.get()["Body"].read().decode("utf-8").splitlines()
                lines = csv.reader(data1)
                rows = list(lines)
                for i, line in enumerate(rows):
                    if len(line) != 0:
                        if "Source database:" in line[0] and ("Oracle" in rows[i + 1][0] or  "DB2" in rows[i + 1][0]):
                            # print(rows[i+1])
                            l = line[0]
                            sub1 = l.split(":")
                            sub2 = sub1[2].split("/")
                            sub3 = sub1[1].split("@")
                            sub4 = sub3[0].split(".")
                            host = sub3[1]
                            if len(sub2) > 1:
                                database = sub2[1]
                            else:
                                database = sub1[-1]
                            schema = sub4[0]
                            if "Oracle" in rows[i + 1][0]:
                                sourcedb = "ORACLE"
                            else:
                                sourcedb = "DB2"
                            banner = rows[i + 1][0]
                            return database, schema
                            # print(host,database,schema,sourcedb,targetdb)
                        if "Source database:" in line[0] and ("SQL" in rows[i + 1][0] or "Adaptive" in rows[i + 1][0]):
                            l = line[0]
                            sub1 = l.split("\\")
                            sub2 = sub1[0].split(":")
                            sub3 = sub2[1].split("@")
                            sub4 = sub3[0].split(".")
                            host = sub3[1]
                            database = sub4[0]
                            schema = sub4[1]
                            if "SQL" in rows[i + 1][0]:
                                sourcedb = "MSSQL"
                            else:
                                sourcedb = "SYBASE"
                            banner = rows[i + 1][0]
                            return database, schema
                            # print(host,database,schema,sourcedb,target)
    return database, schema


def modifyAggregatedFile(data, tmp_file, Bucket, dirname,customerName,BatchName):
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
        database, tmpschema = getDatabaseName(row, Bucket, dirname)
        schema = row["Schema name"].split(".")[-1]
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
                    newRow[key] = row[key]
                for header in ConversionHeaders:
                    conversionHeader = '{0} for "{1}"'.format(header, target)
                    newRow[header] = row[conversionHeader]
                newRows.append(newRow)

    newDirName = os.path.dirname(tmp_file)
    if not os.path.exists(newDirName):
        os.makedirs(newDirName)
    with open(tmp_file, "w") as f:
        FinalHeader = ["Timestamp", "database", "schema"]
        FinalHeader.extend(headers)
        FinalHeader.extend(["Target"])
        FinalHeader.extend(ConversionHeaders)
        FinalHeader.extend(["customerName", "BatchName"])
        csvWriter = csv.DictWriter(f, fieldnames=FinalHeader)
        csvWriter.writeheader()
        csvWriter.writerows(newRows)


"""
def lambda_handler2(event,context):
    files=json.loads(event['Records'][0]['body'])
    modifycsv(files['csvfile'])
"""
