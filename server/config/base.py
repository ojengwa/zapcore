import os

from urllib.parse import urlparse


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
    # Mail settings
    MAIL_SERVER = 'smtp.mailgun.org'
    MAIL_PORT = 587
    MAIL_USERNAME = 'postmaster@myinform.mailgun.org'
    MAIL_PASSWORD = 'myinform'
    DEFAULT_MAIL_CHANNEL = 'mailgun'
    MAIL_DEFAULT_SENDER = 'daemon@inform.com'
    MAIL_SUPPRESS_SEND = True
    MAIL_FAIL_SILENTLY = False
    UPLOADS_DEFAULT_DEST = os.path.join(
        os.path.dirname(os.path.abspath(__name__)), 'uploads')
    CLOUDFILES_USERNAME = 'inform'
    CLOUDFILES_API_KEY = '80a129ef023b8027f4ba4523786feacf'

    PROTOCOL = 'http://'

    ADMIN_USERNAME = 'inform'
    ADMIN_PASSWORD = 'inform'
    ADMIN_EMAIL = 'admin@verifi.ng'
    ADMIN_FULL_NAME = 'Inform Admin'

    ASSETS_DEBUG = False  # not DEBUG

    NAMEKO_AMQP_URI = os.getenv('NAMEKO_AMQP_URI',
                                'amqp://localhost')
    NAMEKO_INITIAL_CONNECTIONS = 3
    NAMEKO_MAX_CONNECTIONS = 10

    REDIS_URL = os.getenv(
        'REDIS_URL',
        'redis://redistogo:f8a84dd02ddd32d65d9ae643a8f25543'
        '@jack.redistogo.com:11455/')

    if REDIS_URL:
        url = urlparse(REDIS_URL)
        REDIS_HOST = url.hostname
        REDIS_PORT = url.port
        REDIS_PASSWORD = url.password

    CELERY_TIMEZONE = 'Africa/Lagos'

    LOGFILE_NAME = 'inform'

    LOGIN_VIEW = 'auth.login'

    # DOMAIN = 'inform.dev:2500'

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

    SETUP_DIR = os.path.join(os.path.dirname(
        os.path.abspath(__name__)), 'setup/')

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))

    TEMPLATE_DIR = os.path.join(os.path.dirname(
        os.path.abspath(__name__)), 'templates/')
    STATIC_DIR = os.path.join(os.path.dirname(
        os.path.abspath(__name__)), 'static/')
