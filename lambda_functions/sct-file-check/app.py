import json
# import requests
import sct_file_validation as sfv
import os
import io
import logging

#Newly added modules
import json
import boto3
import os.path
import csv
from urllib.parse import unquote
import logging
import subprocess
import zipfile

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    ####Newly added modules####
    client = boto3.client("s3")
    # lambdaclient = boto3.client("lambda")
    # s3_resource = boto3.resource("s3")
    # sqs_client = boto3.client("sqs")
    snstopicarn = os.environ["snstopictopublish"]
    # csvqueueurl = os.environ["csvqueue"]
    # outputbucket = os.environ["outbucket"]
    logger.info(event)
    # flag = False
    print("event=", event)
    mesg = json.loads(event["Records"][0]["Sns"]["Message"])

    inbucket = mesg["Records"][0]["s3"]["bucket"]["name"]
    key = unquote(mesg["Records"][0]["s3"]["object"]["key"])
    logger.info(inbucket)
    logger.info(key)
    dirname = os.path.splitext(key)[0]

    try:
        obj = client.get_object(Bucket=inbucket, Key=key)
        # get_zip_file(inbucket, key)
        logger.info("PWD={}".format(os.getcwd()))
        print("PWD={}".format(os.getcwd()))
        # cmd = 'chmod'
        # temp = subprocess.Popen([cmd, '775', '/tmp/'+key], stdout = subprocess.PIPE)
        # cmd = 'ls'
        # temp = subprocess.Popen([cmd, '-ltr', '/tmp/'], stdout = subprocess.PIPE)
        # # get the output as a string
        # output = str(temp.communicate())
        # print("ls cmd output = {}".format(output))
        # cmd = 'cd'
        # temp = subprocess.Popen([cmd, '/tmp'], stdout = subprocess.PIPE)
        # # # get the output as a string
        # output = str(temp.communicate())
        # print("cd cmd output = {}".format(output))
        # print("PWD={}".format(os.getcwd()))
        # cmd = 'ls'
        # temp = subprocess.Popen([cmd, '-ltr', '.'], stdout = subprocess.PIPE)
        # # get the output as a string
        # output = str(temp.communicate())
        # os.chdir('/tmp')
        # print("ls cmd output = {}".format(output))
        # cmd = 'unzip'
        # temp = subprocess.Popen([cmd, '/tmp/' + key], cwd="/tmp/", stdout = subprocess.PIPE)
        # # get the output as a string
        # output = str(temp.communicate())
        # logger.info("unzip cmd output = {}".format(output))

        try:
            # obj = client.get_object(Bucket=inbucket, Key=key)
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
                        #elif "rds" in fileName:
                        #    putFile = client.put_object(
                        #        Bucket=inbucket,
                        #        Key="Inputfile/rdsinfo/" + fileName,
                        #        Body=zipf.read(file),
                        #    )
                        #    putObjects.append(putFile)
                        elif "coderanges" in fileName:
                            putFile = client.put_object(
                                Bucket=inbucket,
                                Key="Inputfile/actioncodes/" + fileName,
                                Body=zipf.read(file),
                            )
                            putObjects.append(putFile)
                        # elif "sct" in fileName:
                        #     putFile = client.put_object(
                        #         Bucket=inbucket,
                        #         Key="Inputfile/sctactioncodes/" + fileName,
                        #         Body=zipf.read(file),
                        #     )
                        #     putObjects.append(putFile)
                        else:
                            putFile = client.put_object(
                                Bucket=inbucket,
                                Key=dirname + "/" + fileName,
                                Body=zipf.read(file),
                            )
                            putObjects.append(putFile)
                        # print(putFile)
            # # Delete zip file after unzip
            # if len(putObjects) > 0:
            #     if "dmaf" in key:
            #         bucket = s3_resource.Bucket(inbucket)
            #         bucket.objects.filter(Prefix=key.split(".")[0] + "/").delete()
            #         deletedObj = client.delete_object(Bucket=inbucket, Key=key)
            #         return
            #     else:
            #         deletedObj = client.delete_object(Bucket=inbucket, Key=key)
            #     logger.info("deleted file:")
            #     logger.info(deletedObj)
        except Exception as e:
            logger.error(e)
            logger.error(
                "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                    key, inbucket
                )
            )
            raise e
        
        key = str(key).removesuffix('.zip')
        print("key=",key)
        # downloadDirectoryFroms3(inbucket, key)
        download_dir(key, '/tmp/', inbucket, client=client)
        print("folder name = {}".format(key))
        file_path = '/tmp/' + key
        print("file_path=", file_path)
    except Exception as e:
        logger.error(e)
        logger.error(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, inbucket
            )
        )
        raise e
    ##########################

    try:
        # file_path = os.environ["FILE_PATH"]
        print("calling sct_file_check_main with file_path=", file_path)
        sct_data = sfv.sct_file_check_main(file_path)
        print("file_path=",file_path)
        with open("/tmp/sct_data.txt", "w" ) as fh:
            fh.write(sct_data)
        print("Reading file....")
        with open("/tmp/sct_data.txt", "r") as fh:
            print(fh.read())
        fh.close()
        upload_file_to_s3(inbucket, "/tmp/sct_data.txt", key + '_sct_data_validation.txt')
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(inbucket)
        bucket.objects.filter(Prefix=key+'/').delete() 
        # for file in bucket.list(prefix=key):
        #     file.delete()
        print("Deleted the folder unzipped for sct-file-check...key=", key)
        # Place original mesg on the sns topic
        snsclient = boto3.client('sns')
        logger.info("Trying to publish mesg to SNS...{}".format(mesg))
        print("Before publishing mesg to topic...")
        print("mesg=",mesg)
        sns_msg = {}

        # sns_msg['default'] = "Sample fallback message"
        # sns_msg['http'] = str(json.dumps(mesg))
        sns_msg = str(json.dumps(mesg))
        response = snsclient.publish(
                    TopicArn=snstopicarn,
                    # Message=json.dumps(mesg),
                    Message=str(sns_msg),
                    Subject='sct-file-check completed'
                    # MessageStructure='json'
                )
        logger.info("response = {}".format(response))
        logger.info("Mesg published successfully")

    except Exception as e:
        logger.error("Error: {}".format(str(e)))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "success",
            "sct_data": sct_data
        }),
    }

def upload_file_to_s3(s3bucket, cmd_file, file_path):
    logger.info("Uploading File={} to Bucket={}".format(cmd_file, s3bucket))
    try:
        s3 = boto3.client('s3')
        with open(cmd_file, "rb") as f:
            # s3.put_object(Bucket=s3bucket, Key=(file_path + os.path.basename(cmd_file)), Body=f)
            s3.put_object(Bucket=s3bucket, Key=file_path, Body=f)
    except Exception as e:
        logger.error("Error in upload log file: {}".format(str(e)))
    finally:
        f.close()

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

def get_zip_file(s3bucket, key):
    s3 = boto3.client('s3')
    print ("Downloading s3 file from {0}/{1}".format(s3bucket, key))
    s3.download_file(s3bucket, key, '/tmp/{}'.format(key))
    print ("File downloaded to /tmp/{}".format(key))

def downloadDirectoryFroms3(bucketName, remoteDirectoryName):
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucketName)
    os.chdir('/tmp')
    for obj in bucket.objects.filter(Prefix = remoteDirectoryName):
        if not os.path.exists(os.path.dirname( obj.key)):
            os.makedirs(os.path.dirname(obj.key))
        bucket.download_file(obj.key, obj.key) # save to same path
        
def download_dir(prefix, local, bucket, client):
    """
    params:
    - prefix: pattern to match in s3
    - local: local path to folder in which to place files
    - bucket: s3 bucket with target contents
    - client: initialized s3 client object
    """
    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket':bucket,
        'Prefix':prefix,
    }
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        results = client.list_objects_v2(**kwargs)
        contents = results.get('Contents')
        for i in contents:
            k = i.get('Key')
            if k[-1] != '/':
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get('NextContinuationToken')
    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
    for k in keys:
        dest_pathname = os.path.join(local, k)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
        client.download_file(bucket, k, dest_pathname)