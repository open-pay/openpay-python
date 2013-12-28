# -*- coding: utf-8 -*-
import sys
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"

fee = openpay.Fee.create(
    customer_id="amce5ycvwycfzyarjf8l",
    amount=12.50,
    description="Fee Charge",
    order_id="oid=1245"
)
print fee

print openpay.Fee.all()

