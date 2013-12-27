# -*- coding: utf-8 -*-
import sys
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"

customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
print customer.transfers.create(customer_id="acuqxruyv0hi1wfdwmym", amount=100, description="Test transfer", order_id="oid-00059")
print customer.transfers.all()