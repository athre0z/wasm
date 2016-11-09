"""Testing & debug stuff."""
from __future__ import print_function, absolute_import, division, unicode_literals

from .formatter import format_instruction
from .opcodes import INSN_ENTER_BLOCK, INSN_LEAVE_BLOCK, OP_CALL
from .modtypes import ModuleHeader, Section, SEC_CODE
from .decode import decode

for _ in range(1):
    with open('demo/hello/hello.wasm', 'rb') as f:
        d = memoryview(f.read())

    hdr = ModuleHeader()
    offs, data = hdr.from_raw(None, d)
    print(hdr.to_string(data))

    while offs != len(d):
        sec = Section()
        size, data = sec.from_raw(None, d[offs:])
        print(sec.to_string(data))
        offs += size

        if data.id == SEC_CODE:
            for i, func in enumerate(data.payload.bodies):
                depth = 1
                print('{x} sub_{id:04X} {x}'.format(x='=' * 35, id=i))
                for insn in decode(func.code):
                    if insn.op.flags & INSN_LEAVE_BLOCK:
                        depth -= 1

                    if insn.op.id == OP_CALL:
                        pass

                    print(' ' * (depth * 2) + format_instruction(insn))

                    if insn.op.flags & INSN_ENTER_BLOCK:
                        depth += 1


