from typing import cast
from pathlib import Path

from zyntex.code_generation.premade import DefaultCodePrinter, FunctionParamPrinter, FunctionPrinter
from zyntex.code_generation import PrinterDispatcher
from zyntex.parsing.syntax import FunctionDeclaration
from zyntex.parsing import SourceFile, SourceCode


class TestFunctionPrinter:

    @classmethod
    def setup_class(cls):
        cls.file = SourceFile(
            str(Path(__file__).resolve().parent / "test_sources" / "functions.zig")
        )
        dispatcher = PrinterDispatcher()
        dispatcher.add(FunctionDeclaration.FunctionParam, FunctionParamPrinter)
        cls.printer = FunctionPrinter(dispatcher)

    def test_file_basic_functions_print(self):
        public_function: FunctionDeclaration = cast(FunctionDeclaration, self.file.content[0])
        assert self.printer.print(public_function).replace("\r\n", "\n") == """
pub fn publicTestFunc() usize {
    return 1;
}""".strip()

        private_function: FunctionDeclaration = cast(FunctionDeclaration, self.file.content[1])
        assert self.printer.print(private_function).replace("\r\n", "\n") == """
fn privateTestFunc(x: usize) usize {
    return x;
}""".strip()

    def test_file_extern_functions_print(self):
        public_function: FunctionDeclaration = cast(FunctionDeclaration, self.file.content[2])
        assert self.printer.print(public_function).replace("\r\n", "\n") == """
pub extern fn publicExternTest(a: usize) !void;""".strip()

        private_function: FunctionDeclaration = cast(FunctionDeclaration, self.file.content[3])
        assert self.printer.print(private_function) == "extern fn privateExternTest() usize;"

    def test_file_export_functions_print(self):
        public_function: FunctionDeclaration = cast(FunctionDeclaration, self.file.content[4])
        assert self.printer.print(public_function).replace("\r\n", "\n") == """
pub export fn publicExportTest(a: ?*u32, b: *myStruct) void {
    _ = a;
    _ = b;
}""".strip()

        private_function: FunctionDeclaration = cast(FunctionDeclaration, self.file.content[5])
        assert self.printer.print(private_function) == "export fn privateExportTest() usize {}"

    def test_file_function_params_print(self):
        function: FunctionDeclaration = cast(FunctionDeclaration, self.file.content[7])
        assert self.printer.print(function).replace("\r\n", "\n") == """
fn testFuncParams(abc: ?usize, comptime len: u32) !void {}
""".strip()

    def test_generic_noalias_and_variadic_parameters(self):
        sources = [
            "fn f(comptime T: type, x: anytype, noalias p: *T) !?T {}",
            "extern fn f(u8, noalias *u8, ...) void;",
            "extern fn f(...) void;",
            "fn f(x: fn(anytype) !u8) E!?[]const u8 {}",
        ]
        for source in sources:
            code = SourceCode(source)
            assert code.errors == []
            function = cast(FunctionDeclaration, code.content[0])
            generated = self.printer.print(function)
            assert generated == source

    def test_edit_parameter_and_return_type(self):
        return_type = "! // inferred error set\n    ?[:0]const u8"
        source = f"fn f(callback: *const fn(u8) void) {return_type} {{}}"
        code = SourceCode(source)
        assert code.errors == []
        function = cast(FunctionDeclaration, code.content[0])
        assert function.params[0].type == "*const fn(u8) void"
        assert function.return_type == return_type
        assert self.printer.print(function) == source

        function.params[0].type = "*const fn(u16) void"
        assert DefaultCodePrinter().print(function.params[0]) == "callback: *const fn(u16) void"
        function.return_type = "E!void"
        assert self.printer.print(function) == "fn f(callback: *const fn(u16) void) E!void {}"
