from ...parsing.source_code import SourceCode
from .default_printer import IDefaultPrintable


class SourceCodePrinter(IDefaultPrintable):
    """Printer for Zig source code."""

    def print(self, target: SourceCode) -> str:
        return f"{self._dispatcher.configuration.line_ending}".join(
            self._dispatcher.print(content) for content in target.content
        )

    @staticmethod
    def target_type() -> type[SourceCode]:
        return SourceCode
