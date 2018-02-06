from .base import BaseService
from flask import current_app as app


class AuthService(BaseService):

    @app.rpc
    def get(self, data):
        pass

    @app.rpc
    def save(self, data):
        pass
