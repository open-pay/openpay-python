# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
import random
import re
import string
import sys
import time
import unittest

from future.builtins import range
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
    "name": "Cliente Colombia",
    "last_name": "Vazquez Juarez",
    "phone_number": "4448936475",
    "email": "juan.vazquez@empresa.co"
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
    'currency': 'COP',
    'iva': '10',
    'description': 'Dummy Charge'
}

DUMMY_CHARGE_MERCHANT = {
    'method': 'card',
    'amount': 100,
    'currency': 'COP',
    'iva': '10',
    'description': 'Dummy Charge',
    'confirm': 'false',
    'redirect_url': 'http://testing-openpay-col.com',
    'customer': DUMMY_CUSTOMER
}

DUMMY_CHARGE_STORE = {
    'method': 'store',
    'amount': 100,
    'currency': 'COP',
    'iva': '10',
    'description': 'Store Charge'
}

DUMMY_CHARGE_STORE_MERCHANT = {
    'method': 'store',
    'amount': 100,
    'currency': 'COP',
    'iva': '10',
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

DUMMY_PSE = {
    'method': 'bank_account',
    'amount': 100,
    'currency': 'COP',
    'iva': '10',
    'description': 'Dummy PSE',
    'confirm': 'false',
    'redirect_url': 'http://testing-openpay-col.com'
}

DUMMY_PSE_MERCHANT = {
    'method': 'bank_account',
    'amount': 100,
    'currency': 'COP',
    'iva': '10',
    'description': 'Dummy PSE',
    'confirm': 'false',
    'redirect_url': 'http://testing-openpay-col.com',
    'customer': DUMMY_CUSTOMER
}

DUMMY_ADDRESS = {
    "city": "Bogotá",
    "country_code": "CO",
    "postal_code": "110511",
    "line1": "Av 5 de Febrero",
    "line2": "Roble 207",
    "line3": "col carrillo",
    "state": "Bogota"
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
            'OPENPAY_API_KEY', 'sk_94a89308b4d7469cbda762c4b392152a')
        openpay.merchant_id = "mwf7x79goz7afkdbuyqd"
        openpay.country = "co"
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
