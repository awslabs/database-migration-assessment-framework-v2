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

from datetime import datetime
import sys
import pyodbc
import os
import cx_Oracle
import csv
import time
import logging
import boto3
from botocore.exceptions import ClientError
import json
import time
import urllib.request

SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))

schemalist = os.path.join(SCRIPTS_DIR, "input.csv")
o_dir_base = SCRIPTS_DIR
o_dir_rpt = os.path.join(SCRIPTS_DIR, "perf_reports")
ORACLE_SQL = os.path.join(SCRIPTS_DIR, "oracle_performance.sql")
MSSQL_SQL = os.path.join(SCRIPTS_DIR, "get_mssql_performance.sql")
now = datetime.now()

DMAF_SECRETS_NAME = os.environ.get("DMAF_SECRETS_NAME", None)
DMAF_REGION = os.environ.get("DMAF_REGION", "us-east-1")
s3inputbucket = os.environ.get("INPUT_BUCKET")

s3 = boto3.resource("s3")
sm_client = boto3.client("secretsmanager", region_name=DMAF_REGION)


response = sm_client.get_secret_value(SecretId=DMAF_SECRETS_NAME)

# print (response)

SecretString = json.loads(response.get("SecretString"))
oracleCredentials = SecretString.get("ORACLE")
msssqlCredentials = SecretString.get("MSSQL")


dblist = open(schemalist, "r")
outbucket = os.environ["OUTPUT_BUCKET"]  # data[3]
print(outbucket)
if os.path.isdir("perf_reports") == False:
    os.system("mkdir " + o_dir_rpt)
    os.system("chmod 777 " + o_dir_rpt + "/")
with open(schemalist,"r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # print (row)
        try:
            s_server = row["Server IP"]
            s_port = row["Port"]
            s_sid = row["SID"]
            schema = row["Schema Names"]
            s_vendor = row["Source Engine"]
            # dbuid = values[6]
            # print(s_server+" "+s_port+" " +s_sid+" "+schema+" "+s_vendor)
        except Exception as e:
            print(str(e))

        if s_vendor == "ORACLE" and os.path.exists(ORACLE_SQL):
            dsn = cx_Oracle.makedsn(s_server, s_port, service_name=s_sid)
            conn = cx_Oracle.connect(
                user=oracleCredentials["username"],
                password=oracleCredentials["password"],
                dsn=dsn,
            )
            f = open(ORACLE_SQL, "r")
            sql = f.read()
            fname = s_server + "_" + s_sid.rstrip() + "_" + "oracle_performance" + ".csv"
            csv_file_dest = os.path.join(o_dir_rpt, fname)
            processed = True
            with open(csv_file_dest, "w") as outputFile:
                #outputFile = open(csv_file_dest, "w")  # 'wb'
                output = csv.writer(
                    outputFile,
                    dialect="excel",
                    lineterminator="\n",
                    quoting=csv.QUOTE_NONNUMERIC,
                )
                # print(sql)
                curs = conn.cursor()
                try:
                    header = "Host"
                    header2 = "collected"
                    curs.execute(sql)
                    records = curs.fetchall()
                    print (records)
                    cols = []
                    rowval = []
                    for col in curs.description:
                        cols.append(col[0].upper())
                    cols.insert(0, header.upper())
                    cols.append(header2.upper())
                    output.writerow(cols)
                    for row_data in records:  # add table rows
                        rowval = list(row_data)
                        # print(rowval)
                        rowval.insert(0, s_server.rstrip())
                        rowval.append(int(round(time.time(), 0)))
                        output.writerow(rowval)
                    outputFile.close()
                    conn.close()
                except Exception as e:
                    processed = False
                    print(str(e))
            f.close()
            if processed:
                print ("uploading perf reports msqlperf/{0}".format(fname))
                s3.meta.client.upload_file(csv_file_dest, outbucket, "oraperf/" + fname)
        if s_vendor == "MSSQL":
            schemas = schema.split(";")
            for schema_name in schemas:
                dbname = schema_name.split(".")[0]
                # database_name = schema.split(".")[0]
                constr = (
                    "DRIVER={ODBC Driver 17 for SQL Server};trusted_Connection=no;SERVER="
                    + s_server.rstrip()
                    + ";PORT="
                    + s_port.rstrip()
                    + ";UID="
                    + msssqlCredentials["username"]
                    + ";PWD="
                    + msssqlCredentials["password"]
                    + ";DATABASE="
                    + dbname.strip()
                )
                # print (constr)
                conn = pyodbc.connect(constr)
                # fw=open('/home/ec2-user/mpi4py-3.0.3/get_mssql_performance',"w")
                # dbname = schema.split(".")[0]
                f = open(MSSQL_SQL, "r")
                sql = f.read()
                # print(sql)
                fname = s_server + "_" + dbname + "_" + "mssql_performance" + ".csv"
                csv_file_dest = os.path.join(o_dir_rpt, fname)
                processed = True
                with open(csv_file_dest, "w") as outputFile:
                    output = csv.writer(
                        outputFile,
                        dialect="excel",
                        lineterminator="\n",
                        quoting=csv.QUOTE_NONNUMERIC,
                    )
                    # print(sql)
                    curs = conn.cursor()
                    # print(curs.rowcount)
                    try:
                        curs.execute(sql)
                        records = curs.fetchall()
                        # print (records)
                        cols = []
                        rowval = []
                        header = "Host"
                        header2 = "collected"
                        for col in curs.description:
                            cols.append(col[0].upper())
                        cols.insert(0, header.upper())
                        cols.append(header2.upper())
                        output.writerow(cols)
                        for row_data in records:  # add table rows
                            rowval = list(row_data)
                            rowval.insert(0, s_server.rstrip())
                            rowval.append(int(round(time.time(), 0)))
                            output.writerow(rowval)
                        # print("no rows")
                        outputFile.close()
                        conn.close()
                    except Exception as e:
                        processed = False
                        print(str(e))
                f.close()
                if processed:
                    print ("uploading perf reports msqlperf/{0}".format(fname))
                    s3.meta.client.upload_file(csv_file_dest, outbucket, "msqlperf/" + fname)
print("upload done")
