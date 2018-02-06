from logging import getLogger
from os import environ
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from .base import Config

logger = getLogger(__name__)


class HerokuConfig(Config):
    ''' Configuration class for site development environment '''

    DOMAIN = 'inform-docs.herokuapps.com'
    DATABASE_URL = environ.get('DATABASE_URL')
    MONGODB_URI = environ.get('MONGODB_URI')

    MAX_RETRY_COUNT = 3

    SECRET_KEY = environ.get('SECRET_KEY')

    # Sentry
    SENTRY_DSN = environ.get('SENTRY_DSN')

    # Exceptional
    EXCEPTIONAL_API_KEY = environ.get('EXCEPTIONAL_API_KEY')

    NAMEKO_AMQP_URI = environ.get('CLOUDAMQP_URL')

    if 'RABBITMQ_URL' in environ:
        BROKER_URL = environ.get('RABBITMQ_URL')

    # Celery w/ RedisCloud
    elif 'REDISCLOUD_URL' in environ:
        BROKER_URL = environ.get('REDISCLOUD_URL')
        BROKER_TRANSPORT = environ.get('REDISCLOUD_URL')

    # Mailgun
    if 'MAILGUN_SMTP_SERVER' in environ:
        SMTP_SERVER = environ.get('MAILGUN_SMTP_SERVER')
        SMTP_LOGIN = environ.get('MAILGUN_SMTP_LOGIN')
        SMTP_PASSWORD = environ.get('MAILGUN_SMTP_PASSWORD')
        MAIL_SERVER = environ.get('MAILGUN_SMTP_SERVER')
        MAIL_USERNAME = environ.get('MAILGUN_SMTP_LOGIN')
        MAIL_PASSWORD = environ.get('MAILGUN_SMTP_PASSWORD')
        MAIL_USE_TLS = True
    # SendGrid
    elif 'SENDGRID_USERNAME' in environ:
        SMTP_SERVER = 'smtp.sendgrid.net'
        SMTP_LOGIN = environ.get('SENDGRID_USERNAME')
        SMTP_PASSWORD = environ.get('SENDGRID_PASSWORD')
        MAIL_SERVER = 'smtp.sendgrid.net'
        MAIL_USERNAME = environ.get('SENDGRID_USERNAME')
        MAIL_PASSWORD = environ.get('SENDGRID_PASSWORD')
        MAIL_USE_TLS = True
    # Postmark
    elif 'POSTMARK_SMTP_SERVER' in environ:
        SMTP_SERVER = 'POSTMARK_SMTP_SERVER'
        SMTP_LOGIN = environ.get('POSTMARK_API_KEY')
        SMTP_PASSWORD = environ.get('POSTMARK_API_KEY')
        MAIL_SERVER = 'POSTMARK_SMTP_SERVER'
        MAIL_USERNAME = environ.get('POSTMARK_API_KEY')
        MAIL_PASSWORD = environ.get('POSTMARK_API_KEY')
        MAIL_USE_TLS = True

    # Heroku Redis
    redis_url = environ.get('REDIS_URL')
    if redis_url:
        url = urlparse(redis_url)
        REDIS_HOST = url.hostname
        REDIS_PORT = url.port
        REDIS_PASSWORD = url.password

    # Redis To Go
    redis_url = environ.get('REDISTOGO_URL')
    if redis_url:
        url = urlparse(redis_url)
        REDIS_HOST = url.hostname
        REDIS_PORT = url.port
        REDIS_PASSWORD = url.password

    cloudant_uri = environ.get('CLOUDANT_URL')
    if cloudant_uri:
        COUCHDB_SERVER = cloudant_uri

    # Memcachier
    CACHE_MEMCACHED_SERVERS = environ.get('MEMCACHIER_SERVERS')
    CACHE_MEMCACHED_USERNAME = environ.get('MEMCACHIER_USERNAME')
    CACHE_MEMCACHED_PASSWORD = environ.get('MEMCACHIER_PASSWORD')
