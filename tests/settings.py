"""Settings module for test app."""
ENV = "Development"
TESTING = True
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
DEBUG_TB_ENABLED = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False  # Allows form testing
