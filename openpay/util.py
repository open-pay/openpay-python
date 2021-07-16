
import logging
import sys

logger = logging.getLogger('stripe')
logger.addHandler(logging.NullHandler()) # https://docs.python-guide.org/writing/logging/#logging-in-a-library

__all__ = ['utf8']


def utf8(value):
    if isinstance(value, unicode) and sys.version_info < (3, 0):
        return value.encode('utf-8')
    else:
        return value
