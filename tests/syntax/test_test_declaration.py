from typing import cast
from zyntex import SourceCode


class TestTestDeclaration:

    def test_empty_test(self):
        from zyntex.syntax import TestDeclaration

        code = SourceCode("test \"empty\" {}")
        assert len(code.content) == 1
        function_decl: TestDeclaration = cast(TestDeclaration, code.content[0])
        assert function_decl.name == "\"empty\""
        assert function_decl.body == "{}"
