from __future__ import print_function, absolute_import, division, unicode_literals

from .modtypes import ModuleHeader, Section
from .decode import decode

if False:
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

        #if data.id == 10:
        #    print(repr(data.payload.bodies[0].pad.tolist()))
        #    break
else:
    bytecode = bytearray((
        2, 127, 35, 10, 33, 1, 35, 10, 32, 0, 106, 36, 10, 35, 10, 65,
        15, 106, 65, 112, 113, 36, 10, 35, 10, 35, 11, 78, 4, 64, 32,
        0, 16, 3, 11, 32, 1, 15, 11, 11
    ))

    dec = decode(bytecode)
    depth = 0
    for insn in dec:
        if insn.op.mnemonic in ('end', 'return', 'else'):
            depth -= 1

        print('{}{} {}'.format(
            ' ' * (depth * 2),
            insn.op.mnemonic,
            ', '.join([
                getattr(insn.op.imm_struct, x[0]).to_string(getattr(insn.imm, x[0]))
                for x in insn.op.imm_struct._meta.fields
            ]) if insn.imm else ''
        ))

        if insn.op.mnemonic in ('block', 'if', 'else'):
            depth += 1
