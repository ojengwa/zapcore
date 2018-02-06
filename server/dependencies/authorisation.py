import jwt

from nameko.extensions import DependencyProvider
from os import environ


class Authorization(DependencyProvider):
    """ DependencyProvider giving services access to the current session.
    """

    class Api:

        def __init__(self, token):
            self._token = token
            self._session = None

        @property
        def session(self):
            if self._session is None:
                # lazily decode the token
                self._session = jwt.decode(self._token, environ['SECRET_KEY'])
            return self._session

        @property
        def username(self):
            return self.session['username']

        def user_is(self, role):
            return role in self.session['roles']

        def user_can(self, perm):
            return perm in self.session['permissions']

    def get_dependency(self, worker_ctx):
        return Authorization.Api(worker_ctx.context_data.get('session'))
