import os
import sys
import textwrap
import warnings

# - Requests is the preferred HTTP library
# - Google App Engine has urlfetch
# - Use Pycurl if it's there (at least it verifies SSL certs)
# - Fall back to urllib2 with a warning if needed
try:
    import urllib2
except ImportError:
    pass

try:
    import pycurl
except ImportError:
    pycurl = None

try:
    import requests
except ImportError:
    requests = None

try:
    from google.appengine.api import urlfetch
except ImportError:
    urlfetch = None


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
