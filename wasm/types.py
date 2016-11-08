"""Defines a simple, generic data (de)serialization mechanism."""
from __future__ import print_function, absolute_import, division, unicode_literals

from .compat import add_metaclass, byte2int
import collections
import logging
import struct as pystruct


logger = logging.getLogger()


class WasmField(object):
    """
    Abstract base class for all fields.

    Fields are purely a (de)serialization mechanism. They don't hold the value
    of decoded information, but take Python data-types and convert them
    to a raw byte format or vice versa. Thus, a field instance can be reused
    to de/encode multiple values.

    Besides the abstract interface, implements type counting and IDing to allow
    field order detection in Python 2, where `__prepare__` doesn't exist yet.
    In order to work correctly, field instances MUST NOT be shared between
    multiple structures using it but have to be instantiated per structure.
    """
    _type_ctr = 0

    def __init__(self):
        self._type_id = WasmField._type_ctr
        WasmField._type_ctr += 1

    def from_raw(self, struct, raw):
        raise NotImplementedError()

    def to_string(self, value):
        return repr(value)


class UIntNField(WasmField):
    """Field handling an unsigned LE int of fixed size."""
    CONVERTER_MAP = {
        8: pystruct.Struct('<B'),
        16: pystruct.Struct('<H'),
        32: pystruct.Struct('<I'),
        64: pystruct.Struct('<Q'),
    }

    def __init__(self, n, **kwargs):
        super(UIntNField, self).__init__(**kwargs)
        self.n = n
        self.byte_size = n // 8
        self.converter = self.CONVERTER_MAP[n]

    def from_raw(self, ctx, raw):
        return self.byte_size, self.converter.unpack(raw[:self.byte_size])[0]

    def to_string(self, value):
        return hex(byte2int(value) if self.n == 8 else value)


class UnsignedLeb128Field(WasmField):
    """
    Field handling unsigned LEB128 values.
    https://en.wikipedia.org/wiki/LEB128
    """
    def from_raw(self, ctx, raw):
        offs = 0
        val = 0

        while True:
            segment = byte2int(raw[offs])
            val |= (segment & 0x7F) << (offs * 7)
            offs += 1
            if not (segment & 0x80):
                break

        return offs, val

    def to_string(self, value):
        return hex(value) if value > 1000 else str(value)


class SignedLeb128Field(WasmField):
    """
    Field handling signed LEB128 values.
    https://en.wikipedia.org/wiki/LEB128
    """
    def from_raw(self, ctx, raw):
        offs = 0
        val = 0
        bits = 0

        while True:
            segment = byte2int(raw[offs])
            val |= (segment & 0x7F) << bits
            offs += 1
            bits += 7
            if not (segment & 0x80):
                break

        if val & (1 << (bits - 1)):
            val -= 1 << bits

        return offs, val


class CondField(WasmField):
    """Optionalizes a field, depending on the context."""
    def __init__(self, field, condition, **kwargs):
        super(CondField, self).__init__(**kwargs)
        self.field = field
        self.condition = condition

    def from_raw(self, ctx, raw):
        if self.condition(ctx):
            return self.field.from_raw(ctx, raw)
        return 0, None

    def to_string(self, value):
        return 'None' if value is None else self.field.to_string(value)


class RepeatField(WasmField):
    """Repeats a field, having the repeat count depend on the context."""
    def __init__(self, field, repeat_count_getter, **kwargs):
        super(RepeatField, self).__init__(**kwargs)
        self.field = field
        self.repeat_count_getter = repeat_count_getter

    def from_raw(self, ctx, raw):
        repeat_count = self.repeat_count_getter(ctx)

        # Avoiding complex processing for byte arrays.
        if type(self.field) == UIntNField and self.field.n == 8:
            return repeat_count, raw[:repeat_count]

        # For more complex types, invoke the field for parsing the
        # individual fields.
        offs = 0
        items = []
        for i in range(repeat_count):
            length, item = self.field.from_raw(ctx, raw[offs:])
            offs += length
            items.append(item)

        return offs, items

    def to_string(self, value):
        if value is None:
            return None
        if len(value) > 100:
            return '<too long>'
        return '[' + ', '.join(self.field.to_string(x) for x in value) + ']'


class ChoiceField(WasmField):
    """Depending on context, either represent this or that field type."""
    def __init__(self, choice_field_map, choice_getter, **kwargs):
        super(ChoiceField, self).__init__(**kwargs)
        self.choice_field_map = choice_field_map
        self.choice_getter = choice_getter

    def from_raw(self, ctx, raw):
        choice = self.choice_getter(ctx)
        if choice is None:
            return 0, None
        return self.choice_field_map[choice].from_raw(ctx, raw)


class ConstField(WasmField):
    """Pseudo-Field, always returning a constant, consuming/generating no data."""
    def __init__(self, const, **kwargs):
        super(ConstField, self).__init__(**kwargs)
        self.const = const

    def from_raw(self, ctx, raw):
        return 0, self.const


class MetaInfo(object):
    """Meta information for a `Structure`."""
    def __init__(self):
        self.fields = []
        self.data_class = None


class StructureData(object):
    """Base class for generated structure data classes."""
    __slots__ = ('_meta', '_data_meta')

    def __init__(self):
        self._data_meta = {'lengths': {}}
        for cur_field_name, cur_field in self._meta.fields:
            setattr(self, cur_field_name, None)


class StructureMeta(type):
    """
    Metaclass used to create `Structure` classes,
    populating their `_meta`field and performing sanity checks.
    """
    def __new__(mcs, name, bases, cls_dict):
        # Inject meta-info.
        meta = cls_dict['_meta'] = MetaInfo()

        # Iterate over fields, move relevant data to meta.
        for cur_field_name, cur_field in list(cls_dict.items()):
            # Is callable, property, private or magic? We don't touch those.
            if (
                isinstance(cur_field, collections.Callable) or
                isinstance(cur_field, property) or
                cur_field_name.startswith('_')
            ):
                pass

            # Is one of our types? Metafy.
            elif isinstance(cur_field, WasmField):
                meta.fields.append((cur_field_name, cur_field))
                # del cls_dict[cur_field_name]

            # Unknown type, print warning.
            else:
                logger.warn(
                    'Non-WasmType field "{}" found on type "{}". '
                    'Ignoring.'.format(cur_field_name, name)
                )

        # Order fields by type ID (see `WasmField` for the "why").
        meta.fields = sorted(meta.fields, key=lambda x: x[1]._type_id)

        # Create data class type for "instances".
        class GeneratedStructureData(StructureData):
            __slots__ = [x for x, _ in meta.fields]
            _meta = meta
        meta.data_class = GeneratedStructureData

        return type.__new__(mcs, name, bases, cls_dict)


@add_metaclass(StructureMeta)
class Structure(WasmField):
    """Represents a collection of named fields."""
    def from_raw(self, ctx, raw):
        offs = 0
        data = self._meta.data_class()
        for cur_field_name, cur_field in self._meta.fields:
            data_len, val = cur_field.from_raw(data, raw[offs:])
            setattr(data, cur_field_name, val)
            data._data_meta['lengths'][cur_field_name] = data_len
            offs += data_len
        return offs, data

    def to_string(self, value):
        header = '- [ {} ] -'.format(self.__class__.__name__)
        return '\n'.join([header] + [
            '  | {} = {}'.format(k, v.to_string(getattr(value, k)))
            for k, v in self._meta.fields
        ])
