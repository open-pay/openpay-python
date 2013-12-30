# -*- coding: utf-8 -*-
import sys
import datetime
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
# charges = customer.charges.all()
# print "\n\nCharges for customer: {0}".format(customer.name)
# for charge in charges:
# 	print charge

# merchant_charges = openpay.Charge.as_merchant()
# print "\n\nCharges as merchant"
# for charge in merchant_charges:
# 	print charge

# print "\n\nRetrieving Charge with ID: t8vgbjfy4vdx3xttigyj"
# charge = openpay.Charge.retrieve_as_merchant('t8vgbjfy4vdx3xttigyj')
# print charge

# print "\n\nRetrieving Charge for customer {0} with ID: teh5ydydhg4he8ympogf".format(customer.name)
# charge = customer.charges.retrieve('teh5ydydhg4he8ympogf')
# print charge

# print "Creating a charge"
# charge = customer.charges.create(source_id="kvxvccpsesm4pwmtgnjb", method="card", amount=100, description="Third charge", order_id="oid-00060", capture=False)
# print charge

# print "Get charge with ID: t2chepfmcfhr0uwqqmrp"
# charge = customer.charges.retrieve('t2chepfmcfhr0uwqqmrp')
# print charge
#charge.capture()
#print charge.refund()

# print "Creating card as merchant"

# print openpay.Card.create(
# 	card_number="4111111111111111",
# 	holder_name="Juan Perez",
# 	expiration_year="20",
# 	expiration_month="12",
# 	cvv2="110",
# 	address={
# 		"city":"Querétaro",
# 		"country_code":"MX",
# 		"postal_code":"76900",
# 		"line1":"Av 5 de Febrero",
# 		"line2":"Roble 207",
# 		"line3":"col carrillo",
# 		"state":"Queretaro"
# 	}
# )
# print "Creating charge as merchant"
# charge = openpay.Charge.create_as_merchant(source_id="k2trvya1nxpcytgww4rt", method="card", amount=100, description="Fourth charge", order_id="oid-00061", capture=False)
# print charge

# print "Retrieve charge with ID: t2uizz6lefdpj20kvucs as merchant"
# charge = openpay.Charge.retrieve_as_merchant("t2uizz6lefdpj20kvucs")
# print "Capturing charge"
# print charge.capture(merchant=True)
# print "Refund charge"
# print charge.refund(merchant=True)

# No hay acceso como merchant para agregar cuentas de banco
# print "Creating bank account as merchant"
# account = openpay.BankAccount.create(clabe="012298026516924616", alias="Cuenta principal", holder_name="Carlos Alberto Aguilar")
# print account

# print "Creating charge as merchant"
# charge = openpay.Charge.create_as_merchant(method="bank_account", amount=100, description="Fifth charge", order_id="oid-00062")
# print charge

print "Retrieve filtered list"
charges = openpay.Charge.all(creation={'lte': datetime.datetime.now().strftime('Y-m-d')})
charge = charges.retrieve(charges.data[0].id)
print type(charge)