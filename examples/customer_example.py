import sys
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
# cus = openpay.Customer.all()
# print cus

print "\n Retrieving customer"
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
print customer
print "\n Retrieving customer cards"
print customer.cards.all()
print "Retrieving card with ID: kvxvccpsesm4pwmtgnjb"
print customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')