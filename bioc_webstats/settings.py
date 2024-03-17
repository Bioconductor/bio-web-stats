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
import bioc_webstats.aws_functions as aws

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
    param_dict = aws.get_parameter_store_values(AWS_PARAMETER_PATH)
    # TODO Transform leaf names to upper case and match .env idnetifiers
    # TODO database connection from db/creentoials viz. DATABASE_URL
    
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

