import os
from logging import getLogger


logger = getLogger(__name__)


class Config(object):
    '''
    Base configuration class. Subclasses should include configurations for
    testing, development and production environments

    '''

    DEBUG = True
    FLASK_DEBUG = 1

    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        '\x91c~\xc0-\xe3\'f\xe19PE\x91`6\x01/\x0c\xed\\\xbdk\xf8')

    SQLALCHEMY_ECHO = False
    DATABASE_URL = os.getenv('DATABASE_URL')
    PROTOCOL = 'http://'

    ASSETS_DEBUG = False  # not DEBUG

    LOGFILE_NAME = 'zapcore'

    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY', 'AKIAI7KGQ4FVKQ5EV3LA')

    AWS_SECRET_ACCESS_KEY = os.getenv(
        'AWS_SECRET_KEY', '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')

    FLASKS3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'zapcore')

    FLASK_ASSETS_USE_S3 = True
    FLASKS3_USE_HTTPS = True
    USE_S3 = True
    FLASKS3_HEADERS = {
        'Expires': 'Thu, 15 Apr 2020 20:00:00 GMT',
        'Cache-Control': 'max-age=86400'
    }
    USE_S3_DEBUG = not USE_S3

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
