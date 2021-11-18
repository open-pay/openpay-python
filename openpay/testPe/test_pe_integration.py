# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import randint

from datetime import datetime, timedelta
import os
import sys
import time
import unittest

from future.builtins import int
from future.builtins import str
from future.builtins import super
from future.builtins import zip
from mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import openpay

from openpay.testPe.helperpe import (
    OpenpayTestCase,
    NOW, DUMMY_CARD, DUMMY_CHARGE, DUMMY_PLAN,
    DUMMY_CHARGE_STORE, generate_order_id, DUMMY_CUSTOMER, DUMMY_ADDRESS, DUMMY_CHECKOUT, DUMMY_CHECKOUT_WITHOUT_CUSTOMER,
    DUMMY_CHARGE_MERCHANT, DUMMY_WEBHOOK, DUMMY_TOKEN)


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
                          order_id="oid-00080", card=EXPIRED_CARD, currency="PEN")

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
            openpay.Charge.create(amount=100,
                                  method='card',
                                  description="Test Order",
                                  order_id="oid-00080",
                                  currency="PEN",
                                  card=EXPIRED_CARD)
        except openpay.error.InvalidRequestError as e:
            self.assertEqual(400, e.http_status)
            self.assertTrue(isinstance(e.http_body, str))
            self.assertTrue(isinstance(e.json_body, dict))


# Note that these are in addition to the core functional charge tests
# OK
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

    def test_charge_with_token(self):
        token = openpay.Token.create(card_number='4111111111111111', holder_name='Juan Perez Ramirez',
                                     expiration_year='28', expiration_month='12', cvv2='110', address=DUMMY_ADDRESS)
        charge_list = openpay.Charge.all()
        DUMMY_CHARGE['device_session_id'] = generate_order_id()
        DUMMY_CHARGE['source_id'] = token.id
        DUMMY_CHARGE['customer'] = DUMMY_CUSTOMER
        charge = charge_list.create(**DUMMY_CHARGE)
        self.assertTrue(isinstance(charge, openpay.Charge))
        self.assertEqual(DUMMY_CHARGE['amount'], charge.amount)

    def test_charge_with_token_and_customer(self):
        customer = openpay.Customer.create(name="Miguel Lopez", email="mlopez@example.com")
        token = openpay.Token.create(card_number='4111111111111111',
                                     holder_name='Juan Perez Ramirez',
                                     expiration_year='28', expiration_month='12', cvv2='110', address=DUMMY_ADDRESS)
        DUMMY_CHARGE['device_session_id'] = generate_order_id()
        DUMMY_CHARGE['source_id'] = token.id
        DUMMY_CHARGE['customer'] = customer.id
        charge = openpay.Charge.create(**DUMMY_CHARGE)
        self.assertTrue(isinstance(charge, openpay.Charge))
        self.assertEqual(DUMMY_CHARGE['amount'], charge.amount)

    def test_charge_list_retrieve(self):
        charge_list = openpay.Charge.all()
        charge = charge_list.retrieve(charge_list.data[0].id)
        self.assertTrue(isinstance(charge, openpay.Charge))

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
        DUMMY_CHARGE_STORE['customer'] = DUMMY_CUSTOMER
        charge = openpay.Charge.create_as_merchant(**DUMMY_CHARGE_STORE)
        self.assertTrue(hasattr(charge, 'payment_method'))
        self.assertTrue(hasattr(charge.payment_method, 'reference'))
        self.assertTrue(hasattr(charge.payment_method, 'barcode_url'))
        self.assertEqual(charge.payment_method.type, "store")
        self.assertTrue(isinstance(charge, openpay.Charge))
        self.assertEqual(
            openpay.Charge.retrieve_as_merchant(charge.id).status,
            'in_progress')

class WebhookTest(OpenpayTestCase):
    def test_list_webhooks(self):
        webhooks = openpay.Webhook.all()
        print (webhooks)
        self.assertTrue(isinstance(webhooks.data, list))

    def test_create_webhook(self):
        webhook = openpay.Webhook.create(**DUMMY_WEBHOOK)
        print (webhook)
        self.assertEqual(webhook.status, 'verified')
        self.assertEqual(webhook.user, DUMMY_WEBHOOK['user'])

    def test_retrieve_webhook(self):
        webhook_id = 'wa8i86qw6zpsgkcankbe'
        webhook = openpay.Webhook.retrieve(webhook_id)
        print webhook
        self.assertEqual(webhook.id, webhook_id)

    def test_delete_webhook(self):
        webhook = openpay.Webhook.create(**DUMMY_WEBHOOK)
        webhook.delete()
        self.assertEqual(webhook, {})

class CustomerTest(OpenpayTestCase):

    def test_list_customers(self):
        customers = openpay.Customer.all()
        print(customers)
        self.assertTrue(isinstance(customers.data, list))

    def test_create_customer(self):
        name = "Miguel Lopez"
        customer = openpay.Customer.create(
            name=name,
            last_name="Mi last name",
            email="col@example.com",
            phone_number="5744484951",
            description="foo bar")
        self.assertEqual(name,customer['name'])

    def test_update_customer(self):
        name = "Miguel Lopez"
        newName = "Miguel Nevo Lopez"
        customer = openpay.Customer.create(
            name=name,
            last_name="Mi last name",
            email="col@example.com",
            phone_number="5744484951",
            description="foo bar")
        customer['name'] = newName
        customer.save()
        self.assertEqual(customer['name'], newName)

    def test_get_customer(self):
        customer = openpay.Customer.all().data[0]
        customer_ = openpay.Customer.retrieve(customer['id'])
        self.assertEqual(customer['id'], customer_['id'])

    def test_delete_customer(self):
        customer = openpay.Customer.create(
            name="Miguel Lopez",
            last_name="Mi last name",
            email="col@example.com",
            phone_number="5744484951",
            description="foo bar")
        openpay.Customer.delete(customer)
        self.assertEqual(customer, {})

    def test_list_customer(self):
        customers = openpay.Customer.all()
        self.assertTrue(isinstance(customers['data'], list))


# ok
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
                          plan=None)
        customer = openpay.Customer.create(
            name="Miguel", last_name="Lopez", email="mlopez@example.com")

        subscription = customer.subscriptions.create(
            plan_id=self.plan_obj.id, card=DUMMY_CARD)

        self.assertTrue(isinstance(subscription, openpay.Subscription))
        subscription.delete()
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
        trial_end = datetime.now() + timedelta(days=15)
        customer = openpay.Customer.create(
            name="Miguel", last_name="Lopez", email="mlopez@example.com")
        subscription = customer.subscriptions.create(
            plan_id=self.plan_obj.id, card=DUMMY_CARD,
            trial_end=trial_end.strftime('Y-m-d'))
        self.assertTrue(subscription.id)

    def test_integer_trial_end(self):
        trial_end_dttm = datetime.now() + timedelta(days=15)
        trial_end_int = int(time.mktime(trial_end_dttm.timetuple()))
        customer = openpay.Customer.create(name="Miguel",
                                           last_name="Lopez",
                                           email="mlopez@example.com")
        subscription = customer.subscriptions.create(
            plan_id=self.plan_obj.id, card=DUMMY_CARD,
            trial_end=trial_end_int)
        self.assertTrue(subscription.id)


# ok
class PlanTest(OpenpayTestCase):

    def setUp(self):
        super(PlanTest, self).setUp()

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


class CardTest(OpenpayTestCase):

    def setUp(self):
        super(CardTest, self).setUp()
        self.customer = openpay.Customer.create(
            name="John", last_name="Doe", description="Test User",
            email="johndoe@example.com")
        self.card = self.customer.cards.create(
            card_number="4111111111111111",
            holder_name="Juan Perez",
            expiration_year="25",
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

    def test_card_zdelete(self):
        card_list = self.customer.cards.all()
        self.card = card_list.data[0]
        self.card.delete()
        self.assertEqual(list(self.card.keys()), [])

    @unittest.skip("Method not available")
    def test_card_update(self):
        card_list = self.customer.cards.all()
        card = card_list.data[0]
        card.holder_name = "Juan Hernandez"
        card.save()
        self.assertEqual(card.holder_name, "Juan Hernandez")

class CheckoutTest(OpenpayTestCase):

    def order_id(self):
        return "oid_" + str(randint(11111, 99999))

    def getFormatedDate(self, date):
        date = date.replace(" ", "T")
        return date + ":00.000-0500"

    def test_checkout_create_with_customer(self):
        order_id = self.order_id()
        DUMMY_CHECKOUT['order_id'] = order_id
        checkout = openpay.Checkout.create(**DUMMY_CHECKOUT)
        self.assertEqual(checkout.order_id, order_id)

    def test_checkout_create_without_customer(self):
        order_id = self.order_id()
        DUMMY_CHECKOUT_WITHOUT_CUSTOMER['order_id'] = order_id
        checkout = openpay.Checkout.create(customer_id="atm7ii76vionfzecvwcx",**DUMMY_CHECKOUT_WITHOUT_CUSTOMER)
        self.assertEqual(checkout.order_id, order_id)

    def test_checkout_list(self):
        checkouts = openpay.Checkout.all()
        self.assertEqual(len(checkouts.data), checkouts.count)
        self.assertTrue(isinstance(checkouts, openpay.resource.ListObject))

    def test_checkout_update(self):
        expiration_date = '2021-10-15 23:36'
        checkouts = openpay.Checkout.all()
        checkout = checkouts.data[0]
        checkout.expiration_date = expiration_date
        checkout.save()
        print checkout.expiration_date
        print self.getFormatedDate(expiration_date)
        self.assertEqual(checkout.expiration_date, self.getFormatedDate(expiration_date))

    def test_checkout_filtered_list(self):
        limit = 3
        startDate = "20211001"
        endDate = "20211011"
        checkouts = openpay.Checkout.all(limit=limit, startDate=startDate, endDate=endDate)
        self.assertEqual(len(checkouts.data), limit)
        self.assertTrue(isinstance(checkouts, openpay.resource.ListObject))

    def test_get_checkout(self):
        limit = 3
        startDate = "20211001"
        endDate = "20211011"
        checkouts = openpay.Checkout.all(limit=limit, startDate=startDate, endDate=endDate)
        checkout = checkouts.data[0]
        my_checkout = openpay.Checkout.retrieve(checkout_id=checkout.id)
        self.assertEqual(my_checkout.id, checkout.id)

    @unittest.skip("Method not available")
    def test_checkout_get_by_order_id(self):
        my_checkout = openpay.Checkout.retrieve(order_id="oid_26851")
        print my_checkout

class TokenTest(OpenpayTestCase):

    def test_create_token(self):
        token = openpay.Token.create(**DUMMY_TOKEN)
        self.assertTrue(isinstance(token, openpay.Token))

    def test_get_token(self):
        token = openpay.Token.create(**DUMMY_TOKEN)
        token_ = openpay.Token.retrieve(token['id'])
        self.assertEqual(token_['id'], token['id'])

if __name__ == '__main__':
    unittest.main()
