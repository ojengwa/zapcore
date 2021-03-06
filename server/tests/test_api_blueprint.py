from __future__ import absolute_import
from flask import current_app

from server.tests import BaseTestCase


class APIBlueprintTest(BaseTestCase):
    """docstring for BasicTest"""

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
