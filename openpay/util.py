
import logging
import sys


logger = logging.getLogger('stripe')

__all__ = ['utf8']


def utf8(value):
    if sys.version_info[0] < 3:
        if isinstance(value, unicode):
            return value.encode('utf-8')
    return value
