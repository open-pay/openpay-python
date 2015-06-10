import sys
import datetime
from os import path, pardir
from passlib.tests.utils import limit
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay

openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"

customers = openpay.Customer.all(
    external_id="AA_00002",
    limit=1
);

print(customers);
