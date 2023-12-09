
import boto3
from botocore.exceptions import ClientError
import json
import psycopg2

# TODO Role/Credentials
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
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return secret

# TODO REFACTOR
secret_name = "rds-db-credentials/cluster-BFK2EVT2EFIRT4B5XVC6PDOXIQ/postgres/1701682809099"
region_name = "us-east-1"
database_name = 'webstats'

    
def psql_get_connection(secret_name=secret_name, region_name=region_name, database_name=database_name):
    """TODO."""
    secret = get_secret(secret_name, region_name)
    db_credentials = json.loads(secret)
    # TODO: add database name to secret in Secrets Manager
    db_credentials['dbname'] = database_name

    # Create the PostgreSQL connection string
    connection_string = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['dbname']}"

    # Use the connection string to connect to your database
    # Example: using psycopg2
    conn = psycopg2.connect(connection_string)
    return conn
