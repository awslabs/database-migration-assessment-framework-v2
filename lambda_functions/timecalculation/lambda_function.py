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
import time
import math
import boto3
import csv
import uuid
import os

"""
Time calculation example:
wqf_time=2.0
occ=3

tottime= 2.0 + (2.0 * exp(-2 * 0.1)) + (2.0 * exp(-3 * 0.1))
"""
# parameters-os enviornment variables#:
decay = 0.1
DATABASE = os.environ["athenadb"]
snsarn = os.environ["snstopic"]
outbucket = os.environ["outputbucket"]
mainlambdafnendpoint = os.environ["modifycsvfilefnarn"]
mainlambdafnname = os.environ["modifycsvfilefn"]
currlambdafnname = os.environ["timecalculationfn"]
queueurl = os.environ["zipqueue"]
##########

client = boto3.client("athena")
s3 = boto3.resource("s3")
sqs_client = boto3.client("sqs")
sts_client = boto3.client("sts")
lambdaclient = boto3.client("lambda")
sns_client = boto3.client("sns")
stsresponse = sts_client.get_caller_identity()
paginator = client.get_paginator("get_query_results")

# queue = sqs_client.get_queue_url(QueueName=Qname,QueueOwnerAWSAccountId=str(stsresponse['Account']))
# queueurl = queue['QueueUrl']
# res = sqs_client.get_queue_attributes(QueueUrl=queueurl,AttributeNames=['All'])


def calculatewithlowerbound(initial, decay, occurence, res1):
    if initial < 0.1:
        res1.append(initial)
        return res1
    val = initial  # *math.exp(-occurence * decay)
    if val < 0.1:
        res1.append(0.1)
    else:
        res1.append(val)
    return res1


def calculatewithoutlowerbound(initial, decay, occurence, res2):
    if initial < 0.1:
        res2.append(initial)
        return res2
    val = initial  # *math.exp(-occurence * decay)
    res2.append(val)
    return res2


def ninetybucket(noofoccurences, initial, decay, ninetytenbucket):
    tenpercent = int(math.ceil(noofoccurences * 0.10))
    ninetypercent = int(math.floor(noofoccurences * 0.90))
    ninetytenbucket.append(tenpercent * initial)
    if initial < 0.1:
        ninetytenbucket.append(ninetypercent * initial)
        return ninetytenbucket
    for occ in range(ninetypercent):
        val = initial  # * math.exp(-occ * decay)
        if val < 0.1:
            ninetytenbucket.append(0.1)
        else:
            ninetytenbucket.append(val)
    return ninetytenbucket


def seventybucket(noofoccurences, initial, decay, seventythirtybucket):
    thirtypercent = int(math.ceil(noofoccurences * 0.30))
    seventypercent = int(math.floor(noofoccurences * 0.70))
    seventythirtybucket.append(thirtypercent * initial)
    if initial < 0.1:
        seventythirtybucket.append(seventypercent * initial)
        return seventythirtybucket
    for occ in range(seventypercent):
        val = initial  # * math.exp(-occ * decay)
        if val < 0.1:
            seventythirtybucket.append(0.1)
        else:
            seventythirtybucket.append(val)
    return seventythirtybucket


def fiftybucket(noofoccurences, initial, decay, fiftyfiftybucket):
    fiftypercent1 = int(math.ceil(noofoccurences * 0.50))
    fiftypercent2 = int(math.floor(noofoccurences * 0.50))
    fiftyfiftybucket.append(fiftypercent1 * initial)
    if initial < 0.1:
        fiftyfiftybucket.append(fiftypercent2 * initial)
        return fiftyfiftybucket
    for occ in range(fiftypercent2):
        val = initial  # * math.exp(-occ * decay)
        if val < 0.1:
            fiftyfiftybucket.append(0.1)
        else:
            fiftyfiftybucket.append(val)
    return fiftyfiftybucket


def check_sqs():
    sqsres = sqs_client.get_queue_attributes(QueueUrl=queueurl, AttributeNames=["All"])
    print(sqsres)
    i = 0
    if sqsres["Attributes"]["ApproximateNumberOfMessages"] != str(0):
        lambdares = lambdaclient.invoke(
            FunctionName=mainlambdafnname, InvocationType="Event"
        )
        print(lambdares)
    else:
        # retry subscription or 3 times
        while i < 3:
            try:
                subres = sns_client.subscribe(
                    TopicArn=snsarn, Protocol="lambda", Endpoint=mainlambdafnendpoint
                )
                print(subres)
                break
            except Exception as e:
                print(str(e))
                time.sleep(5)
                i = i + 1


def getCalculatedValue(occ, wqf, noDiscountPercent):
    valueWithoutDiscount = (float(noDiscountPercent * occ) / 100) * wqf
    valueWithDiscount = (float((100 - noDiscountPercent) * occ) / 100) * (wqf / 2)
    return valueWithoutDiscount + valueWithDiscount


def dataprep(rowdata, body):
    res1, res2, ninetytenbucket, seventythirtybucket, fiftyfiftybucket = (
        [],
        [],
        [],
        [],
        [],
    )
    Data = rowdata
    host = Data["Data"][0]["VarCharValue"]
    database = Data["Data"][1]["VarCharValue"]
    schema = Data["Data"][2]["VarCharValue"]
    occ = int(Data["Data"][3]["VarCharValue"])
    actionitem = Data["Data"][4]["VarCharValue"]
    wqf = float(Data["Data"][5]["VarCharValue"])
    complexity = Data["Data"][6]["VarCharValue"]
    res1.append(wqf)
    res2.append(wqf)
    for i in range(1, occ):
        calculatewithlowerbound(wqf, decay, i, res1)
        calculatewithoutlowerbound(wqf, decay, i, res2)
    # ninetybucket(occ,wqf,decay,ninetytenbucket)
    # seventybucket(occ,wqf,decay,seventythirtybucket)
    # fiftybucket(occ,wqf,decay,fiftyfiftybucket)
    ninetytenbucketValue = getCalculatedValue(occ, wqf, 10)
    seventythirtybucketValue = getCalculatedValue(occ, wqf, 30)
    fiftyfiftybucketValue = getCalculatedValue(occ, wqf, 50)
    ninetytenbucket.append(ninetytenbucketValue)
    seventythirtybucket.append(seventythirtybucketValue)
    fiftyfiftybucket.append(fiftyfiftybucketValue)
    print("res1", res1)
    print("res2", res2)
    print("ninetytenbucket", ninetytenbucket)
    print("seventythirtybucket", seventythirtybucket)
    print("fiftyfiftybucket", fiftyfiftybucket)
    body += (
        host
        + ","
        + database
        + ","
        + schema
        + ","
        + str(occ)
        + ","
        + str(actionitem)
        + ","
        + str(wqf)
        + ","
        + complexity
        + ","
        + str(round(sum(res1), 2))
        + ","
        + str(round(sum(res2), 2))
        + ","
        + str(round(sum(ninetytenbucket), 2))
        + ","
        + str(round(sum(seventythirtybucket), 2))
        + ","
        + str(round(sum(fiftyfiftybucket), 2))
    )
    body += "\n"
    res1, res2, ninetytenbucket, seventythirtybucket, fiftyfiftybucket = (
        [],
        [],
        [],
        [],
        [],
    )
    return body


def getqueryexecutionstate(queryid):
    execstate = False
    while execstate != True:
        queryres = client.get_query_execution(QueryExecutionId=queryid)
        print(queryid, queryres["QueryExecution"]["Status"]["State"] == "SUCCEEDED")
        if queryres["QueryExecution"]["Status"]["State"] == "SUCCEEDED":
            execstate = True
        time.sleep(5)
    return execstate


def pagination_handler(event, context):
    # print(event)
    Athenatoken = event["token"]
    Queryid = event["queryid"]
    body = ""
    result = paginator.paginate(
        QueryExecutionId=Queryid, PaginationConfig={"StartingToken": Athenatoken}
    )
    print(result)
    for j, r in enumerate(result):
        print(r)
        rows2 = len(r["ResultSet"]["Rows"])
        print(rows2)
        for i in range(0, rows2):
            Data = r["ResultSet"]["Rows"][i]
            body = dataprep(Data, body)
            res1, res2, ninetytenbucket, seventythirtybucket, fiftyfiftybucket = (
                [],
                [],
                [],
                [],
                [],
            )
        # print(body)
        if j == 5 and "NextToken" in result:
            msg = json.dumps({"queryid": Queryid, "token": result["NextToken"]})
            lambdaclient.invoke(
                FunctionName="timecalculation", InvocationType="Event", Payload=msg
            )
            s3.Object(
                outbucket,
                "Estimatedtimeperschemapartitions/timeestimates_"
                + str(uuid.uuid1())
                + ".csv",
            ).put(Body=body)
            return
        else:
            # run athena query and move csv to desired location
            output = client.start_query_execution(
                QueryString="SELECT * FROM "
                + '"'
                + DATABASE
                + '"'
                + "."
                + '"'
                + "Estimatedtimeperschemapartitions"
                + '"',
                QueryExecutionContext={"Database": DATABASE},
                ResultConfiguration={
                    "OutputLocation": "s3://" + outbucket + "/timequeryresults/"
                },
            )
            print(output["QueryExecutionId"])
            Queryid = output["QueryExecutionId"]
            time.sleep(5)
            o1 = client.get_query_execution(QueryExecutionId=Queryid)
            filename = o1["QueryExecution"]["ResultConfiguration"][
                "OutputLocation"
            ].split("/")[-1]
            copy_source = {"Bucket": outbucket, "Key": "timequeryresults/" + filename}
            s3.meta.client.copy(
                copy_source, outbucket, "Estimatedtimeperschema/timeestimates.csv"
            )
            # check o1's location and move to desired timeestimate bucket
            # delete all the objects in the s3://sctmultiassessortest2/Estimatedtimeperschemapartitions
            bucket = s3.Bucket(outbucket)
            bucket.objects.filter(Prefix="Estimatedtimeperschemapartitions/").delete()
            # continue the process of next zip file
            check_sqs()


def lambda_handler(event, context):
    # print(event)
    if "token" in event:
        pagination_handler(event, context)
        return

    # first query
    response2 = client.start_query_execution(
        QueryString="SELECT DISTINCT * FROM "
        + '"'
        + DATABASE
        + '"'
        + "."
        + '"'
        + "lambdadata4"
        + '"',
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": "s3://" + outbucket + "/queryresults/"},
    )
    print(response2["QueryExecutionId"])
    Queryid2 = response2["QueryExecutionId"]
    athenares2 = client.get_query_execution(QueryExecutionId=Queryid2)
    print(athenares2)
    # result = client.get_query_results(QueryExecutionId=Queryid)
    # check query results for testimates per action item
    if getqueryexecutionstate(Queryid2):
        res1, res2, ninetytenbucket, seventythirtybucket, fiftyfiftybucket = (
            [],
            [],
            [],
            [],
            [],
        )
        result2 = paginator.paginate(QueryExecutionId=Queryid2)
        body = ""
        for j, r in enumerate(result2):
            print(r)
            rows2 = len(r["ResultSet"]["Rows"])
            print(rows2)
            for i in range(0, rows2):
                if j == 0 and i == 0:
                    Data = r["ResultSet"]["Rows"][0]
                    body = (
                        Data["Data"][0]["VarCharValue"]
                        + ","
                        + Data["Data"][1]["VarCharValue"]
                        + ","
                        + Data["Data"][2]["VarCharValue"]
                        + ","
                        + Data["Data"][3]["VarCharValue"]
                        + ","
                        + "timeestimatewithlowerbound"
                        + ","
                        + "timeestimatewithoutlowerbound"
                        + ","
                        + "90_10_hours"
                        + ","
                        + "70_30_hours"
                        + ","
                        + "50_50_hours"
                    )
                    body += "\n"
                    continue
                Data = r["ResultSet"]["Rows"][i]
                occ = int(Data["Data"][0]["VarCharValue"])
                actionitem = Data["Data"][1]["VarCharValue"]
                wqf = float(Data["Data"][2]["VarCharValue"])
                complexity = Data["Data"][3]["VarCharValue"]
                res1.append(wqf)
                res2.append(wqf)
                for i in range(1, occ):
                    calculatewithlowerbound(wqf, decay, i, res1)
                    calculatewithoutlowerbound(wqf, decay, i, res2)
                # ninetybucket(occ,wqf,decay,ninetytenbucket)
                # seventybucket(occ,wqf,decay,seventythirtybucket)
                # fiftybucket(occ,wqf,decay,fiftyfiftybucket)
                ninetytenbucketValue = getCalculatedValue(occ, wqf, 10)
                seventythirtybucketValue = getCalculatedValue(occ, wqf, 30)
                fiftyfiftybucketValue = getCalculatedValue(occ, wqf, 50)
                ninetytenbucket.append(ninetytenbucketValue)
                seventythirtybucket.append(seventythirtybucketValue)
                fiftyfiftybucket.append(fiftyfiftybucketValue)
                body += (
                    str(occ)
                    + ","
                    + str(actionitem)
                    + ","
                    + str(wqf)
                    + ","
                    + complexity
                    + ","
                    + str(round(sum(res1), 2))
                    + ","
                    + str(round(sum(res2), 2))
                    + ","
                    + str(round(sum(ninetytenbucket), 2))
                    + ","
                    + str(round(sum(seventythirtybucket), 2))
                    + ","
                    + str(round(sum(fiftyfiftybucket), 2))
                )
                body += "\n"
                res1, res2, ninetytenbucket, seventythirtybucket, fiftyfiftybucket = (
                    [],
                    [],
                    [],
                    [],
                    [],
                )
        # print(body)
    s3.Object(outbucket, "Estimatedtimeperactionitem/timeestimates.csv").put(Body=body)

    # next query
    response = client.start_query_execution(
        QueryString="SELECT DISTINCT * FROM "
        + '"'
        + DATABASE
        + '"'
        + "."
        + '"'
        + "lambdadata3"
        + '"',
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": "s3://" + outbucket + "/queryresults/"},
    )
    print(response["QueryExecutionId"])
    Queryid = response["QueryExecutionId"]

    # check query results for time estimate per schema
    if getqueryexecutionstate(Queryid):
        res = paginator.paginate(QueryExecutionId=Queryid)
        body = ""
        for j, result in enumerate(res):
            print(result)
            rows = len(result["ResultSet"]["Rows"])
            print(rows)
            for i in range(0, rows):
                if j == 0 and i == 0:
                    Data = result["ResultSet"]["Rows"][0]
                    body = (
                        Data["Data"][0]["VarCharValue"]
                        + ","
                        + Data["Data"][1]["VarCharValue"]
                        + ","
                        + Data["Data"][2]["VarCharValue"]
                        + ","
                        + Data["Data"][3]["VarCharValue"]
                        + ","
                        + Data["Data"][4]["VarCharValue"]
                        + ","
                        + Data["Data"][5]["VarCharValue"]
                        + ","
                        + Data["Data"][6]["VarCharValue"]
                        + ","
                        + "timeestimatewithlowerbound"
                        + ","
                        + "timeestimatewithoutlowerbound"
                        + ","
                        + "90_10_hours"
                        + ","
                        + "70_30_hours"
                        + ","
                        + "50_50_hours"
                    )
                    body += "\n"
                    continue
                Data = result["ResultSet"]["Rows"][i]
                body = dataprep(Data, body)
            print(str(j) + "th iteration", body)
            if j == 5 and "NextToken" in result:
                # invoke lambda function with next token as parameter
                param = {"queryid": Queryid, "token": result["NextToken"]}
                p = json.dumps(param)
                lambdaclient.invoke(
                    FunctionName=currlambdafnname, InvocationType="Event", Payload=p
                )
                s3.Object(
                    outbucket,
                    "Estimatedtimeperschemapartitions/timeestimates_"
                    + str(uuid.uuid1())
                    + ".csv",
                ).put(Body=body)
                return
    s3.Object(outbucket, "Estimatedtimeperschema/timeestimates.csv").put(Body=body)
    check_sqs()
