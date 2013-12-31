# -*- coding: utf-8 -*-
import datetime
import os
import sys
import time
import unittest
import random

from mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import openpay

from openpay.test.helper import (
    OpenpayTestCase,
    NOW, DUMMY_CARD, DUMMY_CHARGE, DUMMY_PLAN, DUMMY_COUPON,
    DUMMY_RECIPIENT, DUMMY_TRANSFER, DUMMY_INVOICE_ITEM, generate_order_id)


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
        self.patched_api_base = patch('openpay.get_api_base', lambda: 'https://my-invalid-domain.ireallywontresolve/v1')
        get_api_base_mock = self.patched_api_base.start()
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
        customer = openpay.Customer.create(name="Miguel Lopez", email="mlopez@example.com")
        self.assertEqual(customer['creation_date'], customer.creation_date)
        customer['foo'] = 'bar'
        self.assertEqual(customer.foo, 'bar')

    def test_raise(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        expiration_year = NOW.year - 2
        EXPIRED_CARD['expiration_month'] = NOW.month - 2
        EXPIRED_CARD['expiration_year'] = str(expiration_year)[2:]
        self.assertRaises(openpay.error.CardError, openpay.Charge.create,
                          amount=100, method='card', description="Test Order", order_id="oid-00080", card=EXPIRED_CARD)

    def test_unicode(self):
        # Make sure unicode requests can be sent
        self.assertRaises(openpay.error.InvalidRequestError,
                          openpay.Charge.retrieve_as_merchant,
                          id=u'☃'.encode('utf-8'))

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
        except openpay.error.AuthenticationError, e:
            self.assertEqual(401, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))
        finally:
            openpay.api_key = key


class CardErrorTest(OpenpayTestCase):

    def test_declined_card_props(self):
        EXPIRED_CARD = DUMMY_CARD.copy()
        expiration_year = NOW.year - 2
        EXPIRED_CARD['expiration_month'] = NOW.month - 2
        EXPIRED_CARD['expiration_year'] = str(expiration_year)[2:]
        try:
            openpay.Charge.create(amount=100, method='card', description="Test Order", order_id="oid-00080", card=EXPIRED_CARD)
        except openpay.error.CardError, e:
            self.assertEqual(402, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))

# Note that these are in addition to the core functional charge tests


class ChargeTest(OpenpayTestCase):

    def setUp(self):
        super(ChargeTest, self).setUp()

    def test_charge_list_all(self):
        charge_list = openpay.Charge.all(creation={'lte': NOW.strftime('Y-m-d')})
        list_result = charge_list.all(creation={'lte': NOW.strftime('Y-m-d')})

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

        self.assertTrue(charge is charge.capture())
        self.assertTrue(openpay.Charge.retrieve_as_merchant(charge.id).captured)


class CustomerTest(OpenpayTestCase):

    def test_list_customers(self):
        customers = openpay.Customer.all()
        self.assertTrue(isinstance(customers.data, list))

    def test_list_charges(self):
        customer = openpay.Customer.create(name="Miguel Lopez", email="mlopez@example.com", description="foo bar",
                                           card=DUMMY_CARD)

        customer.charges.create(
            amount=100, method="card", description="Customer test charge", order_id=generate_order_id(), card=DUMMY_CARD)

        self.assertEqual(1,
                         len(customer.charges.all().data))

    def test_unset_description(self):
        customer = openpay.Customer.create(name="Miguel", last_name="Lopez", email="mlopez@example.com", description="foo bar")

        customer.description = None
        customer.save()

        self.assertEqual(None, customer.retrieve(customer.id).get('description'))

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


class TransferTest(OpenpayTestCase):

    def test_list_transfers(self):
        customer = openpay.Customer.retrieve("amce5ycvwycfzyarjf8l")
        transfers = customer.transfers.all()
        self.assertTrue(isinstance(transfers.data, list))
        self.assertTrue(isinstance(transfers.data[0], openpay.Transfer))


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
        customer = openpay.Customer.create(name="Miguel", last_name="Lopez", email="mlopez@example.com")
        customer.update_subscription(plan_id=self.plan_obj.id, trial_days="5", card=DUMMY_CARD)
        self.assertTrue(hasattr(customer, 'subscription'))
        self.assertFalse(hasattr(customer, 'plan'))
        customer.cancel_subscription()
        customer.delete()
        self.assertFalse(hasattr(customer, 'subscription'))
        self.assertFalse(hasattr(customer, 'plan'))
        # self.assertTrue(customer.deleted)

    def test_update_and_cancel_subscription(self):
        customer = openpay.Customer.create(name="Miguel", last_name="Lopez", email="mlopez@example.com")

        sub = customer.update_subscription(plan_id=self.plan_obj.id, card=DUMMY_CARD)
        self.assertEqual(customer.subscription.id, sub.id)
        # self.assertEqual(DUMMY_PLAN['id'], sub.plan.id)

        customer.cancel_subscription(at_period_end=True)
        self.assertEqual(customer.subscription.status, 'active')
        self.assertTrue(customer.subscription.cancel_at_period_end)
        customer.cancel_subscription()
        self.assertEqual(customer.subscription.status, 'canceled')

    def test_datetime_trial_end(self):
        trial_end = datetime.datetime.now() + datetime.timedelta(days=15)
        customer = openpay.Customer.create(
            name="Miguel", last_name="Lopez", email="mlopez@example.com",
            plan=DUMMY_PLAN['id'], card=DUMMY_CARD,
            trial_end=trial_end.strftime('Y-m-d'))
        self.assertTrue(customer.id)

    def test_integer_trial_end(self):
        trial_end_dttm = datetime.datetime.now() + datetime.timedelta(days=15)
        trial_end_int = int(time.mktime(trial_end_dttm.timetuple()))
        customer = openpay.Customer.create(name="Miguel",
                                           last_name="Lopez",
                                           email="mlopez@example.com",
                                           plan=DUMMY_PLAN['id'],
                                           card=DUMMY_CARD,
                                           trial_end=trial_end_int)
        self.assertTrue(customer.id)


class InvalidRequestErrorTest(OpenpayTestCase):

    def test_nonexistent_object(self):
        try:
            openpay.Charge.retrieve('invalid')
        except openpay.error.InvalidRequestError, e:
            self.assertEqual(404, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))

    def test_invalid_data(self):
        try:
            openpay.Charge.create()
        except openpay.error.InvalidRequestError, e:
            self.assertEqual(400, e.http_status)
            self.assertTrue(isinstance(e.http_body, basestring))
            self.assertTrue(isinstance(e.json_body, dict))


class PlanTest(OpenpayTestCase):

    def setUp(self):
        super(PlanTest, self).setUp()
        try:
            openpay.Plan(DUMMY_PLAN['id']).delete()
        except openpay.error.InvalidRequestError:
            pass

    def test_create_plan(self):
        self.assertRaises(openpay.error.InvalidRequestError,
                          openpay.Plan.create, amount=2500)
        p = openpay.Plan.create(**DUMMY_PLAN)
        self.assertTrue(hasattr(p, 'amount'))
        self.assertTrue(hasattr(p, 'id'))
        self.assertEqual(DUMMY_PLAN['amount'], p.amount)
        p.delete()
        self.assertEqual(p.keys(), [])
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


# class MetadataTest(OpenpayTestCase):

#     def setUp(self):
#         super(MetadataTest, self).setUp()
#         self.initial_metadata = {
#             'address': '77 Massachusetts Ave, Cambridge',
#             'uuid': 'id'
#         }

#         charge = stripe.Charge.create(
#             metadata=self.initial_metadata, **DUMMY_CHARGE)
#         customer = stripe.Customer.create(
#             metadata=self.initial_metadata, card=DUMMY_CARD)
#         recipient = stripe.Recipient.create(
#             metadata=self.initial_metadata, **DUMMY_RECIPIENT)
#         transfer = stripe.Transfer.create(
#             metadata=self.initial_metadata, **DUMMY_TRANSFER)

#         self.support_metadata = [charge, customer, recipient, transfer]

#     def test_noop_metadata(self):
#         for obj in self.support_metadata:
#             obj.description = 'test'
#             obj.save()
#             metadata = obj.retrieve(obj.id).metadata
#             self.assertEqual(self.initial_metadata, metadata)

#     def test_unset_metadata(self):
#         for obj in self.support_metadata:
#             obj.metadata = None
#             expected_metadata = {}
#             obj.save()
#             metadata = obj.retrieve(obj.id).metadata
#             self.assertEqual(expected_metadata, metadata)

#     def test_whole_update(self):
#         for obj in self.support_metadata:
#             expected_metadata = {'txn_id': '3287423s34'}
#             obj.metadata = expected_metadata.copy()
#             obj.save()
#             metadata = obj.retrieve(obj.id).metadata
#             self.assertEqual(expected_metadata, metadata)

#     def test_individual_delete(self):
#         for obj in self.support_metadata:
#             obj.metadata['uuid'] = None
#             expected_metadata = {'address': self.initial_metadata['address']}
#             obj.save()
#             metadata = obj.retrieve(obj.id).metadata
#             self.assertEqual(expected_metadata, metadata)

#     def test_individual_update(self):
#         for obj in self.support_metadata:
#             obj.metadata['txn_id'] = 'abc'
#             expected_metadata = {'txn_id': 'abc'}
#             expected_metadata.update(self.initial_metadata)
#             obj.save()
#             metadata = obj.retrieve(obj.id).metadata
#             self.assertEqual(expected_metadata, metadata)

#     def test_combo_update(self):
#         for obj in self.support_metadata:
#             obj.metadata['txn_id'] = 'bar'
#             obj.metadata = {'uid': '6735'}
#             obj.save()
#             metadata = obj.retrieve(obj.id).metadata
#             self.assertEqual({'uid': '6735'}, metadata)

#         for obj in self.support_metadata:
#             obj.metadata = {'uid': '6735'}
#             obj.metadata['foo'] = 'bar'
#             obj.save()
#             metadata = obj.retrieve(obj.id).metadata
#             self.assertEqual({'uid': '6735', 'foo': 'bar'}, metadata)


if __name__ == '__main__':
    unittest.main()
