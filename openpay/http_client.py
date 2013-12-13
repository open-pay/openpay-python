import os
import sys
import textwrap
import warnings


class HTTPClient(object):
    pass


class RequestsClient(HTTPClient):
    pass


class UrlFetchClient(HTTPClient):
    pass


class PycurlClient(HTTPClient):
    pass


class Urllib2Client(HTTPClient):
    pass
