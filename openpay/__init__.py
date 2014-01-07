from __future__ import unicode_literals
from future.builtins import str

api_key = None
merchant_id = None

production = False

api_version = None
verify_ssl_certs = True

# Resource
from openpay.resource import (  # noqa
    Card, Charge, Customer, Plan, Transfer,
    Fee, BankAccount, Payout, Subscription)

# Error imports.  Note that we may want to move these out of the root
# namespace in the future and you should prefer to access them via
# the fully qualified `openpay.error` module.

from openpay.error import (  # noqa
    OpenpayError, APIError, APIConnectionError, AuthenticationError, CardError,
    InvalidRequestError)


#from openpay.resource import (
#    convert_to_openpay_object, BaseObject, APIResource)
#from openpay.util import logger

import sys as _sys
#import warnings as _warnings
#from inspect import isclass as _isclass, ismodule as _ismodule

_dogetattr = object.__getattribute__
_ALLOWED_ATTRIBUTES = (
    'api_key',
    'api_base',
    'api_version',
    'verify_ssl_certs',
    'TEST_MODE',
)
_original_module = _sys.modules[__name__]


def get_api_base():
    if not production:
        api_base = str("https://sandbox-api.openpay.mx")
    else:
        api_base = str("https://api.openpay.mx")

    return api_base
