"""Defines compatibility quirks for Python 2.7."""
from __future__ import print_function, absolute_import, division, unicode_literals

import sys


def add_metaclass(metaclass):
    """
    Class decorator for creating a class with a metaclass.
    Borrowed from `six` module.
    """
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


def indent(text, prefix, predicate=None):
    """Adds 'prefix' to the beginning of selected lines in 'text'.

    If 'predicate' is provided, 'prefix' will only be added to the lines
    where 'predicate(line)' is True. If 'predicate' is not provided,
    it will default to adding 'prefix' to all non-empty lines that do not
    consist solely of whitespace characters.

    Borrowed from Py3 `textwrap` module.
    """
    if predicate is None:
        def predicate(line):
            return line.strip()

    def prefixed_lines():
        for line in text.splitlines(True):
            yield (prefix + line if predicate(line) else line)
    return ''.join(prefixed_lines())


if sys.version_info[0] >= 3:
    def byte2int(x):
        return x

elif sys.version_info[0] == 2:
    def byte2int(x):
        return ord(x) if type(x) == str else x

else:
    raise Exception("Unsupported Python version")


