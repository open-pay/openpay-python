"""
Openpay python bindings

API docs http://www.openpay.mx/api-v1/
Author: Carlos Aguilar <caguilar@dwdandsolutions.com>
"""

api_key = None

test_mode = None

api_version = None
verify_ssl_certs = True

from openpay.resource import (
	convert_to_openpay_object, BaseObject, APIResource)
from openpay.util import logger

import sys as _sys
import warnings as _warnings
from inspect import isclass as _isclass, ismodule as _ismodule

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
	if test_mode:
	    api_base = "https://sandbox-api.openpay.mx"
	else:
	    api_base = "https://api.openpay.mx"

	return api_base
