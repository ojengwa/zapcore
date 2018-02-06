from flask import current_app

from server.tests import BaseTestCase


class DevConfigTest(BaseTestCase):
    """docstring for BasicTest"""

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])


class TestConfigTest(BaseTestCase):
    """docstring for BasicTest"""

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])


class StagingConfigTest(BaseTestCase):
    """docstring for BasicTest"""

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])


class ProductionConfigTest(BaseTestCase):
    """docstring for BasicTest"""

    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
