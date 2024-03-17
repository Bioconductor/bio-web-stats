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
    
def get_parameter_store_values(parameter_path: str) -> dict:
    """Get all SSM parameter store values for a specific configuration.

    Arguments:
        parameter_path -- The prefix for the configure. Example: "/bioc/webstats/dev"

    Returns:
        A dictionary of parameter names (excluding the prefix) and their values.
    """
 
 
    ssm_client = boto3.client('ssm')
    plist = ssm_client.get_parameters_by_path(Path = parameter_path, Recursive=True)
    # HACK Start from the top with SSM paramater store included
    for item in plist["Parameters"]:
        plist = ssm_client.get_parameters_by_path(Path = parameter_path, Recursive=True)
        result = {item["Name"][len(parameter_path)+1:] : item["Value"] for item in plist["Parameters"]}
    return result
    

if __name__ == "__main__":
    # result = aws_assume_sts_role(
    #     'arn:aws:iam::931729544676:role/bioc-webstats-webrunner',
    #     'webstats.tester')
    # pass
    
    t = get_parameter_store_values("/bioc/webstats/dev")
    pass
    print("| Path | Value  |")
    print("| -----| ------ |")
    for k,v in t.items():
        print("|", k, "|", v , "|") 
