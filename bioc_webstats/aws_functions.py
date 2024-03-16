''' aws_functions TODO rename this.'''
import boto3
from botocore.exceptions import ClientError

def aws_assume_sts_role(role_arn, role_session_name):

    # Create an STS client
    sts_client = boto3.client('sts')

    # Assume the specified role
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name
    )

    # Credentials to be used for the session with the assumed role
    credentials = assumed_role_object['Credentials']
    return credentials

    # # Use the temporary credentials that AssumeRole returns to make a connection to Amazon S3
    # s3_resource = boto3.resource(
    #     's3',
    #     aws_access_key_id=credentials['AccessKeyId'],
    #     aws_secret_access_key=credentials['SecretAccessKey'],
    #     aws_session_token=credentials['SessionToken'],
    # )

    # Now you can use the s3_resource object to interact with S3
    
if __name__ == "__main__":
    result = aws_assume_sts_role(
        'arn:aws:iam::931729544676:role/bioc-webstats-webrunner',
        'webstats.tester')
    pass
    