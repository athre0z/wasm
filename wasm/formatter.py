"""Defines functions converting raw instructions into textual form."""
from __future__ import print_function, absolute_import, division, unicode_literals

import itertools

from .opcodes import INSN_LEAVE_BLOCK, INSN_ENTER_BLOCK
from .decode import decode_bytecode
from .wasmtypes import VAL_TYPE_I32, VAL_TYPE_I64, VAL_TYPE_F32, VAL_TYPE_F64, MUTABLE, IMMUTABLE


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

_mutability_str_mapping = {
    MUTABLE: "mut",
    IMMUTABLE: ""
}

def format_mutability(mutability):
    """Takes a value type `int`, returning its string representation."""
    try:
        return _mutability_str_mapping[mutability]
    except KeyError:
        raise ValueError('Bad value for value type ({})'.format(mutability))

_lang_type_str_mapping = {
    VAL_TYPE_I32: 'i32',
    VAL_TYPE_I64: 'i64',
    VAL_TYPE_F32: 'f32',
    VAL_TYPE_F64: 'f64',
}


def format_lang_type(lang_type):
    """Takes a value type `int`, returning its string representation."""
    try:
        return _lang_type_str_mapping[lang_type]
    except KeyError:
        raise ValueError('Bad value for value type ({})'.format(lang_type))


def format_function(
    func_body,
    func_type=None,
    indent=2,
    format_locals=True,
):
    """
    Takes a `FunctionBody` and optionally a `FunctionType`, yielding the string 
    representation of the function line by line. The function type is required
    for formatting function parameter and return value information.
    """
    if func_type is None:
        yield 'func'
    else:
        param_section = ' (param {})'.format(' '.join(
            map(format_lang_type, func_type.param_types)
        )) if func_type.param_types else ''
        result_section = ' (result {})'.format(
            format_lang_type(func_type.return_type)
        ) if func_type.return_type else ''
        yield 'func' + param_section + result_section

    if format_locals and func_body.locals:
        yield '(locals {})'.format(' '.join(itertools.chain.from_iterable(
            itertools.repeat(format_lang_type(x.type), x.count)
            for x in func_body.locals
        )))

    level = 1
    for cur_insn in decode_bytecode(func_body.code):
        if cur_insn.op.flags & INSN_LEAVE_BLOCK:
            level -= 1
        yield ' ' * (level * indent) + format_instruction(cur_insn)
        if cur_insn.op.flags & INSN_ENTER_BLOCK:
            level += 1
