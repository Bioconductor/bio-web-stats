# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env
import boto3

env = Env()
env.read_env()
# TODO Raise a FATAL error if no .env file is found.

# If AWS_ROLE is defined, then set the role and get the AWS parameters
AWS_ROLE = env.str('AWS_ROLE', None)

# If the environment variable AWS_ROLE exists, then get the parameters from SSM parameter Store

if AWS_ROLE is not None:
    
    # If AWS_ROLE is not the null string, then use the value to set the role name with STS
    if AWS_ROLE != '':
            

    AWS_PARAMETER_PATH = env.str('AWS_PARAMETER_PATH', None)

    if env.str('AWS_PARAMETER_PATH', None) is not None:
        ssm_client = boto3.client('ssm')
        plist = ssm_client.get_parameters_by_path(Path = AWS_PARAMETER_PATH, Recursive=True)
        param_dict = {item["Name"][len(AWS_PARAMETER_PATH)+1:] : item["Value"] for item in plist["Parameters"]}
        pass

    # TODO PROCESS param_dict and store in variables as appropriate

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SECRET_KEY = env.str("SECRET_KEY")
SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT")
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "SimpleCache"  # Can be "MemcachedCache", "RedisCache", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
URI_PATH_PREFIX = "/packages/stats"

