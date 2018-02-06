from .base import *


class ProdConfig(Config):
    ''' Configuration class for site testing environment '''

    # DOMAIN = 'inform.verifi.ng'
    # SERVER_NAME = 'Inform Dashboard'
    DEBUG = False
    TEST = False
    SQLALCHEMY_ECHO = False

    MAX_RETRY_COUNT = 3

    FLASKS3_USE_HTTPS = True
