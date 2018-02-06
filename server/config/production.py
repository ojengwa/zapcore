from .base import *


class ProdConfig(Config):
    ''' Configuration class for site testing environment '''

    # DOMAIN = 'inform.verifi.ng'
    # SERVER_NAME = 'Inform Dashboard'
    DEBUG = False
    TEST = False
    SQLALCHEMY_ECHO = False
    DATABASE_URL = 'postgresql://postgres:[]{}?@@inform:5433/inform'
    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb://heroku_gs38cfwx:dui5dhnfogtq16i0s561fbnojv@ds137435.'
        'mlab.com:37435/heroku_gs38cfwx')

    LOGIN_VIEW = 'auth.login'

    MAX_RETRY_COUNT = 3

    NAMEKO_AMQP_URI = os.getenv(
        'NAMEKO_AMQP_URI',
        'amqp://rvugybhn:ztDYBviBEQCg-8o_O7jgtjIGABFWF44O@impala.rmq.'
        'cloudamqp.com/rvugybhn')
    NAMEKO_INITIAL_CONNECTIONS = 2
    NAMEKO_MAX_CONNECTIONS = 5

    # Configuring sentry logging
    SENTRY_DSN = os.getenv(
        'SENTRY_DSN',
        'http://d2793cd20be84b32a0f0af8e3750e8de:6e86677'
        'a4645400d9e1a7575aaa5d94b@sentry.blustair.com/4')
    SENTRY_INCLUDE_PATHS = ['inform']
    SENTRY_USER_ATTRS = ['username', 'full_name', 'email']

    # FLASKS3_USE_HTTPS = True
