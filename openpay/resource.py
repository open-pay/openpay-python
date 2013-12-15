"""
File: resource.py
Author: Carlos Aguilar
Description: Define classes for every resource
"""
try:
    import json
except ImportError:
    import simplejson as json

import requests
import openpay
from openpay.api import APIClient


def convert_to_openpay_object(resp, api_key):
    types = {'charge': Charge, 'customer': Customer,
             'invoice': Invoice, 'invoiceitem': InvoiceItem,
             'plan': Plan, 'coupon': Coupon, 'token': Token, 'event': Event,
             'transfer': Transfer, 'list': ListObject, 'recipient': Recipient,
             'card': Card, 'application_fee': ApplicationFee}

    if isinstance(resp, list):
        return [convert_to_openpay_object(i, api_key) for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, BaseObject):
        resp = resp.copy()
        klass_name = resp.get('object')
        if isinstance(klass_name, basestring):
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
                "You may set %s.%s = None to delete the property" % (
                k, str(self), v))

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
                    (k, k, ', '.join(self.keys())))
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

        for k, v in values.iteritems():
            super(BaseObject, self).__setitem__(
                k, convert_to_openpay_object(v, api_key))

        self._previous_metadata = values.get('metadata')

    def request(self, method, url, params=None):
        if params is None:
            params = self._retrieve_params

        requestor = APIClient(self.api_key)
        response, api_key = requestor.request(method, url, params)

        return convert_to_openpay_object(response, api_key)

    def __repr__(self):
        ident_parts = [type(self).__name__]

        if isinstance(self.get('object'), basestring):
            ident_parts.append(self.get('object').encode('utf-8'))

        if isinstance(self.get('id'), basestring):
            ident_parts.append('id=%s' % (self.get('id').encode('utf8'),))

        return '<%s at %s> JSON: %s' % (
            ' '.join(ident_parts), hex(id(self)), str(self))

    def __str__(self):
        return json.dumps(self, sort_keys=True, indent=2)

    @property
    def stripe_id(self):
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
    def class_url(cls):
        cls_name = cls.class_name()
        return "/v1/%ss" % (cls_name,)

    def instance_url(self):
        id = self.get('id')
        if not id:
            raise error.InvalidRequestError(
                'Could not determine which URL to request: %s instance '
                'has invalid ID: %r' % (type(self).__name__, id), 'id')
        id = util.utf8(id)
        base = self.class_url()
        extn = urllib.quote_plus(id)
        return "%s/%s" % (base, extn)
