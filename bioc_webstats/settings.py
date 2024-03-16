# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.

See https://pypi.org/project/environs/ for more information.
"""
import os
from environs import Env
import boto3

def get_str(target, default):
    """Get parameter from SSM parameter store if present, otherwise from Env()"""
    if target in param_dict:
        return param_dict[target]
    return env.str(target, default)

env = Env()
env.read_env()

# Do we have a parameter set in AWS SSM Parameter Store?
AWS_PARAMETER_PATH = env.str('AWS_PARAMETER_PATH', None)
if env.str('AWS_PARAMETER_PATH', None) is  None:
    param_dict = {}
else:
    # Yes Add the values to the parameter set
    ssm_client = boto3.client('ssm')
    plist = ssm_client.get_parameters_by_path(Path = AWS_PARAMETER_PATH, Recursive=True)
    # HACK Start from the top with SSM paramater store included
    for item in plist["Parameters"]:
        plist = ssm_client.get_parameters_by_path(Path = AWS_PARAMETER_PATH, Recursive=True)
        param_dict = {item["Name"][len(AWS_PARAMETER_PATH)+1:] : item["Value"] for item in plist["Parameters"]}

# TODO Refactor Parameter store config variables to match local
# TODO Complete parameters
# TODO Secret manager for database values

ENV = get_str("FLASK_ENV", default="production")
DEBUG = get_str('DEBUG', ENV == "development")
SQLALCHEMY_DATABASE_URI = get_str("DATABASE_URL")
SECRET_KEY = get_str("SECRET_KEY")
SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT")
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "SimpleCache"  # Can be "MemcachedCache", "RedisCache", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
URI_PATH_PREFIX = "/packages/stats"

