from .base import *


class StagingConfig(Config):
    ''' Configuration class for site development environment '''

    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL')
    MAX_RETRY_COUNT = 3

    SECRET_KEY = os.getenv('SECRET_KEY')
