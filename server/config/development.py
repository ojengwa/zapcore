from .base import *


class DevConfig(Config):
    ''' Configuration class for site testing environment '''

    DEBUG = True
    TEST = False

    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = (
        'mysql://root:@localhost/zapacore')

    FLASKS3_USE_HTTPS = False
