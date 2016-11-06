"""Implements bytecode decoding utilities."""
from __future__ import print_function, absolute_import, division, unicode_literals

from collections import namedtuple
from .opcodes import OPCODE_MAP
from .compat import byte2int


Instruction = namedtuple('Instruction', 'op imm')


def decode(bytecode):
    bytecode = memoryview(bytecode)
    while bytecode:
        opcode_id = byte2int(bytecode[0])
        opcode = OPCODE_MAP[opcode_id]

        if opcode.imm_struct is not None:
            offs, imm = opcode.imm_struct.from_raw(None, bytecode)
        else:
            imm = None
            offs = 0

        yield Instruction(opcode, imm)
        bytecode = bytecode[1 + offs:]
