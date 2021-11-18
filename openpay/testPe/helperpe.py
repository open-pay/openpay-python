# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
import random
import re
import sys
import time
import unittest

from future.builtins import str
from future.builtins import super
from mock import patch, Mock

import openpay


def generate_order_id():
    order_id = 'oid-test-{0}-{1}'.format(
        random.randint(1, 3000), str(time.time())[7:])
    if len(order_id) > 20:
        order_id = order_id[:20]

    return order_id


NOW = datetime.datetime.now()
DUMMY_CUSTOMER = {
    "name": "Cliente Peru",
    "last_name": "Vazquez Juarez",
    "phone_number": "4448936475",
    "email": "juan.vazquez@empresa.pe"
}
DUMMY_CARD = {
    'holder_name': 'Juan Lopez',
    'card_number': '4111111111111111',
    "cvv2": "110",
    'expiration_month': NOW.month,
    'expiration_year': str(NOW.year + 4)[2:]
}

DUMMY_CHARGE = {
    'method': 'card',
    'amount': 100,
    'currency': 'PEN',
    'source_id': '',
    'description': 'Dummy Charge',
    'device_session_id': ''
}

DUMMY_CHARGE_MERCHANT = {
    'method': 'card',
    'amount': 100,
    'currency': 'PEN',
    'description': 'Dummy Charge',
    'confirm': 'false',
    'redirect_url': 'http://testing-openpay-pe.com',
    'customer': DUMMY_CUSTOMER
}

DUMMY_CHARGE_STORE = {
    'method': 'store',
    'amount': 100,
    'currency': 'PEN',
    'description': 'Store Charge'
}

DUMMY_CHARGE_STORE_MERCHANT = {
    'method': 'store',
    'amount': 100,
    'currency': 'PEN',
    'description': 'Store Charge',
    'customer': DUMMY_CUSTOMER
}

DUMMY_PLAN = {
    'name': 'Amazing Gold Plan',
    'amount': 2000,
    'repeat_every': 1,
    'repeat_unit': 'month',
    'retry_times': 2,
    'status_after_retry': 'cancelled',
    'trial_days': 0
}

DUMMY_TRANSFER = {
    'amount': 400,
    'customer_id': 'acuqxruyv0hi1wfdwmym',
    'description': 'Dummy Transfer',
    'order_id': 'oid-00099',
}

DUMMY_ADDRESS = {
    "city": "Lima",
    "country_code": "PE",
    "postal_code": "02002",
    "line1": "Av 5 de Febrero",
    "line2": "Roble 207",
    "line3": "col carrillo",
    "state": "Lima"
}

DUMMY_CHECKOUT = {
    "amount": 250,
    "currency": "PEN",
    "description": "Cargo cobro con link",
    "redirect_url": "https://misitioempresa.pe",
    "order_id": "oid-12331",
    "expiration_date": "2021-08-31 12:50",
    "send_email": True,
    "customer": DUMMY_CUSTOMER
}

DUMMY_CHECKOUT_WITHOUT_CUSTOMER = {
    "amount": 250,
    "currency": "PEN",
    "description": "Cargo cobro con link",
    "redirect_url": "https://misitioempresa.pe",
    "order_id": "oid-12331",
    "expiration_date": "2021-08-31 12:50",
    "send_email": True
}

DUMMY_WEBHOOK = {
    "url": "https://webhook.site/99e29beb-fd9e-4c3f-9b49-ad28bac3daa5",
    "user": "juanito",
    "password": "passjuanito",
    "event_types":
        [
            "charge.refunded",
            "charge.failed",
            "charge.cancelled",
            "charge.created",
            "chargeback.accepted"
        ]
}

DUMMY_TOKEN = {
    "card_number": "4111111111111111",
    "holder_name": "Juan Perez Ramirez",
    "expiration_year": "21",
    "expiration_month": "12",
    "cvv2": "110",
    "address": {
        "city": "Lima",
        "country_code": "PE",
        "postal_code": "110511",
        "line1": "Av 5 de Febrero",
        "line2": "Roble 207",
        "line3": "col carrillo",
        "state": "Lima"
    }
}

class OpenpayTestCase(unittest.TestCase):
    RESTORE_ATTRIBUTES = ('api_version', 'api_key')

    def setUp(self):
        super(OpenpayTestCase, self).setUp()

        self._openpay_original_attributes = {}

        for attr in self.RESTORE_ATTRIBUTES:
            self._openpay_original_attributes[attr] = getattr(openpay, attr)

        api_base = os.environ.get('OPENPAY_API_BASE')
        if api_base:
            openpay.api_base = api_base
        # Sandbox
        openpay.api_key = os.environ.get(
            'OPENPAY_API_KEY', 'sk_f934dfe51645483e82106301d985a4f6')
        openpay.merchant_id = "m3cji4ughukthjcsglv0"
        openpay.country = "pe"
        # Dev
        # openpay.api_key = os.environ.get(
        #    'OPENPAY_API_KEY', '68df281c16184d47bb773d70abd4191b')
        # openpay.merchant_id = "m4se8bd4fef1mkzk6d1b"
        openpay.verify_ssl_certs = False

    def tearDown(self):
        super(OpenpayTestCase, self).tearDown()

        for attr in self.RESTORE_ATTRIBUTES:
            setattr(openpay, attr, self._openpay_original_attributes[attr])

    # Python < 2.7 compatibility
    def assertRaisesRegexp(self, exception, regexp, callable, *args, **kwargs):
        try:
            callable(*args, **kwargs)
        except exception as err:
            if regexp is None:
                return True

            if isinstance(regexp, str):
                regexp = re.compile(regexp)
            if not regexp.search(str(err)):
                raise self.failureException('"%s" does not match "%s"' %
                                            (regexp.pattern, str(err)))
        else:
            raise self.failureException(
                '%s was not raised' % (exception.__name__,))


class OpenpayUnitTestCase(OpenpayTestCase):
    REQUEST_LIBRARIES = ['urlfetch', 'requests', 'pycurl']

    if sys.version_info >= (3, 0):
        REQUEST_LIBRARIES.append('urllib.request')
    else:
        REQUEST_LIBRARIES.append('urllib2')

    def setUp(self):
        super(OpenpayUnitTestCase, self).setUp()

        self.request_patchers = {}
        self.request_mocks = {}
        for lib in self.REQUEST_LIBRARIES:
            patcher = patch("openpay.http_client.%s" % (lib,))

            self.request_mocks[lib] = patcher.start()
            self.request_patchers[lib] = patcher

    def tearDown(self):
        super(OpenpayUnitTestCase, self).tearDown()

        for patcher in list(self.request_patchers.values()):
            patcher.stop()


class OpenpayApiTestCase(OpenpayTestCase):

    def setUp(self):
        super(OpenpayApiTestCase, self).setUp()

        self.requestor_patcher = patch('openpay.api.APIClient')
        requestor_class_mock = self.requestor_patcher.start()
        self.requestor_mock = requestor_class_mock.return_value

    def tearDown(self):
        super(OpenpayApiTestCase, self).tearDown()

        self.requestor_patcher.stop()

    def mock_response(self, res):
        self.requestor_mock.request = Mock(return_value=(res, 'reskey'))


class MyResource(openpay.resource.APIResource):
    pass


class MySingleton(openpay.resource.SingletonAPIResource):
    pass


class MyListable(openpay.resource.ListableAPIResource):
    pass


class MyCreatable(openpay.resource.CreateableAPIResource):
    pass


class MyUpdateable(openpay.resource.UpdateableAPIResource):
    pass


class MyDeletable(openpay.resource.DeletableAPIResource):
    pass


class MyComposite(openpay.resource.ListableAPIResource,
                  openpay.resource.CreateableAPIResource,
                  openpay.resource.UpdateableAPIResource,
                  openpay.resource.DeletableAPIResource):
    pass
