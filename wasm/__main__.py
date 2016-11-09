"""Testing & debug stuff."""
from __future__ import print_function, absolute_import, division, unicode_literals

import argparse
import sys

from .formatter import format_instruction
from .opcodes import INSN_ENTER_BLOCK, INSN_LEAVE_BLOCK, OP_CALL
from .modtypes import SEC_CODE
from .decode import decode_bytecode, decode_module


def dump():
    parser = argparse.ArgumentParser()
    parser.add_argument('wasm_file', type=str)
    parser.add_argument('--disas', action='store_true', help="Disassemble code")
    args = parser.parse_args()

    try:
        with open(args.wasm_file, 'rb') as raw:
            raw = raw.read()
    except IOError as exc:
        print("[-] Can't open input file: " + str(exc), file=sys.stderr)
        return

    mod_iter = iter(decode_module(raw))
    hdr, hdr_data = next(mod_iter)
    print(hdr.to_string(hdr_data))

    for cur_sec, cur_sec_data in mod_iter:
        print(cur_sec.to_string(cur_sec_data))

        if args.disas and cur_sec_data.id == SEC_CODE:
            for i, func in enumerate(cur_sec_data.payload.bodies):
                depth = 1
                print('{x} sub_{id:04X} {x}'.format(x='=' * 35, id=i))
                for insn in decode_bytecode(func.code):
                    if insn.op.flags & INSN_LEAVE_BLOCK:
                        depth -= 1

                    if insn.op.id == OP_CALL:
                        pass

                    print(' ' * (depth * 2) + format_instruction(insn))

                    if insn.op.flags & INSN_ENTER_BLOCK:
                        depth += 1
