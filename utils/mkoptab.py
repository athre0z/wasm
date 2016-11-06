import re

for line in open('insns'):
    m = re.search(r'^\| `(.*?)` \| `(0x.*?)`', line)
    if m:
        mnem, op = m.groups()
        l = "    Opcode({}, '{}',".format(op, mnem)
        r = "None),"
        print(l.ljust(40) + r)
    else:
        print()
