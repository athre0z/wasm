"""Defines functions converting raw instructions into textual form."""
from __future__ import print_function, absolute_import, division, unicode_literals


def format_instruction(insn):
    """
    Takes a raw `Instruction` and translates it into a human readable text
    representation. As of writing, the text representation for WASM is not yet
    standardized, so we just emit some generic format.
    """
    text = insn.op.mnemonic

    if not insn.imm:
        return text

    return text + ' ' + ', '.join([
        getattr(insn.op.imm_struct, x.name).to_string(
            getattr(insn.imm, x.name)
        )
        for x in insn.op.imm_struct._meta.fields
    ])
