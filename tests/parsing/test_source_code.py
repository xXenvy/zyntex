from typing import cast

from zyntex.parsing.syntax import FunctionDeclaration
from zyntex.parsing.bindings import PrimitiveType
from zyntex.parsing import SourceCode


class TestSourceCode:

    def test_basic_usage(self):
        code = SourceCode("fn testing() void {}")
        assert len(code.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, code.content[0])
        assert function_decl.name == "testing"
        assert function_decl.is_public is False
        assert function_decl.body == "{}"

        assert function_decl.return_type.is_type()
        assert not function_decl.return_type.const
        assert function_decl.return_type.absolute_type == PrimitiveType.void
