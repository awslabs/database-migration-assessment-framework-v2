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


def modifycsv(files):
    client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    #host, database, schema, sourcedb, targetdb = "", "", "", "", ""
    host, database, schema, sourcedb, targetdb, port = "", "", "", "", "",""
    
    headers = ["Host", "Database", "Sourcedb", "Targetdb"]
    # inbucket='sctmultiassessortest'
    # outbucket='sctmultiassessortest2'
    # region='us-west-1'

    for j, file in enumerate(files):
        print(file)
        fsplit = file.split("/")
        # seperates path from file name
        fsplit.pop()  # path
        # fname=":".join(fsplit)
        s3_object1 = s3_resource.Object(inbucket, file)
        data1 = s3_object1.get()["Body"].read().decode("utf-8").splitlines()
        lines = csv.reader(data1)
        rows = list(lines)
        body = ""
        # get host,dbname,schema and banners
        for i, line in enumerate(rows):
            if len(line) != 0:
                if "Source database:" in line[0] and ("Oracle" in rows[i + 1][0] or "DB2" in rows[i + 1][0]):
                    # print(rows[i+1])
                    l = line[0]
                    sub1 = l.split(":")
                    sub2 = sub1[2].split("/")
                    sub3 = sub1[1].split("@")
                    sub4 = sub3[0].split(".")
                    
                    if len(sub2) > 1:
                        database = sub2[1]
                        port = sub2[0]
                    else:
                        database = sub1[-1]
                        port = sub1[2]
                        

                    #host = sub3[1]
                    if len(port) > 1:
                        host = sub3[1] + ":" + port
                    else:
                        host = sub3[1]    
                                            
                    schema = sub4[0]
                    if "Oracle" in rows[i + 1][0]:
                        sourcedb = "ORACLE"
                    else:
                        sourcedb = "DB2"
                    banner = rows[i + 1][0]
                    # print(host,database,schema,sourcedb,targetdb)
                if "Source database:" in line[0] and ("SQL" in rows[i + 1][0] or "Adaptive" in rows[i + 1][0]):
                    
                    l= re.sub('"', "", line[0])
                    sub1 = l.split("\\")
                    
                    if(len(sub1)) > 1:
                        
                        for ind in sub1:
                            
                            if (re.search(":", ind) and ("Source database:" in ind)):
                                sub2 = l.split(":")
                                sub3 = sub2[1].split("@")
                                port=''
                                
                            if (re.search(":", ind) and ("Source database:" not in ind)):
                                sub2 = ind.split(":")
                                port = re.sub('"', "", sub2[1])
                                
                    else:
                        sub2 = sub1[0].split(":")
                        sub3 = sub2[1].split("@")
                        port = sub2[2]
                    
                    sub4 = sub3[0].split(".")
                    
                    database = sub4[0]
                    schema = sub4[1]
                            
                    if len(port) > 1:
                        host = sub3[1] + ":" + port
                    else:
                        host = sub3[1]
                    
                    database = sub4[0]
                    schema = sub4[1]
                    if "SQL" in rows[i + 1][0]:
                        sourcedb = "MSSQL"
                    else:
                        sourcedb = "SYBASE"
                    banner = rows[i + 1][0]
                    # print(host,database,schema,sourcedb,target)
        targetdb = fsplit[-1]
        fname = host + ":" + database + ":" + schema + ":" + targetdb
        # print (banner)
        # exit(0)
        # get all files in path (csv + )
        result = client.list_objects(Bucket=inbucket, Prefix="/".join(fsplit))
        for file in result["Contents"]:
            # print(file)
            # parse schema and check if it's mssql and schema is in format db.schema then split
            if "Csv-report_Action_Items_Summary.csv" in file["Key"] and host != "":
                s3_object2 = s3_resource.Object(inbucket, file["Key"])
                data2 = s3_object2.get()["Body"].read().decode("utf-8").splitlines()
                lines = csv.reader(data2)
                rows = list(lines)
                # print(rows)
                f = open("/tmp/Csv-report_Action_Items_Summary_" + fname + ".csv", "w+")
                temp_csv_file = csv.writer(f)
                # if(sourcedb=='MSSQL' and "." in schema):
                for i, row in enumerate(rows):
                    print("-----> ", row)
                    if i == 0:
                        row.insert(0, "Source")
                        row.insert(1, "Target")
                        row.insert(2, headers[0])
                        row.insert(3, headers[1])
                        temp_csv_file.writerow(row)
                        print(row)

                    else:
                        # bits=row.split(',')
                        # print('----> ',bits)
                        print(row)
                        # newrow=[sourcedb,targetdb,host,database,row[0].replace('.',','),row[1],row[2],row[3],row[4]]
                        newrow = [
                            sourcedb,
                            targetdb,
                            host,
                            database,
                            row[0].split(".")[-1],
                            row[1],
                            row[2],
                            row[3],
                            row[4],
                        ]
                        print(newrow)
                        temp_csv_file.writerow(newrow)
                f.close()
                client.upload_file(
                    "/tmp/Csv-report_Action_Items_Summary_" + fname + ".csv",
                    outbucket,
                    "actionitemsummary/Csv-report_Action_Items_Summary_"
                    + fname
                    + ".csv",
                )

            if "Csv-report.csv" in file["Key"] and host != "":
                data3 = client.get_object(Bucket=inbucket, Key=file["Key"])
                s3_object3 = s3_resource.Object(inbucket, file["Key"])
                data3 = s3_object3.get()["Body"].read().decode("utf-8").splitlines()
                lines = csv.reader(data3)
                rows = list(lines)
                f1 = open("/tmp/Csv-report_" + fname + ".csv", "w+")
                temp_csv_file1 = csv.writer(f1)
                for i, row in enumerate(rows):
                    if i == 0:
                        row.insert(0, "Source")
                        row.insert(1, "Target")
                        row.insert(2, headers[0])
                        row.insert(3, headers[1])
                        row.insert(4, "Schema")
                        temp_csv_file1.writerow(row)
                    else:
                        row.insert(0, sourcedb)
                        row.insert(1, targetdb)
                        row.insert(2, host)
                        row.insert(3, database)
                        row.insert(4, schema)

                        temp_csv_file1.writerow(row)
                f1.close()
                # print(csvreportbody)
                # s3_resource.Object('sctmultiassessortest2', 'sctfile/Csv-report_'+fname+'_'+str(j)+'.csv').put(Body=csvreportbody)
                client.upload_file(
                    "/tmp/Csv-report_" + fname + ".csv",
                    outbucket,
                    "sctfile/Csv-report_" + fname + ".csv",
                )
            # put keys in Summary rows stopping at first empty row (between data and source, banner lines)
            if "Csv-report_Summary.csv" in file["Key"] and host != "":
                data4 = client.get_object(Bucket=inbucket, Key=file["Key"])
                s3_object4 = s3_resource.Object(inbucket, file["Key"])
                data4 = s3_object4.get()["Body"].read().decode("utf-8").splitlines()
                lines = csv.reader(data4)
                rows = list(lines)
                f2 = open("/tmp/Csv-report_Summary_" + fname + ".csv", "w+")
                temp_csv_file2 = csv.writer(f2)
                for i, row in enumerate(rows):
                    if i == 0:
                        row.insert(0, "Source")
                        row.insert(1, "Target")
                        row.insert(2, "Banner")
                        row.insert(3, headers[0])
                        row.insert(4, headers[1])
                        row.insert(5, "Schema")

                        temp_csv_file2.writerow(row)
                    else:
                        if not row:
                            break
                        row.insert(0, sourcedb)
                        row.insert(1, targetdb)
                        row.insert(2, banner)
                        row.insert(3, host)
                        row.insert(4, database)
                        row.insert(5, schema)
                        temp_csv_file2.writerow(row)
                f2.close()
                client.upload_file(
                    "/tmp/Csv-report_Summary_" + fname + ".csv",
                    outbucket,
                    "reportsummary/Csv-report_Summary_" + fname + ".csv",
                )

            if "Pdf-report.pdf" in file["Key"] and host != "":
                fname = host + ":" + database + ":" + schema + ":" + targetdb
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
                f3 = open("/tmp/assmnt2pdfmap_" + fname + ".csv", "w+")
                temp_csv_file3 = csv.writer(f3)
                for i in range(2):
                    if i == 0:
                        rows.insert(0, headers[0])
                        rows.insert(1, headers[1])
                        rows.insert(2, "Schema")
                        rows.insert(3, "Source")
                        rows.insert(4, "Target")
                        rows.insert(5, "Path")
                        temp_csv_file3.writerow(rows)
                        rows = []
                    if i == 1:
                        rows.insert(0, host)
                        rows.insert(1, database)
                        rows.insert(2, schema)
                        rows.insert(3, sourcedb)
                        rows.insert(4, targetdb)
                        rows.insert(5, pdfurl)
                        temp_csv_file3.writerow(rows)
                f3.close()
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
