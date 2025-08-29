from zyntex import SourceCode
from zyntex.syntax import VariableDeclaration

src = SourceCode("const result: usize = 15 + 15;")

for content in src.content:
    if isinstance(content, VariableDeclaration):
        print(content.name)  # result
        print(content.const)  # True
