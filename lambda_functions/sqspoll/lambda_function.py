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
import time
import os

# enviornment variables
queueurl = os.environ["csvqueue"]
eventrulename = os.environ["sqscheckevent"]
lambdafnname = os.environ["timecalculationfn"]


def lambda_handler(event, context):
    # sts_client = boto3.client('sts')
    # response = sts_client.get_caller_identity()
    sqs_client = boto3.client("sqs")
    lambdaclient = boto3.client("lambda")
    # queue = sqs_client.get_queue_url(QueueName='csvqueue',QueueOwnerAWSAccountId=str(response['Account']))
    # queueurl = queue['QueueUrl']
    for i in range(5):
        res = sqs_client.get_queue_attributes(QueueUrl=queueurl, AttributeNames=["All"])
        print(res)
        if res["Attributes"]["ApproximateNumberOfMessages"] == str(0) and res[
            "Attributes"
        ]["ApproximateNumberOfMessagesNotVisible"] == str(0):
            response = lambdaclient.invoke(
                FunctionName=lambdafnname, InvocationType="Event"
            )
            print(response)
            events = boto3.client("events")
            response = events.disable_rule(Name=eventrulename)
            break
        time.sleep(120)
