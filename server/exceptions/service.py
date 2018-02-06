import json


class ServiceException(Exception):
    '''

    Exception to raise at the caller if an exception\
     occurred in the remote worker.

    Extends:
        Exception

    '''

    message = 'Service Exception'

    def __init__(self, message=None):
        self.feedback = dict(message=self.message)
        self.feedback['exc_type'] = self.__class__.__name__
        self.feedback['origin'] = 'site-service'
        if message is not None:
            self.feedback['message'] = message

        message = '{}'.format(json.dumps(self.feedback))
        super(ServiceException, self).__init__(message)


class NotFound(ServiceException):
    '''This error should be raise when element is not found in resource.'''
    message = 'Item not found'


class NoArgument(ServiceException):
    '''This error should be raise when no specified parameters are send.'''
    message = 'Invalid argument'


class Error(ServiceException):
    '''This error should be raise when any different error does not fit.'''
    message = 'Error'


class ElementExists(ServiceException):
    '''This error should be raise when an element already exist in db.'''
    message = 'Item already exists'
