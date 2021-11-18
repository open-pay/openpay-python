from __future__ import unicode_literals
from future.builtins import str
from openpay.util import logger
api_key = None
merchant_id = None
production = False
api_version = None
verify_ssl_certs = True
country = "mx"
# Resource

from openpay.resource import (  # noqa
    Card, Charge, Customer, Plan, Transfer,
    Fee, BankAccount, Payout, Subscription, Pse, Token, Checkout, Webhook)

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
    api_base = None
    if country is None or (country != "mx" and country != "co" and country != "pe"):
        errorMessage = "Country is " + country + ", you can set country with value 'mx', 'co' or 'pe', Mexico, Colombia or Peru respectively"
        logger.error(errorMessage)
        raise error.InvalidCountryError(errorMessage, None, None, 400, None)
    if country == "mx":
        logger.info("Country Mexico")
        if not production:
            api_base = str("https://sandbox-api.openpay.mx")
        else:
            api_base = str("https://api.openpay.mx")
    if country == "co":
        logger.info("Country Mexico")
        if not production:
            api_base = str("https://sandbox-api.openpay.co")
        else:
            api_base = str("https://api.openpay.co")
    if country == "pe":
        logger.info("Country Peru")
        if not production:
            api_base = str("https://sandbox-api.openpay.pe")
        else:
            api_base = str("https://api.openpay.pe")
    return api_base
