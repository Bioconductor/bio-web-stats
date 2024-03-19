import os

class Config(object):
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AWS_PARAMETER_PATH='/bioc/webstats/dev'
    LOG_LEVEL="warning"
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = "SimpleCache"  # Can be "MemcachedCache", "RedisCache", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    URI_PATH_PREFIX = "/packages/stats"
    SECRET_KEY = ''

class ProdConfig(Config):
    ENV="production"
    DATABASE_URL=""
    # TODO Temporarily harrd-coded to sandbox rds cluster
    SEND_FILE_MAX_AGE_DEFAULT=0

class DevConfig(Config):
    ENV="development"
    DEVELOPMENT=True
    TESTING=True
    LOG_LEVEL="debug"
    SEND_FILE_MAX_AGE_DEFAULT=31556926
    DATABASE_URL="sqlite:///dev.db"
    
