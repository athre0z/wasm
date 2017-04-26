"""Provides functions for decoding WASM modules and bytecode."""
from __future__ import print_function, absolute_import, division, unicode_literals

from collections import namedtuple
from .modtypes import ModuleHeader, Section, SEC_UNK, SEC_NAME, NameSubSection
from .opcodes import OPCODE_MAP
from .compat import byte2int


Instruction = namedtuple('Instruction', 'op imm len')
ModuleFragment = namedtuple('ModuleFragment', 'type data')


def decode_bytecode(bytecode):
    """Decodes raw bytecode, yielding `Instruction`s."""
    bytecode_wnd = memoryview(bytecode)
    while bytecode_wnd:
        opcode_id = byte2int(bytecode_wnd[0])
        opcode = OPCODE_MAP[opcode_id]

        if opcode.imm_struct is not None:
            offs, imm, _ = opcode.imm_struct.from_raw(None, bytecode_wnd[1:])
        else:
            imm = None
            offs = 0

        insn_len = 1 + offs
        yield Instruction(opcode, imm, insn_len)
        bytecode_wnd = bytecode_wnd[insn_len:]


def decode_module(module, decode_name_subsections=False):
    """Decodes raw WASM modules, yielding `ModuleFragment`s."""
    module_wnd = memoryview(module)

    # Read & yield module header.
    hdr = ModuleHeader()
    hdr_len, hdr_data, _ = hdr.from_raw(None, module_wnd)
    yield ModuleFragment(hdr, hdr_data)
    module_wnd = module_wnd[hdr_len:]

    # Read & yield sections.
    while module_wnd:
        sec = Section()
        sec_len, sec_data, _ = sec.from_raw(None, module_wnd)

        # If requested, decode name subsections when encountered.
        if (
            decode_name_subsections and
            sec_data.id == SEC_UNK and
            sec_data.name == SEC_NAME
        ):
            sec_wnd = sec_data.payload
            while sec_wnd:
                subsec = NameSubSection()
                subsec_len, subsec_data, _ = subsec.from_raw(None, sec_wnd)
                yield ModuleFragment(subsec, subsec_data)
                sec_wnd = sec_wnd[subsec_len:]
        else:
            yield ModuleFragment(sec, sec_data)

        module_wnd = module_wnd[sec_len:]
