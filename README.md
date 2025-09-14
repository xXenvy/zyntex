# Zyntex - Zig code parser for Python
![Downloads](https://img.shields.io/pypi/dm/zyntex?style=flat-square&color=%234287f5)
![License](https://img.shields.io/github/license/xXenvy/zyntex?style=flat-square&color=%234287f5)
![Python Version](https://img.shields.io/pypi/pyversions/zyntex?style=flat-square&color=%234287f5)
![Zig](https://img.shields.io/badge/zig-v0.15.1-0074C1?style=flat-square&?logo=zig&logoColor=white&color=%234287f5)

Zyntex is a Python library that allows you to parse and generate Zig code at a high level.
Function bodies and other low-level elements are currently returned as raw strings.
Currently, it can parse Zig code written in version **0.15.1** - the
supported parsing version will be continuously updated in the future.

Internally, it uses bindings to Zig's std AST parser, making it both fast and memory-efficient.
**Important:** currently bindings are only available for `windows-x86_64`, `macos-x86_64`, and `linux-x86_64`.
For more information, read the [docs](https://zyntex.readthedocs.io/en/stable).

**Be aware that the project is at a very early stage of development
and is actively being developed.**

## Features
- Parse Zig source from strings or files.
- Code generation - emitting Zig code from Python objects via premade printers.
- High-performance, low-memory parsing powered by Zig’s `std` parser.
- Easy-to-use, Pythonic API designed for inspection Zig code.
- Zero-dependency - the project requires no external dependencies on either the Zig side or the Python side.

## Installation
```bash
pip install zyntex
```

## Minimal example
```python
from typing import cast

from zyntex.code_generation.premade import DefaultCodePrinter
from zyntex.parsing.syntax import VariableDeclaration
from zyntex.parsing import SourceCode

code_printer = DefaultCodePrinter()
src = SourceCode("const result: usize = 15 + 15;")

variable = cast(VariableDeclaration, src.content[0])
variable.is_public = True
print(code_printer.print(src)) # pub const result: usize = 15 + 15;
```
