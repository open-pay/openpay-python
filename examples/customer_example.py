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
# print "\n Retrieving customer cards"
# cards = customer.cards.all()
# for card in cards.data:
# 	print type(card)
# print "Retrieving card with ID: kvxvccpsesm4pwmtgnjb"
# print customer.cards.retrieve('kvxvccpsesm4pwmtgnjb')
# print "\nCreating new customer"
# customer = openpay.Customer.create(
#     name="Juan",
#     email="somebody@example.com",
#     address={
#         "city": "Queretaro",
#         "state":"Queretaro",
#         "line1":"Calle de las penas no 10",
#         "postal_code":"76000",
#         "line2":"col. san pablo",
#         "line3":"entre la calle de la alegria y la calle del llanto",
#         "country_code":"MX"
#     },
#     last_name="Perez",
#     phone_number="44209087654"
# )
# print openpay.Customer.all()
print "Displaying all user subscriptions"
print customer.subscriptions.all()
print "Retrieving specific subscription"
print customer.subscriptions.retrieve("sl7zlwys6hxicr8dbhmo")