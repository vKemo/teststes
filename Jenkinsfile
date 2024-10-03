pipeline {
    agent any

    parameters {
        string(name: 'SOURCE_AWS_ACCOUNT_ID', description: 'AWS Aaccount ID')
        string(name: 'SOURCE_BUCKET', description: 'Source S3 Bucket Name')
        string(name: 'REPORT_BUCKET', description: 'S3 Report Bucket Name')
        string(name: 'BATCH_OPERATION_ROLE_ARN', description: 'Batch Operation IAM Role Name')
        string(name: 'BUILDER_ROLE_ARN', description: 'Builder Role to be Assumed')
        string(name: 'AWS_REGION', description: 'AWS Region for Source Bucket')
    }

    stages{
        stage('Clone Repository'){
            steps {
                git branch: 'main', url: 'https://bbgithub.dev.bloomberg.com/Media-Infrastructure/aws-s3-batch-operation-python'
            }
        }
        stage('Install requierment'){
            steps{
                sh '''#!bin/bash
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install boto3
                '''
            }
        }
        stage('Create Batch Operation'){
            steps {
                sh '''#!bin/bash
                    source venv/bin/activate
                    python3 -m main --source_aws_account_id=${SOURCE_AWS_ACCOUNT_ID} --source_bucket=${SOURCE_BUCKET}  --report_bucket=${REPORT_BUCKET} --builder_role_arn=${BUILDER_ROLE_ARN} --batch_operation_role_arn=${BATCH_OPERATION_ROLE_ARN} --aws_region=${AWS_REGION}
                '''
            }
        }
    }
}
