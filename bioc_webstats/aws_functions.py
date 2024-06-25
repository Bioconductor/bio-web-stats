""" aws_functions TODO rename this. """
import json
import logging
import boto3
import psycopg2
from botocore.exceptions import ClientError


import boto3
import logging


def aws_assume_sts_role(role_arn, role_session_name):

    try:
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

    except Exception as e:
        logging.critical(f"Could not assume AWS role {role_arn}. {e}")
        raise SystemExit(1) 

    
def get_parameter_store_values(parameter_path: str, region_name='us-east-1') -> dict:
    """Get all SSM parameter store values for a specific configuration.

    Arguments:
        parameter_path -- The prefix for the configure. Example: "/bioc/webstats/dev"

    Returns:
        A dictionary of parameter names (excluding the prefix) and their values.
    """

    try:
        ssm_client = boto3.client('ssm', region_name = region_name)
        plist = ssm_client.get_parameters_by_path(Path = parameter_path, Recursive=True)
        for item in plist["Parameters"]:
            plist = ssm_client.get_parameters_by_path(Path = parameter_path, Recursive=True)
            result = {item["Name"][len(parameter_path)+1:] : item["Value"] for item in plist["Parameters"]}
        return result

    except Exception as e:
        logging.critical(f"Failed to read AWS parameter store {parameter_path}. {e}")
        raise SystemExit(1) 


def get_secret(secret_name, region_name):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response['SecretString']
        return secret

    except Exception as e:
        logging.critical(f"Could not read AWS secret {secret_name}. {e}")
        raise SystemExit(1) 

def psql_get_connection(secret_name, region_name, database_name):
    """TODO."""

    try:
        connection_string = aws_secret_to_psql_url(secret_name, region_name, database_name)
        conn = psycopg2.connect(connection_string)
        return conn

    except Exception as e:
        logging.critical(f"Could not open psql {database_name} with {secret_name}. {e}")
        raise SystemExit(1) 


def aws_secret_to_psql_url(secret_name, region_name, database_name):
    secret = get_secret(secret_name, region_name)
    db_credentials = json.loads(secret)
    # TODO: add database name to secret in Secrets Manager
    db_credentials['dbname'] = database_name

    # Create the PostgreSQL connection string
    connection_string = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['dbname']}"
    return connection_string


def uri_to_arn(uri):
    # Parse the URI to extract the components
    scheme, path = uri.split("://", 1)
    if scheme != "awsarn":
        raise ValueError("Invalid scheme in URI: expected 'awsarn'")
    
    # Split the path into its components
    service_region, account_id, resource_type_path = path.split("/", 2)
    service, region = service_region.split(".", 1)
    
    # Construct the ARN
    arn = f"arn:aws:{service}:{region}:{account_id}:{resource_type_path}"
    
    return arn

# Example usage
# uri = "awsarn://secretsmanager.us-east-1.amazonaws.com/931729544676/secret/bioc/rdb/login/webstats_runner-fQFuUn"
# arn = uri_to_arn(uri)
# print(arn)


def arn_to_uri(arn):
    # Validate and parse the ARN
    parts = arn.split(':')
    if len(parts) != 6 or parts[0] != 'arn' or parts[1] != 'aws':
        raise ValueError("Invalid ARN format")

    # Extract the ARN components
    _, _, service, region, account_id, resource_path = parts

    # Construct the URI
    uri = f"awsarn://{service}.{region}.amazonaws.com/{account_id}/{resource_path}"
    
    return uri

# Example usage
# arn = "arn:aws:secretsmanager:us-east-1:931729544676:secret:/bioc/rdb/login/webstats_runner-fQFuUn"
# uri = arn_to_uri(arn)
# print(uri)

def cloudfront_invalidation(distribution_id, paths):
    """Invalidate Cloudfront Cache

    Keyword Arguments:
        distribution_id -- _description_ (default: {'E1TVLJONPTUXV3'})
        paths -- _description_ (default: {['/packages/stats/*']})
    """


    # TODO move distribution_id and paths defaults to flask dispatcher
    client = boto3.client('cloudfront')

    # Distribution ID and the paths you want to invalidate

    # Create the invalidation
    response = client.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': len(paths),
                'Items': paths
            },
            'CallerReference': str(hash(frozenset(paths)))  # Unique reference
        }
    )

    # TODO  from response, log error if needed, otherwise report timestamp for invalidation
