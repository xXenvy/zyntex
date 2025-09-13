from typing import cast

from zyntex.parsing.syntax import VariableDeclaration
from zyntex.parsing import SourceCode

src = SourceCode("const result: usize = 15 + 15;")
variable = cast(VariableDeclaration, src.content[0])

print(variable.name)  # result
print(variable.is_const)  # True
