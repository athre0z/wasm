from __future__ import print_function, absolute_import, division, unicode_literals

from .types import *


def _make_shortcut(klass, *args, **kwargs):
    return lambda: klass(*args, **kwargs)


UInt8Field = _make_shortcut(UIntNField, 8)
UInt16Field = _make_shortcut(UIntNField, 16)
UInt32Field = _make_shortcut(UIntNField, 32)
UInt64Field = _make_shortcut(UIntNField, 64)

VarUInt1Field = _make_shortcut(VarUIntNField, 1)
VarUInt7Field = _make_shortcut(VarUIntNField, 7)
VarUInt32Field = _make_shortcut(VarUIntNField, 32)

VarInt7Field = _make_shortcut(VarIntNField, 7)
VarInt32Field = _make_shortcut(VarIntNField, 32)
VarInt64Field = _make_shortcut(VarIntNField, 64)


ElementTypeField = VarInt7Field
ValueTypeField = VarInt7Field
ExternalKindField = UInt8Field
BlockTypeField = VarInt7Field
