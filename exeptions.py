from requests import RequestException


class SendMessageError(Exception):
    """ Base class for send message errors. """

    def __init__(self, *args, **kwargs):
        pass


class GetAPIError(RequestException):
    """ Base class for get API errors. """

    def __init__(self, *args, **kwargs):
        pass
