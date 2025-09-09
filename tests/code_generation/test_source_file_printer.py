from pathlib import Path

from zyntex.code_generation.premade import SourceFilePrinter, VariablePrinter, TestPrinter
from zyntex.code_generation import PrinterDispatcher
from zyntex.syntax import TestDeclaration, VariableDeclaration
from zyntex import SourceFile


class TestSourceFilePrinter:

    @classmethod
    def setup_class(cls):
        cls.file = SourceFile(
            str(Path(__file__).resolve().parent / "test_sources" / "tests.zig")
        )
        dispatcher = PrinterDispatcher()
        dispatcher.add(TestDeclaration, TestPrinter)
        dispatcher.add(VariableDeclaration, VariablePrinter)
        cls.printer = SourceFilePrinter(dispatcher)

    def test_prints_source_file_with_default_configuration(self):
        assert self.printer.print(self.file).replace("\r\n", "\n") == """const std = @import("std");

test "Empty test" {}

test "assert example" {
    std.testing.assert(2 + 2 == 4);
}"""

    def test_prints_source_file_with_custom_line_ending(self):
        self.printer.dispatcher.configuration.line_ending = "\n"
        assert self.printer.print(self.file).replace("\r\n", "\n") == """const std = @import("std");
test "Empty test" {}
test "assert example" {
    std.testing.assert(2 + 2 == 4);
}"""
        self.printer.dispatcher.configuration.line_ending = "\n\n"

