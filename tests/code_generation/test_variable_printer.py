from typing import cast
from pathlib import Path

from zyntex.code_generation.premade import VariablePrinter, TypePrinter
from zyntex.code_generation import PrinterDispatcher
from zyntex.syntax import VariableDeclaration, TypeNode
from zyntex import SourceFile


class TestVariablePrinter:

    @classmethod
    def setup_class(cls):
        cls.file = SourceFile(
            str(Path(__file__).resolve().parent / "test_sources" / "variables.zig")
        )
        dispatcher = PrinterDispatcher()
        dispatcher.add(TypeNode, TypePrinter)
        cls.printer = VariablePrinter(dispatcher)

    def test_simple_variables(self):
        std_var = cast(VariableDeclaration, self.file.content[0])
        assert self.printer.print(std_var) == "const std = @import(\"std\");"

        public_var = cast(VariableDeclaration, self.file.content[1])
        assert self.printer.print(public_var) == "pub const publicVariable: comptime_int = 10;"

        public_optional_var = cast(VariableDeclaration, self.file.content[2])
        assert self.printer.print(public_optional_var) == "pub var publicOptionalVariable: ?usize = null;"

    def test_extern_variables(self):
        extern_private = cast(VariableDeclaration, self.file.content[3])
        assert self.printer.print(extern_private) == "extern const externPrivateVariable: ?*[2]usize;"

        extern_public = cast(VariableDeclaration, self.file.content[4])
        assert self.printer.print(extern_public) == "pub extern var externPublicVariable: *?*void;"

    def test_export_variables(self):
        export_public = cast(VariableDeclaration, self.file.content[5])
        assert self.printer.print(export_public) == "pub export var exportPublicVariable: u32 = 15;"

        export_private = cast(VariableDeclaration, self.file.content[6])
        assert self.printer.print(export_private) == "export const exportPrivateVariable: i32 = -25;"
