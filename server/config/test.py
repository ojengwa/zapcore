from .base import *


class TestConfig(Config):
    ''' Configuration class for site testing environment '''

    TESTING = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    LIVESERVER_PORT = 0
    LIVESERVER_TIMEOUT = 10
