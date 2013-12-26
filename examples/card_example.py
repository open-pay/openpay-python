import sys
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
print openpay.Customer.retrieve('amce5ycvwycfzyarjf8l').cards.all()