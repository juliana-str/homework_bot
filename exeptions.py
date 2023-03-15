from requests import RequestException


class SendMessageError(BaseException):
    """ Base class for send message errors. """

    def __init__(self, *args, **kwargs):
        pass


class GetAPIExeption(RequestException):
    """ Base class for get API errors. """

    def __init__(self, *args, **kwargs):
        pass
