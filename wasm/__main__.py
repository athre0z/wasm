"""Testing & debug stuff."""
from __future__ import print_function, absolute_import, division, unicode_literals

from .modtypes import ModuleHeader, Section, SEC_CODE
from .decode import decode

with open('demo/hello/hello.wasm', 'rb') as f:
    d = memoryview(f.read())

hdr = ModuleHeader()
offs, data = hdr.from_raw(None, d)
print(hdr.to_string(data))

biggest_func = []
while offs != len(d):
    sec = Section()
    size, data = sec.from_raw(None, d[offs:])
    print(sec.to_string(data))
    offs += size

    if data.id == SEC_CODE:
        for func in data.payload.bodies:
            if len(func.pad) > len(biggest_func):
                biggest_func = func.pad
        break

print()

bytecode = bytearray([
    2, 127, 35, 10, 33, 130, 9,
])

depth = 0
for insn in decode(bytecode):
    if insn.op.mnemonic in ('end', 'return', 'else'):
        depth = max(0, depth - 1)

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
