from zyntex.code_generation.premade import (
    SourceCodePrinter,
    VariablePrinter,
    FunctionPrinter,
    TypePrinter
)
from zyntex.code_generation import PrinterDispatcher
from zyntex.syntax import FunctionDeclaration, VariableDeclaration, TypeNode
from zyntex import SourceCode


class TestSourceCodePrinter:

    @classmethod
    def setup_class(cls):
        cls.source = SourceCode("""pub const ABC: comptime_int = 15;

pub fn testFunc(arg: [ABC]usize) void {
    _ = arg;
}
""")
        dispatcher = PrinterDispatcher()
        dispatcher.add(FunctionDeclaration, FunctionPrinter)
        dispatcher.add(VariableDeclaration, VariablePrinter)
        dispatcher.add(TypeNode, TypePrinter)
        cls.printer = SourceCodePrinter(dispatcher)

    def test_prints_source_code_with_default_configuration(self):
        assert self.printer.print(self.source) == """pub const ABC: comptime_int = 15;

pub fn testFunc(arg: [ABC]usize) void {
    _ = arg;
}"""

    def test_prints_source_code_with_custom_line_ending(self):
        self.printer.dispatcher.configuration.line_ending = "\n"
        assert self.printer.print(self.source) == """pub const ABC: comptime_int = 15;
pub fn testFunc(arg: [ABC]usize) void {
    _ = arg;
}"""
        self.printer.dispatcher.configuration.line_ending = "\n\n"

