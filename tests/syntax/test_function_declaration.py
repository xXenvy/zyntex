from typing import cast

from zyntex import SourceCode
from zyntex.syntax import FunctionDeclaration
from zyntex.bindings import PrimitiveType


class TestFunctionDeclaration:

    def test_public_function(self):
        code = SourceCode("pub fn testFunc() usize { return 10; }")
        assert len(code.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, code.content[0])
        assert function_decl.name == "testFunc"
        assert function_decl.is_public is True
        assert function_decl.is_extern is False
        assert function_decl.is_export is False
        assert function_decl.body == "{ return 10; }"
        assert function_decl.params == []
        assert function_decl.return_type.is_type()
        assert function_decl.return_type.const is False
        assert function_decl.return_type.absolute_type == PrimitiveType.usize

    def test_private_function(self):
        code = SourceCode("fn testFunc() void { const a = 10;\n_ = a; }")
        assert len(code.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, code.content[0])
        assert function_decl.name == "testFunc"
        assert function_decl.is_public is False
        assert function_decl.is_extern is False
        assert function_decl.is_export is False
        assert function_decl.body == "{ const a = 10;\n_ = a; }"
        assert function_decl.params == []
        assert function_decl.return_type.is_type()
        assert function_decl.return_type.const is False
        assert function_decl.return_type.absolute_type == PrimitiveType.void

    def test_function_params(self):
        code = SourceCode("fn testFunc(a: usize, b: usize) usize { return a + b; }")
        assert len(code.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, code.content[0])
        assert function_decl.name == "testFunc"
        assert function_decl.is_public is False
        assert function_decl.is_extern is False
        assert function_decl.is_export is False
        assert function_decl.body == "{ return a + b; }"

        assert function_decl.return_type.is_type()
        assert function_decl.return_type.const is False
        assert function_decl.return_type.absolute_type == PrimitiveType.usize

        assert len(function_decl.params) == 2
        assert function_decl.params[0].name == "a"
        assert function_decl.params[1].name == "b"

        assert function_decl.params[0].type.is_type()
        assert function_decl.params[0].type.const is False
        assert function_decl.params[0].type.absolute_type == PrimitiveType.usize

        assert function_decl.params[1].type.is_type()
        assert function_decl.params[1].type.const is False
        assert function_decl.params[1].type.absolute_type == PrimitiveType.usize

    def test_function_extern(self):
        code = SourceCode("pub extern fn testing(a: *const u32) ?void;")
        assert len(code.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, code.content[0])
        assert function_decl.name == "testing"
        assert function_decl.is_public is True
        assert function_decl.body is None
        assert function_decl.is_extern is True
        assert function_decl.is_export is False

        assert function_decl.return_type.is_optional()
        assert function_decl.return_type.is_type() is False
        assert function_decl.return_type.const is False
        assert function_decl.return_type.optional_type.type == PrimitiveType.void
        assert function_decl.return_type.absolute_type == PrimitiveType.void

        assert len(function_decl.params) == 1
        assert function_decl.params[0].type.is_pointer()
        assert function_decl.params[0].type.const is False
        assert function_decl.params[0].type.pointer_type.const
        assert function_decl.params[0].type.pointer_type.type == PrimitiveType.u32
        assert function_decl.params[0].type.absolute_type == PrimitiveType.u32

    def test_function_export(self):
        code = SourceCode("pub export fn testExport() *void {}")
        assert len(code.content) == 1
        function_decl: FunctionDeclaration = cast(FunctionDeclaration, code.content[0])
        assert function_decl.name == "testExport"
        assert function_decl.is_public is True
        assert function_decl.body == "{}"
        assert function_decl.is_extern is False
        assert function_decl.is_export is True
        assert function_decl.return_type.is_type() is False
        assert function_decl.return_type.const is False
        assert function_decl.return_type.is_pointer()
        assert function_decl.return_type.pointer_type.type == PrimitiveType.void
        assert function_decl.return_type.absolute_type == PrimitiveType.void
        assert len(function_decl.params) == 0
