import logging
import os

from flask import Flask
from flask_assets import Environment
from flask_compress import Compress
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from raven.contrib.flask import Sentry

from .extensions.allows import Allows
from .extensions.babel import Babel
from .extensions.gzip import Gzip
# from .extensions.minify import HTMLMIN
from .extensions.redis import RedisExtension
from .extensions.response import Response

from .providers.proxies import FlaskPooledClusterRpcProxy

from pymongo import MongoClient

# App factories
SENTRY_DSN = ('https://00d8a063e7cc433f8fd0821fc8432c33:'
              'dfd25db9211a4f08a79aba497ba423ea@sentry.io/272338')


mail = Mail()
moment = Moment()
compress = Compress()
csrf = CSRFProtect()
# minify = HTMLMIN()

login_manager = LoginManager()
login_manager.session_protection = 'strong'  # use strong session protection
login_manager.login_view = 'auth.login'


class FlaskVue(Flask):
    """docstring for FlaskVue"""

    # Change jinja2 template variable marker
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='{%',
        block_end_string='%}',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='{#',
        comment_end_string='#}',
    ))


def create_app(app_name, config_obj):
    """ Generates and configures the main shop application. All additional """
    # Launching application
    factory = FlaskVue(app_name,
                       static_folder="dist/static",
                       template_folder="dist")
    factory.config.from_object(config_obj)

    moment.init_app(factory)

    csrf.init_app(factory)

    # register 'main' blueprint
    from .views.main import main as main_blueprint
    factory.register_blueprint(main_blueprint)

    # register 'api' blueprint
    from .views.api import api as api_blueprint
    factory.register_blueprint(api_blueprint, url_prefix='/_api')

    # Add RPC proxy
    rpc = FlaskPooledClusterRpcProxy(factory)

    factory.rpc = rpc

    db_client = MongoClient(factory.config.get('MONGODB_URI'))

    factory.db = db_client.get_database()

    # add CORS support
    CORS(factory)

    # add GZip support
    Gzip(factory)

    # Assets
    Environment(factory)

    # Authorisation decorator
    Allows(factory)

    # Redis extension
    redis = RedisExtension(
        factory, **{'decode_responses': True,
                    'charset': 'utf-8'})

    factory.redis = redis._redis_client

    # Add custom response formatter
    Response(factory)

    # Add translation support
    Babel(factory)

    # Initialize Logging
    if factory.debug:
        from logging.handlers import RotatingFileHandler
        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(factory)
        os.environ.setdefault('FLASK_SETTINGS_MODULE', 'app.config.DevConfig')
        file_handler = RotatingFileHandler(
            "%s/logs/%s.log" % (
                factory.config.get('BASE_DIR'),
                factory.config.get(
                    "LOGFILE_NAME",
                    app_name)),
            maxBytes=500 * 1024)

        file_handler.setLevel(logging.WARNING)
        from logging import Formatter
        file_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        factory.logger.addHandler(file_handler)
    else:
        # from flask_sslify import SSLify
        # SSLify(factory)
        # Enable Sentry logging
        sentry = Sentry(
            app=factory, dsn=SENTRY_DSN,
            logging=True, level=logging.WARN)
        factory.sentry = sentry

    return factory
