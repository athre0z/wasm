from __future__ import print_function, absolute_import, division, unicode_literals

from .compat import add_metaclass, byte2int
import collections
import logging
import struct


logger = logging.getLogger()


class WasmField(object):
    _type_ctr = 0

    def __init__(self):
        self._type_id = WasmField._type_ctr
        WasmField._type_ctr += 1

    def from_raw(self, struct, raw):
        raise NotImplementedError()

    #def to_raw(self, struct, value):
    #    raise NotImplementedError()

    def to_string(self, value):
        return repr(value)


def _make_shortcut(klass, *args, **kwargs):
    return lambda: klass(*args, **kwargs)


class UIntNField(WasmField):
    CONVERTER_MAP = {
        8: struct.Struct('<B'),
        16: struct.Struct('<H'),
        32: struct.Struct('<I'),
    }

    def __init__(self, n):
        super(UIntNField, self).__init__()
        self.n = n
        self.byte_size = n // 8
        self.converter = self.CONVERTER_MAP[n]

    def from_raw(self, struct, raw):
        return self.byte_size, self.converter.unpack(raw[:self.byte_size])[0]

    #def to_raw(self, struct, value):
    #    return value.to_bytes(self._byte_size, 'little')

    def to_string(self, value):
        return hex(byte2int(value) if self.n == 8 else value)


UInt8Field = _make_shortcut(UIntNField, 8)
UInt16Field = _make_shortcut(UIntNField, 16)
UInt32Field = _make_shortcut(UIntNField, 32)


class VarUIntNField(WasmField):
    def __init__(self, n):
        super(VarUIntNField, self).__init__()
        self.n = n

    def from_raw(self, struct, raw):
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
        return hex(value)


VarUInt1Field = _make_shortcut(VarUIntNField, 1)
VarUInt7Field = _make_shortcut(VarUIntNField, 7)
VarUInt32Field = _make_shortcut(VarUIntNField, 32)


class VarIntNField(WasmField):
    def __init__(self, n):
        super(VarIntNField, self).__init__()
        self.n = n

    def from_raw(self, struct, raw):
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


VarInt7Field = _make_shortcut(VarIntNField, 7)
VarInt32Field = _make_shortcut(VarIntNField, 32)
VarInt64Field = _make_shortcut(VarIntNField, 64)


class MetaInfo(object):
    def __init__(self):
        self.fields = []
        self.data_class = None


class StructureMeta(type):
    def __new__(mcs, name, bases, cls_dict):
        # Inject meta-info.
        meta = cls_dict['_meta'] = MetaInfo()

        # Iterate over fields, move relevant data to meta.
        for cur_field_name, cur_field in list(cls_dict.items()):
            # import inspect
            # from pprint import pprint
            # print(type(cur_field))
            # pprint(inspect.getclasstree(inspect.getmro(type(cur_field))))

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
                logger.warn('Non-WasmType field "{}" found on type "{}". Ignoring.'.format(
                    cur_field_name, name
                ))

        # As Py2 doesn't have __prepare__, we use a type counter in order to
        # determine the field order in the class.
        meta.fields = sorted(meta.fields, key=lambda x: x[1]._type_id)

        # Create data class.
        class StructureData(object):
            def __init__(self):
                for cur_field_name, cur_field in meta.fields:
                    setattr(self, cur_field_name, None)

        meta.data_class = StructureData
        return type.__new__(mcs, name, bases, cls_dict)


@add_metaclass(StructureMeta)
class Structure(WasmField):
    def from_raw(self, struct, raw):
        offs = 0
        data = self._meta.data_class()
        for cur_field_name, cur_field in self._meta.fields:
            data_len, val = cur_field.from_raw(data, raw[offs:])
            # print('{}_len = {}'.format(cur_field_name, data_len))
            # print('{} = {}'.format(cur_field_name, val))
            setattr(data, cur_field_name, val)
            offs += data_len
        return offs, data

    def to_string(self, value):
        header = '- [ {} ] -'.format(self.__class__.__name__)
        return '\n'.join([header] + [
            '  | {} = {}'.format(k, v.to_string(getattr(value, k)))
            for k, v in self._meta.fields
        ])


class CondField(WasmField):
    def __init__(self, field, condition):
        super(CondField, self).__init__()
        self.field = field
        self.condition = condition

    def from_raw(self, struct, raw):
        if self.condition(struct):
            return self.field.from_raw(struct, raw)
        return 0, None

    def to_string(self, value):
        return 'None' if value is None else self.field.to_string(value)


class RepeatField(WasmField):
    def __init__(self, field, repeat_count_getter):
        super(RepeatField, self).__init__()
        self.field = field
        self.repeat_count_getter = repeat_count_getter

    def from_raw(self, struct, raw):
        repeat_count = self.repeat_count_getter(struct)

        # Avoiding complex processing for byte arrays.
        if type(self.field) == UIntNField and self.field.n == 8:
            return repeat_count, raw[:repeat_count]

        # For more complex types, invoke the field for parsing the
        # individual fields.
        offs = 0
        items = []
        for i in range(repeat_count):
            length, item = self.field.from_raw(struct, raw[offs:])
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
    def __init__(self, choice_field_map, choice_getter):
        super(ChoiceField, self).__init__()
        self.choice_field_map = choice_field_map
        self.choice_getter = choice_getter

    def from_raw(self, struct, raw):
        choice = self.choice_getter(struct)
        if choice is None:
            return 0, None
        return self.choice_field_map[choice].from_raw(struct, raw)


class NoneField(WasmField):
    def from_raw(self, struct, raw):
        return 0, None
