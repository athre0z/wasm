from __future__ import print_function, absolute_import, division, unicode_literals

from .types import *
from .compat import byte2int


ElementType = VarInt7Field
ValueType = VarInt7Field
ExternalKind = UInt8Field


class ModuleHeader(Structure):
    magic = UInt32Field()
    version = UInt32Field()


class FunctionImportEntryData(Structure):
    type = VarUInt32Field()


class ResizableLimits(Structure):
    flags = VarUInt32Field()
    initial = VarUInt32Field()
    maximum = CondField(VarUInt32Field(), lambda x: x.flags & 1)


class TableType(Structure):
    element_type = ElementType()
    limits = ResizableLimits()


class MemoryType(Structure):
    limits = ResizableLimits()


class GlobalType(Structure):
    content_type = ValueType()
    mutability = VarUInt1Field()


class ImportEntry(Structure):
    module_len = VarUInt32Field()
    module_str = RepeatField(UInt8Field(), lambda x: x.module_len)
    field_len = VarUInt32Field()
    field_str = RepeatField(UInt8Field(), lambda x: x.field_len)
    kind = ExternalKind()
    type = ChoiceField({
        0: FunctionImportEntryData(),
        1: TableType(),
        2: MemoryType(),
        3: GlobalType(),
    }, lambda x: x.kind)


class ImportSection(Structure):
    count = VarUInt32Field()
    entries = RepeatField(ImportEntry(), lambda x: x.count)


class FuncType(Structure):
    form = VarInt7Field()
    param_count = VarUInt32Field()
    param_types = RepeatField(ValueType(), lambda x: x.param_count)
    return_count = VarUInt1Field()
    return_type = CondField(ValueType(), lambda x: bool(x.return_count))


class TypeSection(Structure):
    count = VarUInt32Field()
    entries = RepeatField(FuncType(), lambda x: x.count)


class FunctionSection(Structure):
    count = VarUInt32Field()
    types = RepeatField(VarUInt32Field(), lambda x: x.count)


class TableSection(Structure):
    count = VarUInt32Field()
    entries = RepeatField(TableType(), lambda x: x.count)


class MemorySection(Structure):
    count = VarUInt32Field()
    entries = RepeatField(MemoryType(), lambda x: x.count)


class InitExpr(WasmField):
    # TODO

    def from_raw(self, struct, raw):
        offs = 0
        while True:
            offs += 1
            if byte2int(raw[offs - 1]) == 0x0b:
                break
        return offs, None


class GlobalEntry(Structure):
    type = GlobalType()
    init = InitExpr()


class GlobalSection(Structure):
    count = VarUInt32Field()
    globals = RepeatField(GlobalEntry(), lambda x: x.count)


class ExportEntry(Structure):
    field_len = VarUInt32Field()
    field_str = RepeatField(UInt8Field(), lambda x: x.field_len)
    kind = ExternalKind()
    index = VarUInt32Field()


class ExportSection(Structure):
    count = VarUInt32Field()
    entries = RepeatField(ExportEntry(), lambda x: x.count)


class StartSection(Structure):
    index = VarUInt32Field()


class ElementSegment(Structure):
    index = VarUInt32Field()
    offset = InitExpr()
    num_elem = VarUInt32Field()
    elems = RepeatField(VarUInt32Field(), lambda x: x.num_elem)


class ElementSection(Structure):
    count = VarUInt32Field()
    entries = RepeatField(ElementSegment(), lambda x: x.count)


class LocalEntry(Structure):
    count = VarUInt32Field()
    type = ValueType()


class FunctionBody(Structure):
    body_size = VarUInt32Field()
    pad = RepeatField(UInt8Field(), lambda x: x.body_size)
    """
    local_count = VarUInt32Field()
    locals = RepeatField(LocalEntry(), lambda x: x.local_count)
    code = RepeatField(UInt8Field(), lambda x: <body_size> - <local shit>)
    """


class CodeSection(Structure):
    count = VarUInt32Field()
    bodies = RepeatField(FunctionBody(), lambda x: x.count)


class DataSegment(Structure):
    index = VarUInt32Field()
    offset = InitExpr()
    size = VarUInt32Field()
    data = RepeatField(UInt8Field(), lambda x: x.size)


class DataSection(Structure):
    count = VarUInt32Field()
    entries = DataSegment()


class Section(Structure):
    id = VarUInt7Field()
    payload_len = VarUInt32Field()
    name_len = CondField(VarUInt32Field(), lambda x: x.id == 0)
    name = CondField(RepeatField(UInt8Field(), lambda x: x.name_len), lambda x: x.id == 0)

    payload = ChoiceField({
        0: NoneField(),
        1: TypeSection(),
        2: ImportSection(),
        3: FunctionSection(),
        4: TableSection(),  # untested
        5: MemorySection(),  # untested
        6: GlobalSection(),
        7: ExportSection(),
        8: StartSection(),  # untested
        9: ElementSection(),
        10: CodeSection(),
        11: DataSection(),
    }, lambda x: x.id)

    overhang = RepeatField(
        UInt8Field(),
        lambda x: (
            (x.payload_len - ((1 + len(x.name)) if x.name else 0))
            if x.payload is None else 0
        )
    )
