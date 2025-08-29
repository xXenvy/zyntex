from typing import cast

from zyntex.syntax import VariableDeclaration
from zyntex import SourceCode

src = SourceCode("const result: usize = 15 + 15;")
variable = cast(VariableDeclaration, src.content[0])

print(variable.name)  # result
print(variable.const)  # True
