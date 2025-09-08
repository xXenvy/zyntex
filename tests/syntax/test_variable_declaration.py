from typing import cast

from zyntex import SourceCode
from zyntex.syntax import VariableDeclaration
from zyntex.bindings import PrimitiveType


class TestVariableDeclaration:

    def test_simple_variable_decl(self):
        code = SourceCode("var x = 15;")
        assert len(code.content) == 1
        variable_decl: VariableDeclaration = cast(VariableDeclaration, code.content[0])
        assert variable_decl.name == "x"
        assert variable_decl.is_const is False
        assert variable_decl.is_public is False
        assert variable_decl.is_export is False
        assert variable_decl.is_extern is False
        assert variable_decl.type_hint is None
        assert variable_decl.value == "15"
        assert variable_decl.alignment is None

    def test_constant_variable_decl(self):
        code = SourceCode("const x: usize = 15;")
        assert len(code.content) == 1
        variable_decl: VariableDeclaration = cast(VariableDeclaration, code.content[0])
        assert variable_decl.name == "x"
        assert variable_decl.is_const is True
        assert variable_decl.is_public is False
        assert variable_decl.is_export is False
        assert variable_decl.is_extern is False
        assert variable_decl.type_hint.absolute_type == PrimitiveType.usize
        assert variable_decl.value == "15"
        assert variable_decl.alignment is None

    def test_public_variable_decl(self):
        code = SourceCode("pub const X: usize = 25;")
        assert len(code.content) == 1
        variable_decl: VariableDeclaration = cast(VariableDeclaration, code.content[0])
        assert variable_decl.name == "X"
        assert variable_decl.is_const is True
        assert variable_decl.is_public is True
        assert variable_decl.is_export is False
        assert variable_decl.is_extern is False
        assert variable_decl.type_hint.absolute_type == PrimitiveType.usize
        assert variable_decl.value == "25"
        assert variable_decl.alignment is None

    def test_aligned_variable_decl(self):
        code = SourceCode("const abc align(8) = 100;")
        assert len(code.content) == 1
        variable_decl: VariableDeclaration = cast(VariableDeclaration, code.content[0])
        assert variable_decl.name == "abc"
        assert variable_decl.is_const is True
        assert variable_decl.is_public is False
        assert variable_decl.type_hint is None
        assert variable_decl.is_export is False
        assert variable_decl.is_extern is False
        assert variable_decl.value == "100"
        assert variable_decl.alignment == "8"

    def test_export_variable_decl(self):
        code = SourceCode("export var ABC: i64 = 12;")
        assert len(code.content) == 1
        variable_decl: VariableDeclaration = cast(VariableDeclaration, code.content[0])
        assert variable_decl.name == "ABC"
        assert variable_decl.is_const is False
        assert variable_decl.is_public is False
        assert variable_decl.type_hint.absolute_type == PrimitiveType.i64
        assert variable_decl.is_export is True
        assert variable_decl.is_extern is False
        assert variable_decl.value == "12"
        assert variable_decl.alignment is None

    def test_extern_variable_decl(self):
        code = SourceCode("extern const X: usize;")
        assert len(code.content) == 1
        variable_decl: VariableDeclaration = cast(VariableDeclaration, code.content[0])
        assert variable_decl.name == "X"
        assert variable_decl.is_const is True
        assert variable_decl.is_public is False
        assert variable_decl.type_hint.absolute_type == PrimitiveType.usize
        assert variable_decl.is_export is False
        assert variable_decl.is_extern is True
        assert variable_decl.value is None
        assert variable_decl.alignment is None
