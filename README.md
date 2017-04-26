wasm
====

Python module capable of decoding and disassembling WebAssembly modules 
and bytecode, according to the MVP specification of the WASM binary
format.

As there is no official text format defined yet, the text format 
implemented doesn't correspond to any existing definition and is a 
simple `mnemonic op1, op2, ...` format. Functions are formatted in a
way similar to how Google Chrome does in the debug console.

### Installation

```
# From PyPi
pip install wasm

# From GitHub
pip install git+https://github.com/athre0z/wasm.git
```

### Examples

Parsing a WASM module, printing the types of sections found.
```python
from wasm.decode import decode_module

with open('input-samples/hello/hello.wasm', 'rb') as raw:
    raw = raw.read()
    
mod_iter = iter(decode_module(raw))
header, header_data = next(mod_iter)

for cur_sec, cur_sec_data in mod_iter:
    print(cur_sec_data.get_decoder_meta()['types']['payload'])
```

Possible output:
```
<wasm.modtypes.TypeSection object at 0x10dec52e8>
<wasm.modtypes.ImportSection object at 0x10dec5320>
<wasm.modtypes.FunctionSection object at 0x10dec5358>
<wasm.modtypes.GlobalSection object at 0x10dec5400>
<wasm.modtypes.ExportSection object at 0x10dec5438>
<wasm.modtypes.ElementSection object at 0x10dec54a8>
<wasm.modtypes.CodeSection object at 0x10dec54e0>
<wasm.modtypes.DataSection object at 0x10dec5518>
```

Manually disassemble WASM bytecode, printing each instruction.
```python
from wasm.decode import decode_bytecode
from wasm.formatter import format_instruction
from wasm.opcodes import INSN_ENTER_BLOCK, INSN_LEAVE_BLOCK

raw = bytearray([2, 127, 65, 24, 16, 28, 65, 0, 15, 11])
indent = 0
for cur_insn in decode_bytecode(raw):
    if cur_insn.op.flags & INSN_LEAVE_BLOCK:
        indent -= 1
    print('  ' * indent + format_instruction(cur_insn))
    if cur_insn.op.flags & INSN_ENTER_BLOCK:
        indent += 1
```

Output:
```
block -1
  i32.const 24
  call 28
  i32.const 0
  return
end
```

### `wasmdump` command-line tool
The module also comes with a simple command-line tool called `wasmdump`, 
dumping all module struct in sexy tree format. Optionally, it also 
disassembles all functions found when invoked with `--disas` (slow).

### Version support
The library was successfully tested on Python 2.7, Python 3.5 and 
PyPy 5.4.
