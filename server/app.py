import logging

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_s3 import FlaskS3
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from raven.contrib.flask import Sentry

from .extensions.gzip import Gzip
from .extensions.json import JSONEncoder

SENTRY_DSN = ('https://00d8a063e7cc433f8fd0821fc8432c33:'
              'dfd25db9211a4f08a79aba497ba423ea@sentry.io/272338')


s3 = FlaskS3()
csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()


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
    factory.json_encoder = JSONEncoder
    factory.config.from_object(config_obj)

    db.init_app(factory)
    s3.init_app(factory)
    csrf.init_app(factory)
    migrate.init_app(factory, db)

    # register 'main' blueprint
    from .views.main import main as main_blueprint
    factory.register_blueprint(main_blueprint)

    # register 'api' blueprint
    from .views.api import api as api_blueprint
    factory.register_blueprint(api_blueprint, url_prefix='/_api')

    # add GZip support
    Gzip(factory)

    # Initialize Logging
    if factory.debug:
        from logging.handlers import RotatingFileHandler
        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(factory)

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

        sentry = Sentry(
            app=factory, dsn=SENTRY_DSN,
            logging=True, level=logging.WARN)
        factory.sentry = sentry

    return factory
