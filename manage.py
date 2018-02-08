#! /usr/bin/env python

import os


import flask_s3
from flask_script import Manager
from flask_script import Shell

from server.app import create_app


application = create_app(
    'zapcore',
    os.getenv('FLASK_SETTINGS_MODULE',
              'server.config.DevConfig'))


# Initializing script manager
manager = Manager(application)
manager.help_args = ('-h', '-?', '--help')


def make_shell_context():
    """
    Automatically import application objects into interactive
    shell.
    """
    return dict(app=application)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def runserver():
    """ Start the server"""
    application.run()


@manager.command
def test():
    """
    Run the unit tests.
    """
    import unittest
    tests = unittest.TestLoader().discover('server/tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def collectstatic():
    """ Uploads static assets to Amazon s3 """
    application.logger.info("Starting static files uploads ")
    flask_s3.create_all(application)
    application.logger.info("Static files upload complete")


if __name__ == "__main__":
    manager.run()
