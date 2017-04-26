"""Testing & debug stuff."""
from __future__ import print_function, absolute_import, division, unicode_literals

import argparse
import sys

from .formatter import format_function
from .modtypes import SEC_CODE, SEC_TYPE, SEC_FUNCTION, Section
from .decode import decode_module


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

    # Parse & print header.
    mod_iter = iter(decode_module(raw, decode_name_subsections=False))
    hdr, hdr_data = next(mod_iter)
    print(hdr.to_string(hdr_data))

    # Parse & print other sections.
    code_sec = None
    type_sec = None
    func_sec = None
    for cur_sec, cur_sec_data in mod_iter:
        print(cur_sec.to_string(cur_sec_data))
        if type(cur_sec) == Section:
            if cur_sec_data.id == SEC_CODE:
                code_sec = cur_sec_data.payload
            elif cur_sec_data.id == SEC_TYPE:
                type_sec = cur_sec_data.payload
            elif cur_sec_data.id == SEC_FUNCTION:
                func_sec = cur_sec_data.payload

    # If ordered to disassemble, do so.
    # TODO: We might want to make use of debug names, if available.
    if args.disas and code_sec is not None:
        for i, func_body in enumerate(code_sec.bodies):
            print('{x} sub_{id:04X} {x}'.format(x='=' * 35, id=i))

            # If we have type info, use it.
            func_type = type_sec.entries[func_sec.types[i]] if (
                None not in (type_sec, func_sec)
            ) else None

            print()
            print('\n'.join(format_function(func_body, func_type)))
            print()
