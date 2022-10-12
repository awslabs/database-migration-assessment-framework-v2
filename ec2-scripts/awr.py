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
import logging



SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))

logs_dir = os.path.join(SCRIPTS_DIR,"logs")

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh = logging.FileHandler(os.path.join(logs_dir,'awr.log'))
fh.setLevel(logging.INFO)
fh.setFormatter(format)
logger.addHandler(fh)

schemalist = os.path.join(SCRIPTS_DIR, "input.csv")
o_dir_base = SCRIPTS_DIR
o_dir_rpt = os.path.join(SCRIPTS_DIR, "perf_reports")
ORACLE_SQL = os.path.join(SCRIPTS_DIR, "oracle_performance.sql")
MSSQL_SQL = os.path.join(SCRIPTS_DIR, "get_mssql_performance.sql")
now = datetime.now()

DMAF_REGION = os.environ.get("DMAF_REGION", "us-east-1")
s3inputbucket = os.environ.get("INPUT_BUCKET")

s3 = boto3.resource("s3")
sm_client = boto3.client("secretsmanager", region_name=DMAF_REGION)

dblist = open(schemalist, "r")
outbucket = os.environ["OUTPUT_BUCKET"]  # data[3]
print(outbucket)
if os.path.isdir("perf_reports") == False:
    os.system("mkdir " + o_dir_rpt)
    os.system("chmod 777 " + o_dir_rpt + "/")
logger.info("Reading the input csv file : {0}".format(schemalist))
with open(schemalist,"r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # print (row)
        try:
            ###########Start - Logic to handle secret manager fetch!##########
            if row["Password"] != "" and row["Password"].strip() != "":
                if row["Login"] != "" and row["Login"].strip() != "":
                  print("Source Engine={0}, Login={1}, Password={2}".format(row["Source Engine"], row["Login"], row["Password"]))
                else:
                    print("Error: 'Login' is not defined in input.csv file. Please define both Login & Password fields.Row[Name]={0}".format(row["Name"]))
                    raise Exception("Error: 'Login' is not defined in input.csv file. Please define both Login & Password fields. Row[Name]={0}".format(row["Name"]))
            elif row["Secret Manager Key"] != "" and row["Secret Manager Key"].strip() != "":
                print("Connecting to secrets manager to read username/password for secret manager key = {0}".format(row["Secret Manager Key"]))
                try:
                    response = sm_client.get_secret_value(SecretId=row["Secret Manager Key"])
                    #print (response)
                    SecretString = json.loads(response.get("SecretString"))
                    row["Login"] = SecretString.get("username")
                    row["Password"] = SecretString.get("password")
                    if row["Server IP"] == "":
                        row["Server IP"] = SecretString.get("host")
                    if row["Port"] == "":
                        row["Port"] = SecretString.get("port")
                    if row["Database name"] == "":
                        row["Database name"] = SecretString.get("dbname")
                    print("Source Engine={0}, Login={1}, Password={2}, ServerIP={3}, Port={4}, DBName={5}".format(row["Source Engine"], 
                            row["Login"], row["Password"], row["Server IP"], row["Port"], row["Database name"]))
                except Exception as e:
                    print("Error: connection to secrets manager failed. Error Msg = ", str(e))
            elif row["Password"].strip() == "" and row["Secret Manager Key"].strip() == "":
               #print("Error: Both 'Password' and 'Secret Manager Key' fields are not defined in input.csv file. Row[Name]={0}".format(row["Name"]))
               raise Exception("Error: Both 'Password' and 'Secret Manager Key' fields are not defined in input.csv file. Row[Name]={0}".format(row["Name"]))
            ###########End - Logic to handle secret manager fetch!##########
            s_server = row["Server IP"]
            s_port = row["Port"]
            # SID is not a valid column/field in input.csv file
            # s_sid = row["SID"]
            s_sid = row["Service Name"]
            schema = row["Schema Names"]
            s_vendor = row["Source Engine"]
            # dbuid = values[6]
            # print(s_server+" "+s_port+" " +s_sid+" "+schema+" "+s_vendor)
        except Exception as e:
            print(str(e))
            logger.error("Failed to fetch data")
            logger.error(str(e))

        if s_vendor == "ORACLE" and os.path.exists(ORACLE_SQL):
            dsn = cx_Oracle.makedsn(s_server, s_port, service_name=s_sid)
            logger.info("Oracle : Connecting to DB {0}@{1}".format(s_sid,s_server))
            conn = cx_Oracle.connect(
                # user=oracleCredentials["username"],
                # password=oracleCredentials["password"],
                user=row["Login"],
                password=row["Password"],
                dsn=dsn,
            )
            f = open(ORACLE_SQL, "r")
            sql = f.read()
            
            #fname = s_server + "_" + s_sid.rstrip() + "_" + "oracle_performance" + ".csv"
            fname = s_server + "_" + s_port + "_" + s_sid.rstrip() + "_" + "oracle_performance" + ".csv"
            
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
                    logger.info (records)
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
                        #rowval.insert(0, s_server.rstrip())
                        rowval.insert(0, s_server.rstrip() + ':' + s_port.rstrip())
                        rowval.append(int(round(time.time(), 0)))
                        output.writerow(rowval)
                    outputFile.close()
                    conn.close()
                except Exception as e:
                    processed = False
                    print(str(e))
                    logger.error("Failed to fetch data")
                    logger.error(str(e))
            f.close()
            if processed:
                logger.info ("uploading perf reports msqlperf/{0}".format(fname))
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
                    # + msssqlCredentials["username"]
                    + row["Login"]
                    + ";PWD="
                    # + msssqlCredentials["password"]
                    + row["Password"]
                    + ";DATABASE="
                    + dbname.strip()
                )
                logger.info("MSSQL : Connecting to DB {0}@{1}".format(s_sid,dbname.strip()))
                # print (constr)
                conn = pyodbc.connect(constr)
                # fw=open('/home/ec2-user/mpi4py-3.0.3/get_mssql_performance',"w")
                # dbname = schema.split(".")[0]
                f = open(MSSQL_SQL, "r")
                sql = f.read()
                # print(sql)
                #fname = s_server + "_" + dbname + "_" + "mssql_performance" + ".csv"
                fname = s_server + "_" + s_port + "_" + dbname + "_" + "mssql_performance" + ".csv"
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
                        logger.info(records)
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
                            #rowval.insert(0, s_server.rstrip())
                            rowval.insert(0, s_server.rstrip() + ':' + s_port.rstrip())
                            rowval.append(int(round(time.time(), 0)))
                            output.writerow(rowval)
                        # print("no rows")
                        outputFile.close()
                        conn.close()
                    except Exception as e:
                        processed = False
                        print(str(e))
                        logger.error("Failed to fetch data")
                        logger.error(str(e))
                f.close()
                if processed:
                    logger.info ("uploading perf reports msqlperf/{0}".format(fname))
                    s3.meta.client.upload_file(csv_file_dest, outbucket, "msqlperf/" + fname)
print("upload done")
