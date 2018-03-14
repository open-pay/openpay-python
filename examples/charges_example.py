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
print "customer: ", customer

card = customer.cards.create(
	card_number="4111111111111111",
	holder_name="Juan Perez Ramirez",
	expiration_year="20",
	expiration_month="12",
	cvv2="110",
	address={
		"city":"Querétaro",
		"country_code":"MX",
		"postal_code":"76900",
		"line1":"Av 5 de Febrero",
		"line2":"Roble 207",
		"line3":"col carrillo",
		"state":"Queretaro"
   })

print "Card: ", card

print "Creating card as customer"
charge = customer.charges.create(source_id=card.id, method="card", amount=100, description="Charge", capture=False)

print "charge: ", charge

print charge.refund()

print "Creating card as merchant"

card = openpay.Card.create(
	card_number="4111111111111111",
	holder_name="Juan Perez",
	expiration_year="20",
	expiration_month="12",
	cvv2="110",
	address={
		"city":"Querétaro",
		"country_code":"MX",
		"postal_code":"76900",
		"line1":"Av 5 de Febrero",
		"line2":"Roble 207",
		"line3":"col carrillo",
		"state":"Queretaro"
	}
)

print "Card: ", card

print "Creating charge as merchant"
charge = openpay.Charge.create_as_merchant(
 	source_id="k2trvya1nxpcytgww4rt", 
 	method="card", amount=100, 
 	description="Fourth charge", 
 	capture=False)
print "charge: ", charge

print "Retrieve charge with ID as merchant"
charge = openpay.Charge.retrieve_as_merchant(charge.id)
print "charge: ", charge

print "Capturing charge"
print charge.capture(merchant=True)

print "Refund charge"
print charge.refund(merchant=True)


