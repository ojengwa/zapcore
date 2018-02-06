from flask_testing import LiveServerTestCase

from server.app import create_app as _create_app


FLASK_SETTINGS_MODULE = 'server.config.TestConfig'


class BaseTestCase(LiveServerTestCase):

    render_templates = False

    def create_app(self):

        app = _create_app(__name__, FLASK_SETTINGS_MODULE)
        return app

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        self.app_context.pop()
