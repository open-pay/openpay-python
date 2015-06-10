from __future__ import unicode_literals

try:
    import json
except ImportError:
    import simplejson as json

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus

from future.builtins import super
from future.builtins import hex
from future.builtins import str
import openpay
from openpay import api, error
from openpay.util import utf8, logger


def convert_to_openpay_object(resp, api_key, item_type=None):
    types = {'charge': Charge, 'customer': Customer,
             'plan': Plan, 'transfer': Transfer, 'list': ListObject,
             'card': Card, 'payout': Payout, 'subscription': Subscription,
             'bank_account': BankAccount, 'fee': Fee}

    if isinstance(resp, list):
        return [convert_to_openpay_object(i, api_key, item_type) for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, BaseObject):
        resp = resp.copy()
        klass_name = resp.get('object')
        if klass_name:
            klass_name = str(klass_name)

        if not klass_name and item_type:
            klass_name = str(item_type)
        if isinstance(klass_name, str):
            klass = types.get(klass_name, BaseObject)
        else:
            klass = BaseObject
        return klass.construct_from(resp, api_key)
    else:
        return resp


class BaseObject(dict):

    def __init__(self, id=None, api_key=None, **params):
        super(BaseObject, self).__init__()

        self._unsaved_values = set()
        self._transient_values = set()

        self._retrieve_params = params
        self._previous_metadata = None

        object.__setattr__(self, 'api_key', api_key)

        if id:
            self['id'] = id

    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super(BaseObject, self).__setattr__(k, v)
        else:
            self[k] = v

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(
                "You cannot set %s to an empty string. "
                "We interpret empty strings as None in requests."
                "You may set %s.%s = None to delete the property" %
                (k, str(self), v))

        super(BaseObject, self).__setitem__(k, v)
        self._unsaved_values.add(k)

    def __getitem__(self, k):
        try:
            return super(BaseObject, self).__getitem__(k)
        except KeyError as err:
            if k in self._transient_values:
                raise KeyError(
                    "%r.  HINT: The %r attribute was set in the past."
                    "It was then wiped when refreshing the object with "
                    "the result returned by Openpay's API, probably as a "
                    "result of a save().  The attributes currently "
                    "available on this object are: %s" %
                    (k, k, ', '.join(list(self.keys()))))
            else:
                raise err

    def __delitem__(self, k):
        raise TypeError(
            "You cannot delete attributes on a BaseObject. "
            "To unset a property, set it to None.")

    @classmethod
    def construct_from(cls, values, api_key):
        instance = cls(values.get('id'), api_key)
        instance.refresh_from(values, api_key)
        return instance

    def refresh_from(self, values, api_key=None, partial=False):
        self.api_key = api_key or getattr(values, 'api_key', None)

        # Wipe old state before setting new.  This is useful for e.g.
        # updating a customer, where there is no persistent card
        # parameter.  Mark those values which don't persist as transient
        if partial:
            self._unsaved_values = (self._unsaved_values - set(values))
        else:
            removed = set(self.keys()) - set(values)
            self._transient_values = self._transient_values | removed
            self._unsaved_values = set()

            self.clear()

        self._transient_values = self._transient_values - set(values)

        for k, v in values.items():
            super(BaseObject, self).__setitem__(
                k, convert_to_openpay_object(v, api_key))

        self._previous_metadata = values.get('metadata')

    def request(self, method, url, params=None):
        if params is None:
            params = self._retrieve_params

        requestor = api.APIClient(self.api_key)
        response, api_key = requestor.request(method, url, params)

        if isinstance(response, list):
            for item in response:
                if 'object' not in list(item.keys()):
                    item.update({'object': self.get('item_type')})

            data = {
                'object': 'list',
                'count': len(response),
                'url': url,
                'data': response,
                "item_type": self.get('item_type')
            }

            response = data

        if isinstance(response, dict) and self.get('item_type'):
            if 'object' not in list(response.keys()):
                response.update({'object': self.get('item_type')})

        return convert_to_openpay_object(response, api_key)

    def __repr__(self):
        ident_parts = [type(self).__name__]

        if isinstance(self.get('object'), str):
            ident_parts.append(self.get('object').encode('utf-8'))

        if isinstance(self.get('id'), str):
            ident_parts.append('id=%s' % (self.get('id').encode('utf8'),))

        return '<%s at %s> JSON: %s' % (
            ' '.join(ident_parts), hex(id(self)), str(self))

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    @property
    def openapay_id(self):
        return self.id


class APIResource(BaseObject):

    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        instance = cls(id, api_key, **params)
        instance.refresh()
        return instance

    def refresh(self):
        self.refresh_from(self.request('get', self.instance_url()))
        return self

    @classmethod
    def class_name(cls):
        if cls == APIResource:
            raise NotImplementedError(
                'APIResource is an abstract class. You should perform '
                'action on its subclasses (e.g. Charge, Customer)')
        return str(cls.__name__.lower())

    @classmethod
    def class_url(cls, params=None):
        merchant_id = openpay.merchant_id
        cls_name = cls.class_name()
        if params and 'customer' in list(params.keys()):
            return "/v1/{0}/customers/{1}/{2}s".format(
                merchant_id, params.get('customer'), cls_name)
        else:
            return "/v1/%s/%ss" % (merchant_id, cls_name)

    def instance_url(self):
        id = self.get('id')
        if not id:
            raise error.InvalidRequestError(
                'Could not determine which URL to request: %s instance '
                'has invalid ID: %r' % (type(self).__name__, id), 'id')
        id = utf8(id)
        params = None
        if 'customer' in list(self._retrieve_params.keys()):
            params = {'customer': self._retrieve_params.get('customer')}

        base = self.class_url(params)
        extn = quote_plus(id)
        return "%s/%s" % (base, extn)


class ListObject(BaseObject):

    def all(self, **params):
        return self.request('get', self['url'], params)

    def create(self, **params):
        return self.request('post', self['url'], params)

    def retrieve(self, id, **params):
        base = self.get('url')
        id = utf8(id)
        extn = quote_plus(id)
        url = "%s/%s" % (base, extn)

        return self.request('get', url, params)


class SingletonAPIResource(APIResource):

    @classmethod
    def retrieve(cls, api_key=None):
        return super(SingletonAPIResource, cls).retrieve(
            None, api_key=api_key)

    @classmethod
    def class_url(cls):
        merchant_id = openpay.merchant_id
        cls_name = cls.class_name()
        return "/v1/{0}/{1}".format(merchant_id, cls_name)

    def instance_url(self):
        return self.class_url()


# Classes of API operations
class ListableAPIResource(APIResource):

    @classmethod
    def all(cls, api_key=None, **params):
        requestor = api.APIClient(api_key)
        url = cls.class_url(params)
        
        response, api_key = requestor.request('get', url, params)
        klass_name = cls.__name__.lower()
        for item in response:
            if 'object' not in list(item.keys()):
                item.update({'object': klass_name})

        data = {
            'object': 'list',
            'count': len(response),
            'url': url,
            'data': response,
            'item_type': klass_name,
        }

        return convert_to_openpay_object(data, api_key)


class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, api_key=None, **params):
        requestor = api.APIClient(api_key)
        url = cls.class_url(params)
        
        if "clean_params" in dir(cls):
            params = cls.clean_params(params)
        
        response, api_key = requestor.request('post', url, params)
        klass_name = cls.__name__.lower()
        return convert_to_openpay_object(response, api_key, klass_name)


class UpdateableAPIResource(APIResource):

    def save(self):
        updated_params = self.serialize(self)

        if getattr(self, 'metadata', None):
            updated_params['metadata'] = self.serialize_metadata()

        if updated_params:
            updated_params = self.copy()
            if ('balance' in list(updated_params.keys())
                    and 'status' in list(updated_params.keys())):
                updated_params.update({'status': None, 'balance': None})
            else:
                updated_params.update({'status': None})

            self.refresh_from(self.request('put', self.instance_url(),
                                           updated_params))
        else:
            logger.debug("Trying to save already saved object %r", self)
        return self

    def serialize_metadata(self):
        if 'metadata' in self._unsaved_values:
            # the metadata object has been reassigned
            # i.e. as object.metadata = {key: val}
            metadata_update = self.metadata
            keys_to_unset = set(self._previous_metadata.keys()) - \
                set(self.metadata.keys())
            for key in keys_to_unset:
                metadata_update[key] = ""

            return metadata_update
        else:
            return self.serialize(self.metadata)

    def serialize(self, obj):
        params = {}
        if obj._unsaved_values:
            for k in obj._unsaved_values:
                if k == 'id' or k == '_previous_metadata':
                    continue
                v = getattr(obj, k)
                params[k] = v if v is not None else ""
        return params


class DeletableAPIResource(APIResource):

    def delete(self, **params):
        self.refresh_from(self.request('delete', self.instance_url(), params))
        return self

# API objects


class Card(ListableAPIResource, UpdateableAPIResource,
           DeletableAPIResource, CreateableAPIResource):

    @classmethod
    def class_url(cls, params=None):
        merchant_id = openpay.merchant_id
        cls_name = cls.class_name()
        if params and 'customer' in list(params.keys()):
            return "/v1/{0}/customers/{1}/{2}s".format(
                merchant_id, params.get('customer'), cls_name)
        else:
            return "/v1/%s/%ss" % (merchant_id, cls_name)

    def instance_url(self):
        self.id = utf8(self.id)
        if hasattr(self, 'customer'):
            self.customer = utf8(self.customer)
        else:
            self.customer = utf8(self.customer_id)

        base = Customer.class_url()
        cust_extn = self.customer
        extn = quote_plus(self.id)

        return "%s/%s/cards/%s" % (base, cust_extn, extn)

    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        raise NotImplementedError(
            "Can't retrieve a card without a customer ID. Use "
            "customer.cards.retrieve('card_id') instead.")

    def save(self):
        raise NotImplementedError("This feature is not supported yet by API")


class Charge(CreateableAPIResource, ListableAPIResource,
             UpdateableAPIResource):

    @classmethod
    def clean_params(cls, params=None):
        if params and params.get('customer', None) != None:
            del params['customer']
        
        return params
    
    @classmethod
    def class_url(cls, params=None):
        merchant_id = openpay.merchant_id
        cls_name = cls.class_name()
        if params and 'customer' in list(params.keys()):
            return "/v1/{0}/customers/{1}/{2}s".format(
                merchant_id, params.get('customer'), cls_name)
        else:
            return "/v1/%s/%ss" % (merchant_id, cls_name)

    def instance_url(self):
        self.id = utf8(self.id)

        if hasattr(self, '_as_merchant'):
            base = Charge.class_url()
            extn = quote_plus(self.id)
            url = "{0}/{1}".format(base, extn)
        else:
            self.customer = utf8(self.customer_id)
            base = Customer.class_url()
            cust_extn = self.customer
            extn = quote_plus(self.id)
            url = "%s/%s/charges/%s" % (base, cust_extn, extn)

        return url

    def refund(self, **params):
        if 'merchant' in list(params.keys()):
            self._as_merchant = True
        else:
            self._as_merchant = False

        del params['merchant']
        url = self.instance_url() + '/refund'
        self.refresh_from(self.request('post', url, params))
        return self

    def capture(self, **params):
        if 'merchant' in list(params.keys()):
            self._as_merchant = True
            del params['merchant']
        else:
            self._as_merchant = False

        url = self.instance_url() + '/capture'
        self.refresh_from(self.request('post', url, params))
        return self

    def update_dispute(self, **params):
        requestor = api.APIClient(self.api_key)
        url = self.instance_url() + '/dispute'
        response, api_key = requestor.request('post', url, params)
        self.refresh_from({'dispute': response}, api_key, True)
        return self.dispute

    def close_dispute(self):
        requestor = api.APIClient(self.api_key)
        url = self.instance_url() + '/dispute/close'
        response, api_key = requestor.request('post', url, {})
        self.refresh_from({'dispute': response}, api_key, True)
        return self.dispute

    @classmethod
    def as_merchant(cls):

        params = {}
        if hasattr(cls, 'api_key'):
            api_key = cls.api_key
        else:
            api_key = openpay.api_key

        requestor = api.APIClient(api_key)
        url = cls.class_url()
        response, api_key = requestor.request('get', url, params)
        return convert_to_openpay_object(response, api_key, 'charge')

    @classmethod
    def retrieve_as_merchant(cls, id):
        params = {}
        if hasattr(cls, 'api_key'):
            api_key = cls.api_key
        else:
            api_key = openpay.api_key

        cls._as_merchant = True
        requestor = api.APIClient(api_key)
        url = cls.class_url()
        id = utf8(id)
        extn = quote_plus(id)
        url = "%s/%s" % (url, extn)
        response, api_key = requestor.request('get', url, params)
        return convert_to_openpay_object(response, api_key, 'charge')

    @classmethod
    def create_as_merchant(cls, **params):
        if hasattr(cls, 'api_key'):
            api_key = cls.api_key
        else:
            api_key = openpay.api_key

        requestor = api.APIClient(api_key)
        url = cls.class_url()
        # charge over merchant
        response, api_key = requestor.request('post', url, params)
        return convert_to_openpay_object(response, api_key, 'charge')


class Customer(CreateableAPIResource, UpdateableAPIResource,
               ListableAPIResource, DeletableAPIResource):

    @property
    def cards(self):
        data = {
            'object': 'list',
            'url': Card.class_url({'customer': self.id}),
            'count': 0,
            'item_type': 'card'
        }

        if not hasattr(self, '_cards'):
            self._cards = convert_to_openpay_object(data, self.api_key)

        return self._cards

    @property
    def charges(self):
        data = {
            'object': 'list',
            'url': Charge.class_url({'customer': self.id}),
            'count': 0,
            'item_type': 'charge'
        }

        if not hasattr(self, '_charges'):
            self._charges = convert_to_openpay_object(data, self.api_key)

        return self._charges

    @property
    def transfers(self):
        data = {
            'object': 'list',
            'url': Transfer.class_url({'customer': self.id}),
            'count': 0,
            'item_type': 'transfer'
        }

        if not hasattr(self, '_transfers'):
            self._transfers = convert_to_openpay_object(data, self.api_key)

        return self._transfers

    @property
    def payouts(self):
        data = {
            'object': 'list',
            'url': Payout.class_url({'customer': self.id}),
            'count': 0,
            'item_type': 'payout'
        }

        if not hasattr(self, '_payouts'):
            self._payouts = convert_to_openpay_object(data, self.api_key)

        return self._payouts

    @property
    def bank_accounts(self):
        data = {
            'object': 'list',
            'url': BankAccount.class_url({'customer': self.id}),
            'count': 0,
            'item_type': 'bank_account'
        }

        if not hasattr(self, '_back_accounts'):
            self._back_accounts = convert_to_openpay_object(data, self.api_key)

        return self._back_accounts

    @property
    def subscriptions(self):
        data = {
            'object': 'list',
            'url': Subscription.class_url({'customer': self.id}),
            'count': 0,
            'item_type': 'subscription'
        }

        if not hasattr(self, '_subscriptions'):
            self._subscriptions = convert_to_openpay_object(data, self.api_key)

        return self._subscriptions


class Plan(CreateableAPIResource, DeletableAPIResource,
           UpdateableAPIResource, ListableAPIResource):
    pass


class Transfer(CreateableAPIResource, UpdateableAPIResource,
               ListableAPIResource):
    pass


class BankAccount(CreateableAPIResource, UpdateableAPIResource,
                  DeletableAPIResource, ListableAPIResource):
    pass


class Payout(CreateableAPIResource, ListableAPIResource):

    @classmethod
    def create_as_merchant(cls, **params):
        if hasattr(cls, 'api_key'):
            api_key = cls.api_key
        else:
            api_key = openpay.api_key

        requestor = api.APIClient(api_key)
        url = cls.class_url()
        response, api_key = requestor.request('post', url, params)
        return convert_to_openpay_object(response, api_key, 'payout')

    @classmethod
    def retrieve_as_merchant(cls, payout_id):
        params = {}
        if hasattr(cls, 'api_key'):
            api_key = cls.api_key
        else:
            api_key = openpay.api_key

        requestor = api.APIClient(api_key)
        url = cls.class_url()
        url = "{0}/{1}".format(url, payout_id)
        response, api_key = requestor.request('get', url, params)
        return convert_to_openpay_object(response, api_key, 'payout')


class Fee(CreateableAPIResource, ListableAPIResource):
    pass


class Subscription(DeletableAPIResource, UpdateableAPIResource):

    def instance_url(self):
        self.id = utf8(self.id)
        if hasattr(self, 'customer'):
            self.customer = utf8(self.customer)
        else:
            self.customer = utf8(self.customer_id)

        base = Customer.class_url()
        cust_extn = self.customer
        extn = quote_plus(self.id)

        return "%s/%s/subscriptions/%s" % (base, cust_extn, extn)
