import os

"""The configuration dictionary establishes application specific configuration parameters
and nmaps hierarchical names to flask names
"""
configuration_dictionary = [
    {
        "Name": "db/dbname",
        "FlaskName": "DBNAME",
        "Type": "String",
        "Value": "webstats",
        "Description": "Postgres database name, default 'webstats'",
    },
    {
        "Name": "db/credentials",
        "FlaskName": "DBCREDENTIALS",
        "Type": "String",
        "Value": "arn:aws:secretsmanager:reference-to-database-credentials-secret",
        "Description": "arn tof secrets manager secret",
    },
    {
        "Name": "db/dbuser",
        "FlaskName": "DBUSER",
        "Type": "String",
        "Value": "webstats_runner",
        "Description": "PostgrSQL user name, default 'webstats_runner'",
    },
    {
        "Name": "db/port",
        "FlaskName": "DBPORT",
        "Type": "String",
        "Value": "5432",
        "Description": "Server endpoint port number",
    },
    {
        "Name": "db/server",
        "FlaskName": "DBSERVER",
        "Type": "String",
        "Value": "TBD",
        "Description": "The symbolic address of the endpoint for the Postgres server",
    },
    {
        "Name": "flask/flask_app",
        "FlaskName": "APP",
        "Type": "String",
        "Value": "bioc_webstats.app:create_app('development')",
        "Description": "Default initiation call for Flask",
    },
    {
        "Name": "flask/approot",
        "FlaskName": "APPROOT",
        "Type": "String",
        "Value": "/var/www/webstats",
        "Description": "Working directory for app",
    },
    {
        "Name": "flask/logroot",
        "FlaskName": "LOGROOT",
        "Type": "String",
        "Value": "/var/log/bioc-webstats",
        "Description": "Location of log files for the app",
    },
    {
        "Name": "flask/osgroup",
        "FlaskName": "OSGROUP",
        "Type": "String",
        "Value": "webstats",
        "Description": "Execution group name",
    },
    {
        "Name": "flask/osuser",
        "FlaskName": "OSUSER",
        "Type": "String",
        "Value": "webstats",
        "Description": "Execution user name",
    },
    {
        "Name": "flask/flask_debug",
        "FlaskName": "DEBUG",
        "Type": "String",
        "Value": "FALSE",
        "Description": "False' Caution: Do not enable in production",
    },
    {
        "Name": "flask/log_level",
        "FlaskName": "LOG_LEVEL",
        "Type": "String",
        "Value": "INFO",
        "Description": "Standard log levels, default 'INFO'",
    },
    {
        "Name": "flask/secret_key",
        "FlaskName": "SECRET_KEY",
        "Type": "String",
        "Value": "TBD",
        "Description": "Secret key for activating web client flask debugging tools",
    },
]


class Config(object):
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_LEVEL = "INFO"
    LOG_NAME = 'webstats'
    LOG_FILEPATH = '/var/log/bioc-webstats/webstats.log'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = "SimpleCache"  # Can be "MemcachedCache", "RedisCache", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    URI_PATH_PREFIX = "/packages/stats"
    SECRET_KEY = ''

class productionConfig(Config):
    ENV="production"
    DATABASE_URL=os.getenv('DATABASE_URL', '')
    DEVELOPMENT=False
    TESTING=False
    AWS_PATH_PARAMETER='/bioc/webstats/prod'
    # TODO Temporarily harrd-coded to sandbox rds cluster
    SEND_FILE_MAX_AGE_DEFAULT=0

class developmentConfig(Config):
    ENV="development"
    DEVELOPMENT=True
    TESTING=True
    LOG_LEVEL="DEBUG"
    AWS_PATH_PARAMETER='/bioc/webstats/dev'
    # TODO Temporarily harrd-coded to sandbox rds cluster
    LOG_FILEPATH = './instance/webstats.log'
    SEND_FILE_MAX_AGE_DEFAULT=31556926
    DATABASE_URL = os.getenv('DATABASE_URL', "sqlite:///dev.db")

class debugConfig(Config):
    # TODO Create a Debug ENV value
    ENV = "development"
    TESTING = True
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'
    LOG_FILEPATH = './instance/webstats.log'
    DEBUG_TB_ENABLED = False
    CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Allows form testing
