from typing import cast
from pathlib import Path

from zyntex.code_generation.premade import TestPrinter
from zyntex.code_generation import PrinterDispatcher
from zyntex.syntax import TestDeclaration
from zyntex import SourceFile


class TestTestPrinter:

    @classmethod
    def setup_class(cls):
        cls.file = SourceFile(
            str(Path(__file__).resolve().parent / "test_sources" / "tests.zig")
        )
        cls.printer = TestPrinter(PrinterDispatcher())

    def test_empty_test(self):
        empty_test = cast(TestDeclaration, self.file.content[1])
        assert self.printer.print(empty_test) == "test \"Empty test\" {}"

    def test_basic_test(self):
        basic_test = cast(TestDeclaration, self.file.content[2])
        assert self.printer.print(basic_test).replace("\r\n", "\n") == """
test "assert example" {
    std.testing.assert(2 + 2 == 4);
}
""".strip()

    def test_basic_anonymous_test(self):
        anonymous_test = TestDeclaration(name=None, body="{ std.debug.print(\"ABC\", .{}); }")
        assert self.printer.print(anonymous_test) == "test { std.debug.print(\"ABC\", .{}); }"
