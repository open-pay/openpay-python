# -*- coding: utf-8 -*-
import sys
from os import path, pardir
PROJECT_ROOT = path.dirname(path.abspath(__file__))
sys.path.append(path.join(PROJECT_ROOT, pardir))

import openpay
openpay.api_key = "sk_10d37cc4da8e4ffd902cdf62e37abd1b"
openpay.verify_ssl_certs = False
openpay.merchant_id = "mynvbjhtzxdyfewlzmdo"
# Creating a plan
#plan = openpay.Plan.create(amount=150.00, status_after_retry="cancelled", retry_times=2,
#                           name="Curso de Ingles", repeat_unit="month", trial_days=30, repeat_every=1)
#print plan

# print "Updating plan with ID: pbkliysxavp8bvvp8f0k"
# plan = openpay.Plan.retrieve('pbkliysxavp8bvvp8f0k')
# plan.name="Curso de Ingles II"
# plan.save()
# print "All Plans"
# plans = openpay.Plan.all()
# print plans
customer = openpay.Customer.retrieve('amce5ycvwycfzyarjf8l')
# print customer.cards.create(
# 	card_number="4111111111111111",
# 	holder_name="Juan Perez Ramirez",
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
#    })
print "Adding plan to user {0}".format(customer.name)
customer.update_subscription(plan_id="pbkliysxavp8bvvp8f0k", trial_days="5", card_id="kvxvccpsesm4pwmtgnjb")

