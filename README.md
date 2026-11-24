# Zyntex - Zig parsing and code generation for Python

**Parse, inspect, and generate Zig code from Python.**

[![Python](https://img.shields.io/pypi/pyversions/zyntex?style=flat-square&color=4287f5)](https://pypi.org/project/zyntex/) [![Zig](https://img.shields.io/badge/Zig-0.17.1-4287f5?style=flat-square&logoColor=white)](https://ziglang.org/) [![Downloads](https://img.shields.io/pypi/dm/zyntex?style=flat-square&color=4287f5)](https://pypi.org/project/zyntex/) [![License](https://img.shields.io/github/license/xXenvy/zyntex?style=flat-square&color=4287f5)](https://github.com/xXenvy/zyntex/blob/master/LICENSE)

[Documentation](https://zyntex.readthedocs.io/en/stable/)
· [Examples](https://github.com/xXenvy/zyntex/tree/master/examples)
· [Contributing](https://zyntex.readthedocs.io/en/stable/contributing.html)

Zyntex wraps Zig's standard AST parser and exposes Python objects for working with
source code. Inspect declarations, edit their properties, and emit Zig code using
the built-in printers.

> Zyntex is in early development. Breaking API changes are expected.

## Features

- **Parse source** from strings, files, or directories of Zig files.
- **Inspect and edit top-level elements** - parsing is currently limited to this level.
- **Generate Zig code** from Python objects with built-in or custom printers.
- **Defer parsing** until needed, or parse multiple files concurrently.
- **No Python runtime dependencies**, with native bindings to Zig's standard parser.

Type annotations and declaration bodies are exposed as Zig source strings.

## Installation

```bash
pip install zyntex
```

Requirements:

- **Python 3.9+**.
- **Windows, Linux, or macOS on x86_64**. Other CPU architectures are not yet supported.

## Quick start

```python
from typing import cast

from zyntex.code_generation.premade import DefaultCodePrinter
from zyntex.parsing import SourceCode
from zyntex.parsing.syntax import VariableDeclaration

source = SourceCode("const count: u32 = 42;")
variable = cast(VariableDeclaration, source.content[0])

variable.is_public = True
variable.type_hint = "u64"

print(DefaultCodePrinter().print(source))
```

Output:

```zig
pub const count: u64 = 42;
```

For a larger example, see the [Zig code linter](https://github.com/xXenvy/zyntex/tree/master/examples/zig_code_linter).

## Development

- `python/` — Python package, tests, and packaging configuration.
- `zig/` — native library, tests, and AST enum generator.
- `tools/` — native library and documentation build scripts.
- `docs/` — documentation sources.
- `examples/` — usage examples.

See the [contributing guide](https://zyntex.readthedocs.io/en/stable/contributing.html)
for setup, building native libraries, and running tests.

