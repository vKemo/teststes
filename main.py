import boto3
import argparse
import uuid
import os

def assume_builder_role(builder_role_arn: str) -> dict:
    """
    Assume the builder role to be able to create the batch job.

    Args: 
        builder_role_arn (str): builder role to be assumed.
    
    Returns:
        dict: AWS credentials to be used.
    """
    sts_client = boto3.client('sts')
    session_identifier = str(uuid.uuid4())
    try:
        response = sts_client.assume_role(
            RoleArn=builder_role_arn,
            RoleSessionName=session_identifier
        )
        return response['Credentials']
    except Exception as e:
        print(f'Error assuming role: {str(e)}')

def get_s3control_client(credentials: dict, aws_region: str) -> boto3.client:
    """
    Create an S3 control client with the provided AWS credentials.

    Args:
        credentials (dict): AWS credentials to be used to create the batch operation.
        aws_region (str): AWS resion to create the batch operation in.
    
    Returns:
        boto3.client: A boto3 S3 Control client.
    """

    boto3_session = boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    return boto3_session.client('s3control', region_name = aws_region)

def create_batch_operation_job(credentials: dict, source_aws_account_id: str, source_bucker: str, report_bucket: str, role_arn: str, aws_region: str) -> None:
    """
    Create a batch job to copy existing objects from the source bucket to the destination

    Args:
        credentials (dict): AWS credentials to be used to create the batch operation.
        source_aws_account_id (str): Source AWS account ID.
        source_bucker (str): Source bucket name.
        report_bucket (str): Report bucket name.
        role_arn (str): Role name to be used in the batch operation.
        aws_region (str): AWS resion to create the batch operation in.
    """
    if credentials is None:
        print('Failed to assume role.')

    token = str(uuid.uuid4())
    s3_client = get_s3control_client(credentials, aws_region)

    s3_client.create_job(
        AccountId = source_aws_account_id,
        ConfirmationRequired = False,
        Operation= {
            'S3ReplicateObject': {}
        },
        Report = {
            'Bucket': f'arn:aws:s3:::{report_bucket}',
            'Format': 'Report_CSV_20180820',
            'Enable': True,
            'Prefix': 'report/',
            'ReportScope': 'AllTasks'
        },
        ClientRequestToken = token,
        ManifestGenerator = {
            'S3JobManifestGenerator': {
                'ExpectedBucketOwner': source_aws_account_id,
                'SourceBucket': f'arn:aws:s3:::{source_bucker}',
                'Filter': {
                    'EligibleForReplication': True
                },
                'EnableManifestOutput': True
            }
        },
        priority = 1,
        RoleArn = role_arn
    )

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Required args to create batch operation job')
    parser.add_argument('--source_aws_account_id', required=True)
    parser.add_argument('--source_bucket', required=True)
    parser.add_argument('--report_bucket', required=True)
    parser.add_argument('--batch_operation_role_arn', required=True)
    parser.add_argument('--builder_role_arn', required=True)
    parser.add_argument('--aws_region', required=False, default='us-east-1')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    credentials = assume_builder_role(args.builder_role_arn)
    create_batch_operation_job(
        credentials,
        args.source_aws_account_id,
        args.source_bucket,
        args.report_bucket,
        args.batch_operation_role_arn,
        args.aws_region
    )
