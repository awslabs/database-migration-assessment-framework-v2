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
from logging import currentframe
import os
import subprocess
import csv
import sys
import shutil

import boto3
import glob
import psutil

SCRIPTS_DIR = os.path.dirname(os.path.realpath(__file__))

DMAF_REGION = os.environ.get("DMAF_REGION","us-east-1")

s3 = boto3.resource('s3')
sm_client = boto3.client('secretsmanager',region_name=DMAF_REGION)

drivers_path = os.path.join(SCRIPTS_DIR,"drivers")
sql_drivers = glob.glob(drivers_path + "/mssql*jre11*.jar")
sql_jar_path = ""
if len(sql_drivers) > 0:
    print (sql_drivers)
    sql_jar_path = sql_drivers[0]
else:
    print ("No MSSQL Drivers found.")
oracle_drivers = glob.glob(drivers_path + "/ojdbc8.jar")
ora_jar_path = ""
if len(oracle_drivers) > 0:
    print (oracle_drivers)
    ora_jar_path = oracle_drivers[0]
else:
    print ("No Oracle Drivers found.")
db2_drivers = glob.glob(drivers_path + "/db2jcc4.jar")
db2_jar_path = ""
if len(db2_drivers) > 0:
    print (db2_drivers)
    db2_jar_path = db2_drivers[0]
else:
    print ("No DB2 Drivers found.")
sybase_drivers = glob.glob(drivers_path + "/jconn4.jar")
sybase_jar_path = ""
if len(sybase_drivers):
    print (sybase_drivers)
    sybase_jar_path = sybase_drivers[0]
else:
    print ("No SYBASE Drivers found.")


current_ram_usage = psutil.virtual_memory().percent
percentage_ram_for_sct = 100 - current_ram_usage - 10

total_ram_gb = int (int(psutil.virtual_memory().total)/ 1024/1024/1024 )

min_ram_for_sct = int(total_ram_gb * 25 /100)
max_ram_for_sct = int(total_ram_gb * percentage_ram_for_sct /100)

SCT_INPUT_CSV_HEADERS = ["Name","Description","Secret Manager Key","Server IP","Port","Service Name","Database name","Source Engine","Schema Names","Use Windows Authentication","Login","Password","Use SSL","Trust store","Key store","SSL authentication","Target Engines"]

logs_dir = os.path.join(SCRIPTS_DIR,"logs")

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)


sctInputFile=os.path.join(SCRIPTS_DIR,'sctInput.csv')

def populateCredentialsToCSV(fileName):
    newRows = []
    with open(fileName,"r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Password"] != "" and row["Password"].strip() != "":
                if row["Login"] != "" and row["Login"].strip() != "":
                  print("Source Engine={0}, Login={1}, Password={2}".format(row["Source Engine"], row["Login"], row["Password"]))
                  newRows.append(row)
                  continue
                else:
                    print("Error: 'Login' is not defined in input.csv file. Please define both Login & Password fields. Row[Name]={0}".format(row["Name"]))
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
                    newRows.append(row)
                except Exception as e:
                    print("Error: connection to secrets manager failed. Error Msg = ", str(e))
            elif row["Password"].strip() == "" and row["Secret Manager Key"].strip() == "":
               print("Error: Both 'Password' and 'Secret Manager Key' fields are not defined in input.csv file. Row[Name]={0}".format(row["Name"]))

    with open(sctInputFile,"w") as f:
        writer = csv.DictWriter(f,fieldnames=SCT_INPUT_CSV_HEADERS)
        writer.writeheader()
        writer.writerows(newRows)


def uploads3(dir_name,filename,s3inputbucket):
    import boto3
    s3 = boto3.resource('s3')
    shutil.make_archive(filename, 'zip', dir_name)
    print(dir_name+'.zip file is created successfully!')
    # os.system("sudo mv "+filename+".zip "+"/")
    s3.meta.client.upload_file(filename+'.zip', s3inputbucket, filename+'.zip')
    print("upload done")


def main():
    #run java command
    import boto3
    s_vendor='ORACLE'
    t_vendor='POSTGRESQL'
    print (sys.argv)
    directory=SCRIPTS_DIR
    ProjectName=sys.argv[1]
    s3inputbucket=os.environ["INPUT_BUCKET"]
    print(s3inputbucket)
    s3 = boto3.client('s3')
    os.system("rm {0}/*".format(logs_dir))
    
    #s3.download_file(s3inputbucket, 'Inputfile/input.csv', 'input.csv')
    inputfile=os.path.join(SCRIPTS_DIR,'input.csv')
    #populateCredentialsToCSV(inputfile)
    batchscts="SetGlobalSettings \n" + \
        "   -settings: "+"'"+"[{"+"\n"+\
        "                       "+"\""+"name"+"\""+":"+"\""+"mssql_driver_file"+"\""+","+"\n"+\
        "                       "+"\""+"value"+"\""+":"+"\""+sql_jar_path+"\""+"\n"+\
        "                   "+"},"+"\n"+\
        "                   "+"{"+"\n"+\
        "                       "+"\""+"name"+"\""+":"+"\""+"oracle_driver_file"+"\""+","+"\n"+\
        "                       "+"\""+"value"+"\""+":"+"\""+ora_jar_path+"\""+"\n"+\
        "                   "+"},"+"\n"+\
        "                   "+"{"+"\n"+\
        "                       "+"\""+"name"+"\""+":"+"\""+"db2luw_driver_file"+"\""+","+"\n"+\
        "                       "+"\""+"value"+"\""+":"+"\""+db2_jar_path+"\""+"\n"+\
        "                   "+"},"+"\n"+\
        "                   "+"{"+"\n"+\
        "                       "+"\""+"name"+"\""+":"+"\""+"sybase_ase_driver_file"+"\""+","+"\n"+\
        "                       "+"\""+"value"+"\""+":"+"\""+sybase_jar_path+"\""+"\n"+\
        "                   "+"}]"+"'"+"\n"+\
        "/" +"\n"+ \
        "CreateProject \n" + \
        "   -name: "+"'"+ProjectName  +"'"+ "\n" + \
        "   -directory: "+"'"+directory +"'"+ "\n"+ \
        "   -source: "+"'"+s_vendor +"'"+ "\n"+ \
        "   -target: "+"'"+t_vendor +"'"+ "\n" + \
        "/" + "\n" + \
        "CreateAggregatedReport \n" + \
        "   -directory: "+"'"+directory+"'"+"\n"+\
        "   -projectName: "+"'"+ProjectName +"'"+"\n"+\
        "   -connectionsFile: "+"'"+inputfile+ "'"+"\n"+\
        "/"
    # os.system("sudo chmod 777 "+directory)

    sctConfifFIle = os.path.join(SCRIPTS_DIR,'aggregated.scts')
    sctLogFIle = os.path.join(SCRIPTS_DIR,'logs/sctlog.txt')

    project_dir = os.path.join(directory,ProjectName)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)



    # -Xmx8G -Xms1G 
    xmx = "-Xmx{0}G".format(max_ram_for_sct)
    xms = "-Xms{0}G".format(min_ram_for_sct)
    with open(sctConfifFIle,"w") as f:
        f.write(batchscts)
    try:
         #print(os.system("java --version"))
         with open(sctLogFIle,"w") as output:
            args = ['java', xms, xmx, '-jar', '/opt/aws-schema-conversion-tool/lib/app/AWSSchemaConversionToolBatch.jar', '-type' ,'scts', '-script', sctConfifFIle]
            rcode=subprocess.Popen(args,stdout=output,stderr=output)
            rcode.wait()
    except Exception as e:
        print(str(e))
    #os.remove(sctInputFile)
    uploads3(project_dir,ProjectName,s3inputbucket)
if __name__ == "__main__":
    main()
