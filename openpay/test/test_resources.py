import openpay
from openpay import util

from openpay.test.helper import (
    OpenpayUnitTestCase)


class BaseObjectTests(OpenpayUnitTestCase):

    def test_initializes_with_parameters(self):
        obj = openpay.resource.BaseObject(
            'foo', 'bar', myparam=5, yourparam='boo')

        self.assertEqual('foo', obj.id)
        self.assertEqual('bar', obj.api_key)
