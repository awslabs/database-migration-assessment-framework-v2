import argparse
import json
import time
import boto3


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-cf', '--cf_name', required=True, help="CF_QS_Stack_name")
    args = vars(ap.parse_args())
    cf_name = args['cf_name']
    accountID = boto3.client('sts').get_caller_identity()['Account']
    region = boto3.client('sts').meta.region_name
    return cf_name, accountID, region


def get_cf_outputs(cf_name, region):
    cf_r = boto3.resource('cloudformation', region_name=region)
    stack = cf_r.Stack(cf_name)
    outputs = stack.outputs
    template = list(filter(lambda x: x['OutputKey'] == 'QSTemplate', outputs))[0]['OutputValue']
    vw_datamart_dataset = list(filter(lambda x: x['OutputKey'] == 'QSDataSetVWDatamart', outputs))[0]['OutputValue']
    vw_urldocumentation_dataset = list(filter(lambda x: x['OutputKey'] == 'QSDataSetVWUrldocumentation', outputs))[0][
        'OutputValue']
    return template, vw_datamart_dataset, vw_urldocumentation_dataset


def get_principal(cf_name, region, accountID):
    cf_r = boto3.resource('cloudformation', region_name=region)
    stack = cf_r.Stack(cf_name)
    parameters = stack.parameters
    QSPrincipalType = list(filter(lambda x: x['ParameterKey'] == 'QSPrincipalType', parameters))[0]['ParameterValue']
    QSPrincipalName = list(filter(lambda x: x['ParameterKey'] == 'QSPrincipalName', parameters))[0]['ParameterValue']
    principal = f'arn:aws:quicksight:us-east-1:{accountID}:{QSPrincipalType}/default/{QSPrincipalName}'
    return principal


def prepare_analysis_attributes(template):
    analysis_id = template.rsplit('/')[-1].replace('template', 'analysis')
    actions = ['quicksight:RestoreAnalysis', 'quicksight:UpdateAnalysisPermissions', 'quicksight:DeleteAnalysis',
               'quicksight:DescribeAnalysisPermissions', 'quicksight:QueryAnalysis', 'quicksight:DescribeAnalysis',
               'quicksight:UpdateAnalysis']
    return analysis_id, actions


def create_analysis(accountID, region, analysis_id, principal, actions, vw_datamart_dataset,
                    vw_urldocumentation_dataset, template):
    qs = boto3.client('quicksight', region_name=region)
    response = qs.create_analysis(
        AwsAccountId=accountID,
        AnalysisId=analysis_id,
        Name=analysis_id,
        Permissions=[
            {
                'Principal': principal,
                'Actions': actions
            },
        ],
        SourceEntity={
            'SourceTemplate': {
                'DataSetReferences': [
                    {
                        'DataSetPlaceholder': 'vw_datamart',
                        'DataSetArn': vw_datamart_dataset
                    },
                    {
                        'DataSetPlaceholder': 'vw_urldocumentation',
                        'DataSetArn': vw_urldocumentation_dataset
                    },
                ],
                'Arn': template
            }
        }
    )
    print(json.dumps(response, indent=4, default=str))


def main():
    # Fetching and creating parameters
    cf_name, accountID, region = get_args()
    template, vw_datamart_dataset, vw_urldocumentation_dataset = get_cf_outputs(cf_name, region)
    principal = get_principal(cf_name, region, accountID)
    analysis_id, actions = prepare_analysis_attributes(template)

    # creating Analysis
    create_analysis(accountID, region, analysis_id, principal, actions, vw_datamart_dataset,
                    vw_urldocumentation_dataset, template)

    # Printing and Validating
    qs = boto3.client('quicksight', region_name=region)
    print('----------------------------------------------\n', 'waiting for 10 sec')
    time.sleep(10)
    print('----------------------------------------------\n')
    print('Describe Analysis: \n')
    response = qs.describe_analysis(AwsAccountId=accountID,
                                    AnalysisId=analysis_id)
    print('AnalysisName: ', response['Analysis']['Name'], '\n', 'Status: ', response['Analysis']['Status'])
    print('----------------------------------------------')
    print('Describe Analysis Permissions: \n')
    response = qs.describe_analysis_permissions(AwsAccountId=accountID,
                                                AnalysisId=analysis_id)
    print('Next Principal has access to Analysis: ', response['Permissions'][0]['Principal'], '\nwith permissions:\n')
    for a in response['Permissions'][0]['Actions']:
        print(a)
    print('FINISHED')


if __name__ == '__main__':
    main()
