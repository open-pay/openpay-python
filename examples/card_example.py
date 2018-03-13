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

print "customer stored cards -------------> ", customer.cards.all().count

card = customer.cards.create(
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
print "customer card ----------------->"
print card

print "customer stored cards -------------> ", customer.cards.all().count

print "deleting card -------------> ", card.id
card.delete()
print "customer stored cards -------------> ", customer.cards.all().count


print "Creating merchant card: "
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
print "merchant card: ", card
