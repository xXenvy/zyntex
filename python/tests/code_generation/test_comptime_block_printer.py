from typing import cast
from pathlib import Path

from zyntex.code_generation.premade import ComptimeBlockPrinter, DefaultCodePrinter
from zyntex.code_generation import PrinterDispatcher
from zyntex.parsing.syntax import ComptimeBlock
from zyntex.parsing import SourceFile


class TestComptimeBlockPrinter:

    @classmethod
    def setup_class(cls):
        cls.file = SourceFile(
            str(Path(__file__).resolve().parent / "test_sources" / "comptime.zig")
        )
        cls.printer = ComptimeBlockPrinter(PrinterDispatcher())

    def test_basic_comptime_block(self):
        comptime_block: ComptimeBlock = cast(ComptimeBlock, self.file.content[1])
        assert self.printer.print(comptime_block).replace("\r\n", "\n") == """
comptime {
    var suma: usize = 0;
    suma += 1;
}
""".strip()

    def test_default_comptime_block_printer(self):
        printer = DefaultCodePrinter()
        assert printer.print(self.file).replace("\r\n", "\n") == """
comptime {}

comptime {
    var suma: usize = 0;
    suma += 1;
}
""".strip()
