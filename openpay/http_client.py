from __future__ import unicode_literals
from future.builtins import str
from future.builtins import bytes

import os
import sys
import textwrap
import warnings

from openpay import error

# - Requests is the preferred HTTP library
# - Google App Engine has urlfetch
# - Use Pycurl if it's there (at least it verifies SSL certs)
# - Fall back to urllib2 with a warning if needed
try:
    import urllib2
    # import contextlib
except ImportError:
    import urllib.request
    import urllib.error

try:
    # base64.encodestring is deprecated in Python 3.x
    from base64 import encodebytes
except ImportError:
    # Python 2.x
    from base64 import encodestring as encodebytes

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


def new_default_http_client(*args, **kwargs):
    if urlfetch:
        impl = UrlFetchClient
    elif requests:
        impl = RequestsClient
    elif pycurl:
        impl = PycurlClient
    else:
        impl = Urllib2Client
        warnings.warn(
            "Warning: the Openpay library is falling back to urllib2/urllib "
            "because neither requests nor pycurl are installed. "
            "urllib2's SSL implementation doesn't verify server "
            "certificates. For improved security, we suggest installing "
            "requests.")

    return impl(*args, **kwargs)


class HTTPClient(object):

    def __init__(self, verify_ssl_certs=True):
        self._verify_ssl_certs = verify_ssl_certs

    def request(self, method, url, headers, post_data=None, user=None):
        raise NotImplementedError(
            'HTTPClient subclasses must implement `request`')


class RequestsClient(HTTPClient):
    name = 'requests'

    def request(self, method, url, headers, post_data=None, user=None):
        kwargs = {}

        if self._verify_ssl_certs:
            kwargs['verify'] = os.path.join(
                os.path.dirname(__file__), 'data/ca-certificates.crt')
        else:
            kwargs['verify'] = False

        try:
            try:
                result = requests.request(method,
                                          url,
                                          headers=headers,
                                          data=post_data,
                                          timeout=80,
                                          auth=(user, ''),
                                          ** kwargs)
            except TypeError as e:
                raise TypeError(
                    'Warning: It looks like your installed version of the '
                    '"requests" library is not compatible with Openpay\'s '
                    'usage thereof. (HINT: The most likely cause is that '
                    'your "requests" library is out of date. You can fix '
                    'that by running "pip install -U requests".) The '
                    'underlying error was: %s' % (e,))

            # This causes the content to actually be read, which could cause
            # e.g. a socket timeout. TODO: The other fetch methods probably
            # are succeptible to the same and should be updated.
            content = result.content

            status_code = result.status_code
        except Exception as e:
            # Would catch just requests.exceptions.RequestException, but can
            # also raise ValueError, RuntimeError, etc.
            self._handle_request_error(e)
        return content, status_code

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = ("Unexpected error communicating with Openpay.  "
                   "If this problem persists, let us know at "
                   "support@openpay.mx.")
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = ("Unexpected error communicating with Openpay. "
                   "It looks like there's probably a configuration "
                   "issue locally.  If this problem persists, let us "
                   "know at support@openpay.mx.")
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise error.APIConnectionError(msg)


class UrlFetchClient(HTTPClient):
    pass


class PycurlClient(HTTPClient):
    pass


class Urllib2Client(HTTPClient):
    if sys.version_info >= (3, 0):
        name = 'urllib.request'
    else:
        name = 'urllib2'

    def request(self, method, url, headers, post_data=None, user=None):
        if sys.version_info >= (3, 0) and isinstance(post_data, str):
            post_data = post_data.encode('utf-8')

        if sys.version_info >= (3, 0):
            req = urllib.request.Request(url, post_data, headers)
            user_string = '%s:%s' % (user, '')
            base64string = encodebytes(bytes(user_string, encoding='utf-8'))
            base64string = base64string.decode('utf-8').replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)

            if method not in ('get', 'post'):
                req.get_method = lambda: method.upper()

            try:
                with urllib.request.urlopen(req) as response:
                    rbody = response.read()
                    rcode = response.code
            except urllib.error.HTTPError as e:
                rcode = e.code
                rbody = e.read()
            except (urllib.error.URLError, ValueError) as e:
                self._handle_request_error(e)
            return rbody, rcode
        else:
            req = urllib2.Request(url, post_data, headers)
            base64string = encodebytes('%s:%s' % (user, ''))
            auth_string = "Basic %s" % base64string
            auth_string = auth_string.replace('\n', '')
            req.add_header("Authorization", auth_string)

            if method not in ('get', 'post'):
                req.get_method = lambda: method.upper()

            try:
                response = urllib2.urlopen(req)
                rbody = response.read()
                rcode = response.code
            except urllib2.HTTPError as e:
                rcode = e.code
                rbody = e.read()
            except (urllib2.URLError, ValueError) as e:
                self._handle_request_error(e)
            return rbody, rcode

    def _handle_request_error(self, e):
        msg = ("Unexpected error communicating with Openpay. "
               "If this problem persists, let us know at support@openpay.mx.")
        msg = textwrap.fill(msg) + "\n\n(Network error: " + str(e) + ")"
        raise error.APIConnectionError(msg)
