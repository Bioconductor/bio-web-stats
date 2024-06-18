from decouple import config

# Flask configuration
ENV = config('FLASK_ENV', default='Production')
DEBUG = ENV == 'Development'
SEND_FILE_MAX_AGE_DEFAULT = 0
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = config('SQLALCHEMY_DATABASE_URI', default='sqlite:///development.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Cache configuration
CACHE_TYPE = config('CACHE_TYPE', default='SimpleCache')