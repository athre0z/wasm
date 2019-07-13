from __future__ import unicode_literals

__version__ = '1.2'

from .decode import (
    decode_bytecode,
    decode_module,
)

from .formatter import (
    format_function,
    format_instruction,
    format_lang_type,
    format_mutability,
)

from .modtypes import (
    ModuleHeader,
    FunctionImportEntryData,
    ResizableLimits,
    TableType,
    MemoryType,
    GlobalType,
    ImportEntry,
    ImportSection,
    FuncType,
    TypeSection,
    FunctionSection,
    TableSection,
    MemorySection,
    InitExpr,
    GlobalEntry,
    GlobalSection,
    ExportEntry,
    ExportSection,
    StartSection,
    ElementSegment,
    ElementSection,
    LocalEntry,
    FunctionBody,
    CodeSection,
    DataSegment,
    DataSection,
    Naming,
    NameMap,
    LocalNames,
    LocalNameMap,
    NameSubSection,
    Section,
)

from .immtypes import (
    BlockImm,
    BranchImm,
    BranchTableImm,
    CallImm,
    CallIndirectImm,
    LocalVarXsImm,
    GlobalVarXsImm,
    MemoryImm,
    CurGrowMemImm,
    I32ConstImm,
    I64ConstImm,
    F32ConstImm,
    F64ConstImm,
)

from .opcodes import (
    Opcode,
    INSN_ENTER_BLOCK,
    INSN_LEAVE_BLOCK,
    INSN_BRANCH,
    INSN_NO_FLOW,
)

for cur_op in opcodes.OPCODES:
    globals()[
        'OP_' + cur_op.mnemonic.upper().replace('.', '_').replace('/', '_')
    ] = cur_op.id

from .wasmtypes import (
    UInt8Field,
    UInt16Field,
    UInt32Field,
    UInt64Field,
    VarUInt1Field,
    VarUInt7Field,
    VarUInt32Field,
    VarInt7Field,
    VarInt32Field,
    VarInt64Field,
    ElementTypeField,
    ValueTypeField,
    ExternalKindField,
    BlockTypeField,
    SEC_UNK,
    SEC_TYPE,
    SEC_IMPORT,
    SEC_FUNCTION,
    SEC_TABLE,
    SEC_MEMORY,
    SEC_GLOBAL,
    SEC_EXPORT,
    SEC_START,
    SEC_ELEMENT,
    SEC_CODE,
    SEC_DATA,
    SEC_NAME,
    LANG_TYPE_I32,
    LANG_TYPE_I64,
    LANG_TYPE_F32,
    LANG_TYPE_F64,
    LANG_TYPE_ANYFUNC,
    LANG_TYPE_FUNC,
    LANG_TYPE_EMPTY,
    VAL_TYPE_I32,
    VAL_TYPE_I64,
    VAL_TYPE_F32,
    VAL_TYPE_F64,
    NAME_SUBSEC_FUNCTION,
    NAME_SUBSEC_LOCAL,
    IMMUTABLE,
    MUTABLE,
)
