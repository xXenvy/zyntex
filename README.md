# Zyntex - High-level Zig parser for Python
Zyntex focuses on high-level elements of Zig code (e.g. functions, variables, tests).
Function bodies and other low-level constructs are currently returned as raw strings.
Support for deeper elements is planned. Internally, it uses bindings to Zig's std AST parser,
making it both fast and memory-efficient.
Important: currently bindings are only available for `windows-x86_64`, `macos-x86_64`, and `linux-x86_64`.
On other architectures the library will not work. Support for additional targets is planned, 
but low priority.

## Features

- Parse Zig source from strings or files.
- High-performance, low-memory parsing powered by Zig’s `std` parser.
- Easy-to-use, Pythonic API designed for inspection and transformation of Zig code.
- Planned: code generation (printers) to emit Zig from Python objects.

## Installation

```bash
pip install zyntex
```

## Minimal example
```python
from typing import cast

from zyntex.syntax import VariableDeclaration
from zyntex import SourceCode

src = SourceCode("const result: usize = 15 + 15;")
variable = cast(VariableDeclaration, src.content[0])

print(variable.name)  # result
print(variable.const)  # True
```

## License
See the `LICENSE` file in the repository.

---
For questions or contributions, open an issue or PR on the project repository.
