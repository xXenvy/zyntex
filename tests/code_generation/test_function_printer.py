from typing import cast
from pathlib import Path

from zyntex.code_generation.premade import FunctionPrinter, TypePrinter
from zyntex.code_generation import PrinterDispatcher
from zyntex.parsing.syntax import FunctionDeclaration, TypeNode
from zyntex.parsing import SourceFile


class TestFunctionPrinter:

    @classmethod
    def setup_class(cls):
        cls.file = SourceFile(
            str(Path(__file__).resolve().parent / "test_sources" / "functions.zig")
        )
        dispatcher = PrinterDispatcher()
        dispatcher.add(TypeNode, TypePrinter)
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
pub extern fn publicExternTest(a: usize) void;""".strip()

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
