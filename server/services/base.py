from flask import current_app as app

from ..providers.config import Config


rpc = app.rpc


class BaseService(object):
    name = 'auths_service'

    config = Config()

    @rpc
    def create(self, *args, **kwargs):
        '''
            For creating new resource.

        '''

        raise NotImplementedError

    @rpc
    def report(self, bvn, *args, **kwargs):
        '''
            For reporting streams of record identified by the BVN
        '''

        raise NotImplementedError

    @rpc
    def score(self, bvn):
        '''
            Get bucket score for the profile identified by the BVN
        '''

        raise NotImplementedError
