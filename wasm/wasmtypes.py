"""Defines types used for both modules and bytecode."""
from __future__ import print_function, absolute_import, division, unicode_literals

from .types import UIntNField, UnsignedLeb128Field, SignedLeb128Field


def _make_shortcut(klass, *args, **kwargs):
    return lambda: klass(*args, **kwargs)


UInt8Field = _make_shortcut(UIntNField, 8)
UInt16Field = _make_shortcut(UIntNField, 16)
UInt32Field = _make_shortcut(UIntNField, 32)
UInt64Field = _make_shortcut(UIntNField, 64)

VarUInt1Field = _make_shortcut(UnsignedLeb128Field)
VarUInt7Field = _make_shortcut(UnsignedLeb128Field)
VarUInt32Field = _make_shortcut(UnsignedLeb128Field)

VarInt7Field = _make_shortcut(SignedLeb128Field)
VarInt32Field = _make_shortcut(SignedLeb128Field)
VarInt64Field = _make_shortcut(SignedLeb128Field)

ElementTypeField = VarInt7Field
ValueTypeField = VarInt7Field
ExternalKindField = UInt8Field
BlockTypeField = VarInt7Field
