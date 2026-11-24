from zyntex.code_generation.premade import (
    SourceCodePrinter,
    VariablePrinter,
    FunctionPrinter,
    FunctionParamPrinter,
)
from zyntex.code_generation import PrinterDispatcher
from zyntex.parsing.syntax import FunctionDeclaration, VariableDeclaration
from zyntex.parsing import SourceCode


class TestSourceCodePrinter:

    @classmethod
    def setup_class(cls):
        cls.source = SourceCode("""pub const ABC: comptime_int = 15;

pub fn testFunc(arg: [ABC]usize) void {
    _ = arg;
}
""")
        cls.dispatcher = PrinterDispatcher()
        cls.dispatcher.add(FunctionDeclaration, FunctionPrinter)
        cls.dispatcher.add(FunctionDeclaration.FunctionParam, FunctionParamPrinter)
        cls.dispatcher.add(VariableDeclaration, VariablePrinter)
        cls.printer = SourceCodePrinter(cls.dispatcher)

    def test_prints_source_code_with_default_configuration(self):
        assert self.printer.print(self.source) == """pub const ABC: comptime_int = 15;

pub fn testFunc(arg: [ABC]usize) void {
    _ = arg;
}"""

    def test_prints_source_code_with_custom_line_ending(self):
        self.dispatcher.configuration.line_ending = "\n"
        assert self.printer.print(self.source) == """pub const ABC: comptime_int = 15;
pub fn testFunc(arg: [ABC]usize) void {
    _ = arg;
}"""

