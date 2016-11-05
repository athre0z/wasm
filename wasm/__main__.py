from __future__ import print_function, absolute_import, division, unicode_literals

from .structs import ModuleHeader, Section


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
