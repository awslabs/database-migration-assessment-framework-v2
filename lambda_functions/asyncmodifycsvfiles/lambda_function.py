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
import csv
import os
import re

# environment variables
inbucket = os.environ["inbucket"]
outbucket = os.environ["outbucket"]
eventname = os.environ["cweventname"]
region = os.environ["region"]

CSV_REPORTS_HEADER = [
    "SourceType",
    "TargetType",
    "Server IP address and port",
    "Database",
    "Schema",
    "Category",
    "Occurrence",
    "Action item",
    "Subject",
    "Group",
    "Description",
    "Documentation references",
    "Recommended action",
    "Filtered",
    "Estimated complexity",
    "Line",
    "Position",
    "Source",
    "Target",
]
CSV_REPORT_SUMMARY_HEADER = [
    "SourceType",
    "TargetType",
    "Banner",
    "Host",
    "Database",
    "Schema",
    "Category",
    "Number of objects",
    "Objects automatically converted",
    "Objects with simple actions",
    "Objects with medium-complexity actions",
    "Objects with complex actions",
    "Total lines of code",
]
ACTION_ITEM_SUMMARY_HEADER = [
    "SourceType",
    "TargetType",
    "Host",
    "Database",
    "Schema",
    "Action item",
    "Number of occurrences",
    "Learning curve efforts",
    "Efforts to convert an occurrence of the action item",
    "Action item description",
    "Recommended action",
]
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
ASSESMENT_TO_PDFMAP_HEADERS = ["Host", "Database", "Schema", "Source", "Target", "Path"]


def modifycsv(files):
    client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    host, database, schema, sourcedb, targetdb, port = "", "", "", "", "", ""

    for j, file in enumerate(files):
        print(file)
        fsplit = file.split("/")
        # seperates path from file name
        fsplit.pop()  # path
        s3_object1 = s3_resource.Object(inbucket, file)
        data1 = s3_object1.get()["Body"].read().decode("utf-8").splitlines()
        lines = csv.reader(data1)
        rows = list(lines)
        body = ""
        # get host,dbname,schema and banners
        for i, line in enumerate(rows):
            if len(line) != 0:
                if "Source database:" in line[0] and (
                    "Oracle" in rows[i + 1][0] or "DB2" in rows[i + 1][0]
                ):
                    # print(rows[i+1])
                    if "Oracle" in rows[i + 1][0]:
                        sourcedb = "ORACLE"
                    else:
                        sourcedb = "DB2"
                    banner = rows[i + 1][0]
                    # print(host,database,schema,sourcedb,targetdb)
                if "Source database:" in line[0] and (
                    "SQL" in rows[i + 1][0] or "Adaptive" in rows[i + 1][0]
                ):

                    if "SQL" in rows[i + 1][0]:
                        sourcedb = "MSSQL"
                    else:
                        sourcedb = "SYBASE"
                    banner = rows[i + 1][0]
                if "Source database:" in line[0] and (
                    "MySQL" in rows[i + 1][0] or "distribution" in rows[i + 1][0]
                ):
                    sourcedb = "MYSQL"
                    banner = rows[i + 1][0]
                    # print(host,database,schema,sourcedb,target)
        targetdb = fsplit[-1].strip()

        csv_report_file = file.replace("Csv-report_Summary.csv", "Csv-report.csv")

        csv_s3_obj = s3_resource.Object(inbucket, csv_report_file)
        csv_data = csv_s3_obj.get()["Body"].read().decode("utf-8").splitlines()
        lines = csv.DictReader(csv_data)

        for line in lines:
            database = line.get("Database name", "").strip()
            schema = line.get("Schema name", "").strip()
            if database == "":
                DB_SCHEMA = schema.split(".")
                database = DB_SCHEMA[0].strip()
                
            DB_SCHEMA = schema.split(".")
            schema = DB_SCHEMA[-1].strip()
            
            host = line["Server IP address and port"].strip()
            break

        fname = host + ":" + database + ":" + schema + ":" + targetdb
        # print (banner)ac
        # exit(0)
        # get all files in path (csv + )
        result = client.list_objects(Bucket=inbucket, Prefix="/".join(fsplit))
        for file in result["Contents"]:
            # print(file)
            # parse schema and check if it's mssql and schema is in format db.schema then split
            if "Csv-report_Action_Items_Summary.csv" in file["Key"] and host != "":

                s3_object2 = s3_resource.Object(inbucket, file["Key"])
                data2 = s3_object2.get()["Body"].read().decode("utf-8").splitlines()
                lines = csv.DictReader(data2)
                rows = []
                for line in lines:
                    row = dict()
                    for k in ACTION_ITEM_SUMMARY_HEADER:
                        if k in line:
                            row[k] = line[k]
                    row["Database"] = database
                    row["Schema"] = schema
                    row["Host"] = host
                    row["SourceType"] = sourcedb
                    row["TargetType"] = targetdb
                    rows.append(row)
                with open(
                    "/tmp/Csv-report_Action_Items_Summary_" + fname + ".csv", "w+"
                ) as f1:
                    temp_csv_file1 = csv.DictWriter(
                        f1, fieldnames=ACTION_ITEM_SUMMARY_HEADER
                    )
                    temp_csv_file1.writeheader()
                    temp_csv_file1.writerows(rows)

                client.upload_file(
                    "/tmp/Csv-report_Action_Items_Summary_" + fname + ".csv",
                    outbucket,
                    "actionitemsummary/Csv-report_Action_Items_Summary_"
                    + fname
                    + ".csv",
                )

            if "Csv-report.csv" in file["Key"] and host != "":
                s3_object3 = s3_resource.Object(inbucket, file["Key"])
                data3 = s3_object3.get()["Body"].read().decode("utf-8").splitlines()
                lines = csv.DictReader(data3)
                rows = []
                for line in lines:
                    row = dict()
                    for k in CSV_REPORTS_HEADER:
                        if k in line:
                            row[k] = line[k]
                    row["Database"] = database
                    row["Schema"] = schema
                    row["SourceType"] = sourcedb
                    row["TargetType"] = targetdb
                    rows.append(row)
                with open("/tmp/Csv-report_" + fname + ".csv", "w+") as f1:
                    temp_csv_file1 = csv.DictWriter(f1, fieldnames=CSV_REPORTS_HEADER)
                    temp_csv_file1.writeheader()
                    temp_csv_file1.writerows(rows)
                client.upload_file(
                    "/tmp/Csv-report_" + fname + ".csv",
                    outbucket,
                    "sctfile/Csv-report_" + fname + ".csv",
                )
            # put keys in Summary rows stopping at first empty row (between data and source, banner lines)
            if "Csv-report_Summary.csv" in file["Key"] and host != "":

                s3_object4 = s3_resource.Object(inbucket, file["Key"])
                data4 = s3_object4.get()["Body"].read().decode("utf-8").splitlines()
                lines = csv.DictReader(data4)
                rows = []
                for line in lines:
                    if line.get("Number of objects") is not None:
                        row = dict()
                        for k in CSV_REPORT_SUMMARY_HEADER:
                            if k in line:
                                row[k] = line[k]
                        row["Database"] = database
                        row["Schema"] = schema
                        row["Host"] = host
                        row["SourceType"] = sourcedb
                        row["TargetType"] = targetdb
                        row["Banner"] = banner
                        rows.append(row)
                with open("/tmp/Csv-report_Summary_" + fname + ".csv", "w+") as f1:
                    temp_csv_file1 = csv.DictWriter(
                        f1, fieldnames=CSV_REPORT_SUMMARY_HEADER
                    )
                    temp_csv_file1.writeheader()
                    temp_csv_file1.writerows(rows)

                client.upload_file(
                    "/tmp/Csv-report_Summary_" + fname + ".csv",
                    outbucket,
                    "reportsummary/Csv-report_Summary_" + fname + ".csv",
                )

            if "Pdf-report.pdf" in file["Key"] and host != "":
                object = s3_resource.Object(inbucket, file["Key"])
                object.copy_from(
                    CopySource={"Bucket": inbucket, "Key": file["Key"]},
                    MetadataDirective="REPLACE",
                    ContentType="application/pdf",
                )
                # url = boto3.client('s3').generate_presigned_url(ClientMethod='get_object', Params={'Bucket': inbucket, 'Key': "/".join(fsplit)+'/Pdf-report.pdf','ResponseContentType': 'application/pdf'},ExpiresIn=3600)
                pdfurl = (
                    "https://"
                    + inbucket
                    + ".s3."
                    + region
                    + ".amazonaws.com/"
                    + "/".join(fsplit)
                    + "/Pdf-report.pdf"
                )
                rows = []
                # print(host,database,sourcedb,targetdb,url)
                row = dict()
                row["Database"] = database
                row["Schema"] = schema
                row["Host"] = host
                row["Source"] = sourcedb
                row["Target"] = targetdb
                row["Path"] = pdfurl
                rows.append(row)

                with open("/tmp/assmnt2pdfmap_" + fname + ".csv", "w+") as f1:
                    temp_csv_file1 = csv.DictWriter(
                        f1, fieldnames=ASSESMENT_TO_PDFMAP_HEADERS
                    )
                    temp_csv_file1.writeheader()
                    temp_csv_file1.writerows(rows)

                client.upload_file(
                    "/tmp/assmnt2pdfmap_" + fname + ".csv",
                    outbucket,
                    "assmnt2pdfmap/" + fsplit[-1] + "assmnt2pdfmap_" + fname + ".csv",
                )


def lambda_handler(event, context):
    print(event)
    files = json.loads(event["Records"][0]["body"])
    events = boto3.client("events")
    response = events.enable_rule(Name=eventname)
    modifycsv(files["csvfile"])
