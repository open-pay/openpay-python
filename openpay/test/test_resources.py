from __future__ import print_function
from __future__ import unicode_literals
from future.builtins import super
#import json
import openpay
#from openpay import util

from openpay.test.helper import (
    OpenpayUnitTestCase, OpenpayApiTestCase,
    MySingleton, MyListable, MyCreatable, MyUpdateable, MyDeletable,
    MyResource)


class BaseObjectTests(OpenpayUnitTestCase):

    def test_initializes_with_parameters(self):
        obj = openpay.resource.BaseObject(
            'foo', 'bar', myparam=5, yourparam='boo')

        self.assertEqual('foo', obj.id)
        self.assertEqual('bar', obj.api_key)

    def test_access(self):
        obj = openpay.resource.BaseObject('myid', 'mykey', myparam=5)

        # Empty
        self.assertRaises(AttributeError, getattr, obj, 'myattr')
        self.assertRaises(KeyError, obj.__getitem__, 'myattr')
        self.assertEqual('def', obj.get('myattr', 'def'))
        self.assertEqual(None, obj.get('myattr'))

        # Setters
        obj.myattr = 'myval'
        obj['myitem'] = 'itval'
        self.assertEqual('sdef', obj.setdefault('mydef', 'sdef'))

        # Getters
        self.assertEqual('myval', obj.setdefault('myattr', 'sdef'))
        self.assertEqual('myval', obj.myattr)
        self.assertEqual('myval', obj['myattr'])
        self.assertEqual('myval', obj.get('myattr'))

        self.assertEqual(['id', 'myattr', 'mydef', 'myitem'],
                         sorted(obj.keys()))
        self.assertEqual(['itval', 'myid', 'myval', 'sdef'],
                         sorted(obj.values()))

        # Illegal operations
        self.assertRaises(ValueError, setattr, obj, 'foo', '')
        self.assertRaises(TypeError, obj.__delitem__, 'myattr')

    def test_refresh_from(self):
        obj = openpay.resource.BaseObject.construct_from({
            'foo': 'bar',
            'trans': 'me',
        }, 'mykey')

        self.assertEqual('mykey', obj.api_key)
        self.assertEqual('bar', obj.foo)
        self.assertEqual('me', obj['trans'])

        obj.refresh_from({
            'foo': 'baz',
            'johnny': 5,
        }, 'key2')

        self.assertEqual(5, obj.johnny)
        self.assertEqual('baz', obj.foo)
        self.assertRaises(AttributeError, getattr, obj, 'trans')
        self.assertEqual('key2', obj.api_key)

        obj.refresh_from({
            'trans': 4,
            'metadata': {'amount': 42}
        }, 'key2', True)

        self.assertEqual('baz', obj.foo)
        self.assertEqual(4, obj.trans)
        self.assertEqual({'amount': 42}, obj._previous_metadata)

#    def test_refresh_from_nested_object(self):
#        obj = openpay.resource.BaseObject.construct_from(
#            SAMPLE_INVOICE, 'key')
#
#        self.assertEqual(1, len(obj.lines.subscriptions))
#        self.assertTrue(
#            isinstance(obj.lines.subscriptions[0],
#                       openpay.resource.BaseObject))
#        self.assertEqual('month', obj.lines.subscriptions[0].plan.interval)

#    def test_to_json(self):
#        obj = openpay.resource.BaseObject.construct_from(
#            SAMPLE_INVOICE, 'key')
#
#        self.check_invoice_data(json.loads(str(obj)))

    def check_invoice_data(self, data):
        # Check rough structure
        self.assertEqual(20, len(list(data.keys())))
        self.assertEqual(3, len(list(data['lines'].keys())))
        self.assertEqual(0, len(data['lines']['invoiceitems']))
        self.assertEqual(1, len(data['lines']['subscriptions']))

        # Check various data types
        self.assertEqual(1338238728, data['date'])
        self.assertEqual(None, data['next_payment_attempt'])
        self.assertEqual(False, data['livemode'])
        self.assertEqual('month',
                         data['lines']['subscriptions'][0]['plan']['interval'])


class ListObjectTests(OpenpayApiTestCase):

    def setUp(self):
        super(ListObjectTests, self).setUp()

        self.lo = openpay.resource.ListObject.construct_from({
            'id': 'me',
            'url': '/my/path',
            'item_type': 'charge'
        }, 'mykey')

        self.mock_response([{
            'foo': 'bar',
        }])

    def assertResponse(self, res):
        self.assertTrue(isinstance(res.data[0], openpay.Charge))
        self.assertEqual('bar', res.data[0].foo)

    def test_all(self):
        res = self.lo.all(myparam='you')

        self.requestor_mock.request.assert_called_with(
            'get', '/my/path', {'myparam': 'you'})

        self.assertResponse(res)

    def test_create(self):
        res = self.lo.create(myparam='eter')

        self.requestor_mock.request.assert_called_with(
            'post', '/my/path', {'myparam': 'eter'})

        self.assertResponse(res)

    def test_retrieve(self):
        res = self.lo.retrieve('myid', myparam='cow')

        self.requestor_mock.request.assert_called_with(
            'get', '/my/path/myid', {'myparam': 'cow'})

        self.assertResponse(res)


class APIResourceTests(OpenpayApiTestCase):

    def test_retrieve_and_refresh(self):
        self.mock_response({
            'id': 'foo2',
            'bobble': 'scrobble',
        })

        res = MyResource.retrieve('foo*', myparam=5)

        url = '/v1/{0}/myresources/foo%2A'.format(openpay.merchant_id)
        self.requestor_mock.request.assert_called_with(
            'get', url, {'myparam': 5}
        )

        self.assertEqual('scrobble', res.bobble)
        self.assertEqual('foo2', res.id)
        self.assertEqual('reskey', res.api_key)

        self.mock_response({
            'frobble': 5,
        })

        res = res.refresh()

        url = '/v1/{0}/myresources/foo2'.format(openpay.merchant_id)
        self.requestor_mock.request.assert_called_with(
            'get', url, {'myparam': 5}
        )

        self.assertEqual(5, res.frobble)
        self.assertRaises(KeyError, res.__getitem__, 'bobble')

    def test_convert_to_openpay_object(self):
        sample = {
            'foo': 'bar',
            'adict': {
                'object': 'charge',
                'id': 42,
                'amount': 7,
            },
            'alist': [
                {
                    'object': 'customer',
                    'name': 'chilango'
                }
            ]
        }

        converted = openpay.resource.convert_to_openpay_object(sample, 'akey')

        # Types
        self.assertTrue(isinstance(converted, openpay.resource.BaseObject))
        self.assertTrue(isinstance(converted.adict, openpay.Charge))
        self.assertEqual(1, len(converted.alist))
        self.assertTrue(isinstance(converted.alist[0], openpay.Customer))

        # Values
        self.assertEqual('bar', converted.foo)
        self.assertEqual(42, converted.adict.id)
        self.assertEqual('chilango', converted.alist[0].name)

        # Stripping
        # TODO: We should probably be stripping out this property
        # self.assertRaises(AttributeError, getattr, converted.adict, 'object')


class SingletonAPIResourceTests(OpenpayApiTestCase):

    def test_retrieve(self):
        self.mock_response({
            'single': 'ton'
        })
        res = MySingleton.retrieve()
        url = '/v1/{0}/mysingleton'.format(openpay.merchant_id)
        self.requestor_mock.request.assert_called_with(
            'get', url, {})

        self.assertEqual('ton', res.single)


class ListableAPIResourceTests(OpenpayApiTestCase):

    def test_all(self):
        self.mock_response([
            {
                'object': 'charge',
                'name': 'jose',
            },
            {
                'object': 'charge',
                'name': 'curly',
            }
        ])

        res = MyListable.all()
        url = '/v1/{0}/mylistables'.format(openpay.merchant_id)
        self.requestor_mock.request.assert_called_with(
            'get', url, {})

        self.assertEqual(2, len(res.data))
        self.assertTrue(all(
            isinstance(obj, openpay.Charge) for obj in res.data))
        self.assertEqual('jose', res.data[0].name)
        self.assertEqual('curly', res.data[1].name)


class CreateableAPIResourceTests(OpenpayApiTestCase):

    def test_create(self):
        self.mock_response({
            'object': 'charge',
            'foo': 'bar',
        })

        res = MyCreatable.create()
        url = '/v1/{0}/mycreatables'.format(openpay.merchant_id)
        self.requestor_mock.request.assert_called_with(
            'post', url, {})

        self.assertTrue(isinstance(res, openpay.Charge))
        self.assertEqual('bar', res.foo)


class UpdateableAPIResourceTests(OpenpayApiTestCase):

    def setUp(self):
        super(UpdateableAPIResourceTests, self).setUp()

        self.mock_response({
            'thats': 'it'
        })

        self.obj = MyUpdateable.construct_from({
            'id': 'myid',
            'foo': 'bar',
            'baz': 'boz',
            'metadata': {
                'size': 'l',
                'score': 4,
                'height': 10
            }
        }, 'mykey')

    def checkSave(self):
        self.assertTrue(self.obj is self.obj.save())

        self.assertEqual('it', self.obj.thats)
        # TODO: Should we force id to be retained?
        # self.assertEqual('myid', obj.id)
        self.assertRaises(AttributeError, getattr, self.obj, 'baz')

    def test_save(self):
        self.obj.baz = 'updated'
        self.obj.other = 'newval'
        self.obj.metadata.size = 'm'
        self.obj.metadata.info = 'a2'
        self.obj.metadata.height = None

        self.checkSave()

        self.requestor_mock.request.assert_called_with(
            'put',
            '/v1/{0}/myupdateables/myid'.format(openpay.merchant_id),
            MyUpdateable.construct_from({
                'id': 'myid',
                'foo': 'bar',
                'baz': 'updated',
                'other': 'newval',
                'status': None,
                'metadata': {
                    'size': 'm',
                    'info': 'a2',
                    'height': None,
                    'score': 4
                }
            }, 'mykey')
        )

    def test_save_replace_metadata(self):
        self.obj.baz = 'updated'
        self.obj.other = 'newval'
        self.obj.metadata = {
            'size': 'm',
            'info': 'a2',
            'score': 4,
        }

        self.checkSave()

        self.requestor_mock.request.assert_called_with(
            'put',
            '/v1/{0}/myupdateables/myid'.format(openpay.merchant_id),
            MyUpdateable.construct_from({
                'baz': 'updated',
                'other': 'newval',
                'id': 'myid',
                'foo': 'bar',
                'status': None,
                'metadata': {
                    'size': 'm',
                    'info': 'a2',
                    'height': '',
                    'score': 4,
                }
            }, 'mykey')
        )


class DeletableAPIResourceTests(OpenpayApiTestCase):

    def test_delete(self):
        self.mock_response({
            'id': 'mid',
            'deleted': True,
        })

        obj = MyDeletable.construct_from({
            'id': 'mid'
        }, 'mykey')

        self.assertTrue(obj is obj.delete())

        self.assertEqual(True, obj.deleted)
        self.assertEqual('mid', obj.id)
