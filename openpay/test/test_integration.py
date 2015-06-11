# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from future.builtins import zip
from future.builtins import int
from future.builtins import str
from future.builtins import super

import datetime
import os
import sys
import time
import unittest

from mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import openpay

from openpay.test.helper import (
    OpenpayTestCase,
    NOW, DUMMY_CARD, DUMMY_CHARGE, DUMMY_PLAN,
    DUMMY_CHARGE_STORE, generate_order_id)


class FunctionalTests(OpenpayTestCase):
    request_client = openpay.http_client.Urllib2Client

    def setUp(self):
        super(FunctionalTests, self).setUp()

        def get_http_client(*args, **kwargs):
            return self.request_client(*args, **kwargs)

        self.client_patcher = patch(
            'openpay.http_client.new_default_http_client')

        client_mock = self.client_patcher.start()
        client_mock.side_effect = get_http_client

    def tearDown(self):
        super(FunctionalTests, self).tearDown()

        self.client_patcher.stop()

    def test_dns_failure(self):
        self.patched_api_base = patch(
            'openpay.get_api_base',
            lambda: 'https://my-invalid-domain.ireallywontresolve/v1')
       # get_api_base_mock = self.patched_api_base.start()
        self.patched_api_base.start()
        try:
            self.assertRaises(openpay.error.APIConnectionError,
                              openpay.Customer.create)
        finally:
            self.patched_api_base.stop()

    def test_run(self):
        DUMMY_CHARGE['order_id'] = generate_order_id()
        charge = openpay.Charge.create(**DUMMY_CHARGE)
        # self.assertFalse(hasattr(charge, 'refund'))
        charge.refund(merchant=True)
        self.assertTrue(hasattr(charge, 'refund'))

    def test_refresh(self):
        DUMMY_CHARGE['order_id'] = generate_order_id()
        charge = openpay.Charge.create(**DUMMY_CHARGE)
        charge2 = openpay.Charge.retrieve_as_merchant(charge.id)
        self.assertEqual(charge2.creation_date, charge.creation_date)

        charge2.junk = 'junk'
        charge2.refresh()
        self.assertRaises(AttributeError, lambda: charge2.junk)

    def test_list_accessors(self):
        customer = openpay.Customer.create(
            name="Miguel Lopez", email="mlopez@example.com")
        self.assertEqual(customer['creation_date'], customer.creation_date)
        customer['foo'] = 'bar'
        self.assertEqual(customer.foo, 'bar')

    def test_raise(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        expiration_year = NOW.year - 2
        EXPIRED_CARD['expiration_month'] = NOW.month
        EXPIRED_CARD['expiration_year'] = str(expiration_year)[2:]
        self.assertRaises(openpay.error.InvalidRequestError, openpay.Charge.create,
                          amount=100, method='card', description="Test Order",
                          order_id="oid-00080", card=EXPIRED_CARD)

    def test_unicode(self):
        # Make sure unicode requests can be sent
        self.assertRaises(openpay.error.InvalidRequestError,
                          openpay.Charge.retrieve_as_merchant,
                          id=u'☃')

    # def test_none_values(self):
    #     customer = openpay.Customer.create(name=None, last_name=None)
    #     self.assertTrue(customer.id)

    def test_missing_id(self):
        customer = openpay.Customer()
        self.assertRaises(openpay.error.InvalidRequestError, customer.refresh)


class RequestsFunctionalTests(FunctionalTests):
    request_client = openpay.http_client.RequestsClient

# Avoid skipTest errors in < 2.7
if sys.version_info >= (2, 7):
    class UrlfetchFunctionalTests(FunctionalTests):
        request_client = 'urlfetch'

        def setUp(self):
            if openpay.http_client.urlfetch is None:
                self.skipTest(
                    '`urlfetch` from Google App Engine is unavailable.')
            else:
                super(UrlfetchFunctionalTests, self).setUp()


# class PycurlFunctionalTests(FunctionalTests):
#     def setUp(self):
#         if sys.version_info >= (3, 0):
#             self.skipTest('Pycurl is not supported in Python 3')
#         else:
#             super(PycurlFunctionalTests, self).setUp()

#     request_client = openpay.http_client.PycurlClient


class AuthenticationErrorTest(OpenpayTestCase):

    def test_invalid_credentials(self):
        key = openpay.api_key
        try:
            openpay.api_key = 'invalid'
            openpay.Customer.create()
        except openpay.error.AuthenticationError as e:
            self.assertEqual(401, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))
        finally:
            openpay.api_key = key


class CardErrorTest(OpenpayTestCase):

    def test_declined_card_props(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        expiration_year = NOW.year - 2
        EXPIRED_CARD['expiration_month'] = NOW.month
        EXPIRED_CARD['expiration_year'] = str(expiration_year)[2:]
        try:
            openpay.Charge.create(amount=100, method='card',
                                  description="Test Order",
                                  order_id="oid-00080",
                                  card=EXPIRED_CARD)
        except openpay.error.InvalidRequestError as e:
            self.assertEqual(400, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))

# Note that these are in addition to the core functional charge tests


class ChargeTest(OpenpayTestCase):

    def setUp(self):
        super(ChargeTest, self).setUp()

    def test_charge_list_all(self):
        charge_list = openpay.Charge.all(
            creation={'lte': NOW.strftime("%Y-%m-%d")})
        list_result = charge_list.all(
            creation={'lte': NOW.strftime("%Y-%m-%d")})

        self.assertEqual(len(charge_list.data),
                         len(list_result.data))

        for expected, actual in zip(charge_list.data,
                                    list_result.data):
            self.assertEqual(expected.id, actual.id)

    def test_charge_list_create(self):
        charge_list = openpay.Charge.all()
        DUMMY_CHARGE['order_id'] = generate_order_id()
        charge = charge_list.create(**DUMMY_CHARGE)

        self.assertTrue(isinstance(charge, openpay.Charge))
        self.assertEqual(DUMMY_CHARGE['amount'], charge.amount)

    def test_charge_list_retrieve(self):
        charge_list = openpay.Charge.all()
        charge = charge_list.retrieve(charge_list.data[0].id)
        self.assertTrue(isinstance(charge, openpay.Charge))

    def test_charge_capture(self):
        params = DUMMY_CHARGE.copy()
        params['capture'] = False

        charge = openpay.Charge.create(**params)

        self.assertFalse(hasattr(charge, 'captured'))

        self.assertTrue(charge is charge.capture(merchant=True))
        self.assertEqual(
            openpay.Charge.retrieve_as_merchant(charge.id).status,
            'completed')

    def test_charge_store_as_customer(self):
        customer = openpay.Customer.create(
            name="Miguel Lopez", email="mlopez@example.com")
        charge = customer.charges.create(**DUMMY_CHARGE_STORE)
        self.assertTrue(hasattr(charge, 'payment_method'))
        self.assertTrue(hasattr(charge.payment_method, 'reference'))
        self.assertTrue(hasattr(charge.payment_method, 'barcode_url'))
        self.assertEqual(
            customer.charges.retrieve(charge.id).status,
            'in_progress')

    def test_charge_store_as_merchant(self):
        charge = openpay.Charge.create(**DUMMY_CHARGE_STORE)

        self.assertTrue(hasattr(charge, 'payment_method'))
        self.assertTrue(hasattr(charge.payment_method, 'reference'))
        self.assertTrue(hasattr(charge.payment_method, 'barcode_url'))
        self.assertEqual(charge.payment_method.type, "store")
        self.assertTrue(isinstance(charge, openpay.Charge))
        self.assertEqual(
            openpay.Charge.retrieve_as_merchant(charge.id).status,
            'in_progress')


class CustomerTest(OpenpayTestCase):

    def test_list_customers(self):
        customers = openpay.Customer.all()
        self.assertTrue(isinstance(customers.data, list))

    def test_list_charges(self):
        customer = openpay.Customer.create(
            name="Miguel Lopez",
            email="mlopez@example.com",
            description="foo bar")

        customer.charges.create(
            amount=100, method="card",
            description="Customer test charge",
            order_id=generate_order_id(), card=DUMMY_CARD)

        self.assertEqual(1,
                         len(customer.charges.all().data))

    def test_unset_description(self):
        customer = openpay.Customer.create(
            name="Miguel", last_name="Lopez",
            email="mlopez@example.com", description="foo bar")

        customer.description = None
        customer.save()

        self.assertEqual(
            None,
            customer.retrieve(customer.id).get('description'))

    def test_cannot_set_empty_string(self):
        customer = openpay.Customer()
        self.assertRaises(ValueError, setattr, customer, "description", "")

    # def test_update_customer_card(self):
    #     customer = openpay.Customer.all(limit=1).data[0]
    #     card = customer.cards.create(**DUMMY_CARD)
    #     print card
    #     card.name = 'Python bindings test'
    #     card.save()

    #     self.assertEqual('Python bindings test',
    #                      customer.cards.retrieve(card.id).name)


class CustomerPlanTest(OpenpayTestCase):

    def setUp(self):
        super(CustomerPlanTest, self).setUp()
        try:
            self.plan_obj = openpay.Plan.create(**DUMMY_PLAN)
        except openpay.error.InvalidRequestError:
            self.plan_obj = None

    def tearDown(self):
        if self.plan_obj:
            try:
                self.plan_obj.delete()
            except openpay.error.InvalidRequestError:
                pass
        super(CustomerPlanTest, self).tearDown()

    def test_create_customer(self):
        self.assertRaises(openpay.error.InvalidRequestError,
                          openpay.Customer.create,
                          plan=DUMMY_PLAN['id'])
        customer = openpay.Customer.create(
            name="Miguel", last_name="Lopez", email="mlopez@example.com")

        subscription = customer.subscriptions.create(
            plan_id=self.plan_obj.id, trial_days="0", card=DUMMY_CARD)

        self.assertTrue(isinstance(subscription, openpay.Subscription))
        subscription.delete()
        customer.delete()
        self.assertFalse(hasattr(customer, 'subscription'))
        self.assertFalse(hasattr(customer, 'plan'))

    def test_update_and_cancel_subscription(self):
        customer = openpay.Customer.create(
            name="Miguel", last_name="Lopez", email="mlopez@example.com")

        sub = customer.subscriptions.create(
            plan_id=self.plan_obj.id, card=DUMMY_CARD)

        sub.cancel_at_period_end = True
        sub.save()
        self.assertEqual(sub.status, 'active')
        self.assertTrue(sub.cancel_at_period_end)
        sub.delete()

    def test_datetime_trial_end(self):
        trial_end = datetime.datetime.now() + datetime.timedelta(days=15)
        customer = openpay.Customer.create(
            name="Miguel", last_name="Lopez", email="mlopez@example.com")
        subscription = customer.subscriptions.create(
            plan_id=self.plan_obj.id, card=DUMMY_CARD,
            trial_end=trial_end.strftime('Y-m-d'))
        self.assertTrue(subscription.id)

    def test_integer_trial_end(self):
        trial_end_dttm = datetime.datetime.now() + datetime.timedelta(days=15)
        trial_end_int = int(time.mktime(trial_end_dttm.timetuple()))
        customer = openpay.Customer.create(name="Miguel",
                                           last_name="Lopez",
                                           email="mlopez@example.com")
        subscription = customer.subscriptions.create(
            plan_id=self.plan_obj.id, card=DUMMY_CARD,
            trial_end=trial_end_int)
        self.assertTrue(subscription.id)


class InvalidRequestErrorTest(OpenpayTestCase):

    def test_nonexistent_object(self):
        try:
            openpay.Charge.retrieve('invalid')
        except openpay.error.InvalidRequestError as e:
            self.assertEqual(404, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))

    def test_invalid_data(self):
        try:
            openpay.Charge.create()
        except openpay.error.InvalidRequestError as e:
            self.assertEqual(400, e.http_status)

class PlanTest(OpenpayTestCase):

    def setUp(self):
        super(PlanTest, self).setUp()
        try:
            openpay.Plan(DUMMY_PLAN['id']).delete()
        except openpay.error.InvalidRequestError:
            pass

    def test_create_plan(self):
        self.assertRaises(openpay.error.InvalidRequestError,
                          openpay.Plan.create, amount=250)
        p = openpay.Plan.create(**DUMMY_PLAN)
        self.assertTrue(hasattr(p, 'amount'))
        self.assertTrue(hasattr(p, 'id'))
        self.assertEqual(DUMMY_PLAN['amount'], p.amount)
        p.delete()
        self.assertEqual(list(p.keys()), [])
        # self.assertTrue(p.deleted)

    def test_update_plan(self):
        p = openpay.Plan.create(**DUMMY_PLAN)
        name = "New plan name"
        p.name = name
        p.save()
        self.assertEqual(name, p.name)
        p.delete()

    def test_update_plan_without_retrieving(self):
        p = openpay.Plan.create(**DUMMY_PLAN)

        name = 'updated plan name!'
        plan = openpay.Plan(p.id)
        plan.name = name

        # should only have name and id
        self.assertEqual(sorted(['id', 'name']), sorted(plan.keys()))
        plan.save()

        self.assertEqual(name, plan.name)
        # should load all the properties
        self.assertEqual(p.amount, plan.amount)
        p.delete()


class PayoutTest(OpenpayTestCase):

    def setUp(self):
        super(PayoutTest, self).setUp()
        self.customer = openpay.Customer.create(
            name="John", last_name="Doe", description="Test User",
            email="johndoe@example.com")
        self.bank_account = self.customer.bank_accounts.create(
            clabe="032180000118359719",
            alias="Cuenta principal",
            holder_name="John Doe")

        self.card = self.customer.cards.create(
            card_number="4111111111111111",
            holder_name="Juan Perez",
            expiration_year="20",
            expiration_month="12",
            cvv2="110",
            address={
                "city": "Querétaro",
                "country_code": "MX",
                "postal_code": "76900",
                "line1": "Av 5 de Febrero",
                "line2": "Roble 207",
                "line3": "col carrillo",
                "state": "Querétaro"
            }
        )

        self.customer.charges.create(source_id=self.card.id, method="card",
                                     amount=100, description="Test Charge",
                                     order_id=generate_order_id())

    def test_create_payout_with_bank_account(self):
        payout = self.customer.payouts.create(
            method='bank_account',
            destination_id=self.bank_account.id,
            amount="10",
            description="First payout",
            order_id=generate_order_id())

        self.assertTrue(hasattr(payout, 'id'))
        self.assertTrue(isinstance(payout, openpay.Payout))

    def test_create_payout_with_card(self):
        payout = self.customer.payouts.create(method="card",
                                              destination_id=self.card.id,
                                              amount=25,
                                              description="Payout with card",
                                              order_id=generate_order_id())
        self.assertTrue(hasattr(payout, 'id'))
        self.assertTrue(isinstance(payout, openpay.Payout))

    def test_list_all_payout(self):
        payout_list = self.customer.payouts.all()
        self.assertTrue(isinstance(payout_list.data, list))
        self.assertEqual(len(payout_list.data), payout_list.count)


class CardTest(OpenpayTestCase):

    def setUp(self):
        super(CardTest, self).setUp()
        self.customer = openpay.Customer.create(
            name="John", last_name="Doe", description="Test User",
            email="johndoe@example.com")
        self.card = self.customer.cards.create(
            card_number="4111111111111111",
            holder_name="Juan Perez",
            expiration_year="20",
            expiration_month="12",
            cvv2="110",
            address={
                "city": "Querétaro",
                "country_code": "MX",
                "postal_code": "76900",
                "line1": "Av 5 de Febrero",
                "line2": "Roble 207",
                "line3": "col carrillo",
                "state": "Queretaro"
            }
        )

    def test_card_created(self):
        self.assertTrue(isinstance(self.card, openpay.Card))

    def test_card_list_all(self):
        card_list = self.customer.cards.all()
        self.assertEqual(card_list.count, 1)
        self.assertEqual(len(card_list.data), card_list.count)
        self.assertTrue(isinstance(card_list, openpay.resource.ListObject))

    def test_card_retrieve(self):
        card_list = self.customer.cards.all()
        card = card_list.data[0]
        retrieved_card = self.customer.cards.retrieve(card.id)
        self.assertEqual(card.id, retrieved_card.id)

    def test_card_delete(self):
        self.card.delete()
        self.assertEqual(list(self.card.keys()), [])


class FeeTest(OpenpayTestCase):

    def setUp(self):
        super(FeeTest, self).setUp()
        self.customer = openpay.Customer.create(
            name="John", last_name="Doe", description="Test User",
            email="johndoe@example.com")
        self.bank_account = self.customer.bank_accounts.create(
            clabe="032180000118359719",
            alias="Cuenta principal",
            holder_name="John Doe")

        self.card = self.customer.cards.create(
            card_number="4111111111111111",
            holder_name="Juan Perez",
            expiration_year="20",
            expiration_month="12",
            cvv2="110",
            address={
                "city": "Querétaro",
                "country_code": "MX",
                "postal_code": "76900",
                "line1": "Av 5 de Febrero",
                "line2": "Roble 207",
                "line3": "col carrillo",
                "state": "Queretaro"
            }
        )

        self.charge = self.customer.charges.create(
            source_id=self.card.id, method="card",
            amount=10, description="Test Charge",
            order_id=generate_order_id())

    def test_fee_create(self):
        fee = openpay.Fee.create(
            customer_id=self.customer.id, amount=5,
            description="Test Fee", order_id=generate_order_id())
        self.assertTrue(isinstance(fee, openpay.Fee))
        self.assertTrue(hasattr(fee, 'id'))

    def test_fee_list_all(self):
        fee_list = openpay.Fee.all()
        self.assertTrue(isinstance(fee_list, openpay.resource.ListObject))
        self.assertTrue(isinstance(fee_list.data, list))
        self.assertEqual(fee_list.count, len(fee_list.data))


class TransferTest(OpenpayTestCase):

    def setUp(self):
        super(TransferTest, self).setUp()
        self.customer = openpay.Customer.create(
            name="John", last_name="Doe", description="Test User",
            email="johndoe@example.com")
        self.bank_account = self.customer.bank_accounts.create(
            clabe="032180000118359719",
            alias="Cuenta principal",
            holder_name="John Doe")

        self.card = self.customer.cards.create(
            card_number="4111111111111111",
            holder_name="Juan Perez",
            expiration_year="20",
            expiration_month="12",
            cvv2="110",
            address={
                "city": "Querétaro",
                "country_code": "MX",
                "postal_code": "76900",
                "line1": "Av 5 de Febrero",
                "line2": "Roble 207",
                "line3": "col carrillo",
                "state": "Queretaro"
            }
        )

        self.charge = self.customer.charges.create(
            source_id=self.card.id, method="card",
            amount=100, description="Test Charge",
            order_id=generate_order_id())

        self.second_customer = openpay.Customer.all().data[3]

    def test_transfer_create(self):
        transfer = self.customer.transfers.create(
            customer_id=self.second_customer.id, amount=10,
            description="Test transfer", order_id=generate_order_id())
        self.assertTrue(isinstance(transfer, openpay.Transfer))
        self.assertTrue(hasattr(transfer, 'id'))

    def test_transfer_list_all(self):
        transfer_list = self.customer.transfers.all()
        self.assertTrue(isinstance(transfer_list, openpay.resource.ListObject))
        self.assertTrue(isinstance(transfer_list.data, list))
        self.assertEqual(transfer_list.count, len(transfer_list.data))

    def test_transfer_retrieve(self):
        transfer = self.customer.transfers.create(
            customer_id=self.second_customer.id, amount=10,
            description="Test transfer", order_id=generate_order_id())
        transfer_list = self.customer.transfers.all()
        test_transfer = transfer_list.data[0]
        transfer = self.customer.transfers.retrieve(test_transfer.id)
        self.assertTrue(isinstance(transfer, openpay.Transfer))

    def test_list_transfers(self):
        customer = openpay.Customer.retrieve("amce5ycvwycfzyarjf8l")
        transfers = customer.transfers.all()
        self.assertTrue(isinstance(transfers.data, list))
        self.assertTrue(isinstance(transfers.data[0], openpay.Transfer))

if __name__ == '__main__':
    unittest.main()
