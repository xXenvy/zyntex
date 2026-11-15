from typing import cast
from zyntex.parsing import SourceCode


class TestTestDeclaration:

    def test_empty_test(self):
        from zyntex.parsing.syntax import TestDeclaration

        code = SourceCode("test \"empty\" {}")
        assert len(code.content) == 1
        function_decl: TestDeclaration = cast(TestDeclaration, code.content[0])
        assert function_decl.name == "\"empty\""
        assert function_decl.body == "{}"

    def test_anonymous_empty_test(self):
        from zyntex.parsing.syntax import TestDeclaration

        code = SourceCode("test {}")
        assert len(code.content) == 1
        function_decl: TestDeclaration = cast(TestDeclaration, code.content[0])
        assert function_decl.name is None
        assert function_decl.body == "{}"
