import os

class Config(object):
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_LEVEL="warning"
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = "SimpleCache"  # Can be "MemcachedCache", "RedisCache", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    URI_PATH_PREFIX = "/packages/stats"
    SECRET_KEY = ''

class ProductionConfig(Config):
    ENV="Production"
    DATABASE_URL=""
    AWS_PARAMETER_PATH='/bioc/webstats/prod'
    # TODO Temporarily harrd-coded to sandbox rds cluster
    SEND_FILE_MAX_AGE_DEFAULT=0

class DevelopmentConfig(Config):
    ENV="Development"
    DEVELOPMENT=True
    TESTING=True
    LOG_LEVEL="debug"
    SEND_FILE_MAX_AGE_DEFAULT=31556926
    DATABASE_URL="sqlite:///dev.db"
