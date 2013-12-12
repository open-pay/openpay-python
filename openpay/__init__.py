"""
Openpay python bindings

API docs http://www.openpay.mx/api-v1/
Author: Carlos Aguilar <caguilar@dwdandsolutions.com>
"""

api_key = None

TEST_MODE = False

if TEST_MODE:
    api_base = "https://sandbox-api.openpay.mx/"
else:
    api_base = "https://api.openpay.mx"

_ALLOWED_ATTRIBUTES = (
    'api_key',
    'api_base',
    'api_version',
    'verify_ssl_certs',
    'TEST_MIRROR',
)