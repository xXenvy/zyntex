from typing import cast

from zyntex import SourceCode
from zyntex.syntax import FunctionDeclaration
from zyntex.bindings import PrimitiveType


class TestSourceCode:

    def test_basic_usage(self):
        code = SourceCode("fn testing() void {}")
        assert len(code.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, code.content[0])
        assert function_decl.name == "testing"
        assert function_decl.public is False
        assert function_decl.body == "{}"

        assert function_decl.return_type.is_type()
        assert not function_decl.return_type.is_const()
        assert function_decl.return_type.absolute_type == PrimitiveType.void
