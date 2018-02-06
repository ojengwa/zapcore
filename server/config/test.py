from .base import *


class TestConfig(Config):
    ''' Configuration class for site testing environment '''

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True
    SQLALCHEMY_ECHO = True

    LIVESERVER_PORT = 0
    LIVESERVER_TIMEOUT = 10
