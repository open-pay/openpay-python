import sys
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
charges = customer.charges()
print "\n\nCharges for customer: {0}".format(customer.name)
for charge in charges:
	print charge

merchant_charges = openpay.Charge.as_merchant()
print "\n\nCharges as merchant"
for charge in merchant_charges:
	print charge

print "\n\nRetrieving Charge with ID: t8vgbjfy4vdx3xttigyj"
charge = openpay.Charge.retrieve_as_merchant('t8vgbjfy4vdx3xttigyj')
print charge

print "\n\nRetrieving Charge for customer {0} with ID: teh5ydydhg4he8ympogf".format(customer.name)
charge = customer.retrieve_charge(charge='teh5ydydhg4he8ympogf')
print charge