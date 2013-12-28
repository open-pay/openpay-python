import sys
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
charges = customer.charges.all()
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
charge = customer.charges.retrieve('teh5ydydhg4he8ympogf')
print charge

# print "Creating a charge"
# charge = customer.charges.create(source_id="kvxvccpsesm4pwmtgnjb", method="card", amount=100, description="Third charge", order_id="oid-00060", capture=False)
# print charge

print "Get charge with ID: t2chepfmcfhr0uwqqmrp"
charge = customer.charges.retrieve('t2chepfmcfhr0uwqqmrp')
#charge.capture()
print charge.refund()