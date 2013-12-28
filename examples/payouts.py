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

bank_account = customer.bank_accounts.all()[0] # We get the first account
# print customer.payouts.create(method='bank_account', destination_id=bank_account.id, amount="100", description="First payout", order_id="oid-00058")

print "Retrieving payout with ID: tbs6a7g4pypww4eq640d"
print customer.payouts.retrieve("tbs6a7g4pypww4eq640d")

print "Creating payout as merchant"
print openpay.Payout.create_as_merchant(method="bank_account", destination_id="bkjj51ovzkv2tr1mn0n8", amount=200.00, description="Second payout", order_id="oid-00064")
