from .base import *


class DevConfig(Config):
    ''' Configuration class for site testing environment '''

    DEBUG = True
    TEST = False
    SQLALCHEMY_ECHO = True
    DATABASE_URL = 'postgresql://postgres:[]{}?@@local:5433/inform'

    FLASKS3_USE_HTTPS = False
