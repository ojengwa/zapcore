from urllib.request import urlopen
from flask import current_app

from server.tests import BaseTestCase


class MainBlueprintTest(BaseTestCase):
    """docstring for BasicTest"""

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_server_is_up_and_running(self):
        print(self.get_server_url())
        response = urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)
